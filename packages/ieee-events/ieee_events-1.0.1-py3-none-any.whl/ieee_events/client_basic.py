import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import json

class IEEEEventsClient:
    """
    Client for interacting with IEEE vTools Events API.
    Provides methods for querying, filtering, and retrieving IEEE event data.
    """
    
    BASE_URL = "https://events.vtools.ieee.org/RST/events/api/public/v7"
    
    def __init__(self, cache_enabled: bool = True):
        self.cache = {} if cache_enabled else None
        self.session = requests.Session()
    
    def get_events(
        self,
        limit: int = 500,
        span_start: Optional[str] = None,
        span_end: Optional[str] = None,
        location_type: str = "all",
        sort_by: str = "-start-time",
        tags: Optional[List[str]] = None,
        tags_connector: str = "OR",
        include_speakers: bool = False,
        include_media: bool = False,
        output_format: str = "json"
    ) -> Dict:
        """
        Retrieve events from IEEE vTools API with filtering options.
        
        Args:
            limit: Maximum number of events to retrieve (default 500)
            span_start: Start date for event filtering (ISO 8601 format)
            span_end: End date for event filtering (ISO 8601 format)
            location_type: Filter by "virtual", "physical", "hybrid", or "all"
            sort_by: Sort attribute (prefix with "-" for descending)
            tags: List of tags to filter by
            tags_connector: "AND" or "OR" for multiple tags
            include_speakers: Include speaker data in response
            include_media: Include media data in response
            output_format: Response format ("json", "xml", "ical", "rss", "html", "csv")
        """
        params = {
            "limit": limit,
            "sort": sort_by,
            "location_type": location_type
        }
        
        if span_start or span_end:
            span_value = f"{span_start or ''}~{span_end or ''}"
            params["span"] = span_value
        
        if tags:
            params["tags"] = ",".join(tags)
            params["tags_connector"] = tags_connector
        
        include_params = []
        if include_speakers:
            include_params.append("speakers")
        if include_media:
            include_params.append("media")
        if include_params:
            params["include"] = ",".join(include_params)
        
        extension = "" if output_format == "json" else f".{output_format}"
        url = f"{self.BASE_URL}/events/list{extension}"
        
        cache_key = f"{url}:{json.dumps(params, sort_keys=True)}"
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json() if output_format == "json" else response.text
        
        if self.cache is not None:
            self.cache[cache_key] = data
        
        return data
    
    def get_upcoming_events(self, days: int = 30, limit: int = 100) -> Dict:
        """Get events starting within the next N days."""
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        future = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat().replace('+00:00', 'Z')
        
        return self.get_events(
            span_start=now,
            span_end=future,
            limit=limit,
            sort_by="start-time"
        )
    
    def get_virtual_events(self, limit: int = 100) -> Dict:
        """Get upcoming virtual events."""
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        return self.get_events(
            span_start=now,
            location_type="virtual",
            limit=limit
        )
    
    def get_events_by_tags(self, tags: List[str], match_all: bool = False, limit: int = 100) -> Dict:
        """Get events matching specific tags."""
        connector = "AND" if match_all else "OR"
        
        return self.get_events(
            tags=tags,
            tags_connector=connector,
            limit=limit
        )
    
    def get_events_delta(self, since: str, limit: int = 500) -> Dict:
        """Get events created or updated since a specific time."""
        params = {
            "delta": since,
            "limit": limit
        }
        
        url = f"{self.BASE_URL}/events/list"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_categories(self) -> Dict:
        """Retrieve all available event categories and subcategories."""
        cache_key = "categories"
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.BASE_URL}/categories/list"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        if self.cache is not None:
            self.cache[cache_key] = data
        
        return data
    
    def get_countries(self) -> Dict:
        """Retrieve all available countries and states."""
        cache_key = "countries"
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.BASE_URL}/countries/list"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        if self.cache is not None:
            self.cache[cache_key] = data
        
        return data
    
    def export_to_ical(self, filename: str, **kwargs) -> None:
        """Export events to iCal format."""
        data = self.get_events(output_format="ics", **kwargs)
        with open(filename, "w") as f:
            f.write(data)
    
    def export_to_csv(self, filename: str, **kwargs) -> None:
        """Export events to CSV format."""
        data = self.get_events(output_format="csv", **kwargs)
        with open(filename, "w") as f:
            f.write(data)


class IEEEEventAnalyzer:
    """
    Analyzer for IEEE event data providing insights and statistics.
    """
    
    def __init__(self, client: IEEEEventsClient):
        self.client = client
    
    def analyze_event_distribution(self, events_data: Dict) -> Dict[str, int]:
        """Analyze geographic distribution of events."""
        distribution = {}
        
        for event in events_data.get("data", []):
            attrs = event.get("attributes", {})
            country = attrs.get("country", {}).get("name", "Unknown")
            distribution[country] = distribution.get(country, 0) + 1
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_virtual_vs_physical(self, events_data: Dict) -> Dict[str, int]:
        """Analyze distribution of virtual vs physical events."""
        distribution = {"virtual": 0, "physical": 0, "hybrid": 0}
        
        for event in events_data.get("data", []):
            attrs = event.get("attributes", {})
            if attrs.get("virtual"):
                distribution["virtual"] += 1
            else:
                distribution["physical"] += 1
        
        return distribution
    
    def get_trending_topics(self, events_data: Dict, top_n: int = 10) -> List[tuple]:
        """Extract trending topics from event keywords."""
        keywords_count = {}
        
        for event in events_data.get("data", []):
            attrs = event.get("attributes", {})
            keywords = attrs.get("keywords", "").split(",")
            
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    keywords_count[keyword] = keywords_count.get(keyword, 0) + 1
        
        return sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_monthly_event_count(self, events_data: Dict) -> Dict[str, int]:
        """Count events by month."""
        monthly_count = {}
        
        for event in events_data.get("data", []):
            attrs = event.get("attributes", {})
            start_time = attrs.get("start-time", "")
            
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    month_key = dt.strftime("%Y-%m")
                    monthly_count[month_key] = monthly_count.get(month_key, 0) + 1
                except:
                    pass
        
        return dict(sorted(monthly_count.items()))


def main():
    """Example usage of IEEE Events API client."""
    
    client = IEEEEventsClient()
    analyzer = IEEEEventAnalyzer(client)
    
    print("=== IEEE vTools Events API Demo ===\n")
    
    print("1. Fetching upcoming events for next 30 days...")
    upcoming = client.get_upcoming_events(days=30, limit=50)
    event_count = len(upcoming.get("data", []))
    print(f"Found {event_count} upcoming events\n")
    
    if event_count > 0:
        first_event = upcoming["data"][0]["attributes"]
        print("Sample Event:")
        print(f"  Title: {first_event.get('title', 'N/A')}")
        print(f"  Start: {first_event.get('start-time', 'N/A')}")
        print(f"  Location: {first_event.get('city', 'N/A')}, {first_event.get('country', {}).get('name', 'N/A')}")
        print(f"  Virtual: {first_event.get('virtual', False)}\n")
    
    print("2. Analyzing geographic distribution...")
    geo_dist = analyzer.analyze_event_distribution(upcoming)
    print("Top 5 countries:")
    for country, count in list(geo_dist.items())[:5]:
        print(f"  {country}: {count} events")
    print()
    
    print("3. Virtual vs Physical events...")
    location_dist = analyzer.analyze_virtual_vs_physical(upcoming)
    for location_type, count in location_dist.items():
        print(f"  {location_type.capitalize()}: {count} events")
    print()
    
    print("4. Fetching virtual events only...")
    virtual = client.get_virtual_events(limit=20)
    virtual_count = len(virtual.get("data", []))
    print(f"Found {virtual_count} virtual events\n")
    
    print("5. Analyzing trending topics...")
    topics = analyzer.get_trending_topics(upcoming, top_n=5)
    print("Top 5 topics:")
    for topic, count in topics:
        print(f"  {topic}: {count} events")
    print()
    
    print("6. Fetching available categories...")
    categories = client.get_categories()
    cat_count = len(categories.get("data", []))
    print(f"Found {cat_count} categories")
    
    if cat_count > 0:
        first_cat = categories["data"][0]["attributes"]
        print(f"Example: {first_cat.get('name', 'N/A')}")
        subcats = first_cat.get("subcategories", [])
        if subcats:
            print(f"  Subcategories: {', '.join([s['name'] for s in subcats[:3]])}")
    print()
    
    print("7. Exporting to iCal format...")
    try:
        client.export_to_ical("ieee_events.ics", limit=10)
        print("Exported to ieee_events.ics")
    except Exception as e:
        print(f"Export failed: {e}")
    print()
    
    print("Demo complete!")


if __name__ == "__main__":
    main()
