"""
IEEE vTools Events API - Comprehensive Examples
Demonstrates all API features with practical use cases
"""

from ieee_events import (
    IEEEEventsClientEnhanced,
    SpanBuilder,
    LocationType,
    TagsConnector,
    OutputFormat,
    TimeUnit
)
from datetime import datetime, timedelta, timezone


def example_basic_queries():
    """Example 1: Basic event queries"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Event Queries")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Get all upcoming events
    print("\n1.1 Get all upcoming events (next 30 days):")
    events = client.get_upcoming_events(days=30, limit=10)
    print(f"Found {len(events['data'])} events")
    if events['data']:
        first = events['data'][0]['attributes']
        print(f"First event: {first['title']}")
        print(f"Date: {first['start-time']}")
    
    # Get events for next week
    print("\n1.2 Get events for next 7 days:")
    week_events = client.get_upcoming_events(days=7, limit=10)
    print(f"Found {len(week_events['data'])} events")
    
    # Get events for next quarter
    print("\n1.3 Get events for next 90 days:")
    quarter_events = client.get_upcoming_events(days=90, limit=20)
    print(f"Found {len(quarter_events['data'])} events")


def example_location_filtering():
    """Example 2: Location-based filtering"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Location-Based Filtering")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Virtual events only
    print("\n2.1 Virtual events only:")
    virtual = client.get_virtual_events(days=60, limit=10)
    print(f"Found {len(virtual['data'])} virtual events")
    
    # Physical events only
    print("\n2.2 Physical events only:")
    physical = client.get_physical_events(days=60, limit=10)
    print(f"Found {len(physical['data'])} physical events")
    
    # Hybrid events only
    print("\n2.3 Hybrid events only:")
    hybrid = client.get_hybrid_events(days=60, limit=10)
    print(f"Found {len(hybrid['data'])} hybrid events")
    
    # Compare distribution
    print("\n2.4 Event distribution by location type:")
    print(f"  Virtual: {len(virtual['data'])}")
    print(f"  Physical: {len(physical['data'])}")
    print(f"  Hybrid: {len(hybrid['data'])}")


def example_advanced_span_queries():
    """Example 3: Advanced span queries with time arithmetic"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Advanced Span Queries")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Next 15 days
    print("\n3.1 Events in next 15 days:")
    span1 = SpanBuilder.now_plus(15, TimeUnit.DAYS)
    print(f"Span: {span1}")
    events1 = client.get_events(span=span1, limit=10)
    print(f"Found: {len(events1['data'])} events")
    
    # Next 2 months
    print("\n3.2 Events in next 2 months:")
    span2 = SpanBuilder.now_plus(2, TimeUnit.MONTHS)
    print(f"Span: {span2}")
    events2 = client.get_events(span=span2, limit=10)
    print(f"Found: {len(events2['data'])} events")
    
    # Last 30 days (past events)
    print("\n3.3 Events in last 30 days:")
    span3 = SpanBuilder.now_minus(30, TimeUnit.DAYS)
    print(f"Span: {span3}")
    events3 = client.get_events(span=span3, limit=10)
    print(f"Found: {len(events3['data'])} events")
    
    # From now onwards (no end date)
    print("\n3.4 All future events:")
    span4 = SpanBuilder.from_now_onwards()
    print(f"Span: {span4}")
    events4 = client.get_events(span=span4, limit=5)
    print(f"Found: {len(events4['data'])} events")
    
    # Events starting in 1 week, ending in 2 months
    print("\n3.5 Events between 1 week and 2 months from now:")
    span5 = SpanBuilder.range_from_now(7, 60, TimeUnit.DAYS)
    print(f"Span: {span5}")
    events5 = client.get_events(span=span5, limit=10)
    print(f"Found: {len(events5['data'])} events")
    
    # Last 6 hours
    print("\n3.6 Events in last 6 hours:")
    span6 = SpanBuilder.now_minus(6, TimeUnit.HOURS)
    print(f"Span: {span6}")
    events6 = client.get_events(span=span6, limit=5)
    print(f"Found: {len(events6['data'])} events")


def example_tag_based_search():
    """Example 4: Tag-based event search"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Tag-Based Event Search")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Single tag search
    print("\n4.1 Events with 'AI' tag:")
    ai_events = client.get_events_by_tags(["AI"], days=90, limit=10)
    print(f"Found: {len(ai_events['data'])} events")
    
    # Multiple tags with OR logic
    print("\n4.2 Events with 'AI' OR 'robotics' OR 'machine learning':")
    or_events = client.get_events_by_tags(
        ["AI", "robotics", "machine learning"],
        match_all=False,
        days=90,
        limit=10
    )
    print(f"Found: {len(or_events['data'])} events")
    
    # Multiple tags with AND logic
    print("\n4.3 Events with 'AI' AND 'robotics' (both required):")
    and_events = client.get_events_by_tags(
        ["AI", "robotics"],
        match_all=True,
        days=90,
        limit=10
    )
    print(f"Found: {len(and_events['data'])} events")
    
    # IEEE Day events
    print("\n4.4 Events with '#ieeeday' tag:")
    ieeeday = client.get_events_by_tags(["#ieeeday"], days=365, limit=10)
    print(f"Found: {len(ieeeday['data'])} events")


def example_delta_queries():
    """Example 5: Delta queries for incremental updates"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Delta Queries (Incremental Updates)")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Events updated in last 24 hours
    print("\n5.1 Events updated in last 24 hours:")
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().split('.')[0] + 'Z'
        delta1 = client.get_events_delta(since=yesterday, limit=20)
        print(f"Found: {len(delta1['data'])} events updated since {yesterday}")
    except Exception as e:
        print(f"✗ Failed (known API limitation): {type(e).__name__}")
    
    # Events updated in last week
    print("\n5.2 Events updated in last 7 days:")
    try:
        last_week = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().split('.')[0] + 'Z'
        delta2 = client.get_events_delta(since=last_week, limit=50)
        print(f"Found: {len(delta2['data'])} events updated since last week")
    except Exception as e:
        print(f"✗ Failed (known API limitation): {type(e).__name__}")
    
    # Events updated in last hour
    print("\n5.3 Events updated in last hour:")
    try:
        last_hour = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().split('.')[0] + 'Z'
        delta3 = client.get_events_delta(since=last_hour, limit=10)
        print(f"Found: {len(delta3['data'])} events updated in last hour")
    except Exception as e:
        print(f"✗ Failed (known API limitation): {type(e).__name__}")


def example_including_extra_data():
    """Example 6: Including speakers, media, and enhanced reports"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Including Extra Data (Speakers, Media, Reports)")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Include speaker data
    print("\n6.1 Events with speaker information:")
    with_speakers = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        include=["speakers"],
        limit=5
    )
    print(f"Found: {len(with_speakers['data'])} events")
    if with_speakers['data']:
        for event in with_speakers['data'][:2]:
            attrs = event['attributes']
            print(f"  - {attrs['title']}")
            # Speaker data would be in 'included' section per JSON:API spec
    
    # Include media data
    print("\n6.2 Events with media attachments:")
    with_media = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        include=["media"],
        limit=5
    )
    print(f"Found: {len(with_media['data'])} events")
    
    # Include everything
    print("\n6.3 Events with speakers, media, and enhanced reports:")
    with_all = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        include=["speakers", "media", "enhanced_report"],
        limit=5
    )
    print(f"Found: {len(with_all['data'])} events")


def example_pagination():
    """Example 7: Pagination for large datasets"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Pagination")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Manual pagination
    print("\n7.1 Manual pagination (10 events per page):")
    page1 = client.get_events(
        span=SpanBuilder.now_plus(90, TimeUnit.DAYS),
        limit=10,
        page=1
    )
    paging = page1['meta']['paging']
    print(f"Page 1 of {paging['total_pages']}")
    print(f"Events on this page: {len(page1['data'])}")
    print(f"Limit per page: {paging['limit']}")
    
    # Automatic pagination
    print("\n7.2 Automatic pagination (get 250 events total):")
    all_events = client.get_paginated_events(
        total_limit=250,
        page_size=50,
        span=SpanBuilder.now_plus(180, TimeUnit.DAYS)
    )
    print(f"Retrieved: {len(all_events)} events")


def example_export_formats():
    """Example 8: Exporting to different formats"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Export to Different Formats")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    print("\n8.1 Export to iCal format:")
    try:
        client.export_to_ical("examples_export.ics", days=60)
        print("✓ Successfully exported to examples_export.ics")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n8.2 Export to CSV format:")
    try:
        client.export_to_csv("examples_export.csv", days=60)
        print("✓ Successfully exported to examples_export.csv")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n8.3 Export to RSS format:")
    try:
        client.export_to_rss("examples_export.rss", days=60)
        print("✓ Successfully exported to examples_export.rss")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n8.4 Get HTML format (for embedding):")
    try:
        html = client.get_events(
            span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
            output_format=OutputFormat.HTML,
            limit=10
        )
        print(f"✓ Retrieved HTML ({len(html)} characters)")
    except Exception as e:
        print(f"✗ Failed: {e}")


def example_category_filtering():
    """Example 9: Category and subcategory filtering"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Category and Subcategory Filtering")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Get all categories first
    print("\n9.1 Available categories:")
    categories = client.get_categories()
    for cat in categories['data'][:3]:
        attrs = cat['attributes']
        print(f"  - {attrs['name']} (ID: {attrs['id']})")
        if attrs['subcategories']:
            for subcat in attrs['subcategories'][:2]:
                print(f"    - {subcat['name']} (ID: {subcat['id']})")
    
    # Filter by category
    print("\n9.2 Events in category ID 1 (Professional):")
    cat_events = client.get_events(
        category_id=[1],
        span=SpanBuilder.now_plus(60, TimeUnit.DAYS),
        limit=10
    )
    print(f"Found: {len(cat_events['data'])} events")
    
    # Filter by multiple categories
    print("\n9.3 Events in categories 1 and 2:")
    multi_cat = client.get_events(
        category_id=[1, 2],
        span=SpanBuilder.now_plus(60, TimeUnit.DAYS),
        limit=10
    )
    print(f"Found: {len(multi_cat['data'])} events")


def example_geographic_queries():
    """Example 10: Geographic queries"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Geographic Queries")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Get countries list
    print("\n10.1 Available countries (first 5):")
    countries = client.get_countries()
    for country in countries['data'][:5]:
        attrs = country['attributes']
        print(f"  - {attrs['name']} ({attrs['abbreviation']})")
        if attrs['states']:
            print(f"    States: {len(attrs['states'])}")
    
    # Get events and filter by country (client-side)
    print("\n10.2 Events by country (client-side filtering):")
    events = client.get_events(
        span=SpanBuilder.now_plus(60, TimeUnit.DAYS),
        limit=100
    )
    
    country_counts = {}
    for event in events['data']:
        country_name = event['attributes'].get('country', {}).get('name', 'Unknown')
        country_counts[country_name] = country_counts.get(country_name, 0) + 1
    
    print("Top 5 countries by event count:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {country}: {count} events")


def example_combined_filters():
    """Example 11: Combining multiple filters"""
    print("\n" + "="*80)
    print("EXAMPLE 11: Combined Filters")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Virtual + Tags + Time range
    print("\n11.1 Virtual AI/ML events in next 2 months:")
    combo1 = client.get_events(
        span=SpanBuilder.now_plus(60, TimeUnit.DAYS),
        location_type=LocationType.VIRTUAL,
        tags=["AI", "machine learning"],
        tags_connector=TagsConnector.OR,
        include=["speakers"],
        limit=20
    )
    print(f"Found: {len(combo1['data'])} events")
    
    # Physical + Published + Reported
    print("\n11.2 Published and reported physical events:")
    combo2 = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        location_type=LocationType.PHYSICAL,
        published=True,
        reported=True,
        limit=20
    )
    print(f"Found: {len(combo2['data'])} events")
    
    # Category + Tags + Location
    print("\n11.3 Professional category robotics events (virtual or hybrid):")
    # Note: This would require category ID lookup first
    combo3 = client.get_events(
        span=SpanBuilder.now_plus(90, TimeUnit.DAYS),
        tags=["robotics"],
        limit=20
    )
    # Filter for virtual/hybrid client-side
    vh_events = [e for e in combo3['data'] 
                 if e['attributes'].get('virtual', False)]
    print(f"Found: {len(vh_events)} virtual/hybrid robotics events")


def example_real_world_scenarios():
    """Example 12: Real-world usage scenarios"""
    print("\n" + "="*80)
    print("EXAMPLE 12: Real-World Scenarios")
    print("="*80)
    
    client = IEEEEventsClientEnhanced()
    
    # Scenario 1: Weekly newsletter
    print("\n12.1 Weekly Newsletter: Events in next 7 days")
    newsletter_events = client.get_upcoming_events(days=7, limit=50)
    print(f"Newsletter would include: {len(newsletter_events['data'])} events")
    
    # Scenario 2: Mobile app - nearby events
    print("\n12.2 Mobile App: Upcoming events (with all details)")
    mobile_events = client.get_events(
        span=SpanBuilder.now_plus(14, TimeUnit.DAYS),
        include=["speakers", "media"],
        sort="start-time",
        limit=20
    )
    print(f"Mobile app would show: {len(mobile_events['data'])} events")
    
    # Scenario 3: Analytics dashboard - this month's events
    print("\n12.3 Analytics: Current month statistics")
    analytics = client.get_events(
        span=SpanBuilder.now_plus(30, TimeUnit.DAYS),
        limit=500
    )
    virtual_count = sum(1 for e in analytics['data'] if e['attributes'].get('virtual'))
    physical_count = len(analytics['data']) - virtual_count
    print(f"Total events: {len(analytics['data'])}")
    print(f"Virtual: {virtual_count} ({virtual_count/len(analytics['data'])*100:.1f}%)")
    print(f"Physical: {physical_count} ({physical_count/len(analytics['data'])*100:.1f}%)")
    
    # Scenario 4: Researcher - historical trend analysis
    print("\n12.4 Research: Past quarter events")
    try:
        historical = client.get_past_events(days=90, limit=500)
        print(f"Historical analysis: {len(historical['data'])} events in past quarter")
    except Exception as e:
        print(f"✗ Failed (known API limitation): {type(e).__name__}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("IEEE VTOOLS EVENTS API - COMPREHENSIVE EXAMPLES")
    print("="*80)
    
    try:
        example_basic_queries()
        example_location_filtering()
        example_advanced_span_queries()
        example_tag_based_search()
        example_delta_queries()
        example_including_extra_data()
        example_pagination()
        example_export_formats()
        example_category_filtering()
        example_geographic_queries()
        example_combined_filters()
        example_real_world_scenarios()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

