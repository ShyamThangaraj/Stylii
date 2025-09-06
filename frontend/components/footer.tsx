export function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12 px-4">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-6 md:mb-0">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF4DA6] to-[#FF6B9D] flex items-center justify-center">
                <span className="text-white font-bold text-sm">S</span>
              </div>
              <span className="text-2xl font-bold" style={{ color: "#FF4DA6" }}>
                Stylii
              </span>
            </div>
            <p className="text-gray-400 max-w-md text-balance">
              AI-powered room design that brings your vision to life.
            </p>
          </div>

          <div className="text-center md:text-right">
            <p className="text-sm text-gray-400 mb-2">AI images may include watermarks</p>
            <p className="text-sm text-gray-400 mb-2">Product suggestions are approximations</p>
            <p className="text-sm text-gray-400">Budgets are estimates</p>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-gray-400 text-sm">© 2024 Stylii. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
