/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {'hippie-blue': {
        '50': '#f2f9f9',
        '100': '#deedef',
        '200': '#c0dce1',
        '300': '#94c2cc',
        '400': '#61a0af',
        '500': '#4d92a3',
        '600': '#3d6e7d',
        '700': '#365a68',
        '800': '#334c57',
        '900': '#2e414b',
        '950': '#1b2a31',
        }
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false
  },
}