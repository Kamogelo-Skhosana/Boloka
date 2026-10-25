import { defineTheme, ThemeEngine } from '@themeloom/core'

const bolokaTheme = defineTheme({
  id: 'boloka',
  category: 'brand',
  name: 'Boloka',
  description: 'Calm, clear colours designed for everyday money decisions.',
  swatch: '#32d6a6',
  color: {
    bg: '#12161c',
    bgAlt: '#232932',
    text: '#f3f5f7',
    textDim: '#b9c2cd',
    accent: '#32d6a6',
    accentText: '#12161c',
    border: '#414b59',
    cardBg: '#1c222b',
    warning: '#f6c14b',
    danger: '#ff8a80',
    success: '#32d6a6',
  },
  type: {
    display: 'Inter, ui-sans-serif, system-ui, sans-serif',
    body: 'Inter, ui-sans-serif, system-ui, sans-serif',
    heroWeight: 760,
    letterSpacing: '-0.04em',
    lineHeight: 1.55,
  },
  shape: {
    radius: '0.65rem',
    radiusLarge: '1.1rem',
    shadow: '0 16px 50px rgba(0, 0, 0, 0.24)',
    borderWidth: '1px',
    space: '1rem',
  },
  motion: { duration: '140ms', ease: 'ease-out', durationSlow: '240ms' },
})

export const themeEngine = new ThemeEngine({
  themes: [bolokaTheme],
  default: 'boloka',
  persist: false,
  prefix: 'pt',
})
