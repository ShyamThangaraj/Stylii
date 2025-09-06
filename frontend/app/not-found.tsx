import Link from "next/link"
import { Button } from "@/components/ui/button"
import { TopBar } from "@/components/top-bar"

export default function NotFound() {
  return (
    <div className="min-h-screen">
      <TopBar />

      <div className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-24 h-24 mx-auto mb-8 rounded-2xl bg-gradient-to-br from-[#FF4DA6] to-[#FF6B9D] flex items-center justify-center">
            <span className="text-white font-bold text-4xl">?</span>
          </div>

          <h1 className="text-4xl font-bold mb-4">Page Not Found</h1>
          <p className="text-xl text-gray-600 mb-8 text-balance">
            Sorry, we couldn't find the page you're looking for.
          </p>

          <Button asChild className="bg-[#FF4DA6] hover:bg-[#FF4DA6]/90 text-white">
            <Link href="/">Back to Home</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
