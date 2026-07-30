/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        blush: '#fbf2f3',
        ink: '#15151a',
        plum: '#332433',
        rosebrand: '#8f2f45',
        paper: '#ffffff',
        line: '#eadde0'
      },
      fontFamily: {
        display: ['Segoe UI', 'Arial', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        sans: ['Segoe UI', 'Arial', 'ui-sans-serif', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        soft: '0 10px 28px rgba(21,21,26,.07)'
      }
    },
  },
  plugins: [],
};
