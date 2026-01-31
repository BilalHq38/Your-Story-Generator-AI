/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Custom story atmosphere colors
        'story': {
          'dark': '#0a0a0f',
          'darker': '#050508',
          'accent': '#8b5cf6',
          'accent-light': '#a78bfa',
          'muted': '#1a1a2e',
          'border': '#2a2a3e',
        },
        // Narrator persona colors
        'narrator': {
          'mysterious': '#6366f1',
          'epic': '#f59e0b',
          'horror': '#ef4444',
          'comedic': '#10b981',
          'romantic': '#ec4899',
        },
      },
      fontFamily: {
        'story': ['Crimson Text', 'Georgia', 'serif'],
        'ui': ['Inter', 'system-ui', 'sans-serif'],
        'urdu': ['Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Nafees Nastaleeq', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'typewriter': 'typewriter 0.05s steps(1) infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(139, 92, 246, 0.6)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'story-gradient': 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%)',
      },
    },
  },
  plugins: [],
}
