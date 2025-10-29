/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#10b981", // emerald
        accent: "#14b8a6",
        dark: "#1e293b"
      }
    },
  },
  plugins: [],
};
