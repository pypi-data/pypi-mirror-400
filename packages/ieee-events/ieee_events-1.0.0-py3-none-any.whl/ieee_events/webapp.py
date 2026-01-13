from flask import Flask, render_template_string, request, jsonify
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import json

app = Flask(__name__)

class IEEEEventsService:
    BASE_URL = "https://events.vtools.ieee.org/RST/events/api/public/v7"
    
    @staticmethod
    def get_events(params: Dict) -> Dict:
        """Fetch events from IEEE API with given parameters."""
        url = f"{IEEEEventsService.BASE_URL}/events/list"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_upcoming_events(days: int = 30, location_type: str = "all") -> Dict:
        """Get upcoming events within specified days."""
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        future = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat().replace('+00:00', 'Z')
        
        params = {
            "span": f"{now}~{future}",
            "limit": 100,
            "sort": "start-time",
            "location_type": location_type
        }
        
        return IEEEEventsService.get_events(params)
    
    @staticmethod
    def search_events(query: str, limit: int = 50) -> Dict:
        """Search events by title or keyword."""
        params = {
            "limit": limit,
            "sort": "-start-time"
        }
        
        data = IEEEEventsService.get_events(params)
        
        if query:
            filtered_events = []
            query_lower = query.lower()
            
            for event in data.get("data", []):
                attrs = event.get("attributes", {})
                title = attrs.get("title", "").lower()
                keywords = attrs.get("keywords", "").lower()
                description = attrs.get("description", "").lower()
                
                if query_lower in title or query_lower in keywords or query_lower in description:
                    filtered_events.append(event)
            
            data["data"] = filtered_events
        
        return data
    
    @staticmethod
    def get_categories() -> Dict:
        """Get all event categories."""
        url = f"{IEEEEventsService.BASE_URL}/categories/list"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEEE Events Explorer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 16px;
        }
        
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .control-group {
            flex: 1;
            min-width: 200px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        
        input, select, button {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .event-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .event-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .event-title {
            color: #333;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .event-meta {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
        }
        
        .meta-icon {
            width: 16px;
            height: 16px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-virtual {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .badge-physical {
            background: #f3e5f5;
            color: #7b1fa2;
        }
        
        .badge-hybrid {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .event-link {
            display: inline-block;
            margin-top: 10px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .event-link:hover {
            text-decoration: underline;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 18px;
        }
        
        .no-results {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>IEEE Events Explorer</h1>
            <p class="subtitle">Discover technical events from IEEE worldwide</p>
        </header>
        
        <div class="controls">
            <div class="control-group">
                <label for="search">Search Events</label>
                <input type="text" id="search" placeholder="Keywords or topics...">
            </div>
            
            <div class="control-group">
                <label for="timeframe">Timeframe</label>
                <select id="timeframe">
                    <option value="7">Next 7 days</option>
                    <option value="30" selected>Next 30 days</option>
                    <option value="60">Next 60 days</option>
                    <option value="90">Next 90 days</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="location-type">Location Type</label>
                <select id="location-type">
                    <option value="all">All Events</option>
                    <option value="virtual">Virtual Only</option>
                    <option value="physical">Physical Only</option>
                    <option value="hybrid">Hybrid Only</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>&nbsp;</label>
                <button onclick="loadEvents()">Search Events</button>
            </div>
        </div>
        
        <div class="stats" id="stats"></div>
        <div id="events-container"></div>
    </div>
    
    <script>
        async function loadEvents() {
            const container = document.getElementById('events-container');
            const statsContainer = document.getElementById('stats');
            
            container.innerHTML = '<div class="loading">Loading events...</div>';
            statsContainer.innerHTML = '';
            
            try {
                const timeframe = document.getElementById('timeframe').value;
                const locationType = document.getElementById('location-type').value;
                const search = document.getElementById('search').value;
                
                const response = await fetch(`/api/events?days=${timeframe}&location_type=${locationType}&search=${encodeURIComponent(search)}`);
                const data = await response.json();
                
                displayStats(data);
                displayEvents(data.data);
            } catch (error) {
                container.innerHTML = '<div class="no-results">Error loading events. Please try again.</div>';
            }
        }
        
        function displayStats(data) {
            const statsContainer = document.getElementById('stats');
            const events = data.data;
            
            const totalEvents = events.length;
            const virtualEvents = events.filter(e => e.attributes.virtual).length;
            const physicalEvents = totalEvents - virtualEvents;
            
            const countries = new Set(events.map(e => e.attributes.country?.name).filter(Boolean));
            
            statsContainer.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${totalEvents}</div>
                    <div class="stat-label">Total Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${virtualEvents}</div>
                    <div class="stat-label">Virtual Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${physicalEvents}</div>
                    <div class="stat-label">Physical Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${countries.size}</div>
                    <div class="stat-label">Countries</div>
                </div>
            `;
        }
        
        function displayEvents(events) {
            const container = document.getElementById('events-container');
            
            if (events.length === 0) {
                container.innerHTML = '<div class="no-results">No events found. Try adjusting your filters.</div>';
                return;
            }
            
            const eventsHtml = events.map(event => {
                const attrs = event.attributes;
                const startDate = new Date(attrs['start-time']);
                const endDate = new Date(attrs['end-time']);
                
                const locationBadge = attrs.virtual ? 
                    '<span class="badge badge-virtual">Virtual</span>' :
                    '<span class="badge badge-physical">Physical</span>';
                
                const location = attrs.virtual ? 
                    'Online Event' :
                    `${attrs.city || 'TBD'}, ${attrs.country?.name || 'TBD'}`;
                
                return `
                    <div class="event-card">
                        <div class="event-title">${attrs.title || 'Untitled Event'}</div>
                        ${locationBadge}
                        <div class="event-meta">
                            <div class="meta-item">
                                <span>📅</span>
                                <span>${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}</span>
                            </div>
                            <div class="meta-item">
                                <span>🕒</span>
                                <span>${startDate.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</span>
                            </div>
                            <div class="meta-item">
                                <span>📍</span>
                                <span>${location}</span>
                            </div>
                            ${attrs['primary-host']?.name ? `
                                <div class="meta-item">
                                    <span>🏢</span>
                                    <span>${attrs['primary-host'].name}</span>
                                </div>
                            ` : ''}
                        </div>
                        ${attrs.link ? `<a href="${attrs.link}" class="event-link" target="_blank">View Details →</a>` : ''}
                    </div>
                `;
            }).join('');
            
            container.innerHTML = `<div class="events-grid">${eventsHtml}</div>`;
        }
        
        loadEvents();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render the main application page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/events')
def api_events():
    """API endpoint for fetching events."""
    try:
        days = int(request.args.get('days', 30))
        location_type = request.args.get('location_type', 'all')
        search_query = request.args.get('search', '')
        
        if search_query:
            data = IEEEEventsService.search_events(search_query)
        else:
            data = IEEEEventsService.get_upcoming_events(days, location_type)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/categories')
def api_categories():
    """API endpoint for fetching categories."""
    try:
        data = IEEEEventsService.get_categories()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
