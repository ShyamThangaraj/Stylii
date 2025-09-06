import type React from "react"
export function StyliiLoader({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  }

  return (
    <div className="flex items-center justify-center">
      <div className={`${sizeClasses[size]} stylii-loader`}>
        <div
          className="w-full h-full rounded-full border-4 border-gray-200 border-t-[#FF4DA6]"
          style={{ borderTopColor: "#FF4DA6" }}
        />
      </div>
    </div>
  )
}

export function StyliiPulse({ children }: { children: React.ReactNode }) {
  return <div className="stylii-pulse">{children}</div>
}
