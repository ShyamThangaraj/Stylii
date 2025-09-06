"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { UploadDropzone } from "./upload-dropzone"
import { StylePickerGrid } from "./style-picker-grid"
import { useStyliiStore } from "@/lib/store"
import { generateDesign } from "@/lib/client"
import { useToast } from "@/hooks/use-toast"

export function DesignForm() {
  const { images, budget, style, notes, isGenerating, setBudget, setNotes, setIsGenerating, setError, addResult } =
    useStyliiStore()

  const { toast } = useToast()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const isValid = images.length >= 3 && style && budget > 0

  const handleSubmit = async () => {
    if (!isValid) return

    setIsGenerating(true)
    setError(null)

    try {
      const result = await generateDesign({
        images,
        style,
        budget,
        notes,
      })

      addResult(result)
      toast({
        title: "Design Generated!",
        description: "Your AI-powered room design is ready.",
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to generate design"
      setError(message)
      toast({
        title: "Generation Failed",
        description: message,
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && isValid && !isGenerating) {
        handleSubmit()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isValid, isGenerating])

  if (!mounted) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-32 bg-gray-200 rounded"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
        <div className="h-48 bg-gray-200 rounded"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Budget Input */}
      <div className="space-y-3">
        <Label htmlFor="budget">Budget</Label>
        <div className="space-y-3">
          <Input
            id="budget"
            type="number"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            placeholder="Enter your budget"
            className="text-lg"
          />
          <div className="px-3">
            <Slider
              value={[budget]}
              onValueChange={([value]) => setBudget(value)}
              max={20000}
              min={500}
              step={100}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500 mt-1">
              <span>$500</span>
              <span className="font-medium">${budget.toLocaleString()}</span>
              <span>$20,000</span>
            </div>
          </div>
        </div>
      </div>

      {/* Image Upload */}
      <div className="space-y-3">
        <Label>Room Photos (3-4 required)</Label>
        <UploadDropzone />
      </div>

      {/* Style Picker */}
      <div className="space-y-3">
        <Label>Design Style</Label>
        <StylePickerGrid />
      </div>

      {/* Notes */}
      <div className="space-y-3">
        <Label htmlFor="notes">Notes to Designer (Optional)</Label>
        <Textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any specific preferences or requirements..."
          className="min-h-[100px]"
        />
      </div>

      {/* Generate Button */}
      <Button
        onClick={handleSubmit}
        disabled={!isValid || isGenerating}
        className="w-full bg-[#FF4DA6] hover:bg-[#FF4DA6]/90 text-white py-6 text-lg rounded-2xl"
      >
        {isGenerating ? "Generating Design..." : "Generate Design"}
      </Button>

      {!isValid && (
        <p className="text-sm text-gray-500 text-center">Upload at least 3 photos and choose a style to begin</p>
      )}

      <p className="text-xs text-gray-400 text-center">Tip: Use Cmd/Ctrl+Enter to generate design</p>
    </div>
  )
}
