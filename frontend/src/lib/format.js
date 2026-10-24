import { languageLocale, translate } from './copy.js'

export const formatMoney = (cents = 0, language = 'en') => new Intl.NumberFormat(languageLocale(language), {
  style: 'currency', currency: 'ZAR', minimumFractionDigits: 2,
}).format(Number(cents || 0) / 100)

export function formatDate(value, language = 'en', options = { day: 'numeric', month: 'short' }) {
  const day = new Date(value + 'T12:00:00Z')
  return !value || Number.isNaN(day.getTime()) ? translate(language, 'notAvailable')
    : new Intl.DateTimeFormat(languageLocale(language), { ...options, timeZone: 'Africa/Johannesburg' }).format(day)
}

export function today() {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en', {
    timeZone: 'Africa/Johannesburg', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(new Date()).map(part => [part.type, part.value]))
  return `${parts.year}-${parts.month}-${parts.day}`
}
