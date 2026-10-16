import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cinemax: {
          dark: "#0b0f19",
          card: "#121826",
          border: "#1f293d",
          accent: "#3b82f6",
          gold: "#eab308",
          ruby: "#ef4444",
          emerald: "#10b981",
          purple: "#8b5cf6"
        }
      }
    },
  },
  plugins: [],
};
export default config;
