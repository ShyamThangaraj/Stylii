import { create } from "zustand"
import type { DesignResult, StreamingProgress } from "./client"

interface StyliiStore {
  // Form state
  images: File[]
  budget: number
  style: string
  notes: string
  selectedProducts: string[]

  // UI state
  isGenerating: boolean
  error: string | null
  currentProgress: StreamingProgress | null

  // Results
  results: DesignResult[]
  currentResultId: string | null

  // Actions
  setImages: (images: File[]) => void
  setBudget: (budget: number) => void
  setStyle: (style: string) => void
  setNotes: (notes: string) => void
  setSelectedProducts: (products: string[]) => void
  setIsGenerating: (isGenerating: boolean) => void
  setError: (error: string | null) => void
  setProgress: (progress: StreamingProgress | null) => void
  addResult: (result: DesignResult) => void
  setCurrentResult: (id: string) => void
  reset: () => void
}

export const useStyliiStore = create<StyliiStore>((set) => ({
  // Initial state
  images: [],
  budget: 5000,
  style: "modern",
  notes: "",
  selectedProducts: [],
  isGenerating: false,
  error: null,
  currentProgress: null,
  results: [],
  currentResultId: null,

  // Actions
  setImages: (images) => set({ images }),
  setBudget: (budget) => set({ budget }),
  setStyle: (style) => set({ style }),
  setNotes: (notes) => set({ notes }),
  setSelectedProducts: (selectedProducts) => set({ selectedProducts }),
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  setError: (error) => set({ error }),
  setProgress: (currentProgress) => set({ currentProgress }),
  addResult: (result) =>
    set((state) => ({
      results: [result, ...state.results],
      currentResultId: result.id,
      isGenerating: false,
      currentProgress: null,
      error: null,
    })),
  setCurrentResult: (id) => set({ currentResultId: id }),
  reset: () =>
    set({
      images: [],
      budget: 5000,
      style: "modern",
      notes: "",
      selectedProducts: [],
      isGenerating: false,
      error: null,
      currentProgress: null,
    }),
}))
