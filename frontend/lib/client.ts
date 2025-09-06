// Mock client functions for Stylii - frontend only, no real APIs

export interface Style {
  id: string
  name: string
  description: string
  thumbnail: string
}

export interface Product {
  id: string
  title: string
  vendor: string
  price: number
  image: string
  url: string
}

export interface DesignResult {
  id: string
  renderUrl: string
  products: Product[]
  style: string
  budget: number
  createdAt: Date
  latency: number
}

export interface GenerateDesignInput {
  images: File[]
  style: string
  budget: number
  notes?: string
}

// Mock delay function
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function generateDesign(input: GenerateDesignInput): Promise<DesignResult> {
  // Simulate processing time
  await delay(3000 + Math.random() * 2000)

  const mockProducts: Product[] = [
    {
      id: "1",
      title: "Modern Sectional Sofa",
      vendor: "West Elm",
      price: 1299,
      image: "/modern-sectional-sofa.png",
      url: "#",
    },
    {
      id: "2",
      title: "Ceramic Table Lamp",
      vendor: "CB2",
      price: 199,
      image: "/placeholder-qh67b.png",
      url: "#",
    },
    {
      id: "3",
      title: "Wool Area Rug",
      vendor: "Article",
      price: 449,
      image: "/wool-area-rug.png",
      url: "#",
    },
    {
      id: "4",
      title: "Oak Coffee Table",
      vendor: "Room & Board",
      price: 699,
      image: "/placeholder-d49af.png",
      url: "#",
    },
  ]

  return {
    id: Math.random().toString(36).substr(2, 9),
    renderUrl: "/placeholder-ypfod.png",
    products: mockProducts,
    style: input.style,
    budget: input.budget,
    createdAt: new Date(),
    latency: 3.2,
  }
}

export async function listStyles(): Promise<Style[]> {
  await delay(500)

  return [
    {
      id: "modern",
      name: "Modern",
      description: "Clean lines, minimal clutter, neutral colors",
      thumbnail: "/modern-interior.png",
    },
    {
      id: "scandinavian",
      name: "Scandinavian",
      description: "Light woods, cozy textures, functional design",
      thumbnail: "/scandinavian-interior.png",
    },
    {
      id: "minimalist",
      name: "Minimalist",
      description: "Less is more, open spaces, simple forms",
      thumbnail: "/minimalist-interior.png",
    },
    {
      id: "rustic",
      name: "Rustic",
      description: "Natural materials, warm tones, vintage charm",
      thumbnail: "/placeholder-u3rao.png",
    },
    {
      id: "industrial",
      name: "Industrial",
      description: "Raw materials, exposed elements, urban feel",
      thumbnail: "/industrial-interior.png",
    },
    {
      id: "boho",
      name: "Boho",
      description: "Eclectic patterns, rich textures, global influences",
      thumbnail: "/placeholder-v34fv.png",
    },
    {
      id: "mid-century",
      name: "Mid-Century",
      description: "Retro furniture, bold colors, geometric shapes",
      thumbnail: "/placeholder-5far1.png",
    },
    {
      id: "traditional",
      name: "Traditional",
      description: "Classic elegance, rich fabrics, timeless appeal",
      thumbnail: "/traditional-interior.png",
    },
    {
      id: "japandi",
      name: "Japandi",
      description: "Japanese minimalism meets Scandinavian hygge",
      thumbnail: "/placeholder-36rnn.png",
    },
    {
      id: "coastal",
      name: "Coastal",
      description: "Ocean-inspired, light blues, natural textures",
      thumbnail: "/placeholder-bh2y5.png",
    },
  ]
}

export async function listPastResults(): Promise<DesignResult[]> {
  await delay(300)

  return [
    {
      id: "1",
      renderUrl: "/modern-living-room.png",
      products: [],
      style: "Modern",
      budget: 5000,
      createdAt: new Date(Date.now() - 86400000),
      latency: 2.8,
    },
    {
      id: "2",
      renderUrl: "/placeholder-fobdf.png",
      products: [],
      style: "Scandinavian",
      budget: 3000,
      createdAt: new Date(Date.now() - 172800000),
      latency: 3.1,
    },
  ]
}
