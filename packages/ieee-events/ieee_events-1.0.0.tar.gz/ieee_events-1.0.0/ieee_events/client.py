"""
IEEE vTools Events API - Enhanced Python Client
Implements all v7 API features including advanced span queries with time arithmetic
"""

import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Union
import json
from enum import Enum


class LocationType(Enum):
    """Event location types"""
    ALL = "all"
    VIRTUAL = "virtual"
    PHYSICAL = "physical"
    HYBRID = "hybrid"


class TagsConnector(Enum):
    """Tag search connectors"""
    OR = "OR"
    AND = "AND"


class OutputFormat(Enum):
    """API output formats"""
    JSON = "json"
    XML = "xml"
    ICAL = "ics"
    RSS = "rss"
    HTML = "html"
    CSV = "csv"


class TimeUnit(Enum):
    """Time units for span arithmetic"""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"
    
    # Singular forms
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class SpanBuilder:
    """
    Builder class for creating span queries with time arithmetic.
    
    Examples:
        SpanBuilder.now_plus(30, TimeUnit.DAYS)  # now~now+30.days
        SpanBuilder.now_minus(90, TimeUnit.MINUTES)  # now~now-90.minutes
        SpanBuilder.range_from_now(7, 30, TimeUnit.DAYS)  # now+7.days~now+30.days
    """
    
    @staticmethod
    def format_time_expression(offset: int = 0, unit: TimeUnit = TimeUnit.DAYS) -> str:
        """Format a time expression like 'now+30.days' or 'now-90.minutes'"""
        if offset == 0:
            return "now"
        
        sign = "+" if offset > 0 else ""
        unit_str = unit.value
        return f"now{sign}{offset}.{unit_str}"
    
    @staticmethod
    def now_plus(value: int, unit: TimeUnit = TimeUnit.DAYS) -> str:
        """Create span from now to now+value.unit"""
        end = SpanBuilder.format_time_expression(value, unit)
        return f"now~{end}"
    
    @staticmethod
    def now_minus(value: int, unit: TimeUnit = TimeUnit.DAYS) -> str:
        """Create span from now-value.unit to now"""
        start = SpanBuilder.format_time_expression(-value, unit)
        return f"{start}~now"
    
    @staticmethod
    def from_now_onwards() -> str:
        """Create span from now onwards (no end date)"""
        return "now~"
    
    @staticmethod
    def until_now() -> str:
        """Create span until now (no start date)"""
        return "~now"
    
    @staticmethod
    def range_from_now(start_offset: int, end_offset: int, 
                       unit: TimeUnit = TimeUnit.DAYS) -> str:
        """Create span from now+start_offset to now+end_offset"""
        start = SpanBuilder.format_time_expression(start_offset, unit)
        end = SpanBuilder.format_time_expression(end_offset, unit)
        return f"{start}~{end}"
    
    @staticmethod
    def custom(start: Optional[str] = None, end: Optional[str] = None) -> str:
        """Create custom span with ISO dates or time expressions"""
        start_str = start or ""
        end_str = end or ""
        return f"{start_str}~{end_str}"


class IEEEEventsClientEnhanced:
    """
    Enhanced client for IEEE vTools Events API v7.
    Supports all API features including advanced span queries, tags, and multiple output formats.
    """
    
    BASE_URL = "https://events.vtools.ieee.org/RST/events/api/public/v7"
    DEFAULT_LIMIT = 500
    
    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 3600):
        """
        Initialize the enhanced IEEE Events API client.
        
        Args:
            cache_enabled: Enable response caching
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.cache = {} if cache_enabled else None
        self.cache_timestamps = {} if cache_enabled else None
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'IEEE-Events-Python-Client/2.0'})
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if self.cache is None or cache_key not in self.cache:
            return False
        
        timestamp = self.cache_timestamps.get(cache_key, 0)
        age = datetime.now().timestamp() - timestamp
        return age < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: any):
        """Save data to cache with timestamp"""
        if self.cache is not None:
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now().timestamp()
    
    def get_events(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        span: Optional[str] = None,
        sort: str = "-start-time",
        delta: Optional[str] = None,
        location_type: LocationType = LocationType.ALL,
        tags: Optional[List[str]] = None,
        tags_connector: TagsConnector = TagsConnector.OR,
        category_id: Optional[List[int]] = None,
        subcategory_id: Optional[List[int]] = None,
        published: Optional[Union[bool, str]] = None,
        reported: Optional[Union[bool, str]] = None,
        event_id: Optional[int] = None,
        include: Optional[List[str]] = None,
        output_format: OutputFormat = OutputFormat.JSON
    ) -> Union[Dict, str]:
        """
        Retrieve events from IEEE vTools API with comprehensive filtering options.
        
        Args:
            limit: Maximum number of events to retrieve (default 500)
            page: Page number for pagination (default 1)
            span: Date range filter (use SpanBuilder for advanced queries)
            sort: Sort attribute (prefix with "-" for descending)
            delta: Get events created/updated since this ISO datetime
            location_type: Filter by location type (virtual/physical/hybrid/all)
            tags: List of tags to filter by
            tags_connector: How to combine multiple tags (AND/OR)
            category_id: List of category IDs to filter by
            subcategory_id: List of subcategory IDs to filter by
            published: Filter by publication status (True/False/"all")
            reported: Filter by report status (True/False/"all")
            event_id: Get specific event by ID
            include: Additional data to include (speakers, media, enhanced_report)
            output_format: Response format (json, xml, ical, rss, html, csv)
        
        Returns:
            Dict for JSON format, str for other formats
        """
        params = {
            "limit": limit,
            "page": page,
            "sort": sort,
            "location_type": location_type.value
        }
        
        # Add optional parameters
        if span:
            params["span"] = span
        
        if delta:
            params["delta"] = delta
        
        if tags:
            params["tags"] = ",".join(tags)
            params["tags_connector"] = tags_connector.value
        
        if category_id:
            params["category_id"] = ",".join(map(str, category_id))
        
        if subcategory_id:
            params["subcategory_id"] = ",".join(map(str, subcategory_id))
        
        # Only add published/reported if explicitly set (these can cause 500 errors with delta/past events)
        if published is not None:
            if isinstance(published, bool):
                params["published"] = "true" if published else "false"
            else:
                params["published"] = str(published)
        
        if reported is not None:
            if isinstance(reported, bool):
                params["reported"] = "true" if reported else "false"
            else:
                params["reported"] = str(reported)
        
        if event_id:
            params["id"] = event_id
        
        if include:
            params["include"] = ",".join(include)
        
        # Build URL with format extension
        extension = "" if output_format == OutputFormat.JSON else f".{output_format.value}"
        url = f"{self.BASE_URL}/events/list{extension}"
        
        # Check cache
        cache_key = f"{url}:{json.dumps(params, sort_keys=True)}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Make request
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        # Parse response
        if output_format == OutputFormat.JSON:
            data = response.json()
        else:
            data = response.text
        
        # Cache response
        self._save_to_cache(cache_key, data)
        
        return data
    
    def get_upcoming_events(
        self,
        days: int = 30,
        location_type: LocationType = LocationType.ALL,
        limit: int = 100,
        **kwargs
    ) -> Dict:
        """
        Get events starting within the next N days.
        
        Args:
            days: Number of days to look ahead
            location_type: Filter by location type
            limit: Maximum number of results
            **kwargs: Additional parameters to pass to get_events()
        """
        span = SpanBuilder.now_plus(days, TimeUnit.DAYS)
        return self.get_events(
            span=span,
            location_type=location_type,
            limit=limit,
            sort="start-time",
            **kwargs
        )
    
    def get_past_events(
        self,
        days: int = 30,
        location_type: LocationType = LocationType.ALL,
        limit: int = 100,
        **kwargs
    ) -> Dict:
        """
        Get events from the past N days.
        
        Note: Past event queries (negative spans) may sometimes cause server errors
        depending on the parameters used. If you encounter 500 errors, try reducing
        the time range or avoid using published/reported parameters.
        
        Args:
            days: Number of days to look back
            location_type: Filter by location type
            limit: Maximum number of results
            **kwargs: Additional parameters to pass to get_events()
        """
        span = SpanBuilder.now_minus(days, TimeUnit.DAYS)
        return self.get_events(
            span=span,
            location_type=location_type,
            limit=limit,
            sort="-start-time",
            **kwargs
        )
    
    def get_virtual_events(self, days: int = 30, limit: int = 100, **kwargs) -> Dict:
        """Get upcoming virtual events."""
        return self.get_upcoming_events(
            days=days,
            location_type=LocationType.VIRTUAL,
            limit=limit,
            **kwargs
        )
    
    def get_physical_events(self, days: int = 30, limit: int = 100, **kwargs) -> Dict:
        """Get upcoming physical events."""
        return self.get_upcoming_events(
            days=days,
            location_type=LocationType.PHYSICAL,
            limit=limit,
            **kwargs
        )
    
    def get_hybrid_events(self, days: int = 30, limit: int = 100, **kwargs) -> Dict:
        """Get upcoming hybrid events."""
        return self.get_upcoming_events(
            days=days,
            location_type=LocationType.HYBRID,
            limit=limit,
            **kwargs
        )
    
    def get_events_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        days: int = 90,
        limit: int = 100,
        **kwargs
    ) -> Dict:
        """
        Get events matching specific tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, use AND logic; if False, use OR logic
            days: Number of days to look ahead
            limit: Maximum number of results
            **kwargs: Additional parameters
        """
        connector = TagsConnector.AND if match_all else TagsConnector.OR
        span = SpanBuilder.now_plus(days, TimeUnit.DAYS)
        
        return self.get_events(
            tags=tags,
            tags_connector=connector,
            span=span,
            limit=limit,
            **kwargs
        )
    
    def get_events_delta(
        self,
        since: str,
        limit: int = DEFAULT_LIMIT,
        **kwargs
    ) -> Dict:
        """
        Get events created or updated since a specific datetime.
        
        Note: Delta queries may sometimes cause server errors when combined with
        certain parameters. If you encounter 500 errors, avoid using published/reported
        parameters with delta queries.
        
        Args:
            since: ISO 8601 datetime string
            limit: Maximum number of results
            **kwargs: Additional parameters
        """
        return self.get_events(
            delta=since,
            limit=limit,
            sort="-created-at",
            **kwargs
        )
    
    def get_event_by_id(self, event_id: int, include: Optional[List[str]] = None) -> Dict:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Event ID
            include: Additional data to include (speakers, media, enhanced_report)
        """
        result = self.get_events(event_id=event_id, include=include, limit=1)
        if result.get("data"):
            return result["data"][0]
        return {}
    
    def get_categories(self) -> Dict:
        """Retrieve all available event categories and subcategories."""
        cache_key = "categories"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.BASE_URL}/categories/list"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        self._save_to_cache(cache_key, data)
        return data
    
    def get_countries(self) -> Dict:
        """Retrieve all available countries and states."""
        cache_key = "countries"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.BASE_URL}/countries/list"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        self._save_to_cache(cache_key, data)
        return data
    
    def export_to_ical(self, filename: str, days: int = 90, **kwargs) -> None:
        """
        Export events to iCal format.
        
        Args:
            filename: Output filename
            days: Number of days to export
            **kwargs: Additional filter parameters
        """
        span = SpanBuilder.now_plus(days, TimeUnit.DAYS)
        data = self.get_events(
            span=span,
            output_format=OutputFormat.ICAL,
            **kwargs
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    
    def export_to_csv(self, filename: str, days: int = 90, **kwargs) -> None:
        """
        Export events to CSV format.
        
        Args:
            filename: Output filename
            days: Number of days to export
            **kwargs: Additional filter parameters
        """
        span = SpanBuilder.now_plus(days, TimeUnit.DAYS)
        data = self.get_events(
            span=span,
            output_format=OutputFormat.CSV,
            **kwargs
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    
    def export_to_rss(self, filename: str, days: int = 90, **kwargs) -> None:
        """
        Export events to RSS format.
        
        Args:
            filename: Output filename
            days: Number of days to export
            **kwargs: Additional filter parameters
        """
        span = SpanBuilder.now_plus(days, TimeUnit.DAYS)
        data = self.get_events(
            span=span,
            output_format=OutputFormat.RSS,
            **kwargs
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    
    def get_paginated_events(
        self,
        total_limit: int = 1000,
        page_size: int = 100,
        **kwargs
    ) -> List[Dict]:
        """
        Get events with automatic pagination.
        
        Args:
            total_limit: Total number of events to retrieve
            page_size: Number of events per page
            **kwargs: Additional filter parameters
        
        Returns:
            List of all event objects
        """
        all_events = []
        page = 1
        
        while len(all_events) < total_limit:
            result = self.get_events(
                limit=page_size,
                page=page,
                **kwargs
            )
            
            events = result.get("data", [])
            if not events:
                break
            
            all_events.extend(events)
            
            # Check if there are more pages
            paging_info = result.get("meta", {}).get("paging", {})
            if page >= paging_info.get("total_pages", page):
                break
            
            page += 1
        
        return all_events[:total_limit]
    
    def clear_cache(self):
        """Clear all cached data."""
        if self.cache is not None:
            self.cache.clear()
            self.cache_timestamps.clear()


def demo_enhanced_features():
    """Demonstrate enhanced API features."""
    
    client = IEEEEventsClientEnhanced()
    
    print("=== IEEE vTools Events API - Enhanced Features Demo ===\n")
    
    # 1. Using span with time arithmetic
    print("1. Events in next 7 days (using SpanBuilder):")
    span_7_days = SpanBuilder.now_plus(7, TimeUnit.DAYS)
    print(f"   Span: {span_7_days}")
    events = client.get_events(span=span_7_days, limit=5)
    print(f"   Found: {len(events.get('data', []))} events\n")
    
    # 2. Virtual events only
    print("2. Virtual events in next 30 days:")
    virtual = client.get_virtual_events(days=30, limit=10)
    print(f"   Found: {len(virtual.get('data', []))} virtual events\n")
    
    # 3. Events with specific tags (OR logic)
    print("3. Events with tags 'AI' OR 'robotics':")
    tagged = client.get_events_by_tags(
        tags=["AI", "robotics"],
        match_all=False,
        days=60
    )
    print(f"   Found: {len(tagged.get('data', []))} events\n")
    
    # 4. Events with specific tags (AND logic)
    print("4. Events with tags 'AI' AND 'robotics':")
    tagged_and = client.get_events_by_tags(
        tags=["AI", "robotics"],
        match_all=True,
        days=60
    )
    print(f"   Found: {len(tagged_and.get('data', []))} events\n")
    
    # 5. Events updated in last 24 hours (Note: delta queries may cause server errors)
    print("5. Events updated in last 24 hours:")
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().split('.')[0] + 'Z'
        delta_events = client.get_events_delta(since=yesterday)
        print(f"   Found: {len(delta_events.get('data', []))} updated events\n")
    except Exception as e:
        print(f"   ⚠ Delta query failed (known API limitation): {type(e).__name__}\n")
    
    # 6. Get event with speakers and media
    print("6. Events with speaker and media data:")
    with_extras = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        include=["speakers", "media"],
        limit=5
    )
    print(f"   Found: {len(with_extras.get('data', []))} events\n")
    
    # 7. Pagination example
    print("7. Getting events with pagination:")
    paged = client.get_events(limit=10, page=1)
    paging_info = paged.get("meta", {}).get("paging", {})
    print(f"   Page: {paging_info.get('page', 'N/A')}")
    print(f"   Total Pages: {paging_info.get('total_pages', 'N/A')}")
    print(f"   Events on this page: {len(paged.get('data', []))}\n")
    
    # 8. Export examples
    print("8. Export operations:")
    try:
        client.export_to_ical("ieee_events_enhanced.ics", days=60)
        print("   ✓ Exported to iCal format")
    except Exception as e:
        print(f"   ✗ iCal export failed: {e}")
    
    try:
        client.export_to_csv("ieee_events_enhanced.csv", days=60)
        print("   ✓ Exported to CSV format")
    except Exception as e:
        print(f"   ✗ CSV export failed: {e}")
    
    try:
        client.export_to_rss("ieee_events_enhanced.rss", days=60)
        print("   ✓ Exported to RSS format")
    except Exception as e:
        print(f"   ✗ RSS export failed: {e}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_enhanced_features()

