import Link from "next/link"
import { Button } from "@/components/ui/button"

export function TopBar() {
  return (
    <header className="border-b border-orange-200 bg-white sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center shadow-sm stylii-logo">
            <span className="font-bold text-sm">S</span>
          </div>
          <span className="text-2xl font-bold text-orange-600">Stylii</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-8">
          <Link href="/" className="text-gray-700 hover:text-orange-600 transition-colors font-medium">
            Home
          </Link>
          <Link href="/design" className="text-gray-700 hover:text-orange-600 transition-colors font-medium">
            Design Studio
          </Link>
          <Link href="/gallery" className="text-gray-700 hover:text-orange-600 transition-colors font-medium">
            Gallery
          </Link>
          <Link href="/about" className="text-gray-700 hover:text-orange-600 transition-colors font-medium">
            About
          </Link>
        </nav>

        <Button asChild className="bg-orange-600 hover:bg-orange-700 text-white shadow-sm rounded-2xl px-6 font-medium">
          <Link href="/design" className="text-white">
            Get Started
          </Link>
        </Button>
      </div>
    </header>
  )
}
