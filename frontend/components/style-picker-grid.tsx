"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { listStyles, type Style } from "@/lib/client"
import { useStyliiStore } from "@/lib/store"

export function StylePickerGrid() {
  const [styles, setStyles] = useState<Style[]>([])
  const [loading, setLoading] = useState(true)
  const { style: selectedStyle, setStyle } = useStyliiStore()

  useEffect(() => {
    listStyles()
      .then(setStyles)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="p-3 animate-pulse">
            <div className="aspect-[4/3] bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {styles.map((style) => (
        <Card
          key={style.id}
          className={`p-3 cursor-pointer transition-all hover:shadow-md ${
            selectedStyle === style.id ? "ring-2 ring-[#FF4DA6] bg-[#FF4DA6]/5" : "hover:ring-1 hover:ring-gray-300"
          }`}
          onClick={() => setStyle(style.id)}
        >
          <div className="aspect-[4/3] mb-2 overflow-hidden rounded">
            <img src={style.thumbnail || "/placeholder.svg"} alt={style.name} className="w-full h-full object-cover" />
          </div>
          <h3 className="font-medium text-sm mb-1">{style.name}</h3>
          <p className="text-xs text-gray-600 text-balance">{style.description}</p>
        </Card>
      ))}
    </div>
  )
}
