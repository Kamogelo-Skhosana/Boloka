export function emptyAccountData() {
  return {
    summary: { balance_cents: 0, this_week_income_cents: 0, set_aside_progress_cents: 0 },
    forecast: { horizon_days: 30, income_estimate_available: false,
      shortfall: { likely: false, date: null, amount_cents: 0, status: 'insufficient_data' },
      set_aside: { weekly_cents: 0, total_cents: 0 }, series: [] },
    income: [], expenses: [], savings: [],
  }
}

// Older API deployments can coexist briefly with a freshly deployed frontend.
// Only a missing route permits the legacy path; never retry auth/server errors.
export async function loadAccountData(api, accessToken) {
  try {
    return await api('/dashboard', { accessToken })
  } catch (error) {
    if (error.status !== 404) throw error
  }
  const [summary, forecast, income, expenses, savings] = await Promise.all(
    ['/summary', '/forecast', '/income', '/expenses', '/savings']
      .map(path => api(path, { accessToken })),
  )
  return { summary, forecast, income: income.items || [], expenses: expenses.items || [], savings: savings.items || [] }
}
