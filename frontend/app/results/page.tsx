"use client"

import { useState } from "react"
import { TopBar } from "@/components/top-bar"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"

const DESIGN_STYLES = [
  {
    id: "modern",
    name: "Modern",
    description: "Clean lines, minimal clutter, neutral colors",
    image: "/modern-living-room.png",
  },
  {
    id: "scandinavian",
    name: "Scandinavian",
    description: "Light woods, cozy textures, hygge vibes",
    image: "/scandinavian-living-room-design.jpg",
  },
  {
    id: "industrial",
    name: "Industrial",
    description: "Raw materials, exposed elements, urban feel",
    image: "/industrial-living-room-design.jpg",
  },
  {
    id: "bohemian",
    name: "Bohemian",
    description: "Eclectic patterns, rich colors, artistic flair",
    image: "/bohemian-living-room-design.jpg",
  },
  {
    id: "mid-century",
    name: "Mid-Century Modern",
    description: "Retro furniture, bold colors",
    image: "/mid-century-modern-living-room-design.jpg",
  },
  {
    id: "traditional",
    name: "Traditional",
    description: "Classic elegance, rich fabrics, timeless appeal",
    image: "/traditional-living-room-design.jpg",
  },
]

export default function ResultsPage() {
  const router = useRouter()
  const [isGenerating, setIsGenerating] = useState(false)

  const handleStyleSelect = (styleId: string) => {
    router.push(`/selected-design?style=${styleId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <TopBar />

      <div className="container mx-auto px-4 py-4 md:py-8">
        {/* Header */}
        <div className="mb-6 md:mb-8">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-4 text-orange-600 hover:text-orange-700 hover:bg-orange-100 rounded-2xl"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Form
          </Button>

          <h1 className="text-2xl md:text-4xl font-bold text-gray-900 mb-4 text-balance">Your Design Options</h1>
        </div>

        <div className="space-y-4 md:space-y-6">
          {DESIGN_STYLES.map((style, index) => (
            <div
              key={style.id}
              className="bg-white rounded-3xl overflow-hidden shadow-xl border-2 border-orange-200 hover:shadow-2xl transition-all duration-300"
            >
              <div className="aspect-[16/9] md:aspect-[16/10] bg-gray-100 relative">
                <img
                  src={style.image || "/placeholder.svg"}
                  alt={`${style.name} design style`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 left-3 md:top-6 md:left-6 bg-orange-500 text-white px-3 py-1 md:px-4 md:py-2 rounded-full text-xs md:text-sm font-medium">
                  ✨ Style {index + 1}
                </div>
              </div>
              <div className="p-4 md:p-8">
                <h3 className="text-xl md:text-3xl font-bold text-gray-900 mb-2 md:mb-3">{style.name}</h3>
                <p className="text-base md:text-lg text-gray-600 mb-4 md:mb-6">{style.description}</p>
                <Button
                  onClick={() => handleStyleSelect(style.id)}
                  className="w-full md:w-auto bg-gradient-to-r from-orange-400 to-amber-400 hover:from-orange-500 hover:to-amber-500 text-white rounded-2xl py-3 md:py-4 px-6 md:px-8 text-base md:text-lg font-medium transition-all duration-200 hover:scale-105"
                >
                  Choose This Design
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Loading State for New Generations */}
      {isGenerating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-3xl p-8 max-w-md mx-4 text-center">
            <div className="animate-spin w-12 h-12 border-4 border-orange-200 border-t-orange-400 rounded-full mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Generating New Design</h3>
            <p className="text-gray-600">Creating your personalized room design...</p>
          </div>
        </div>
      )}
    </div>
  )
}
