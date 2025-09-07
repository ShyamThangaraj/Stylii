"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useStyliiStore } from "@/lib/store"
import Image from "next/image"
import { VideoGeneration } from "@/components/video-generation"

export default function ResultsPage() {
  const router = useRouter()
  const { results, currentResultId, isGenerating } = useStyliiStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen blueprint-grid" style={{backgroundColor: 'var(--blueprint-paper)'}}>
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  const currentResult = results.find(r => r.id === currentResultId) || results[0]

  if (!currentResult && !isGenerating) {
    return (
      <div className="min-h-screen blueprint-grid" style={{backgroundColor: 'var(--blueprint-paper)'}}>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl md:text-4xl font-bold blueprint-text mb-4" style={{color: 'var(--blueprint-charcoal)'}}>No Results Found</h1>
            <p className="blueprint-text mb-6" style={{color: 'var(--blueprint-blue)'}}>Please generate a design first.</p>
            <button
              onClick={() => router.push('/design')}
              className="blueprint-button blueprint-button-primary px-6 py-3"
            >
              Start Design Process
            </button>
          </div>
        </div>
      </div>
    )
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

          <h1 className="text-2xl md:text-4xl font-bold blueprint-text mb-4 text-balance" style={{color: 'var(--blueprint-charcoal)'}}>Design Results</h1>
          <div className="blueprint-label">AI-GENERATED ROOM DESIGN</div>
        </div>

        {currentResult && (
          <div className="space-y-6">
            {/* Generated Image */}
            <div className="blueprint-card overflow-hidden shadow-sm">
              <div className="aspect-[16/9] md:aspect-[16/10] relative" style={{backgroundColor: 'var(--blueprint-light-grey)'}}>
                <img
                  src={currentResult.renderUrl}
                  alt="Generated room design"
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 left-3 md:top-6 md:left-6 blueprint-card px-3 py-1 md:px-4 md:py-2">
                  <span className="blueprint-label" style={{color: 'var(--blueprint-charcoal)'}}>
                    GENERATED DESIGN
                  </span>
                </div>
              </div>
              <div className="p-4 md:p-8">
                <div className="flex items-center gap-4 mb-3">
                  <h3 className="text-xl md:text-3xl font-bold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{currentResult.style} Style</h3>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="blueprint-card p-3">
                    <div className="blueprint-label text-xs mb-1">BUDGET</div>
                    <div className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>${currentResult.budget.toLocaleString()}</div>
                  </div>
                  <div className="blueprint-card p-3">
                    <div className="blueprint-label text-xs mb-1">PRODUCTS</div>
                    <div className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{currentResult.products.length}</div>
                  </div>
                  <div className="blueprint-card p-3">
                    <div className="blueprint-label text-xs mb-1">GENERATED</div>
                    <div className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{currentResult.createdAt.toLocaleTimeString()}</div>
                  </div>
                  <div className="blueprint-card p-3">
                    <div className="blueprint-label text-xs mb-1">LATENCY</div>
                    <div className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{currentResult.latency.toFixed(1)}s</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Video Generation */}
            <VideoGeneration imageUrl={currentResult.renderUrl} />

            {/* Product Recommendations */}
            {currentResult.products.length > 0 && (
              <div className="blueprint-card p-6">
                <h2 className="text-xl font-bold blueprint-text mb-4" style={{color: 'var(--blueprint-charcoal)'}}>Product Recommendations</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {currentResult.products.map((product, index) => (
                    <div key={product.id} className="blueprint-card p-4">
                      <div className="aspect-square bg-gray-100 rounded mb-3 overflow-hidden">
                        <img
                          src={product.image}
                          alt={product.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="blueprint-label text-xs mb-1">{String(index + 1).padStart(2, '0')}</div>
                      <h3 className="font-semibold blueprint-text mb-1" style={{color: 'var(--blueprint-charcoal)'}}>{product.title}</h3>
                      <p className="text-sm blueprint-text mb-2" style={{color: 'var(--blueprint-blue)'}}>{product.vendor}</p>
                      <p className="font-semibold blueprint-text" style={{color: 'var(--blueprint-amber)'}}>${product.price}</p>
                      {product.url && product.url !== '#' && (
                        <a
                          href={product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="blueprint-button blueprint-button-primary w-full mt-3 py-2 text-sm"
                        >
                          View Product
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
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
