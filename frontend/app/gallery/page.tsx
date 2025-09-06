import { TopBar } from "@/components/top-bar"
import { GalleryGrid } from "@/components/gallery-grid"

export default function GalleryPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar />
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Design Gallery</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto text-balance">
            Explore AI-generated room transformations and get inspired for your own space.
          </p>
        </div>
        <GalleryGrid />
      </div>
    </div>
  )
}
