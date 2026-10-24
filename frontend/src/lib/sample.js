import { previewTotals } from './transactions.js'

const referenceSample = {
  summary: {
    balance_cents: 842500,
    this_week_income_cents: 127500,
    set_aside_progress_cents: 30000,
    set_aside_target_cents: 60000,
    next_shortfall: { date: '2026-11-22', amount_cents: 48000 },
  },
  forecast: {
    horizon_days: 30,
    predicted_income_cents: 520000,
    predicted_expenses_cents: 568000,
    shortfall: { likely: true, date: '2026-11-22', amount_cents: 48000 },
    set_aside: {
      weekly_cents: 16000,
      reason: 'Saving about R160.00 each week over three weeks builds toward the estimated gap.',
    },
    confidence: 'low',
    explanation:
      'Sample estimate based on irregular payouts and known monthly costs. Add your own entries to get a forecast based on your history.',
    series: [
      { week_start: '2026-10-26', predicted_income_cents: 130000, lower_cents: 65000, upper_cents: 195000 },
      { week_start: '2026-11-02', predicted_income_cents: 105000, lower_cents: 52500, upper_cents: 157500 },
      { week_start: '2026-11-09', predicted_income_cents: 155000, lower_cents: 77500, upper_cents: 232500 },
      { week_start: '2026-11-16', predicted_income_cents: 130000, lower_cents: 65000, upper_cents: 195000 },
    ],
  },
  income: [
    { id: 'sample-i1', amount_cents: 84500, source: 'Delivery shifts', received_on: '2026-10-23' },
    { id: 'sample-i2', amount_cents: 43000, source: 'Market orders', received_on: '2026-10-21' },
    { id: 'sample-i3', amount_cents: 862000, source: 'Earlier payouts', received_on: '2026-10-01' },
  ],
  expenses: [
    { id: 'sample-e1', amount_cents: 22000, category: 'Transport', spent_on: '2026-10-23' },
    { id: 'sample-e2', amount_cents: 125000, category: 'Rent', spent_on: '2026-10-20', recurring: true },
  ],
  savings: [
    { id: 'sample-s1', amount_cents: 20000, saved_on: '2026-10-18', note: 'Payout set-aside' },
    { id: 'sample-s2', amount_cents: 10000, saved_on: '2026-10-22', note: 'Payout set-aside' },
  ],
}


export function createPreview(today) {
  const data = structuredClone(referenceSample)
  data.forecast.shortfall = { ...data.forecast.shortfall, likely: false, date: null, status: 'sample' }
  data.forecast.confidence = 'low'
  data.summary.next_shortfall = null
  return previewTotals(data, today)
}
