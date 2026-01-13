"""
IEEE vTools Events API - Python Client Library
================================================

A comprehensive Python client library for the IEEE vTools Events API v7.
Provides easy access to IEEE event data worldwide with support for advanced
filtering, multiple output formats, and type-safe operations.

Features:
---------
- Full API v7 support with all endpoints
- Type-safe enums for parameters
- Smart caching with TTL
- Advanced time arithmetic with SpanBuilder
- Multiple output formats (JSON, XML, iCal, RSS, HTML, CSV)
- Tag filtering with AND/OR logic
- Pagination support
- Virtual/Physical/Hybrid event filtering
- Delta queries for incremental updates

Quick Start:
-----------
    from ieee_events import IEEEEventsClientEnhanced, SpanBuilder, TimeUnit
    
    # Create client
    client = IEEEEventsClientEnhanced()
    
    # Get events in next 7 days
    events = client.get_events(span=SpanBuilder.now_plus(7, TimeUnit.DAYS))
    print(f"Found {len(events['data'])} events")
    
    # Get virtual events only
    virtual = client.get_virtual_events(days=30, limit=20)
    
    # Search by tags
    tagged = client.get_events_by_tags(['AI', 'robotics'], match_all=False)
    
    # Export to iCal
    client.export_to_ical("events.ics", days=60)

For more information, visit: https://events.vtools.ieee.org/api/doc
"""

__version__ = "1.0.0"
__author__ = "IEEE vTools API Contributors"
__license__ = "MIT"

# Import main classes from the enhanced client
from .client import (
    IEEEEventsClientEnhanced,
    SpanBuilder,
    LocationType,
    TagsConnector,
    OutputFormat,
    TimeUnit
)

# Import basic client classes
from .client_basic import (
    IEEEEventsClient,
    IEEEEventAnalyzer
)

# Define what gets imported with "from ieee_events import *"
__all__ = [
    # Enhanced Client
    'IEEEEventsClientEnhanced',
    'SpanBuilder',
    'LocationType',
    'TagsConnector',
    'OutputFormat',
    'TimeUnit',
    
    # Basic Client
    'IEEEEventsClient',
    'IEEEEventAnalyzer',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__',
]

