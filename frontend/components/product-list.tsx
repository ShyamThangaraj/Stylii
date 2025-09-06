"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { Product } from "@/lib/client"
import { ExternalLink, Heart, Copy } from "lucide-react"

interface ProductListProps {
  products: Product[]
}

export function ProductList({ products }: ProductListProps) {
  const handleCopyLink = (product: Product) => {
    navigator.clipboard.writeText(product.url)
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {products.map((product) => (
        <Card key={product.id} className="p-4 hover:shadow-md transition-shadow">
          <div className="flex gap-4">
            <img
              src={product.image || "/placeholder.svg"}
              alt={product.title}
              className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-sm mb-1 truncate">{product.title}</h4>
              <p className="text-xs text-gray-600 mb-2">{product.vendor}</p>
              <p className="font-semibold text-lg mb-3">${product.price}</p>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="gap-1 text-xs bg-transparent">
                  <ExternalLink className="w-3 h-3" />
                  View
                </Button>
                <Button size="sm" variant="outline" className="gap-1 text-xs bg-transparent">
                  <Heart className="w-3 h-3" />
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="gap-1 text-xs bg-transparent"
                  onClick={() => handleCopyLink(product)}
                >
                  <Copy className="w-3 h-3" />
                  Copy
                </Button>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
