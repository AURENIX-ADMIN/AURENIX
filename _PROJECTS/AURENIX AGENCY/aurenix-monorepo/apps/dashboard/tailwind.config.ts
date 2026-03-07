import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
        card: "var(--card)",
        secondary: "var(--secondary)",
        primary: "hsl(var(--primary))",
        muted: "hsl(var(--muted))",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
