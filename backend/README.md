# Pandit Pradeep Kiradoo Astrology API v2.0

A FastAPI backend for the Vedic Astrology consultation system with advanced LangGraph-powered conversation flow management.

## Features

- **LangGraph Integration**: Advanced conversation state management and flow control
- **AI Chatbot**: Powered by GROQ API with llama-3.1-70b-versatile model
- **Session Management**: Persistent conversation sessions with state tracking
- **Stage-based Analysis**: Progressive astrological consultation process
- **Astrological Analysis**: Birth chart analysis and planetary insights
- **RESTful API**: Clean and documented API endpoints
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Error Handling**: Comprehensive error handling and validation


## Setup

1. **Create Environment Configuration**:
   ```bash
   python setup_env.py
   ```
   This will create a `.env` file with default configuration.

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables** (Optional):
   Edit the `.env` file to customize:
   - `GROQ_API_KEY`: Your GROQ API key
   - `HOST`: Server host (default: 0.0.0.0)
   - `PORT`: Server port (default: 8000)
   - `ALLOWED_ORIGINS`: CORS origins (comma-separated)
   - `MODEL_NAME`: AI model name
   - `TEMPERATURE`: AI response temperature
   - `MAX_TOKENS`: Maximum tokens per response

4. **Run the Server**:
   ```bash
   python main.py
   ```
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - API status and services
- `GET /health` - Health check endpoint

### Chatbot
- `POST /chat` - Chat with Pandit Pradeep Kiradoo (LangGraph-powered)
- `POST /analyze-birth-details` - Analyze birth details
- `GET /session/{session_id}` - Get session information

## Environment Variables

The API uses the following configuration from the `.env` file:

### Required
- `GROQ_API_KEY`: Your GROQ API key for GROQ services

### Optional (with defaults)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `ALLOWED_ORIGINS`: CORS origins (default: http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173)
- `MODEL_NAME`: AI model name (default: llama-3.1-70b-versatile)
- `TEMPERATURE`: AI response temperature (default: 0.7)
- `MAX_TOKENS`: Maximum tokens per response (default: 800)

### Creating .env File
Run the setup script to create a `.env` file with default values:
```bash
python setup_env.py
```

## Frontend Integration

The backend is configured to work with the React frontend running on:
- http://localhost:5173
- http://localhost:8081

## Chatbot Features

- **LangGraph Conversation Flow**: Advanced state management for progressive consultation
- **Session Management**: Persistent conversation sessions with context preservation
- **Stage-based Analysis**: Structured consultation process (initial → birth details → analysis → remedies)
- **Vedic Astrology Expertise**: Specialized in Jyotish Shastra
- **Birth Chart Analysis**: Planetary influences and remedies
- **Professional Guidance**: Compassionate and supportive responses
- **Dynamic Suggestions**: Context-aware quick questions and responses
- **Error Handling**: Graceful fallback responses

## Development

The chatbot uses LangGraph for conversation flow management and the GROQ API with the `llama-3.1-70b-versatile` model for optimal performance and accuracy in astrological consultations.

### LangGraph Architecture

The conversation flow is managed through a state graph with the following stages:
1. **Initial Greeting**: Welcome and understanding user concerns
2. **Birth Details Collection**: Gathering birth information
3. **Astrological Analysis**: Providing insights based on birth chart
4. **Remedies & Recommendations**: Offering specific guidance and solutions

Each stage maintains conversation context and provides appropriate responses based on the current consultation phase.
