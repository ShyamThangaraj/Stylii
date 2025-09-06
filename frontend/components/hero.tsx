import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Hero() {
  return (
    <section className="py-20 px-4 text-center bg-gradient-to-b from-white to-gray-50">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-8">
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-orange-400 to-amber-500 flex items-center justify-center">
            <span className="text-white font-bold text-2xl">S</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold mb-6 text-balance">
            Design your dream room with <span className="text-orange-500">AI</span>
          </h1>
        </div>

        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto text-balance">
          Upload your space, pick a style, set a budget—Stylii creates a render and a curated shopping list.
        </p>

        <Button
          asChild
          size="lg"
          className="bg-gradient-to-r from-orange-400 to-amber-500 hover:from-orange-500 hover:to-amber-600 text-white text-lg px-8 py-6 rounded-2xl"
        >
          <Link href="/design">Get Started</Link>
        </Button>
      </div>
    </section>
  )
}
