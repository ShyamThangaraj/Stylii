"use client"

import { useState, useEffect } from "react"
import { DesignForm } from "./design-form"
import { DesignResults } from "./design-results"
import { useStyliiStore } from "@/lib/store"

export function DesignStudio() {
  const { currentResultId, results } = useStyliiStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8 h-[calc(100vh-8rem)]">
          <div className="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="space-y-4">
              <div className="h-32 bg-gray-200 rounded"></div>
              <div className="h-16 bg-gray-200 rounded"></div>
              <div className="h-48 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  const currentResult = currentResultId ? results.find((r) => r.id === currentResultId) : null

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid lg:grid-cols-2 gap-8 h-[calc(100vh-8rem)]">
        <div className="bg-white rounded-2xl p-6 shadow-sm overflow-y-auto">
          <h1 className="text-2xl font-bold mb-6">Design Studio</h1>
          <DesignForm />
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm overflow-y-auto">
          <DesignResults result={currentResult} />
        </div>
      </div>
    </div>
  )
}
