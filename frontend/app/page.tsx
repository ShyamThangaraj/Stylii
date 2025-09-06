import { TopBar } from "@/components/top-bar"
import { Hero } from "@/components/hero"
import { HowItWorks } from "@/components/how-it-works"
import { StylePreview } from "@/components/style-preview"
import { Footer } from "@/components/footer"

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <TopBar />
      <Hero />
      <HowItWorks />
      <StylePreview />
      <Footer />
    </div>
  )
}
