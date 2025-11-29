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
        background: '#000000',
        surface: '#1C1C1E',
        surfaceElevated: '#2C2C2E',
        text: '#FFFFFF',
        textSecondary: '#8E8E93',
        accent: '#007AFF',
        border: '#38383A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '16px',
      },
      spacing: {
        '8px': '8px',
        '16px': '16px',
        '24px': '24px',
        '32px': '32px',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.3)',
        'elevated': '0 4px 16px rgba(0, 0, 0, 0.4)',
      },
    },
  },
  plugins: [],
}

