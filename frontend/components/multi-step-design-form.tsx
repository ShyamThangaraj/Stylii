"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { UploadDropzone } from "./upload-dropzone"
import { useStyliiStore } from "@/lib/store"
import { useRouter } from "next/navigation"
import { generateDesign, checkBackendHealth } from "@/lib/client"
import type { StreamingProgress } from "@/lib/client"

const PRODUCT_TYPES = [
  { id: "furniture", label: "Furniture", description: "Sofas, chairs, tables, beds" },
  { id: "appliances", label: "Appliances", description: "Kitchen & home appliances" },
  { id: "decor", label: "Decor", description: "Vases, plants, decorative items" },
  { id: "frames", label: "Frames & Art", description: "Wall art, mirrors, frames" },
  { id: "lighting", label: "Lighting", description: "Lamps, fixtures, ambient lighting" },
  { id: "textiles", label: "Textiles", description: "Rugs, curtains, pillows" },
]

export function MultiStepDesignForm() {
  const [currentStep, setCurrentStep] = useState(0)
  const [mounted, setMounted] = useState(false)
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null)

  const {
    images,
    budget,
    notes,
    selectedProducts,
    style,
    isGenerating,
    currentProgress,
    error,
    setBudget,
    setNotes,
    setSelectedProducts,
    setStyle,
    setIsGenerating,
    setProgress,
    setError,
    addResult,
  } = useStyliiStore()
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
    // Check backend health on mount
    checkBackendHealth().then(setBackendHealthy)
  }, [])

  const steps = [
    {
      title: "Interior Design Consultation",
      subtitle: "Professional AI-powered interior design services",
      component: <IntroStep />,
    },
    {
      title: "Budget Planning",
      subtitle: "Specify your investment range for design recommendations",
      component: <BudgetStep budget={budget} setBudget={setBudget} />,
    },
    {
      title: "Room Documentation",
      subtitle: "Upload high-quality images of your space for analysis",
      component: <PhotoStep />,
    },
    {
      title: "Design Style",
      subtitle: "Choose your preferred interior design style",
      component: <StyleStep style={style} setStyle={setStyle} />,
    },
    {
      title: "Product Categories",
      subtitle: "Select furniture and decor categories for your project",
      component: <ProductTypesStep selectedProducts={selectedProducts} setSelectedProducts={setSelectedProducts} />,
    },
    {
      title: "Design Requirements",
      subtitle: "Provide additional specifications and preferences",
      component: <NotesStep notes={notes} setNotes={setNotes} />,
    },
  ]

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return true // Intro step - always can proceed
      case 1:
        return budget > 0
      case 2:
        return images.length >= 1
      case 3:
        return style !== ""
      case 4:
        return selectedProducts.length > 0
      case 5:
        return true
      default:
        return false
    }
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    if (!images || images.length === 0) {
      setError('Please upload at least one image')
      return
    }

    try {
      setIsGenerating(true)
      setError(null)
      setProgress({ status: 'starting', message: 'Initializing design generation...' })

      const result = await generateDesign(
        {
          images,
          style,
          budget,
          notes,
          selectedProducts,
        },
        (progress: StreamingProgress) => {
          setProgress(progress)
        }
      )

      addResult(result)
      router.push('/results')
    } catch (error) {
      console.error('Design generation failed:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate design')
      setIsGenerating(false)
      setProgress(null)
    }
  }

  if (!mounted) {
    return (
      <div className="bg-white rounded-lg p-8 shadow-sm border animate-pulse">
        <div className="h-6 bg-gray-200 rounded mb-6"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    )
  }

  if (isGenerating) {
    return (
      <div className="fixed inset-0 blueprint-grid flex items-center justify-center z-50" style={{backgroundColor: 'var(--blueprint-paper)'}}>
        <div className="blueprint-card p-8 md:p-12 max-w-md mx-4 text-center shadow-lg">
          <div className="relative mb-6">
            <div className="blueprint-loading w-12 h-12 mx-auto"></div>
          </div>
          <h3 className="text-xl md:text-2xl font-semibold blueprint-text mb-3" style={{color: 'var(--blueprint-charcoal)'}}>Processing Your Request</h3>
          <p className="blueprint-text font-medium text-base mb-2" style={{color: 'var(--blueprint-amber)'}}>
            {currentProgress?.message || 'Processing...'}
          </p>
          <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>Please wait while we analyze your data...</p>
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="blueprint-card blueprint-grid p-6 md:p-8 shadow-sm">
      {/* Backend Health Check */}
      {backendHealthy === false && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-red-700 text-sm">
            ⚠️ Backend service is not available. Please ensure the backend is running on localhost:8000.
          </p>
        </div>
      )}
      
      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Technical Ruler Progress */}
      <div className="mb-6 md:mb-8">
        <div className="flex justify-between items-center mb-4">
          <span className="blueprint-label">
            STEP {currentStep + 1} OF {steps.length}
          </span>
          <span className="blueprint-label">
            {Math.round(((currentStep + 1) / steps.length) * 100)}% COMPLETE
          </span>
        </div>
        <div className="technical-ruler">
          <div
            className="technical-ruler-fill"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
          <div
            className="technical-ruler-marker"
            style={{ left: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Step Content */}
      <div className="mb-6 md:mb-8">
        <h1 className="text-xl md:text-3xl font-bold blueprint-text mb-2 text-balance" style={{color: 'var(--blueprint-charcoal)'}}>{steps[currentStep].title}</h1>
        <p className="blueprint-text text-base md:text-lg mb-6 md:mb-8" style={{color: 'var(--blueprint-blue)'}}>{steps[currentStep].subtitle}</p>

        <div className="min-h-[250px] md:min-h-[300px]">{steps[currentStep].component}</div>
      </div>

      {/* Navigation */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 md:gap-0">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="blueprint-button w-full md:w-auto px-6 py-2.5 order-2 md:order-1 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        {currentStep === steps.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={!canProceed() || backendHealthy === false}
            className="blueprint-button blueprint-button-primary w-full md:w-auto px-8 py-2.5 order-1 md:order-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Generate Design
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="blueprint-button blueprint-button-primary w-full md:w-auto px-6 py-2.5 order-1 md:order-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        )}
      </div>
    </div>
  )
}

function BudgetStep({ budget, setBudget }: { budget: number; setBudget: (budget: number) => void }) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="blueprint-label">BUDGET SPECIFICATION</div>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            placeholder="Enter your budget"
            className="blueprint-input text-xl p-4 text-center w-full"
          />
        </div>
        <div className="px-4">
          <Slider
            value={[budget]}
            onValueChange={([value]) => setBudget(value)}
            max={20000}
            min={500}
            step={100}
            className="w-full"
          />
          <div className="flex justify-between blueprint-label mt-3">
            <span>$500</span>
            <span style={{color: 'var(--blueprint-amber)', fontWeight: 'bold'}}>${budget.toLocaleString()}</span>
            <span>$20,000+</span>
          </div>
        </div>
      </div>
      <div className="blueprint-card p-4">
        <div className="blueprint-label mb-2">GUIDANCE</div>
        <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
          Budget parameters enable product recommendations within specified range and prioritize high-impact design modifications for spatial optimization.
        </p>
      </div>
    </div>
  )
}

function PhotoStep() {
  return (
    <div className="space-y-6">
      <UploadDropzone />
      <div className="blueprint-card p-4">
        <div className="blueprint-label mb-2">DOCUMENTATION REQUIREMENTS</div>
        <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
          Multiple angle documentation with optimal lighting conditions required. Complete room coverage enables comprehensive spatial analysis and design optimization.
        </p>
      </div>
    </div>
  )
}

function ProductTypesStep({
  selectedProducts,
  setSelectedProducts,
}: {
  selectedProducts: string[]
  setSelectedProducts: (products: string[]) => void
}) {
  const toggleProduct = (productId: string) => {
    setSelectedProducts(
      selectedProducts.includes(productId)
        ? selectedProducts.filter((id) => id !== productId)
        : [...selectedProducts, productId],
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-3">
        {PRODUCT_TYPES.map((product, index) => (
          <div
            key={product.id}
            className={`blueprint-card p-4 cursor-pointer transition-all ${
              selectedProducts.includes(product.id)
                ? "bg-amber-50" 
                : "hover:bg-gray-50"
            }`}
            onClick={() => toggleProduct(product.id)}
            style={{
              borderColor: selectedProducts.includes(product.id) 
                ? 'var(--blueprint-amber)' 
                : 'var(--blueprint-charcoal)'
            }}
          >
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={selectedProducts.includes(product.id)}
                onChange={() => toggleProduct(product.id)}
                className="blueprint-checkbox mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="blueprint-label text-xs">{String(index + 1).padStart(2, '0')}</div>
                  <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{product.label}</h3>
                </div>
                <p className="text-sm blueprint-text" style={{color: 'var(--blueprint-blue)'}}>{product.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="blueprint-card p-4">
        <div className="blueprint-label mb-2">SELECTION PARAMETERS</div>
        <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
          Product category selection prioritizes specified elements in design recommendations and optimization algorithms.
        </p>
      </div>
    </div>
  )
}

function IntroStep() {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-6">
        <div className="w-16 h-16 mx-auto blueprint-card flex items-center justify-center">
          <div className="blueprint-label">ID</div>
        </div>
        
        <div className="space-y-4">
          <h2 className="text-3xl font-bold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>Interior Design Assistant</h2>
          <p className="text-lg blueprint-text max-w-2xl mx-auto leading-relaxed" style={{color: 'var(--blueprint-blue)'}}>
            Professional AI-powered interior design consultation. Upload room photos, specify your requirements, and receive comprehensive design recommendations tailored to your space and budget.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="text-center space-y-3 blueprint-card p-4">
            <div className="blueprint-label mb-2">01</div>
            <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>Photo Analysis</h3>
            <p className="text-sm blueprint-text" style={{color: 'var(--blueprint-blue)'}}>Upload room images for detailed spatial analysis</p>
          </div>
          
          <div className="text-center space-y-3 blueprint-card p-4">
            <div className="blueprint-label mb-2">02</div>
            <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>Design Generation</h3>
            <p className="text-sm blueprint-text" style={{color: 'var(--blueprint-blue)'}}>AI-generated design concepts and layouts</p>
          </div>
          
          <div className="text-center space-y-3 blueprint-card p-4">
            <div className="blueprint-label mb-2">03</div>
            <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>Product Recommendations</h3>
            <p className="text-sm blueprint-text" style={{color: 'var(--blueprint-blue)'}}>Curated furniture and decor suggestions</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function StyleStep({ style, setStyle }: { style: string; setStyle: (style: string) => void }) {
  const styles = [
    { id: "modern", name: "Modern", description: "Clean lines, minimal clutter, neutral colors" },
    { id: "scandinavian", name: "Scandinavian", description: "Light woods, cozy textures, functional design" },
    { id: "industrial", name: "Industrial", description: "Raw materials, exposed elements, urban feel" },
    { id: "bohemian", name: "Bohemian", description: "Eclectic patterns, rich textures, global influences" },
    { id: "midcentury modern", name: "Mid-Century Modern", description: "Retro furniture, bold colors, geometric shapes" },
    { id: "traditional", name: "Traditional", description: "Classic elegance, rich fabrics, timeless appeal" },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-3">
        {styles.map((styleOption, index) => (
          <div
            key={styleOption.id}
            className={`blueprint-card p-4 cursor-pointer transition-all ${
              style === styleOption.id
                ? "bg-amber-50" 
                : "hover:bg-gray-50"
            }`}
            onClick={() => setStyle(styleOption.id)}
            style={{
              borderColor: style === styleOption.id 
                ? 'var(--blueprint-amber)' 
                : 'var(--blueprint-charcoal)'
            }}
          >
            <div className="flex items-start gap-3">
              <input
                type="radio"
                checked={style === styleOption.id}
                onChange={() => setStyle(styleOption.id)}
                className="blueprint-radio mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="blueprint-label text-xs">{String(index + 1).padStart(2, '0')}</div>
                  <h3 className="font-semibold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>{styleOption.name}</h3>
                </div>
                <p className="text-sm blueprint-text" style={{color: 'var(--blueprint-blue)'}}>{styleOption.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="blueprint-card p-4">
        <div className="blueprint-label mb-2">STYLE SELECTION</div>
        <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
          Style selection influences AI design generation algorithms and product recommendation filtering parameters.
        </p>
      </div>
    </div>
  )
}

function NotesStep({ notes, setNotes }: { notes: string; setNotes: (notes: string) => void }) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="blueprint-label">DESIGN SPECIFICATIONS</div>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Specify design preferences, material requirements, spatial constraints, or technical specifications..."
          className="blueprint-input min-h-[200px] p-4 text-base w-full resize-none"
        />
      </div>
      <div className="blueprint-card p-4">
        <div className="blueprint-label mb-2">SPECIFICATION NOTES</div>
        <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
          Detailed specifications enable personalized design recommendations aligned with project requirements and spatial parameters.
        </p>
      </div>
    </div>
  )
}
