# Stylii – AI-Powered Interior Design Platform

Stylii is an advanced AI-driven web application that transforms room photographs into photorealistic design renderings with curated product recommendations. The system integrates multi-modal AI models, computer vision, and real-time streaming architectures to deliver intelligent interior design solutions for end users. Built with a modular full-stack architecture, Stylii exemplifies production-style AI integration across all service layers.

---

## Features

- **Room-to-Design Transformation** – Upload a photo and generate multiple design styles (Modern, Scandinavian, Industrial, etc.).
- **Photorealistic Rendering** – Uses state-of-the-art AI models to create high-quality room visualizations.
- **Product Integration** – Recommends real furniture and decor with live pricing and availability.
- **Real-Time Streaming** – Provides progress updates through async streaming and WebSocket support.
- **Multi-Modal AI Analysis** – Combines NLP, computer vision, and generative AI for style detection and layout planning.

---

## System Architecture

```
stylii/
├── frontend/       # Next.js 15 + Tailwind CSS React application
├── backend/        # FastAPI orchestration service with Supabase and Weaviate backend
├── img-gen/        # AI image generation (FalAI integration)
├── products/       # Product search and recommendation service (SerpAPI + Supabase)
├── video_gen/      # Video and audio synthesis service (ElevenLabs audio narration)
└── designer/       # Room analysis and layout classification
```

---

## Technology Stack

Stylii leverages a comprehensive and modular full-stack technology stack designed for scalable, production-grade AI-powered applications.

**Frontend**

- Next.js 15 (React with App Router)
- TypeScript, Tailwind CSS, Radix UI
- Zustand for state management, React Hook Form + Zod

**Backend / Database**

- FastAPI with async/await orchestration
- Python 3.11+ with type hints and Pydantic
- Supabase for backend database and authentication
- Weaviate vector search for semantic data retrieval
- httpx + uvicorn for async orchestration

**AI & ML Integrations**

- **Google Gemini 2.0 Flash** – natural language understanding and room analysis
- **FalAI** – photorealistic image generation and style transfer
- **SerpAPI** – multi-retailer product search and price comparison
- **CrewAI** – orchestration and workflow automation
- **Custom CV Models** – furniture recognition, layout detection, style classification
- **ElevenLabs** – high-quality audio narration for video generation

---

## Quick Start

```bash
git clone https://github.com/ShyamThangaraj/Stylii.git
cd Stylii
./start.sh
```

### Manual Service Setup

**Backend Orchestration**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend Application**

```bash
cd frontend
npm install
npm run dev
```

**Image Generation / Product Services / Video Gen**
Follow the same process with `pip install -r requirements.txt` and run the appropriate server file.

---

## API Endpoints

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## Data Flow

1. **Image Upload** → FastAPI validates and streams data.
2. **Room Analysis** → Gemini + CV models detect layout, furniture, and style.
3. **Product Search** → SerpApi finds matching items across Amazon, Wayfair, etc.
4. **Image Generation** → FalAI renders photorealistic designs with integrated products.
5. **Streaming Updates** → Real-time progress sent to frontend.

---

## Target Users

- Students and first-time renters
- Young adults setting up apartments
- Budget-conscious users seeking AI-assisted design inspiration
- Tech-savvy early adopters of AI tools

---

## License

MIT License – see [LICENSE](LICENSE) for details.

---

## About

Stylii demonstrates the potential of AI in interior design by merging real-time rendering, intelligent product recommendations, and user-driven style preferences into a seamless platform. Its modular architecture and production-style AI integration enable extensibility and robust performance across all components.
