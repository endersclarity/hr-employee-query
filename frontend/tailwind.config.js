/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Responsive breakpoints (Subtask 6.3)
      screens: {
        'sm': '640px',   // mobile
        'md': '768px',   // tablet
        'lg': '1024px',  // desktop
        'xl': '1280px',
      },
      // Custom colors (Subtask 6.2)
      colors: {
        primary: {
          50: '#eff6ff',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
}
