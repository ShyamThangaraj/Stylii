import { MultiStepDesignForm } from "@/components/multi-step-design-form"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <MultiStepDesignForm />
        </div>
      </div>
    </div>
  )
}
