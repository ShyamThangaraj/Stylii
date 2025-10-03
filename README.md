# 🎨 Stylii - AI-Powered Interior Design Assistant

A comprehensive full-stack application that transforms interior design using AI. Upload a photo of your room, and our AI will analyze it, recommend products, and generate a stunning redesigned version with your chosen products seamlessly integrated.

## 🎯 Project Overview

**Stylii** is an AI-powered interior design platform that helps young adults and college students transform their living spaces. The application addresses the common problem of inexperience with interior design by providing:

- **Smart Room Analysis**: AI analyzes your room's current style, layout, and furniture
- **Product Recommendations**: Curated product suggestions based on your budget and preferences
- **AI-Generated Designs**: Creates photorealistic room renders with recommended products integrated
- **Shopping Integration**: Direct links to purchase recommended products
- **Video Generation**: Creates promotional videos of your redesigned space

## ✨ Key Features

### 🏠 **Smart Room Design**

- Upload photos of any room (bedroom, living room, kitchen, etc.)
- AI analyzes room type, current style, and layout
- Personalized product recommendations based on budget and preferences
- Multiple design style options (Modern, Minimalist, Scandinavian, Industrial, etc.)

### 🛍️ **Product Discovery & Shopping**

- AI-powered product search using natural language
- Integration with Amazon, eBay, and other retailers
- Price comparison and budget tracking
- Affiliate link integration for monetization

### 🎨 **AI Image Generation**

- Photorealistic room renders with recommended products
- Style transfer and enhancement
- Before/after comparisons
- High-resolution output images

### 🎬 **Video Generation**

- Automated video creation of redesigned spaces
- Voiceover narration
- Social media ready formats
- 360-degree room tours

### 📱 **Modern Web Interface**

- Responsive design for mobile and desktop
- Real-time progress tracking
- Interactive design studio
- Gallery of previous designs

## 🏗️ Architecture

The application consists of multiple microservices:

```
stylii/
├── frontend/          # Next.js React application
├── backend/           # FastAPI orchestration service
├── img-gen/          # AI image generation service
├── products/         # Product search and recommendation service
├── video_gen/        # Video generation service
└── designer/         # Room analysis and design service
```

### 🔧 **Technology Stack**

**Frontend:**

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component library
- **Zustand** - State management
- **React Hook Form** - Form handling

**Backend Services:**

- **FastAPI** - High-performance Python web framework
- **Python 3.11+** - Core backend language
- **httpx** - Async HTTP client
- **uvicorn** - ASGI server

**AI & ML Services:**

- **Google Gemini 2.0** - Natural language processing
- **SerpApi** - Product search integration
- **FalAI** - Image generation and processing
- **Custom AI Models** - Room analysis and design

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+** and pip
- **Git** for cloning the repository

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/ShyamThangaraj/Stylii.git
cd Stylii

# Start all services with one command
./start.sh
```

### Option 2: Manual Setup

1. **Start the Backend Services:**

```bash
# Backend orchestration service
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. **Start the Frontend:**

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

3. **Start Additional Services (Optional):**

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

Once running, access the application at:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Health Monitoring

Check the status of all services:

```bash
./health.sh
```

This script provides:

- ✅ Service availability checks
- 📊 Detailed status information
- 🎨 Color-coded output for easy monitoring
- 💡 Troubleshooting suggestions

## 📖 Usage Guide

### 1. **Upload Your Room Photo**

- Take or upload a clear photo of your room
- Ensure good lighting and minimal clutter
- Supported formats: JPG, PNG, WebP

### 2. **Set Your Preferences**

- Choose your budget range
- Select preferred design style
- Add any specific requirements or notes

### 3. **AI Analysis & Recommendations**

- AI analyzes your room's current state
- Generates personalized product recommendations
- Shows estimated costs and alternatives

### 4. **Generate Your Design**

- AI creates a photorealistic render
- Products are seamlessly integrated into your space
- Compare before/after results

### 5. **Shop & Share**

- Browse recommended products with direct purchase links
- Generate shareable videos of your new design
- Save designs to your gallery

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

## 🔧 Configuration

### Environment Variables

Create `.env` files in each service directory:

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

## 🎯 Target Audience

**Primary Users:**

- College students and young adults (18-25)
- First-time apartment renters
- Budget-conscious consumers
- Tech-savvy individuals who embrace AI tools

**Pain Points Addressed:**

- Lack of interior design experience
- Overwhelming product choices
- Budget constraints
- Time-consuming research
- Fear of making wrong purchases

## 💰 Monetization Strategy

- **Affiliate Commissions**: Earn from product sales
- **Sponsored Products**: Featured placements
- **Premium Features**: Advanced AI capabilities
- **Design Services**: Professional consultation

## 🚀 Future Roadmap

- **Mobile App**: Native iOS/Android applications
- **AR Integration**: Augmented reality room visualization
- **3D Tours**: Interactive 360-degree room experiences
- **Social Features**: Share designs and get community feedback
- **Professional Services**: Connect with interior designers

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini** for AI capabilities
- **SerpApi** for product search
- **FalAI** for image generation
- **Next.js** and **FastAPI** communities
- **Tailwind CSS** for styling framework

## 📞 Support

For questions, issues, or feature requests:

- Create an issue on GitHub
- Check the documentation
- Review the health check output

---

**Built with ❤️ for Stylii**

_Transforming spaces, one AI-generated design at a time._
