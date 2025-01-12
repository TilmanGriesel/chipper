module.exports = {
  darkMode: "class",
  content: ["templates/*.html", "static/js/*.js"],
  theme: {
    fontFamily: {
      sans: ["ui-sans-serif", "system-ui"],
      serif: ["Lora", "ui-serif", "serif"],
      mono: ["Fira Code NF", "ui-monospace"],
    },
    extend: {
      colors: {
        "brand-a": {
          50: "#F6F1ED",
          100: "#F1E7E0",
          200: "#EBDDD3",
          300: "#E0CBBF",
          400: "#C79273",
          500: "#A06340",
          600: "#804F33",
          700: "#603C26",
          800: "#40281A",
          900: "#20140D",
          950: "#120B07",
        },
        "brand-b": {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#52525b",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b",
        },
      },
    },
  },
  plugins: [],
};
