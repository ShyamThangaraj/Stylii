import { TopBar } from "@/components/top-bar"
import { Footer } from "@/components/footer"

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <TopBar />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">About Stylii</h1>
          <p className="text-xl text-gray-600 text-balance">AI-powered room design that brings your vision to life</p>
        </div>

        <div className="prose prose-lg mx-auto">
          <h2>How Stylii Works</h2>
          <p>
            Stylii uses advanced artificial intelligence to transform your room photos into photorealistic design
            renders. Simply upload 3-4 photos of your space, choose your preferred style, and set your budget—our AI
            will generate a beautiful redesign along with curated product recommendations.
          </p>

          <h2>Important Notes</h2>

          <h3>AI Image Generation</h3>
          <p>
            AI-generated images may include watermarks or artifacts. While we strive for photorealistic results, the
            generated designs are artistic interpretations and may not perfectly reflect real-world lighting,
            proportions, or material textures.
          </p>

          <h3>Product Recommendations</h3>
          <p>
            Product suggestions are approximations based on your style preferences and budget. Actual product
            availability, pricing, and appearance may vary. We recommend verifying all product details with retailers
            before making purchases.
          </p>

          <h3>Budget Estimates</h3>
          <p>
            Budget calculations are estimates based on average market prices and may not reflect current pricing, sales,
            or regional variations. Additional costs such as shipping, installation, and labor are not included in our
            estimates.
          </p>

          <h2>Privacy & Data</h2>
          <p>
            Your uploaded images are used solely for generating your design and are not stored permanently or shared
            with third parties. We respect your privacy and are committed to protecting your personal information.
          </p>
        </div>
      </div>

      <Footer />
    </div>
  )
}
