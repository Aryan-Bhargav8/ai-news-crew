# NewsReporterCrew

An intelligent news research and report generation system powered by **CrewAI**, **FastAPI**, and **Groq LLM**. This application automatically researches trending topics and generates comprehensive reports using a multi-agent AI system.

## 📋 Overview

NewsReporterCrew leverages CrewAI's multi-agent architecture to:
- **Research** trending topics using web search via SerperDev API
- **Analyze** findings with intelligent reasoning
- **Generate** detailed markdown reports with structured insights

The system runs as a FastAPI application, making it easy to integrate into your workflow through REST API endpoints.

## 🎯 Key Features

- **Multi-Agent System**: Two specialized AI agents working collaboratively
  - **Senior Data Researcher**: Conducts thorough web research and gathers information
  - **Reporting Analyst**: Transforms research into detailed, structured reports
- **Web Search Integration**: Uses SerperDev API for real-time information retrieval
- **Fast LLM Inference**: Powered by Groq's optimized LLM endpoints for quick response times
- **REST API**: Simple HTTP endpoints for submitting research queries
- **Docker Support**: Fully containerized for easy deployment
- **CORS Enabled**: Accessible from any frontend application

## 🛠️ Tech Stack

- **Framework**: FastAPI + CrewAI
- **LLM**: Groq (groq/openai/gpt-oss-120b)
- **Search**: SerperDev API
- **Server**: Uvicorn
- **Deployment**: Docker

## 📦 Requirements

- Python 3.13+
- Docker (optional, for containerization)
- API Keys:
  - `GROQ_API_KEY`: Groq API key for LLM access
  - `SERPER_API_KEY`: SerperDev API key for web search

## 🚀 Quick Start

### Local Setup

1. **Clone and install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables** - Create a `.env` file:
   ```env
   GROQ_API_KEY="your_groq_api_key"
   MODEL="groq/openai/gpt-oss-120b"
   SERPER_API_KEY="your_serper_api_key"
   ```

3. **Run the application**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

1. **Build the Docker image**:
   ```bash
   docker build -t newsreportercrew:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -d --name test --env-file .env -p 8000:8000 newsreportercrew:latest
   ```

   Or use the public image:
   ```bash
   docker run -d --name test --env-file .env -p 8000:8000 bhargavaryan8/newsreportercrew:latest
   ```

## 📡 API Endpoints

### Health Check
```bash
GET /
```
Response:
```json
{
  "status": "working",
  "message": "API WORKS FINE"
}
```

### Generate Report
```bash
POST /run
Content-Type: application/json

{
  "topic": "AI Breakthroughs in 2026"
}
```

Response:
```json
{
  "result": "Fully detailed markdown report with research findings..."
}
```

## 📁 Project Structure

```
.
├── main.py              # FastAPI application and API routes
├── agents.py            # CrewAI agent definitions
├── tasks.py             # CrewAI task definitions
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env.example                 # Environment variables example
└── github/workflows/    # CI/CD pipeline
    └── build-push-docker.yml
```

## 🔧 How It Works

1. **User submits a topic** via the `/run` endpoint
2. **Researcher Agent** searches the web for relevant information using SerperDev
3. **Researcher compiles** findings into 10 bullet points
4. **Reporting Analyst** expands bullet points into a comprehensive markdown report
5. **Report is returned** to the user via the API

The entire workflow uses sequential processing, ensuring research is completed before report generation begins.

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | API key for Groq LLM service | `gsk_xxx...` |
| `MODEL` | LLM model identifier | `groq/openai/gpt-oss-120b` |
| `SERPER_API_KEY` | API key for SerperDev search | `abc123...` |
| `PORT` | Server port (default: 8000) | `8000` |

## 🐳 Docker Configuration

The application runs on port 8000 inside the container. The Dockerfile:
- Uses Python 3.13.11-slim as base image
- Installs all dependencies via pip
- Exposes port 8000
- Starts Uvicorn server with dynamic PORT configuration

## 🔄 CI/CD Pipeline

GitHub Actions workflow automatically:
- Builds the Docker image on push
- Pushes to Docker Hub registry
- Tags with latest version

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open-source and available under the MIT License.
