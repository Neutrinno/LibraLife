import type React from "react"

interface BracketFrameProps {
  children: React.ReactNode
  color?: "orange" | "blue" | "gray"
  title?: string
  className?: string
}

export default function BracketFrame({ children, color = "orange", title, className = "" }: BracketFrameProps) {
  const colorClasses = {
    orange: "border-orange-500 text-orange-500",
    blue: "border-blue-500 text-blue-500",
    gray: "border-gray-900 text-gray-900",
  }

  const bgColors = {
    orange: "bg-white",
    blue: "bg-white",
    gray: "bg-white",
  }

  return (
    <div className={`relative ${className}`}>
      <div className={`border-2 ${colorClasses[color]} rounded-lg px-6 py-6 relative`}>
        {/* Top left bracket */}
        <div className={`absolute -left-2 -top-2 w-6 h-6 border-l-3 border-t-3 ${colorClasses[color]}`} />

        {/* Top right bracket */}
        <div className={`absolute -right-2 -top-2 w-6 h-6 border-r-3 border-t-3 ${colorClasses[color]}`} />

        {/* Bottom left bracket */}
        <div className={`absolute -left-2 -bottom-2 w-6 h-6 border-l-3 border-b-3 ${colorClasses[color]}`} />

        {/* Bottom right bracket */}
        <div className={`absolute -right-2 -bottom-2 w-6 h-6 border-r-3 border-b-3 ${colorClasses[color]}`} />

        {/* Title label if provided */}
        {title && (
          <div className={`absolute left-1/2 -translate-x-1/2 -top-5 px-2 ${bgColors[color]}`}>
            <span
              className={`text-sm font-bold ${colorClasses[color]}`}
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              {title}
            </span>
          </div>
        )}

        {/* Content */}
        <div>{children}</div>
      </div>
    </div>
  )
}
