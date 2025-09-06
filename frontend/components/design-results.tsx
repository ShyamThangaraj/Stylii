"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { StyliiLoader, StyliiPulse } from "./stylii-loader"
import { ProductList } from "./product-list"
import { HistoryStrip } from "./history-strip"
import { useStyliiStore } from "@/lib/store"
import type { DesignResult } from "@/lib/client"
import { ZoomIn, Download, Share2 } from "lucide-react"

interface DesignResultsProps {
  result: DesignResult | null
}

export function DesignResults({ result }: DesignResultsProps) {
  const { isGenerating, error } = useStyliiStore()
  const [imageZoomed, setImageZoomed] = useState(false)

  if (isGenerating) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Generating Your Design</h2>

        <div className="text-center py-12">
          <StyliiLoader size="lg" />
          <StyliiPulse>
            <p className="mt-4 text-gray-600">Creating your AI-powered room design...</p>
          </StyliiPulse>
        </div>

        {/* Skeleton loaders */}
        <div className="space-y-4">
          <div className="h-64 bg-gray-200 rounded-2xl animate-pulse"></div>
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg animate-pulse"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Generation Failed</h2>

        <Card className="p-6 text-center border-red-200 bg-red-50">
          <p className="text-red-600 mb-4">{error}</p>
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            className="border-red-300 text-red-600 hover:bg-red-100"
          >
            Try Again
          </Button>
        </Card>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Results</h2>

        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">Ready to create your design?</p>
          <p>Upload photos and choose a style to get started.</p>
        </div>

        <HistoryStrip />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Your Design</h2>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{result.style}</Badge>
          <Badge variant="outline">${result.budget.toLocaleString()}</Badge>
        </div>
      </div>

      {/* Generated Render */}
      <Card className="overflow-hidden">
        <div className="relative group">
          <img
            src={result.renderUrl || "/placeholder.svg"}
            alt="Generated room design"
            className={`w-full transition-transform duration-300 ${
              imageZoomed ? "scale-150 cursor-zoom-out" : "cursor-zoom-in"
            }`}
            onClick={() => setImageZoomed(!imageZoomed)}
          />
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
            <Button size="sm" variant="secondary" className="gap-2">
              <ZoomIn className="w-4 h-4" />
              {imageZoomed ? "Zoom Out" : "Zoom In"}
            </Button>
          </div>
        </div>

        <div className="p-4 flex items-center justify-between bg-gray-50">
          <div className="text-sm text-gray-600">Generated in {result.latency}s</div>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" className="gap-2 bg-transparent">
              <Download className="w-4 h-4" />
              Download
            </Button>
            <Button size="sm" variant="outline" className="gap-2 bg-transparent">
              <Share2 className="w-4 h-4" />
              Share
            </Button>
          </div>
        </div>
      </Card>

      {/* Product Recommendations */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Recommended Products</h3>
        <ProductList products={result.products} />
      </div>

      <HistoryStrip />
    </div>
  )
}
