"use client"

import { useState, useEffect } from "react"
import { TopBar } from "@/components/top-bar"
import { Button } from "@/components/ui/button"
import { useRouter, useSearchParams } from "next/navigation"
import { ArrowLeft, ShoppingBag, Video, ExternalLink } from "lucide-react"

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
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
        <TopBar />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6 w-48"></div>
            <div className="h-96 bg-gray-200 rounded-3xl mb-6"></div>
            <div className="flex gap-4">
              <div className="h-12 bg-gray-200 rounded-2xl w-48"></div>
              <div className="h-12 bg-gray-200 rounded-2xl w-48"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // TODO: Get actual style data based on styleId
  const styleName = styleId.charAt(0).toUpperCase() + styleId.slice(1).replace("-", " ")

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <TopBar />

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-4 text-orange-600 hover:text-orange-700 hover:bg-orange-100"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Results
          </Button>

          <h1 className="text-4xl font-bold text-gray-900 mb-2 text-balance">{styleName} Design</h1>
          <p className="text-xl text-gray-600">Your personalized room design with AI-generated visualization</p>
        </div>

        {/* Main Design Image */}
        <div className="bg-white rounded-3xl overflow-hidden shadow-lg border border-orange-100 mb-8">
          <div className="aspect-[16/10] bg-gray-100 relative">
            {/* TODO: Replace with actual AI-generated image from backend */}
            <img
              src={`/abstract-geometric-shapes.png?height=600&width=960&query=${styleId} living room design detailed view`}
              alt={`${styleName} room design`}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-6 left-6 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full">
              <span className="text-sm font-medium text-gray-700">AI Generated Design</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between gap-4 mb-8">
          <Button
            onClick={() => setShowProducts(!showProducts)}
            className="flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-orange-400 to-amber-400 hover:from-orange-500 hover:to-amber-500 text-white rounded-2xl font-medium text-lg sm:w-auto w-full"
          >
            <ShoppingBag className="w-5 h-5" />
            {showProducts ? "Hide Products" : "Show Product List"}
          </Button>

          <Button
            onClick={handleGenerateVideo}
            disabled={isGeneratingVideo}
            className="flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-2xl font-medium text-lg sm:w-auto w-full"
          >
            <Video className="w-5 h-5" />
            {isGeneratingVideo ? "Generating Video..." : "Generate Video"}
          </Button>
        </div>

        {/* Products List */}
        {showProducts && (
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-orange-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Products</h2>
            <div className="space-y-4">
              {MOCK_PRODUCTS.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between p-4 bg-orange-50 rounded-2xl hover:bg-orange-100 transition-colors"
                >
                  <div>
                    <h3 className="font-semibold text-gray-900">{product.name}</h3>
                    <p className="text-orange-600 font-medium">{product.price}</p>
                  </div>
                  <Button
                    asChild
                    variant="outline"
                    className="border-orange-200 text-orange-600 hover:bg-orange-50 bg-transparent"
                  >
                    <a href={product.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View Product
                    </a>
                  </Button>
                </div>
              ))}
            </div>
            {/* TODO: Replace with actual product recommendations from backend */}
            <p className="text-sm text-gray-500 mt-4 text-center">
              * Product recommendations will be populated from your backend API
            </p>
          </div>
        )}

        {/* Video Generation Loading */}
        {isGeneratingVideo && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-3xl p-8 max-w-md mx-4 text-center">
              <div className="animate-spin w-12 h-12 border-4 border-purple-200 border-t-purple-500 rounded-full mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold mb-2">Generating Video</h3>
              <p className="text-gray-600">Creating a video walkthrough using Fal AI...</p>
              {/* TODO: Integrate with actual Fal AI video generation */}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
