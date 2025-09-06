"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"

// TODO: Replace with actual product data from backend
const MOCK_PRODUCTS = [
  { id: 1, name: "Modern Sectional Sofa", price: "$1,299", url: "https://example.com/sofa" },
  { id: 2, name: "Glass Coffee Table", price: "$399", url: "https://example.com/table" },
  { id: 3, name: "Floor Lamp", price: "$189", url: "https://example.com/lamp" },
  { id: 4, name: "Throw Pillows Set", price: "$79", url: "https://example.com/pillows" },
  { id: 5, name: "Area Rug", price: "$299", url: "https://example.com/rug" },
]

export default function SelectedDesignPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const styleId = searchParams.get("style") || "modern"

  const [showProducts, setShowProducts] = useState(false)
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleGenerateVideo = async () => {
    setIsGeneratingVideo(true)

    // TODO: Integrate with Fal AI to generate video
    // Placeholder for video generation logic
    setTimeout(() => {
      setIsGeneratingVideo(false)
      // TODO: Show generated video or redirect to video page
      alert("Video generation would happen here using Fal AI")
    }, 3000)
  }

  if (!mounted) {
    return (
      <div className="min-h-screen blueprint-grid" style={{backgroundColor: 'var(--blueprint-paper)'}}>
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 blueprint-card rounded mb-6 w-48"></div>
            <div className="h-96 blueprint-card rounded mb-6"></div>
            <div className="flex gap-4">
              <div className="h-12 blueprint-card rounded w-48"></div>
              <div className="h-12 blueprint-card rounded w-48"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // TODO: Get actual style data based on styleId
  const styleName = styleId.charAt(0).toUpperCase() + styleId.slice(1).replace("-", " ")

  return (
    <div className="min-h-screen blueprint-grid" style={{backgroundColor: 'var(--blueprint-paper)'}}>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="blueprint-button mb-4 px-6 py-2"
          >
            Return to Results
          </button>

          <h1 className="text-4xl font-bold blueprint-text mb-2 text-balance" style={{color: 'var(--blueprint-charcoal)'}}>{styleName} Design</h1>
          <div className="blueprint-label mb-2">AI GENERATED DESIGN VISUALIZATION</div>
          <p className="text-xl blueprint-text" style={{color: 'var(--blueprint-blue)'}}>Personalized room design with technical specifications</p>
        </div>

        {/* Main Design Image */}
        <div className="blueprint-card overflow-hidden shadow-lg mb-8">
          <div className="aspect-[16/10] relative" style={{backgroundColor: 'var(--blueprint-light-grey)'}}>
            {/* TODO: Replace with actual AI-generated image from backend */}
            <img
              src={`/abstract-geometric-shapes.png?height=600&width=960&query=${styleId} living room design detailed view`}
              alt={`${styleName} room design`}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-6 left-6 blueprint-card px-4 py-2">
              <span className="blueprint-label text-xs" style={{color: 'var(--blueprint-charcoal)'}}>AI GENERATED DESIGN</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between gap-4 mb-8">
          <button
            onClick={() => setShowProducts(!showProducts)}
            className="blueprint-button blueprint-button-primary flex items-center justify-center gap-3 px-8 py-4 text-lg sm:w-auto w-full"
          >
            {showProducts ? "Hide Product Specifications" : "Show Product Specifications"}
          </button>

          <button
            onClick={handleGenerateVideo}
            disabled={isGeneratingVideo}
            className="blueprint-button flex items-center justify-center gap-3 px-8 py-4 text-lg sm:w-auto w-full disabled:opacity-50"
          >
            {isGeneratingVideo ? "Generating Video..." : "Generate Video Walkthrough"}
          </button>
        </div>

        {/* Products List */}
        {showProducts && (
          <div className="blueprint-card p-8 shadow-lg">
            <div className="blueprint-label mb-6">FEATURED PRODUCT SPECIFICATIONS</div>
            <h2 className="text-2xl font-bold blueprint-text mb-6" style={{color: 'var(--blueprint-charcoal)'}}>Product Recommendations</h2>
            <div className="space-y-4">
              {MOCK_PRODUCTS.map((product, index) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between p-4 border transition-colors hover:bg-gray-50"
                  style={{borderColor: 'var(--blueprint-charcoal)', backgroundColor: 'var(--blueprint-paper)'}}
                >
                  <div className="flex items-center gap-4">
                    <div className="blueprint-label text-xs">{String(index + 1).padStart(2, '0')}</div>
                    <div>
                      <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{product.name}</h3>
                      <p className="blueprint-text font-medium" style={{color: 'var(--blueprint-amber)'}}>{product.price}</p>
                    </div>
                  </div>
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="blueprint-button px-4 py-2"
                  >
                    View Product Details
                  </a>
                </div>
              ))}
            </div>
            {/* TODO: Replace with actual product recommendations from backend */}
            <p className="blueprint-text text-sm mt-4 text-center" style={{color: 'var(--blueprint-blue)'}}>
              Product recommendations will be populated from backend API integration
            </p>
          </div>
        )}

        {/* Video Generation Loading */}
        {isGeneratingVideo && (
          <div className="fixed inset-0 flex items-center justify-center z-50" style={{backgroundColor: 'rgba(44, 62, 80, 0.9)'}}>
            <div className="blueprint-card p-8 max-w-md mx-4 text-center">
              <div className="blueprint-loading w-12 h-12 mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold blueprint-text mb-2" style={{color: 'var(--blueprint-charcoal)'}}>Generating Video Walkthrough</h3>
              <p className="blueprint-text" style={{color: 'var(--blueprint-blue)'}}>Creating video presentation using Fal AI...</p>
              {/* TODO: Integrate with actual Fal AI video generation */}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
