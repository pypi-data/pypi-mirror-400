# SciDX Streaming – Filters

This document defines the **filter language** for SciDX Streaming:

- What users can write (structured filter definitions).
- How those are compiled into a normalized filter object.
- How that object plugs into `create_stream`.

Goals:

- **Predictable** – no hidden magic, no eval of user code.
- **Extensible** – geospatial, temporal, windowed logic can be layered later.
- **Portable** – compiled filters are JSON-serializable, stable, and safe to ship around.

---

## 1. Lifecycle and scope


sources → In memory DataFrame (after mapping?) → MAPPING RULES → FILTER RULES → derived Kafka topic


Two stages:

1. **Mapping rules** decide which columns to keep and how to rename them.
2. **Filter rules** (comparison + group) decide which rows survive.

Public surface:

- `StreamingClient.compile_filters(filter_definitions)`  
  Accepts a sequence of **mapping**, **comparison**, and **group** rules; returns a `CompiledFilters` object.
- `StreamingClient.create_stream(..., filters=compiled)`  
  Attaches compiled filters to a derived stream.

This Defined Sintax Layer (DSL) covers:

- Column-level selection and rename (mapping).
- Row inclusion/exclusion (comparison + group).

Anything beyond that (IF/THEN rules, window functions, transforms) is **out of scope** for now, but they will be able to be added as a new plug-in fitlering module.

---

## 2. Types of rules

There is **one structured way** to define filters. Every rule is a dict with a required `type`:

- `type = "mapping"`   → column-level mapping (drop/rename).
- `type = "comparison"`→ one comparison between a column and a value (or another column).
- `type = "group"`     → logical AND/OR over comparison/group rules.

`compile_filters` takes a **sequence** of such rules (in the order you want them applied).

At the top level:

- All rules are applied in order.
- Mapping rules affect the DataFrame schema for subsequent rules.
- Comparison and group rules are combined with a **global AND** for row inclusion.

---

## 3. Mapping rules

Mapping rules operate on **columns only**, before row filtering.

### 3.1. Purpose

- Select which columns to expose to downstream consumers.
- Rename columns without touching upstream resources.

### 3.2. Shape

```json
{
  "type": "mapping",
  "column": "raw_column_name",
  "action": "rename",
  "new_name": "canonical_name"
}
```

### 3.3. Fields

| Key           | Required                      | Type   | Meaning                                                         |
| ------------- | ----------------------------- | ------ | --------------------------------------------------------------- |
| `type`        | yes                           | string | Must be `"mapping"`.                                            |
| `column`      | yes                           | string | Original column name in the DataFrame before this mapping rule. |
| `action`      | yes                           | string | `"drop"` or `"rename"`.                                         |
| `new_name`    | required if `action="rename"` | string | New column name. Only used when `action = "rename"`.            |
| `description` | no                            | string | Optional human-readable description (for logs / UI).            |

### 3.4. Semantics

* `{"type": "mapping", "column": "temp_raw", "action": "drop"}`
  → Drop column `temp_raw` from the DataFrame.

* `{"type": "mapping", "column": "TEMP", "action": "rename", "new_name": "temperature"}`
  → Rename column `TEMP` to `temperature`.

If multiple mapping rules reference the same column, they are applied **in order**.

---

## 4. Comparison rules

Comparison rules operate on **single columns** and a right-hand side value (literal or another column).

### 4.1. Purpose

* Express simple predicates like `temperature > 25`, `state == "UT"`, `station_id in [...]`.
* Optionally compare two columns (e.g. `max_temp >= min_temp`).

### 4.2. Shape

```json
{
  "type": "comparison",
  "column": "value",
  "op": "gt",
  "value": 100,
  "keep_nulls": false
}
```

### 4.3. Fields

| Key               | Required | Type   | Meaning                                                                                                             |
| ----------------- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------- |
| `type`            | yes      | string | Must be `"comparison"`.                                                                                             |
| `column`          | yes      | string | Name of the column to read from the DataFrame (after all mapping rules).                                            |
| `op`              | yes      | string | Operator name, see [6. Operators](#6-operators).                                                                    |
| `value`           | yes      | any    | Right-hand side: literal value or *other column name* if value is a column.                                  |
| `keep_nulls`      | no       | bool   | If `false` (default), if the column value doesn't pass the filter, we delete the row, if 'true' we just change the value to null/NaN. |
| `description`     | no       | string | Optional description of the rule.                                                                                   |

Notes:

* Literal values can be numbers, strings, booleans, or anything JSON-serializable.
* Column-to-column comparison is supported automatically.

### 4.4. Examples

#### 4.4.1. Numeric literal comparison

```json
{
  "type": "comparison",
  "column": "value",
  "op": "gt",
  "value": 100
}
```

Semantics: keep rows where `value > 100` and `value` is not null.

#### 4.4.2. String equality

```json
{
  "type": "comparison",
  "column": "state",
  "op": "eq",
  "value": "UT",
  "keep_nulls": false
}
```

Semantics: keep rows where `state == "UT"`. Rows with `state` null are dropped.

#### 4.4.3. Column-to-column comparison

```json
{
  "type": "comparison",
  "column": "max_temp",
  "op": "gte",
  "value": "min_temp"
}
```

Semantics: keep rows where `max_temp >= min_temp`. Rows with either null will fail unless you explicitly set `keep_nulls: true`.

---

## 5. Group rules

Group rules combine **comparison** and **group** rules with boolean logic.

### 5.1. Purpose

* Express AND/OR logic and nesting.
* Example: `(state == "UT" AND value > 100) OR (state == "CO" AND value > 200)`.

### 5.2. Shape

```json
{
  "type": "group",
  "logic": "and",
  "rules": [
    { "type": "comparison", "column": "state", "op": "eq", "value": "UT" },
    { "type": "comparison", "column": "value", "op": "gt", "value": 100 }
  ],
  "keep_nulls": false
}
```

### 5.3. Fields

| Key           | Required | Type                 | Meaning                                                                                                       |
| ------------- | -------- | -------------------- | ------------------------------------------------------------------------------------------------------------- |
| `type`        | yes      | string               | Must be `"group"`.                                                                                            |
| `logic`       | yes      | string               | `"and"` or `"or"`.                                                                                            |
| `rules`       | yes      | list of rule objects | Children: comparison rules or nested group rules (future types can be added here without changing the shape). |
| `keep_nulls`  | no       | bool                 | Group-level null policy (see below). Default `false`.                                                         |
| `description` | no       | string               | Optional description of the group.                                                                            |

### 5.4. Null behavior (`keep_nulls`)

* For **comparison rules**, `keep_nulls = false` means: if the column value is null, the row **fails** this rule.
* For **group rules**, `keep_nulls` applies when **all** children that reference a given row return “failed due to nulls”:

  * `keep_nulls = false`: row fails the group.
  * `keep_nulls = true`: row passes the group even if values are null.

In practice, you can keep it simple:

* If you don’t care about nulls being kept at group-level, ignore `keep_nulls` on groups and use comparison-level `keep_nulls` only.

### 5.5. Examples

#### 5.5.1. Simple AND group

```json
{
  "type": "group",
  "logic": "and",
  "rules": [
    { "type": "comparison", "column": "state", "op": "eq", "value": "UT" },
    { "type": "comparison", "column": "value", "op": "gt", "value": 100 }
  ]
}
```

Semantics: `state == "UT" AND value > 100`.

#### 5.5.2. AND with nested OR

```json
{
  "type": "group",
  "logic": "and",
  "rules": [
    { "type": "comparison", "column": "state", "op": "eq", "value": "UT" },
    {
      "type": "group",
      "logic": "or",
      "rules": [
        { "type": "comparison", "column": "status", "op": "eq", "value": "Delayed" },
        { "type": "comparison", "column": "status", "op": "eq", "value": "Cancelled" }
      ]
    }
  ]
}
```

Semantics: `state == "UT" AND (status == "Delayed" OR status == "Cancelled")`.

---

## 6. Operators

These are the **supported operators** for now. All user input is normalized to these canonical names.

### 6.1. Canonical operators

| Operator  | Meaning                 | Example                                                                          |
| --------- | ----------------------- | -------------------------------------------------------------------------------- |
| `eq`      | Equal to                | `{"type": "comparison", "column": "status", "op": "eq", "value": "Active"}`      |
| `neq`     | Not equal to            | `{"type": "comparison", "column": "state", "op": "neq", "value": "CA"}`          |
| `gt`      | Greater than            | `{"type": "comparison", "column": "value", "op": "gt", "value": 100}`            |
| `gte`     | Greater than or equal   | `{"type": "comparison", "column": "score", "op": "gte", "value": 75}`            |
| `lt`      | Less than               | `{"type": "comparison", "column": "age", "op": "lt", "value": 18}`               |
| `lte`     | Less than or equal      | `{"type": "comparison", "column": "age", "op": "lte", "value": 65}`              |
| `in`      | Value is in a list      | `{"type": "comparison", "column": "id", "op": "in", "value": [1, 2, 3]}`         |
| `nin`     | Value is not in a list  | `{"type": "comparison", "column": "category", "op": "nin", "value": ["X", "Y"]}` |
| `between` | Between inclusive range | `{"type": "comparison", "column": "price", "op": "between", "value": [10, 20]}`  |

### 6.2. Normalization rules

To make calling code nicer, the compiler will normalize:

* Operator names are **case-insensitive**:

  * `"EQ"`, `"Eq"`, `"eq"` → `eq`
* Symbol forms and aliases are mapped to canonical names:

  * `"="`, `"=="`, `"eq"` → `eq`
  * `"!="`, `"<>"`, `"ne"`, `"neq"` → `neq`
  * `">"` → `gt`, `">="` → `gte`
  * `"<"` → `lt`, `"<="` → `lte`

If an operator cannot be normalized into one of the canonical names above, `compile_filters` should fail with a clear error.

---

## 7. Putting it together – full example

### 7.1. Example filter definition

```json
[
  {
    "type": "mapping",
    "column": "TEMP",
    "action": "rename",
    "new_name": "temperature"
  },
  {
    "type": "mapping",
    "column": "debug_info",
    "action": "drop"
  },
  {
    "type": "group",
    "logic": "and",
    "rules": [
      {
        "type": "comparison",
        "column": "state",
        "op": "eq",
        "value": "UT"
      },
      {
        "type": "comparison",
        "column": "temperature",
        "op": "gt",
        "value": 20
      },
      {
        "type": "comparison",
        "column": "quality_flag",
        "op": "neq",
        "value": "BAD",
        "keep_nulls": false
      }
    ]
  }
]
```

Semantics:

1. Rename `TEMP` → `temperature`.
2. Drop `debug_info`.
3. Keep rows where:

   * `state == "UT"`, **and**
   * `temperature > 20`, **and**
   * `quality_flag != "BAD"` and not null.

### 7.2. Usage

```python
filters_def = [...]  # as above
compiled = client.compile_filters(filters_def)

stream = client.create_stream(
    resource_ids=[...],
    filters=compiled,
)
```

Internally:

* Mapping rules are applied to each batch DataFrame.
* Comparison and group rules are evaluated to build a boolean mask.
* Only rows where the final mask is `True` are sent to the derived Kafka topic.