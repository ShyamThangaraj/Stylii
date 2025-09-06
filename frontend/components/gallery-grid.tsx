"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

const mockGalleryItems = [
  {
    id: "1",
    beforeImage: "/living-room-before-renovation-sketch.jpg",
    afterImage: "/modern-living-room-after-ai-design.jpg",
    style: "Modern",
    budget: 5000,
  },
  {
    id: "2",
    beforeImage: "/bedroom-before-renovation-sketch.jpg",
    afterImage: "/scandinavian-bedroom-after-ai-design.jpg",
    style: "Scandinavian",
    budget: 3000,
  },
  {
    id: "3",
    beforeImage: "/kitchen-before-renovation-sketch.jpg",
    afterImage: "/minimalist-kitchen-after-ai-design.jpg",
    style: "Minimalist",
    budget: 8000,
  },
  {
    id: "4",
    beforeImage: "/placeholder.svg?height=300&width=400",
    afterImage: "/placeholder.svg?height=300&width=400",
    style: "Rustic",
    budget: 4500,
  },
]

export function GalleryGrid() {
  const [selectedStyle, setSelectedStyle] = useState<string>("all")

  const styles = ["all", "Modern", "Scandinavian", "Minimalist", "Rustic", "Industrial", "Boho"]

  const filteredItems =
    selectedStyle === "all" ? mockGalleryItems : mockGalleryItems.filter((item) => item.style === selectedStyle)

  return (
    <div className="space-y-8">
      {/* Style Filters */}
      <div className="flex flex-wrap gap-2 justify-center">
        {styles.map((style) => (
          <Button
            key={style}
            variant={selectedStyle === style ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedStyle(style)}
            className={selectedStyle === style ? "bg-[#FF4DA6] hover:bg-[#FF4DA6]/90" : ""}
          >
            {style === "all" ? "All Styles" : style}
          </Button>
        ))}
      </div>

      {/* Gallery Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredItems.map((item) => (
          <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="grid grid-cols-2 gap-1">
              <div className="relative">
                <img src={item.beforeImage || "/placeholder.svg"} alt="Before" className="w-full h-48 object-cover" />
                <div className="absolute bottom-2 left-2">
                  <Badge variant="secondary" className="text-xs">
                    Before
                  </Badge>
                </div>
              </div>
              <div className="relative">
                <img src={item.afterImage || "/placeholder.svg"} alt="After" className="w-full h-48 object-cover" />
                <div className="absolute bottom-2 right-2">
                  <Badge className="text-xs bg-[#FF4DA6] hover:bg-[#FF4DA6]/90">After</Badge>
                </div>
              </div>
            </div>

            <div className="p-4">
              <div className="flex items-center justify-between">
                <Badge variant="outline">{item.style}</Badge>
                <span className="text-sm font-medium">${item.budget.toLocaleString()}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
