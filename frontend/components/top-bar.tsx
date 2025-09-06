import Link from "next/link"
import { Button } from "@/components/ui/button"

export function TopBar() {
  return (
    <header className="border-b sticky top-0 z-50 shadow-sm" style={{borderColor: 'var(--blueprint-charcoal)', backgroundColor: 'var(--blueprint-paper)'}}>
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3">
          <div className="w-8 h-8 blueprint-card flex items-center justify-center">
            <span className="blueprint-label text-xs">S</span>
          </div>
          <span className="text-2xl font-bold blueprint-text" style={{color: 'var(--blueprint-charcoal)'}}>Stylii</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-8">
          <Link href="/" className="blueprint-text transition-colors font-medium hover:opacity-75" style={{color: 'var(--blueprint-blue)'}}>
            Home
          </Link>
          <Link href="/design" className="blueprint-text transition-colors font-medium hover:opacity-75" style={{color: 'var(--blueprint-blue)'}}>
            Design Studio
          </Link>
          <Link href="/gallery" className="blueprint-text transition-colors font-medium hover:opacity-75" style={{color: 'var(--blueprint-blue)'}}>
            Gallery
          </Link>
          <Link href="/about" className="blueprint-text transition-colors font-medium hover:opacity-75" style={{color: 'var(--blueprint-blue)'}}>
            About
          </Link>
        </nav>

        <Link href="/design" className="blueprint-button blueprint-button-primary px-6 py-2 font-medium">
          Get Started
        </Link>
      </div>
    </header>
  )
}
