/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg:       "#0a0a0f",
          bgAlt:    "#0d0d18",
          surface:  "#111128",
          border:   "#1e2040",
          cyan:     "#00f5ff",
          cyanDim:  "#00c8d4",
          purple:   "#8b5cf6",
          purpleDim:"#6d28d9",
          red:      "#ff003c",
          orange:   "#ff6b00",
          green:    "#00ff87",
          yellow:   "#ffd700",
          text:     "#e2e8f0",
          textDim:  "#64748b",
        },
      },
      fontFamily: {
        mono:  ["'JetBrains Mono'", "monospace"],
        sans:  ["'Inter'", "sans-serif"],
      },
      boxShadow: {
        "cyber-cyan":   "0 0 20px rgba(0,245,255,0.3)",
        "cyber-purple": "0 0 20px rgba(139,92,246,0.3)",
        "cyber-red":    "0 0 20px rgba(255,0,60,0.4)",
        "glass":        "0 8px 32px rgba(0,0,0,0.4)",
      },
      backgroundImage: {
        "gradient-cyber": "linear-gradient(135deg, #0a0a0f 0%, #0d0d18 100%)",
        "gradient-cyan":  "linear-gradient(135deg, #00f5ff20, #8b5cf620)",
      },
      animation: {
        "pulse-slow":  "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "glow-cyan":   "glow-cyan 2s ease-in-out infinite alternate",
        "scan":        "scan 4s linear infinite",
        "float":       "float 6s ease-in-out infinite",
      },
      keyframes: {
        "glow-cyan": {
          "0%":   { boxShadow: "0 0 5px #00f5ff40" },
          "100%": { boxShadow: "0 0 25px #00f5ff, 0 0 50px #00f5ff40" },
        },
        scan: {
          "0%":   { backgroundPosition: "0% 0%" },
          "100%": { backgroundPosition: "0% 100%" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-8px)" },
        },
      },
    },
  },
  plugins: [],
}
