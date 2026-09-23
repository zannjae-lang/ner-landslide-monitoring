/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          dark: '#17201B',
          surface: '#222D26',
          border: '#2E3A33',
          text: '#E8E5DC',
          muted: '#AEB4AA',
        },
        earth: {
          bg: '#F4F1EA',
          secondary: '#E9E6DD',
          card: '#FAF9F5',
          border: '#D5D2C8',
          borderSubtle: '#E2DFD5',
          textPrimary: '#20251F',
          textSecondary: '#5F665F',
          textMuted: '#889087',
          green: '#496A52',
          olive: '#68754A',
          brown: '#806B52',
          blue: '#55758A',
        },
        risk: {
          normal: '#5C7A61',
          normalBg: '#EDF3EE',
          normalBorder: '#C8D8CB',
          watch: '#B18A3A',
          watchBg: '#FAF5EB',
          watchBorder: '#E5D5B3',
          alert: '#C96B3D',
          alertBg: '#FCF2EC',
          alertBorder: '#ECC5B0',
          critical: '#A83F3F',
          criticalBg: '#FBF0F0',
          criticalBorder: '#E8B8B8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      }
    },
  },
  plugins: [],
}
