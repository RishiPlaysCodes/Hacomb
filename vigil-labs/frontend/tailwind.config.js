/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // ─── VIGIL LABS Design System (Premium Light) ─────────────
        vigil: {
          // Backgrounds
          bg: '#f6f7fb',        // soft off-white page background
          surface: '#ffffff',   // inputs / raised surfaces
          card: '#ffffff',      // cards / panels
          hover: '#f1f5f9',     // hover state

          // Borders
          border: '#e5e8ef',

          // Primary palette
          primary: '#6366f1',
          'primary-light': '#818cf8',
          secondary: '#0891b2',
          accent: '#7c3aed',

          // Semantic
          success: '#059669',
          warning: '#d97706',
          danger: '#dc2626',

          // Text (dark on light)
          text: '#0f172a',
          'text-muted': '#475569',
          'text-dim': '#94a3b8',

          // Neon/Special
          neon: '#6366f1',
          'neon-blue': '#3b82f6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-sm': '0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.1)',
        'glow': '0 4px 16px rgba(99, 102, 241, 0.18), 0 2px 4px rgba(15, 23, 42, 0.06)',
        'glass': '0 1px 3px rgba(15, 23, 42, 0.08), 0 8px 24px rgba(15, 23, 42, 0.06)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(99, 102, 241, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
