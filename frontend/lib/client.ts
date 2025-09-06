// Real API client for backend integration

const API_BASE_URL = 'http://localhost:8000'

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
  thumbnail?: string
}

export interface DesignResult {
  id: string
  renderUrl: string
  products: Product[]
  style: string
  budget: number
  createdAt: Date
  latency: number
  designerData?: any
  roomAnalysis?: any
  designCritique?: any
  userPreferences?: any
}

export interface GenerateDesignInput {
  images: File[]
  style: string
  budget: number
  notes?: string
  selectedProducts?: string[]
}

export interface StreamingProgress {
  status: string
  message: string
  step?: number
  data?: any
}

export type ProgressCallback = (progress: StreamingProgress) => void

// Utility function for delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function generateDesign(
  input: GenerateDesignInput,
  onProgress?: ProgressCallback
): Promise<DesignResult> {
  const startTime = Date.now()
  
  if (!input.images || input.images.length === 0) {
    throw new Error('At least one image is required')
  }

  // Prepare form data for the backend API
  const formData = new FormData()
  formData.append('image', input.images[0]) // Use first image
  
  // Create preferences string from input
  const preferences = {
    budget: input.budget,
    style: input.style,
    notes: input.notes || '',
    selectedProducts: input.selectedProducts || [],
  }
  formData.append('preferences', JSON.stringify(preferences))

  try {
    const response = await fetch(`${API_BASE_URL}/design`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('No response body')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let finalResult: any = null

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // Keep the last incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.error) {
              throw new Error(data.error)
            }
            
            if (data.status === 'completed' && data.success) {
              finalResult = data
            } else if (onProgress) {
              onProgress({
                status: data.status || 'processing',
                message: data.message || 'Processing...',
                data,
              })
            }
          } catch (e) {
            console.warn('Failed to parse SSE data:', line, e)
          }
        }
      }
    }

    if (!finalResult) {
      throw new Error('No final result received from server')
    }

    // Transform backend response to frontend format
    const products: Product[] = (finalResult.designer_data?.product_recommendations || []).map((product: any, index: number) => ({
      id: `${index + 1}`,
      title: product.title || 'Unknown Product',
      vendor: product.vendor || 'Unknown',
      price: product.price || 0,
      image: product.thumbnail || '/placeholder.png',
      url: product.url || '#',
      thumbnail: product.thumbnail,
    }))

    const endTime = Date.now()
    const latency = (endTime - startTime) / 1000

    return {
      id: finalResult.request_id || Math.random().toString(36).substr(2, 9),
      renderUrl: finalResult.generated_image?.data ? `data:image/png;base64,${finalResult.generated_image.data}` : '/placeholder.png',
      products,
      style: input.style,
      budget: input.budget,
      createdAt: new Date(),
      latency,
      designerData: finalResult.designer_data,
      roomAnalysis: finalResult.designer_data?.room_analysis,
      designCritique: finalResult.designer_data?.design_critique,
      userPreferences: finalResult.designer_data?.user_preferences,
    }
  } catch (error) {
    console.error('Error generating design:', error)
    throw error
  }
}

export async function listStyles(): Promise<Style[]> {
  await delay(500)

  // Updated to match backend supported styles
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
      id: "industrial",
      name: "Industrial",
      description: "Raw materials, exposed elements, urban feel",
      thumbnail: "/industrial-interior.png",
    },
    {
      id: "bohemian",
      name: "Bohemian",
      description: "Eclectic patterns, rich textures, global influences",
      thumbnail: "/placeholder-v34fv.png",
    },
    {
      id: "midcentury modern",
      name: "Mid-Century Modern",
      description: "Retro furniture, bold colors, geometric shapes",
      thumbnail: "/placeholder-5far1.png",
    },
    {
      id: "traditional",
      name: "Traditional",
      description: "Classic elegance, rich fabrics, timeless appeal",
      thumbnail: "/traditional-interior.png",
    },
  ]
}

// Health check function for backend connectivity
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.ok
  } catch (error) {
    console.error('Backend health check failed:', error)
    return false
  }
}

export async function listPastResults(): Promise<DesignResult[]> {
  await delay(300)

  // For now, return empty array since backend doesn't store past results
  // In a real app, this would fetch from a database or storage service
  return []
}
