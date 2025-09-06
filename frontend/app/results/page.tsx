"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

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
    <div className="min-h-screen blueprint-grid" style={{backgroundColor: 'var(--blueprint-paper)'}}>
      <div className="container mx-auto px-4 py-4 md:py-8">
        {/* Header */}
        <div className="mb-6 md:mb-8">
          <button
            onClick={() => router.back()}
            className="blueprint-button mb-4 px-6 py-2"
          >
            Return to Form
          </button>

          <h1 className="text-2xl md:text-4xl font-bold blueprint-text mb-4 text-balance" style={{color: 'var(--blueprint-charcoal)'}}>Design Portfolio</h1>
          <div className="blueprint-label">GENERATED DESIGN OPTIONS</div>
        </div>

        <div className="space-y-4 md:space-y-6">
          {DESIGN_STYLES.map((style, index) => (
            <div
              key={style.id}
              className="blueprint-card overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"
            >
              <div className="aspect-[16/9] md:aspect-[16/10] relative" style={{backgroundColor: 'var(--blueprint-light-grey)'}}>
                <img
                  src={style.image || "/placeholder.svg"}
                  alt={`${style.name} design style`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 left-3 md:top-6 md:left-6 blueprint-card px-3 py-1 md:px-4 md:py-2">
                  <span className="blueprint-label" style={{color: 'var(--blueprint-charcoal)'}}>
                    OPTION {String(index + 1).padStart(2, '0')}
                  </span>
                </div>
              </div>
              <div className="p-4 md:p-8">
                <div className="flex items-center gap-4 mb-3">
                  <div className="blueprint-label text-xs">{String(index + 1).padStart(2, '0')}</div>
                  <h3 className="text-xl md:text-3xl font-bold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{style.name}</h3>
                </div>
                <p className="text-base md:text-lg blueprint-text mb-4 md:mb-6" style={{color: 'var(--blueprint-blue)'}}>{style.description}</p>
                <button
                  onClick={() => handleStyleSelect(style.id)}
                  className="blueprint-button blueprint-button-primary w-full md:w-auto py-3 md:py-4 px-6 md:px-8 text-base md:text-lg"
                >
                  Select Design Option
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Loading State */}
      {isGenerating && (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{backgroundColor: 'rgba(44, 62, 80, 0.9)'}}>
          <div className="blueprint-card p-8 max-w-md mx-4 text-center">
            <div className="blueprint-loading w-12 h-12 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold blueprint-text mb-2" style={{color: 'var(--blueprint-charcoal)'}}>Processing Design Request</h3>
            <p className="blueprint-text" style={{color: 'var(--blueprint-blue)'}}>Generating personalized room design...</p>
          </div>
        </div>
      )}
    </div>
  )
}
