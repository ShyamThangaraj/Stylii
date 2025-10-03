# 🎨 Stylii - AI-Powered Interior Design Assistant

Advanced AI-driven interior design platform leveraging multi-modal machine learning, computer vision, and real-time streaming architectures to transform room photographs into photorealistic design renderings with integrated product recommendations.

## 🏗️ System Architecture

```
stylii/
├── frontend/          # Next.js 15 React application with App Router
├── backend/           # FastAPI orchestration service with async streaming
├── img-gen/          # AI image generation service (FalAI integration)
├── products/         # Product search and recommendation service
├── video_gen/        # Video generation service with audio synthesis
└── designer/         # Room analysis and design service
```

## 🛠️ Technology Stack

**Frontend:**

- Next.js 15 with App Router and Server Components
- TypeScript with strict type checking
- Tailwind CSS with custom design system
- Radix UI for accessible components
- Zustand for state management
- React Hook Form with Zod validation

**Backend Services:**

- FastAPI with async/await patterns
- Python 3.11+ with type hints
- httpx for async HTTP client operations
- uvicorn ASGI server with WebSocket support
- Pydantic for data validation and serialization

**AI & ML Integrations:**

- Google Gemini 2.0 Flash for natural language processing
- SerpApi for real-time product search across multiple retailers
- FalAI for advanced image generation and manipulation
- Custom computer vision models for room analysis
- Streaming response architecture for real-time progress updates

## 🚀 Setup & Installation

### Prerequisites

- Node.js 18+ with npm/pnpm
- Python 3.11+ with pip/uv
- Git for version control

### Environment Configuration

Create environment files for each service:

**Backend (.env):**

```bash
BACKEND_URL=http://localhost:8000
DESIGNER_SERVICE_URL=http://localhost:8009
IMG_GEN_SERVICE_URL=http://localhost:8005
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**AI Services (.env):**

```bash
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_KEY=your_serpapi_key
FALAI_API_KEY=your_falai_api_key
```

### Quick Start

```bash
git clone https://github.com/ShyamThangaraj/Stylii.git
cd Stylii
./start.sh
```

### Manual Service Setup

**1. Backend Orchestration Service:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**2. Frontend Application:**

```bash
cd frontend
npm install
npm run dev
```

**3. AI Image Generation Service:**

```bash
cd img-gen
pip install -r requirements.txt
python main.py
```

**4. Product Search & Recommendation Service:**

```bash
cd products
pip install -r requirements.txt
python designer_server.py
```

**5. Video Generation Service:**

```bash
cd video_gen
pip install -r requirements.txt
python server.py
```

## 🌐 Service Endpoints

### Core API Endpoints

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Service Ports

- **Frontend**: 3000
- **Backend Orchestration**: 8000
- **Designer Service**: 8009
- **Image Generation**: 8005
- **Video Generation**: 8007

## 📊 API Architecture

### Streaming Design Endpoint (`POST /design`)

Real-time streaming endpoint that orchestrates multiple AI services:

1. **Room Analysis Phase:**

   - Computer vision analysis of uploaded room image
   - Style classification using pre-trained models
   - Furniture and layout detection
   - Budget and preference parsing

2. **Product Discovery Phase:**

   - Natural language processing of room requirements
   - Multi-retailer product search via SerpApi
   - Price comparison and availability checking
   - Product recommendation scoring algorithm

3. **Image Generation Phase:**
   - FalAI integration for photorealistic rendering
   - Product integration into room scenes
   - Style transfer and enhancement
   - High-resolution output generation

### Synchronous Endpoint (`POST /design-sync`)

Non-streaming alternative for simpler integrations.

## 🔧 Advanced Integrations

### Google Gemini 2.0 Flash Integration

- **Natural Language Processing**: Converts user preferences into structured queries
- **Room Analysis**: AI-powered understanding of room types, styles, and layouts
- **Product Matching**: Intelligent product recommendation based on room context
- **Content Generation**: Automated descriptions and marketing copy

### SerpApi Product Search Integration

- **Multi-Retailer Search**: Amazon, eBay, Wayfair, and other major retailers
- **Real-time Pricing**: Live price comparison across platforms
- **Product Metadata**: Images, descriptions, ratings, and availability
- **Affiliate Link Generation**: Monetization through product sales

### FalAI Image Generation Integration

- **Photorealistic Rendering**: High-quality room visualization
- **Product Integration**: Seamless placement of recommended items
- **Style Transfer**: Multiple design aesthetic applications
- **Batch Processing**: Efficient handling of multiple design variations

### Computer Vision Pipeline

- **Room Type Detection**: Automatic classification of space types
- **Furniture Recognition**: Identification of existing furniture and fixtures
- **Layout Analysis**: Spatial understanding and measurement estimation
- **Style Classification**: Current design aesthetic identification

## 🔍 Health Monitoring

```bash
./health.sh
```

Advanced health checking with:

- Service availability verification
- API endpoint testing
- Database connectivity checks
- AI service status monitoring
- Performance metrics collection

## 🛠️ Development Workflow

### Frontend Development

```bash
cd frontend
npm run dev          # Development server with hot reload
npm run build        # Production build optimization
npm run lint         # ESLint code quality checks
npm run type-check   # TypeScript compilation verification
```

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py       # Development server with auto-reload
```

### Adding New Features

- **Frontend Components**: `frontend/components/`
- **API Endpoints**: `backend/main.py`
- **AI Services**: Individual service directories
- **Database Models**: Pydantic schemas in each service

## 📖 Technical Implementation Details

### Real-time Streaming Architecture

- Server-Sent Events (SSE) for progress updates
- Async/await patterns for non-blocking operations
- WebSocket support for bidirectional communication
- Queue-based task processing for scalability

### AI Model Integration

- **Gemini 2.0 Flash**: Multi-modal AI for text and image understanding
- **Custom CV Models**: Room analysis and furniture detection
- **FalAI Models**: State-of-the-art image generation
- **SerpApi**: Real-time product search and data aggregation

### Data Flow Architecture

1. **Image Upload** → FastAPI file handling with validation
2. **Room Analysis** → Gemini AI + custom CV models
3. **Product Search** → SerpApi multi-retailer aggregation
4. **Image Generation** → FalAI photorealistic rendering
5. **Response Streaming** → Real-time progress updates

### Performance Optimizations

- Async HTTP client operations with httpx
- Image compression and optimization
- Caching strategies for AI model responses
- Database connection pooling
- CDN integration for static assets

## 🎯 Target Users

- College students and young adults (18-25)
- First-time apartment renters
- Budget-conscious consumers
- Tech-savvy individuals who embrace AI tools

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for Stylii**
