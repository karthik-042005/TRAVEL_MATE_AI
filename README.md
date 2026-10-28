# 🌍 TravelMate AI — Agentic Full-Stack Travel Planner

TravelMate AI is an autonomous, agentic travel-planning platform designed to turn complex natural-language travel requests into rich, interactive, and actionable itineraries. Powered by **LangGraph**, **Ollama LLaMA 3.2 3B**, **Geoapify Maps**, **OpenWeatherMap**, **Tavily Live Search**, and a responsive **React + Leaflet** frontend with modern glassmorphism aesthetics.

---

## ✨ Features

- 🧠 **Agentic LangGraph Workflow**: Multi-node state graph orchestrating extraction, research planning, parallel tool retrieval, evidence validation, synthesis, and response formatting.
- 🗺️ **Interactive Route & Destination Maps**: Full Leaflet-based interactive maps rendering destination pins, POI attractions, and color-coded route polyline with OpenStreetMap direction links.
- 🌤️ **Live Weather & Multi-Day Forecasts**: Real-time conditions, humidity, wind speeds, and forecasts up to 5 days with clear indicators when dates fall outside the forecast window.
- 🛡️ **Safety & Hazard Research**: Multi-query web intelligence tracking landslide advisories, road closures, and official regional warnings with severity categorization.
- 📍 **Points of Interest Discovery**: Nearby tourist sights, parks, monuments, and cultural attractions with geographic coordinates and opening hours.
- 🔌 **Model Context Protocol (MCP) Server**: Built-in MCP server (`backend/app/mcp_servers/travel_mcp_server.py`) exposing travel tools via standard MCP protocols.
- 🎨 **Glassmorphism UI**: Custom dark mode with glowing accents, thinking indicators, animated transitions, collapsible safety panels, and mobile-ready responsive layouts.

---

## 🏛️ Architecture

```
User Prompt: "I want to go to Ooty from Bangalore next weekend. Check weather, road safety, and attractions."
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      TravelMate AI UI                       │
│    (React 18 + TailwindCSS + Leaflet Maps + Framer Motion)   │
└──────────────────────────────┬──────────────────────────────┘
                               │  POST /api/v1/travel/plan
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                    │
│                  (Uvicorn on Port 8000)                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                LangGraph StateGraph Workflow                │
│                                                             │
│   Node A: [parse_request]       (Ollama LLaMA 3.2 3B)       │
│              │                                              │
│   Node B: [plan_research]       (Check available tools)     │
│              │                                              │
│   Node C: [retrieve_data]       (Asyncio Parallel Gather)   │
│         ├── OpenWeatherMap API  (Weather observations)      │
│         ├── Geoapify API        (Geocoding & Routing)       │
│         ├── Geoapify Places API (Sights & Attractions)      │
│         └── Tavily Search API   (Safety & Hazard Search)    │
│              │                                              │
│   Node D: [validate_evidence]   (Facts vs warnings vs gap)  │
│              │                                              │
│   Node E: [generate_plan]       (LLM Synthesis)             │
│              │                                              │
│   Node F: [format_response]     (JSON TravelPlanResponse)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                   Structured Plan + Visual Map
```

---

## 🚀 Quickstart

### Prerequisites

- **Python 3.10+** (tested on Python 3.13)
- **Node.js 18+** & npm
- **Ollama** running locally with `llama3.2:3b`:
  ```bash
  ollama run llama3.2:3b
  ```

### 1. Environment Setup

Create `.env` inside `backend/` (or use the root `.env`):

```env
# Ollama LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Live Web Search (Tavily)
TAVILY_API_KEY=your_tavily_key

# Weather (OpenWeatherMap)
OPENWEATHER_API_KEY=your_openweather_key

# Maps & Places (Geoapify)
GEOAPIFY_API_KEY=your_geoapify_key

# Application
FRONTEND_ORIGIN=http://localhost:5173
```

### 2. Backend Setup & Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Tool Status: `http://localhost:8000/api/v1/tools/status`

### 3. Frontend Setup & Run

```bash
cd frontend
npm install
npm run dev
```

- Open `http://localhost:5173` in your browser.

---

## 🛠️ MCP Server (Model Context Protocol)

TravelMate AI provides an MCP server for integration with any standard MCP host:

```bash
cd backend
python -m app.mcp_servers.travel_mcp_server
```

**Exposed MCP Tools:**
- `get_weather(location, target_date)`
- `search_places(location, limit)`
- `calculate_route(origin, destination, mode)`
- `research_safety(destination, travel_date)`
- `search_travel_web(query)`

---

## 🧪 Testing

Run backend tests:
```bash
cd backend
python -c "import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())"
```

Build frontend for production:
```bash
cd frontend
npm run build
```

---

## 🎙️ Presentation & Interview Guide

For a comprehensive presentation script, architecture deep-dive, trade-off analysis, and 20+ interview Q&As, see:
👉 **[INTERVIEW_PRESENTATION.md](file:///c:/Users/ASUS/Downloads/Projects/Travel-Mate/INTERVIEW_PRESENTATION.md)**

