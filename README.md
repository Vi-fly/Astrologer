# Astral Insights Alchemy - Vedic Astrology Consultation System

Welcome to **Pandit Pradeep Kiradoo's** comprehensive Vedic Astrology consultation platform. This application provides deep astrological insights through planetary analysis and cosmic wisdom.

## 🌟 Features

- **Birth Chart Analysis**: Comprehensive analysis based on birth details
- **Planetary Influence Reports**: Detailed insights into planetary positions and their effects
- **Problem Analysis**: Connect life challenges to astrological influences
- **Professional Consultation**: Expert Vedic astrology guidance

## 🚀 Getting Started

### Frontend Setup
1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Access Application**:
   - Open `http://localhost:5173/` in your browser
   - Click the "Chat with Pandit Ji" button for smooth navigation to the chat page
   - Enjoy beautiful animations and transitions between pages
   - Visit `http://localhost:5173/chat` for direct access to the chat page

### Backend Setup
1. **Create Environment Configuration**:
   ```bash
   cd backend
   python setup_env.py
   ```

2. **Install Python Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure API Key** (Optional):
   Edit `backend/.env` file and update the `GROQ_API_KEY` if needed.

4. **Start Backend Server**:
   ```bash
   cd backend
   python main.py
   ```
   Or with uvicorn:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Test Configuration** (Optional):
   ```bash
   cd backend
   python test_config.py
   ```

6. **API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🛠️ Technology Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Build Tool**: Vite
- **Routing**: React Router DOM
- **Animations**: GSAP (GreenSock Animation Platform)
- **Backend**: Python FastAPI with LangGraph
- **AI Integration**: GROQ API (llama-3.1-70b-versatile)
- **Conversation Flow**: LangGraph for state management
- **Consultation System**: Dedicated chat page + AI Chatbot with session management

## 📊 Consultation Process

1. **AI Chatbot Interaction**: Initial guidance and quick questions
2. **Birth Details Collection**: Date, time, and place of birth
3. **Astrological Analysis**: Planetary positions and influences
4. **Life Guidance**: Career, relationships, and personal development
5. **Remedies & Recommendations**: Gemstones, mantras, and spiritual practices

## 🎯 Purpose

This system provides professional Vedic astrology consultations, helping individuals understand their life's challenges and opportunities through the lens of planetary influences and cosmic wisdom.

## 🚀 Current Status

✅ **Fully Functional** - All UI issues have been resolved  
✅ **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices  
✅ **Form Validation** - Comprehensive error handling and user feedback  
✅ **Professional Branding** - Consistent Pandit Pradeep Kiradoo branding throughout  
✅ **Modern UI/UX** - Beautiful animations and smooth interactions  
✅ **Cross-Browser Compatible** - Works on all modern browsers  
✅ **Comprehensive Footer** - Complete contact details, services, and consultation hours  
✅ **Professional Contact Info** - Phone, email, location, and availability details  
✅ **AI Chatbot** - Interactive chatbot powered by GROQ API  
✅ **Python Backend** - FastAPI server with LangGraph conversation flow  
✅ **Dedicated Chat Page** - Full-screen chat interface for better UX  
✅ **LangGraph Integration** - Advanced conversation state management  
✅ **Session Management** - Persistent conversation sessions  
✅ **Stage-based Analysis** - Progressive astrological consultation  
✅ **Privacy Protected** - No personal contact information displayed

---

**Developed by Pandit Pradeep Kiradoo** - Bringing ancient Vedic wisdom to the modern world through technology.
