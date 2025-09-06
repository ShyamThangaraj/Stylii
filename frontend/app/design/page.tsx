import { TopBar } from "@/components/top-bar"
import { MultiStepDesignForm } from "@/components/multi-step-design-form"

export default function DesignPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <TopBar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <MultiStepDesignForm />
        </div>
      </div>
    </div>
  )
}
