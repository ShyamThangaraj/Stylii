"use client"

import { useStyliiStore } from "@/lib/store"
import { Card } from "@/components/ui/card"

export function HistoryStrip() {
  const { results, currentResultId, setCurrentResult } = useStyliiStore()

  if (results.length === 0) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-gray-600">Recent Designs</h3>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {results.slice(0, 5).map((result) => (
          <Card
            key={result.id}
            className={`flex-shrink-0 w-20 h-20 p-1 cursor-pointer transition-all ${
              currentResultId === result.id ? "ring-2 ring-[#FF4DA6]" : "hover:ring-1 hover:ring-gray-300"
            }`}
            onClick={() => setCurrentResult(result.id)}
          >
            <img
              src={result.renderUrl || "/placeholder.svg"}
              alt={`Design ${result.style}`}
              className="w-full h-full object-cover rounded"
            />
          </Card>
        ))}
      </div>
    </div>
  )
}
