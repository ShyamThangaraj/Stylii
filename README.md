# 🎨 Stylii - AI-Powered Interior Design Assistant

AI-powered interior design platform that analyzes room photos, recommends products, and generates photorealistic renders with integrated products.

## 🏗️ Architecture

```
stylii/
├── frontend/          # Next.js React application
├── backend/           # FastAPI orchestration service
├── img-gen/          # AI image generation service
├── products/         # Product search and recommendation service
├── video_gen/        # Video generation service
└── designer/         # Room analysis and design service
```

## 🛠️ Technology Stack

**Frontend:**

- Next.js 15, TypeScript, Tailwind CSS
- Radix UI, Zustand, React Hook Form

**Backend:**

- FastAPI, Python 3.11+, httpx, uvicorn

**AI Services:**

- Google Gemini 2.0, SerpApi, FalAI

## 🚀 Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip

### Quick Start

```bash
git clone https://github.com/ShyamThangaraj/Stylii.git
cd Stylii
./start.sh
```

### Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Additional Services:**

```bash
# Image generation service
cd img-gen
pip install -r requirements.txt
python main.py

# Product search service
cd products
pip install -r requirements.txt
python designer_server.py

# Video generation service
cd video_gen
pip install -r requirements.txt
python server.py
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Health Monitoring

```bash
./health.sh
```

## 📊 API Endpoints

### Core Endpoints

- `POST /design` - Main design generation (streaming)
- `POST /design-sync` - Synchronous design generation
- `GET /health` - Health check
- `GET /status` - Detailed service status

### Design Process

1. **Upload** → Room photo and preferences
2. **Analyze** → AI room analysis and product search
3. **Generate** → AI image generation with products
4. **Return** → Complete design with shopping links

## 🔧 Configuration

### Environment Variables

```bash
# Backend
BACKEND_URL=http://localhost:8000
DESIGNER_SERVICE_URL=http://localhost:8009
IMG_GEN_SERVICE_URL=http://localhost:8005

# AI Services
GEMINI_API_KEY=your_gemini_key
SERPAPI_KEY=your_serpapi_key
FALAI_API_KEY=your_falai_key
```

### Service Ports

- **Frontend**: 3000
- **Backend**: 8000
- **Designer Service**: 8009
- **Image Generation**: 8005
- **Video Generation**: 8007

## 🛠️ Development

### Frontend Development

```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
```

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py       # Start with auto-reload
```

### Adding New Features

- **Frontend**: Components in `frontend/components/`
- **Backend**: API endpoints in `backend/main.py`
- **AI Services**: Individual service directories

## 📖 Usage Flow

1. Upload room photo
2. Set budget and style preferences
3. AI analyzes room and finds products
4. Generate photorealistic design
5. Browse products with purchase links

## 🎯 Target Users

- College students and young adults (18-25)
- First-time apartment renters
- Budget-conscious consumers

## 💰 Monetization

- Affiliate commissions from product sales
- Sponsored product placements
- Premium AI features
- Professional design services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for Stylii**
