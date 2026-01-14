"""Client helpers."""

from .init_client import StreamingClient
from . import filters as filters
from . import registration as registration
from . import search as search
from . import streams as streams

StreamingClient.register_resource = registration.register_resource  
StreamingClient.update_resource = registration.update_resource  
StreamingClient.deactivate_resource = registration.deactivate_resource  
StreamingClient.delete_resource = registration.delete_resource  
StreamingClient.delete_resource_by_name = registration.delete_resource  
StreamingClient.search_resources = search.search_resources  
StreamingClient.compile_filters = filters.compile_filters  
StreamingClient.create_stream = streams.create_stream  
StreamingClient.consume_stream = streams.consume_stream  
StreamingClient.view_my_streams = streams.view_my_streams  
StreamingClient.delete_my_stream = streams.delete_my_stream  

__all__ = ["StreamingClient"]
