import { Upload, Palette, Sparkles } from "lucide-react"

export function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: "Upload",
      description: "Share 3-4 photos of your room from different angles",
    },
    {
      icon: Palette,
      title: "Choose Style & Budget",
      description: "Select your preferred design style and set your budget",
    },
    {
      icon: Sparkles,
      title: "AI Generates Design",
      description: "Get a photorealistic render and curated product recommendations",
    },
  ]

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl font-bold text-center mb-16 text-balance">How it works</h2>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-[#FF4DA6]/10 flex items-center justify-center">
                <step.icon className="w-8 h-8" style={{ color: "#FF4DA6" }} />
              </div>
              <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
              <p className="text-gray-600 text-balance">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
