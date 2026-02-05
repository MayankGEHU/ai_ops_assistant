# AI Operations Assistant

A multi-agent AI system that accepts natural-language tasks, plans execution steps, calls external APIs, and returns structured results. Built with a three-agent architecture (Planner, Executor, Verifier) and integrated with real third-party APIs.

## 🏗️ Architecture

### Multi-Agent System

1. **Planner Agent** (`agents/planner.py`)
   - Converts natural language tasks into structured execution plans
   - Uses LLM with JSON schema constraints for structured outputs
   - Selects appropriate tools for each step

2. **Executor Agent** (`agents/executor.py`)
   - Executes planned steps sequentially
   - Calls external APIs through tool integrations
   - Handles errors and retries with exponential backoff

3. **Verifier Agent** (`agents/verifier.py`)
   - Validates execution results using LLM reasoning
   - Identifies missing or incorrect outputs
   - Determines if retries are needed
   - Formats final structured output

### Tool Integrations

- **GitHub Tool** (`tools/github_tool.py`)
  - Search repositories by query
  - Fetch repository details (stars, description, URL)
  
- **Weather Tool** (`tools/weather_tool.py`)
  - Get current weather by city name
  - Returns temperature, conditions, humidity, wind speed

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API Keys:
  - Google Gemini API key (for LLM)
  - OpenWeatherMap API key (for weather data)
  - GitHub API (no key required, but rate-limited)

### Installation

1. Clone the repository:
```bash
cd ai_ops_assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
```

### Running the Application

#### Option 1: API Server Mode

Start the FastAPI server:
```bash
python main.py --server
# or
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### Option 2: CLI Mode

Run tasks directly from command line:
```bash
python main.py "Get the weather in New York and find top 3 Python repositories"
```

## 📡 API Usage

### Endpoint: POST `/run-task`

Execute a natural language task.

**Request:**
```json
{
  "task": "Get the weather in London and find top 5 JavaScript repositories",
  "max_retries": 3
}
```

**Response:**
```json
{
  "task": "Get the weather in London and find top 5 JavaScript repositories",
  "plan": {
    "steps": [
      {
        "tool": "weather.get_weather",
        "input": {"city": "London"},
        "description": "Get weather for London"
      },
      {
        "tool": "github.search_repos",
        "input": {"query": "javascript", "limit": 5},
        "description": "Find top JavaScript repositories"
      }
    ]
  },
  "results": [
    {
      "step": 1,
      "tool": "weather.get_weather",
      "description": "Get weather for London",
      "input": {"city": "London"},
      "output": {
        "city": "London",
        "temperature": 15.5,
        "condition": "clear sky",
        "humidity": 65,
        "wind_speed": 3.2
      },
      "success": true
    },
    {
      "step": 2,
      "tool": "github.search_repos",
      "description": "Find top JavaScript repositories",
      "input": {"query": "javascript", "limit": 5},
      "output": [
        {
          "name": "freeCodeCamp",
          "stars": 372000,
          "url": "https://github.com/freeCodeCamp/freeCodeCamp",
          "description": "freeCodeCamp.org's open-source codebase"
        }
      ],
      "success": true
    }
  ],
  "verification": {
    "verified": true,
    "summary": "All steps completed successfully",
    "needs_retry": false,
    "retry_steps": [],
    "final_output": {
      "task_completed": true,
      "summary": "Task completed successfully",
      "total_steps": 2,
      "successful_steps": 2,
      "failed_steps": 0,
      "issues": [],
      "data": {
        "get_weather": {
          "city": "London",
          "temperature": 15.5,
          "condition": "clear sky"
        },
        "search_repos": [
          {
            "name": "freeCodeCamp",
            "stars": 372000,
            "url": "https://github.com/freeCodeCamp/freeCodeCamp",
            "description": "freeCodeCamp.org's open-source codebase"
          }
        ]
      }
    }
  }
}
```

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/run-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is the weather in Tokyo?",
    "max_retries": 3
  }'
```

## 🔧 Project Structure

```
ai_ops_assistant/
├── agents/              # Agent implementations
│   ├── __init__.py
│   ├── planner.py      # Planner Agent
│   ├── executor.py     # Executor Agent
│   └── verifier.py     # Verifier Agent
├── tools/              # API tool integrations
│   ├── __init__.py
│   ├── github_tool.py  # GitHub API integration
│   └── weather_tool.py # Weather API integration
├── llm/                # LLM client
│   ├── __init__.py
│   └── client.py      # LLM wrapper with structured outputs
├── main.py             # API server and CLI entry point
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🎯 Features

- ✅ **Multi-Agent Architecture**: Planner, Executor, and Verifier agents
- ✅ **LLM-Powered Reasoning**: Uses Google Gemini for planning and verification
- ✅ **Structured Outputs**: JSON schema-constrained LLM responses
- ✅ **Real API Integrations**: GitHub and Weather APIs
- ✅ **Error Handling**: Retry logic with exponential backoff
- ✅ **Multiple Interfaces**: REST API and CLI
- ✅ **Comprehensive Logging**: Step-by-step execution tracking

## 🔍 How It Works

1. **User submits task** via API or CLI
2. **Planner Agent** analyzes the task and creates a JSON execution plan with tool selections
3. **Executor Agent** iterates through steps, calling appropriate tools (GitHub API, Weather API)
4. **Verifier Agent** validates results using LLM reasoning:
   - Checks completeness
   - Identifies errors
   - Determines if retries are needed
   - Formats final structured output
5. **Retry logic** automatically retries failed steps if needed
6. **Final response** returns structured results

## 🛠️ Development

### Adding New Tools

1. Create a new tool file in `tools/`:
```python
# tools/news_tool.py
def get_news(query: str) -> dict:
    # Implementation
    return {"articles": [...]}
```

2. Register in `agents/executor.py`:
```python
TOOL_MAP = {
    "github.search_repos": search_repos,
    "weather.get_weather": get_weather,
    "news.get_news": get_news  # Add here
}
```

3. Update Planner schema in `agents/planner.py`:
```python
"enum": ["github.search_repos", "weather.get_weather", "news.get_news"]
```

### Testing

Test individual components:
```python
# Test Planner
from agents.planner import create_plan
plan = create_plan("Get weather in Paris")
print(plan)

# Test Executor
from agents.executor import execute_plan
results = execute_plan(plan)
print(results)

# Test Verifier
from agents.verifier import verify_results
verification = verify_results(results)
print(verification)
```

## 📝 Example Tasks

- "Get the weather in San Francisco"
- "Find the top 10 Python repositories on GitHub"
- "What's the weather in Tokyo and show me 3 popular React repositories"
- "Get weather for New York, London, and Tokyo"
- "Find repositories about machine learning and get weather in Boston"

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for LLM | Yes |
| `WEATHER_API_KEY` | OpenWeatherMap API key | Yes |

Get your API keys:
- Gemini: https://makersuite.google.com/app/apikey
- OpenWeatherMap: https://openweathermap.org/api

## 🐛 Troubleshooting

**Issue**: "WEATHER_API_KEY not configured"
- Solution: Add your OpenWeatherMap API key to `.env` file

**Issue**: "LLM Error: API key invalid"
- Solution: Verify your Gemini API key is correct in `.env`

**Issue**: "City not found" for weather
- Solution: Use standard city names (e.g., "New York" not "NYC")

**Issue**: GitHub API rate limiting
- Solution: GitHub API allows 60 requests/hour without authentication. Consider adding a GitHub token for higher limits.

## 🚀 Future Improvements

With more time, consider adding:
- Caching API responses
- Cost tracking per request
- Parallel tool execution
