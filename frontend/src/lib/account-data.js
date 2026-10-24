export function emptyAccountData() {
  return {
    summary: { balance_cents: 0, this_week_income_cents: 0, set_aside_progress_cents: 0 },
    forecast: { horizon_days: 30, income_estimate_available: false,
      shortfall: { likely: false, date: null, amount_cents: 0, status: 'insufficient_data' },
      set_aside: { weekly_cents: 0, total_cents: 0 }, series: [] },
    income: [], expenses: [], savings: [],
  }
}
