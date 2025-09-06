"use client"

import { Card } from "@/components/ui/card"

const DESIGN_STYLES = [
  {
    id: "modern",
    name: "Modern",
    description: "Clean lines, minimal clutter, neutral colors",
    thumbnail: "/modern-living-room.png",
  },
  {
    id: "scandinavian",
    name: "Scandinavian",
    description: "Light woods, cozy textures, hygge vibes",
    thumbnail: "/scandinavian-living-room-design.jpg",
  },
  {
    id: "industrial",
    name: "Industrial",
    description: "Raw materials, exposed elements, urban feel",
    thumbnail: "/industrial-living-room-design.jpg",
  },
  {
    id: "bohemian",
    name: "Bohemian",
    description: "Eclectic patterns, rich colors, artistic flair",
    thumbnail: "/bohemian-living-room-design.jpg",
  },
  {
    id: "mid-century",
    name: "Mid-Century Modern",
    description: "Retro furniture, bold colors, geometric shapes",
    thumbnail: "/mid-century-modern-living-room-design.jpg",
  },
  {
    id: "traditional",
    name: "Traditional",
    description: "Classic elegance, rich fabrics, timeless appeal",
    thumbnail: "/traditional-living-room-design.jpg",
  },
]

export function StylePreview() {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl font-bold text-center mb-16 text-balance">Design Styles</h2>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {DESIGN_STYLES.map((style) => (
            <Card key={style.id} className="p-4 hover:shadow-lg transition-shadow cursor-pointer group">
              <div className="aspect-[4/3] mb-4 overflow-hidden rounded-lg">
                <img
                  src={style.thumbnail || "/placeholder.svg"}
                  alt={style.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <h3 className="font-semibold mb-2">{style.name}</h3>
              <p className="text-sm text-gray-600 text-balance">{style.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
