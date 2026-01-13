# IEEE vTools Events API - Complete Implementation Guide

## Overview

This repository provides a comprehensive implementation of the IEEE vTools Events API, including production-ready Python clients, web application, and extensive examples. The IEEE vTools Events API is a powerful RESTful web service that provides programmatic access to IEEE event data worldwide.

**Official API Documentation:** https://events.vtools.ieee.org/api/doc

## What is IEEE vTools Events API?

The IEEE vTools Events API is a RESTful web service based on JSON:API standards that allows developers to:

- 🔍 Query events by date, location, category, and tags
- 🌐 Filter virtual, physical, or hybrid events
- 📊 Access event metadata including speakers, media, and enhanced reports
- 📤 Export data in multiple formats (JSON, XML, iCal, RSS, HTML, CSV)
- 🔄 Track event updates using delta queries
- 📄 Paginate through large datasets
- 🎯 Use advanced time arithmetic for flexible date ranges

### Key Features

- **Free Public Access:** No authentication required for public events
- **Rich Dataset:** Detailed information on IEEE technical events worldwide
- **Multiple Formats:** JSON, XML, iCal, RSS, HTML, and CSV export
- **Flexible Querying:** Advanced filtering with span, tags, categories
- **Time Arithmetic:** Use "now+7.days" or "now-30.minutes" for dynamic queries
- **High Limits:** Up to 500 results per query with pagination support

## Repository Contents

### 1. **client.py** (Recommended)
Enhanced Python client library with advanced features:
- ✨ `SpanBuilder` for intuitive time arithmetic queries
- 🛡️ Enum-based parameter types for type safety and IDE autocomplete
- 💾 Smart caching with TTL (time-to-live)
- 🔍 Full support for tags with AND/OR logic
- 🔄 Delta queries for incremental updates
- 📦 All output formats supported
- 📄 Automatic pagination for large datasets
- 👥 Include speakers, media, and enhanced reports
- ⚠️ Graceful error handling for API limitations

### 2. **client_basic.py** (Basic)
Simplified Python client library featuring:
- 🎯 Core API integration
- 💾 Basic caching mechanism
- 🔧 Helper methods for common use cases
- 📊 Event analyzer for insights and statistics
- 📤 Export functionality (iCal, CSV)

### 3. **webapp.py**
Complete Flask web application demonstrating:
- 🎨 Modern, responsive UI for event discovery
- 🔍 Real-time event search and filtering
- 📊 Interactive statistics dashboard
- 🖥️ Multiple view options (virtual/physical/all)
- ✨ Professional design with smooth animations
- 🔧 RESTful API backend

### 4. **examples.py**
Comprehensive examples demonstrating:
- 📚 12 different usage scenarios
- 💡 All API features with practical code
- 🌍 Real-world use cases (newsletters, mobile apps, analytics)
- 📤 Export operations in all formats
- 🔗 Combined filter queries
- 📄 Pagination and batch operations

## Installation

### From PyPI (Recommended)

```bash
pip install ieee-events
```

### Optional Dependencies

For the web application:
```bash
pip install ieee-events[webapp]
```

For development:
```bash
pip install ieee-events[dev]
```

### From Source

```bash
git clone https://github.com/yourusername/ieee-events-api-toolkit.git
cd ieee-events-api-toolkit
pip install -e .
```

## Quick Start

### Option 1: Enhanced Client (Recommended)

```python
from ieee_events import IEEEEventsClientEnhanced, SpanBuilder, TimeUnit, LocationType

client = IEEEEventsClientEnhanced()

# Get events in next 7 days
events = client.get_events(span=SpanBuilder.now_plus(7, TimeUnit.DAYS))
print(f"Found {len(events['data'])} events")

# Get virtual events only
virtual = client.get_virtual_events(days=30, limit=20)
print(f"Found {len(virtual['data'])} virtual events")

# Search by tags (OR logic)
tagged = client.get_events_by_tags(['AI', 'robotics'], match_all=False)
print(f"Found {len(tagged['data'])} events")

# Get events with speaker info
with_speakers = client.get_events(
    span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
    include=['speakers', 'media'],
    limit=10
)

# Export to iCal
client.export_events("my_events.ics", format="ics", limit=50)
```

### Option 2: Basic Client

```python
from ieee_events import IEEEEventsClient, IEEEEventAnalyzer

client = IEEEEventsClient()

# Get upcoming events
upcoming = client.get_upcoming_events(days=30)
print(f"Found {len(upcoming['data'])} events")

# Get virtual events
virtual = client.get_virtual_events(limit=20)

# Search by tags
events = client.get_events_by_tags(['robotics', 'AI'], match_all=False)

# Export to iCal
client.export_to_ical("events.ics", limit=50)

# Analyze events
analyzer = IEEEEventAnalyzer()
stats = analyzer.analyze_events(upcoming['data'])
print(f"Virtual: {stats['virtual_count']}, Physical: {stats['physical_count']}")
```

### Option 3: Run Web Application

First, install with webapp support:
```bash
pip install ieee-events[webapp]
```

Then run:
```bash
python -m ieee_events.webapp
```

Or if installed from source:
```bash
python ieee_events/webapp.py
```

Then open http://localhost:5000 in your browser to access the web interface.

### Option 4: Run Comprehensive Examples

```bash
python examples.py
```

This will demonstrate all 12 example scenarios with real API calls.

## API Capabilities

### Base Information

- **Base URL:** `https://events.vtools.ieee.org/RST/events/api/public/v7`
- **Current Version:** v7
- **API Standard:** JSON:API (http://jsonapi.org/)
- **Default Limit:** 500 results per query
- **Official Docs:** https://events.vtools.ieee.org/api/doc

### Endpoints

#### 1. Events List
`/events/list[.format]`

**Supported Formats:**
- `.json` (default) - JSON response
- `.xml` - XML feed
- `.ics` - iCal calendar format
- `.rss` - RSS feed
- `.html` - Embeddable HTML
- `.csv` - CSV export

#### 2. Categories List
`/categories/list`

Returns all event categories with subcategories.

#### 3. Countries List
`/countries/list`

Returns all countries with their states.

### Query Parameters

#### Basic Parameters
- **limit** (integer): Maximum results (default: 500)
- **page** (integer): Page number for pagination
- **sort** (string): Sort by attribute (prefix with `-` for descending)
  - Examples: `start-time`, `-start-time`, `-created-at`

#### Advanced Parameters
- **span** (string): Date range filter with time arithmetic
  - Format: `start~end` (exactly one `~` required)
  - Examples:
    - `now~now+7.days` - Next 7 days
    - `now~now+2.months` - Next 2 months
    - `now-30.days~now` - Last 30 days
    - `now+7.days~now+60.days` - Between 1 week and 2 months from now
  
- **delta** (ISO 8601): Get events created/updated since datetime
  - ⚠️ Note: May cause server errors with certain parameter combinations

- **location_type** (string): Filter by location
  - Options: `virtual`, `physical`, `hybrid`, `all`

- **tags** (comma-separated): Filter by tags
  - Works with `tags_connector` parameter

- **tags_connector** (string): Combine multiple tags
  - Options: `AND`, `OR` (default)

- **category_id** (comma-separated integers): Filter by category IDs

- **subcategory_id** (comma-separated integers): Filter by subcategory IDs

- **include** (comma-separated): Additional data to include
  - Options: `speakers`, `media`, `enhanced_report`

- **published** (boolean/string): Filter by publication status
  - Options: `true`, `false`, `all`

- **reported** (boolean/string): Filter by report status
  - Options: `true`, `false`, `all`

### Time Arithmetic with Span

The API supports powerful time arithmetic for dynamic queries:

```python
# Available time units
"now+15"           # Plus 15 days (default unit)
"now-90.minutes"   # Minus 90 minutes
"now+1.year"       # Plus 1 year
"now-45.seconds"   # Minus 45 seconds
"now-8.months"     # Minus 8 months
"now+60.days"      # Plus 60 days
```

## Practical Use Cases

### 1. Event Discovery Platform
Build a comprehensive event discovery platform for IEEE members and technology enthusiasts.

**Features:**
- Real-time event listings with filters
- Calendar integration via iCal
- Personalized recommendations
- Registration tracking and reminders

**Value:**
- Aggregates scattered IEEE events
- Improves member engagement
- Provides analytics on popular events

### 2. Analytics Dashboard
Create a dashboard for analyzing IEEE event trends and insights.

**Features:**
- Event statistics by location type (virtual/physical/hybrid)
- Popular topics and categories
- Geographic distribution
- Temporal trends

**Implementation:**
```python
from ieee_events import IEEEEventsClientEnhanced, SpanBuilder, TimeUnit

client = IEEEEventsClientEnhanced()
events = client.get_events(span=SpanBuilder.now_plus(30, TimeUnit.DAYS), limit=500)

# Analyze
virtual_count = sum(1 for e in events['data'] if e['attributes'].get('virtual'))
total = len(events['data'])
print(f"Virtual: {virtual_count}/{total} ({virtual_count/total*100:.1f}%)")
```

### 3. Mobile Event App
Develop a mobile application for on-the-go event access.

**Features:**
- Location-based event discovery
- Push notifications for nearby events
- Offline access with caching
- Calendar sync

### 4. Academic Research Tool
Research platform for analyzing IEEE event trends.

**Features:**
- Historical event data analysis
- Topic trend identification
- Geographic visualization
- Speaker network analysis

### 5. Event Management System
Tool for IEEE organizers to track and manage events.

**Features:**
- Event monitoring dashboard
- Attendance tracking
- Post-event reporting
- Member engagement metrics

### 6. Newsletter Service
Automated newsletter generation with upcoming events.

**Implementation:**
```python
client = IEEEEventsClientEnhanced()

# Get next week's events
events = client.get_events(
    span=SpanBuilder.now_plus(7, TimeUnit.DAYS),
    include=['speakers'],
    limit=50
)

# Export to HTML for newsletter
html = client.get_events_html(
    span=SpanBuilder.now_plus(7, TimeUnit.DAYS),
    limit=50
)
```

### 7. Event Aggregation Service
Combine IEEE events with other technical conferences.

**Features:**
- Multi-source event aggregation
- Deduplication
- Unified search interface
- Cross-platform calendar export

## Advanced Features

### SpanBuilder for Time Arithmetic

```python
from ieee_events import SpanBuilder, TimeUnit

# Future events
span = SpanBuilder.now_plus(7, TimeUnit.DAYS)        # Next 7 days
span = SpanBuilder.now_plus(2, TimeUnit.MONTHS)      # Next 2 months
span = SpanBuilder.now_to_future()                   # All future events

# Past events (⚠️ may cause server errors)
span = SpanBuilder.now_minus(30, TimeUnit.DAYS)      # Last 30 days
span = SpanBuilder.now_minus(6, TimeUnit.HOURS)      # Last 6 hours

# Custom ranges
span = SpanBuilder.range(
    start_offset=7, 
    start_unit=TimeUnit.DAYS,
    end_offset=60, 
    end_unit=TimeUnit.DAYS
)  # Between 1 week and 2 months from now

# Date ranges
span = SpanBuilder.date_range(
    start="2026-01-01T00:00:00Z",
    end="2026-12-31T23:59:59Z"
)
```

### Tags with AND/OR Logic

```python
# OR logic (any tag matches)
events = client.get_events_by_tags(
    tags=['AI', 'robotics', 'machine learning'],
    match_all=False
)

# AND logic (all tags must match)
events = client.get_events_by_tags(
    tags=['AI', 'robotics'],
    match_all=True
)
```

### Pagination

```python
# Manual pagination
page1 = client.get_events(limit=10, page=1)
page2 = client.get_events(limit=10, page=2)

# Auto-pagination (gets all results)
all_events = []
page = 1
while True:
    result = client.get_events(limit=100, page=page)
    all_events.extend(result['data'])
    
    paging = result.get('meta', {}).get('paging', {})
    if page >= paging.get('total_pages', 1):
        break
    page += 1
```

### Including Extra Data

```python
# Include speaker information
events = client.get_events(
    span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
    include=['speakers']
)

# Include media attachments
events = client.get_events(include=['media'])

# Include everything
events = client.get_events(
    include=['speakers', 'media', 'enhanced_report']
)
```

### Export to Different Formats

```python
# Export to iCal
client.export_events(
    filename="events.ics",
    format="ics",
    span=SpanBuilder.now_plus(30, TimeUnit.DAYS)
)

# Export to RSS
client.export_events(
    filename="events.rss",
    format="rss",
    limit=50
)

# Get HTML for embedding
html = client.get_events_html(
    span=SpanBuilder.now_plus(7, TimeUnit.DAYS),
    location_type=LocationType.VIRTUAL
)

# CSV export (⚠️ may have connection issues)
try:
    client.export_events("events.csv", format="csv")
except Exception as e:
    print(f"CSV export failed: {e}")
```

### Caching

```python
# Caching is enabled by default with 5-minute TTL
from ieee_events import IEEEEventsClientEnhanced

client = IEEEEventsClientEnhanced(cache_enabled=True)

# Clear cache manually
client.clear_cache()

# Disable caching
client = IEEEEventsClientEnhanced(cache_enabled=False)
```

## Known Limitations

### Delta Queries
Delta queries (incremental updates) may cause HTTP 500 errors when combined with certain parameters. This is a server-side limitation.

**Workaround:**
```python
try:
    delta_events = client.get_events_delta(since="2026-01-01T00:00:00Z")
except Exception as e:
    print(f"Delta query failed: {e}")
```

### Past Events
Queries for past events (negative spans) may sometimes cause server errors depending on the time range and parameters used.

**Workaround:**
```python
try:
    past_events = client.get_past_events(days=30)
except Exception as e:
    print(f"Past events query failed: {e}")
```

### CSV Export
CSV export may occasionally result in connection reset errors.

**Workaround:**
```python
try:
    client.export_events("events.csv", format="csv")
except Exception as e:
    # Fallback to JSON and convert to CSV manually
    events = client.get_events(limit=500)
    # Convert to CSV using pandas or csv module
```

## Best Practices

### 1. Use Caching
Enable caching to reduce API load and improve response times:
```python
from ieee_events import IEEEEventsClientEnhanced

client = IEEEEventsClientEnhanced(cache_enabled=True)
```

### 2. Limit Query Scope
Request only the data you need:
```python
# Good: Specific time range
events = client.get_events(span=SpanBuilder.now_plus(7, TimeUnit.DAYS), limit=50)

# Avoid: Very large queries without limits
events = client.get_events(limit=5000)  # May timeout
```

### 3. Handle Errors Gracefully
Always wrap API calls in try-except blocks:
```python
try:
    events = client.get_events(span=span)
except requests.exceptions.HTTPError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Use Type-Safe Enums
Use the provided enums for better IDE support and fewer errors:
```python
from ieee_events import LocationType, TimeUnit, OutputFormat, TagsConnector

client.get_events(
    location_type=LocationType.VIRTUAL,  # ✓ Type-safe
    # location_type="virtual"  # ✗ String (error-prone)
)
```

### 5. Optimize with Pagination
For large datasets, use pagination instead of large limit values:
```python
# Good: Paginated approach
for page in range(1, 11):
    events = client.get_events(limit=100, page=page)
    process_events(events['data'])

# Avoid: Single large request
events = client.get_events(limit=1000)  # May be slow
```

## Performance Considerations

### Response Times
- **Typical query:** 200-500ms
- **Large queries (500+ results):** 1-3 seconds
- **With includes (speakers, media):** +500ms

### Rate Limiting
The API does not have explicit rate limiting, but please:
- Use caching to minimize requests
- Avoid rapid-fire requests
- Implement exponential backoff for retries

### Data Freshness
- Event data is updated in real-time
- Cache TTL: 5 minutes (configurable)
- Use delta queries for incremental updates (when working)

## Troubleshooting

### HTTP 500 Errors
**Cause:** Server-side error, often due to parameter combinations
**Solution:**
- Remove `published` and `reported` parameters
- Reduce time range
- Avoid delta with complex filters

### Connection Reset
**Cause:** Network issues or server timeout
**Solution:**
- Retry with exponential backoff
- Reduce query complexity
- Use smaller time ranges

### Empty Results
**Cause:** No events match the filters
**Solution:**
- Broaden time range
- Remove restrictive filters
- Check if location_type is too specific

### Slow Queries
**Cause:** Large result sets or complex filters
**Solution:**
- Reduce limit parameter
- Use pagination
- Enable caching
- Narrow time range

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share use cases

## Resources

- **Official API Documentation:** https://events.vtools.ieee.org/api/doc
- **IEEE vTools:** https://vtools.ieee.org
- **IEEE Events Portal:** https://events.vtools.ieee.org

## License

This implementation is provided as-is for educational and development purposes. The IEEE vTools Events API is provided by IEEE and subject to their terms of service.

## Support

For API-specific questions, refer to the official documentation at https://events.vtools.ieee.org/api/doc

For implementation questions about this repository, please open an issue.

---

**Last Updated:** January 2026
**API Version:** v7
**Python Version:** 3.8+
