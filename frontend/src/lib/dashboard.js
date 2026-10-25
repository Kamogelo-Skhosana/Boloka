// Only explicitly dated records after today and through day 30 are upcoming.
// A recurring flag never creates another bill, and zero is not proof of no costs.
export function upcomingCosts(expenses, day) {
  const end = new Date(day + 'T00:00:00Z')
  end.setUTCDate(end.getUTCDate() + 30)
  const lastDay = end.toISOString().slice(0, 10)
  const entries = expenses.filter(item => item.spent_on > day && item.spent_on <= lastDay)
    .toSorted((a, b) => a.spent_on.localeCompare(b.spent_on) || String(a.id).localeCompare(String(b.id)))
  return { entries, totalCents: entries.reduce((sum, item) => sum + item.amount_cents, 0) }
}
