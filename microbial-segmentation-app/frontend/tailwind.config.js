/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Bitcoin DeFi Color System
        void: '#030304',           // True Void - deepest background
        'dark-matter': '#0F1115',  // Dark Matter - elevated surfaces
        stardust: '#94A3B8',       // Stardust - secondary text
        'dim-boundary': '#1E293B', // Dim Boundary - borders
        'bitcoin-orange': '#F7931A', // Bitcoin Orange - primary accent
        'burnt-orange': '#EA580C',   // Burnt Orange - secondary accent
        'digital-gold': '#FFD600',   // Digital Gold - tertiary accent
      },
      fontFamily: {
        heading: ['var(--font-space-grotesk)', 'sans-serif'],
        body: ['var(--font-inter)', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      boxShadow: {
        'orange-glow': '0 0 20px -5px rgba(234, 88, 12, 0.5)',
        'orange-glow-lg': '0 0 30px -5px rgba(247, 147, 26, 0.6)',
        'gold-glow': '0 0 20px rgba(255, 214, 0, 0.3)',
        'card-elevation': '0 0 50px -10px rgba(247, 147, 26, 0.1)',
        'input-focus': '0 10px 20px -10px rgba(247, 147, 26, 0.3)',
      },
      animation: {
        'float': 'float 8s ease-in-out infinite',
        'spin-slow': 'spin 10s linear infinite',
        'spin-reverse': 'spin 15s linear infinite reverse',
        'bounce-slow': 'bounce 3s infinite',
        'bounce-slower': 'bounce 4s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
