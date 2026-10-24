// Pure preview ledger operations. The reference forecast is intentionally static.
export function previewTotals(data, today) {
  const day = new Date(today + 'T12:00:00Z')
  const monday = new Date(day)
  monday.setUTCDate(day.getUTCDate() - (day.getUTCDay() + 6) % 7)
  const weekStart = monday.toISOString().slice(0, 10)
  const sum = (rows, field, start = '') => rows.reduce((total, row) =>
    total + (row[field] >= start && row[field] <= today ? Number(row.amount_cents) : 0), 0)
  return {
    ...data,
    summary: {
      ...data.summary,
      balance_cents: sum(data.income, 'received_on') - sum(data.expenses, 'spent_on'),
      this_week_income_cents: sum(data.income, 'received_on', weekStart),
      set_aside_progress_cents: sum(data.savings || [], 'saved_on', today.slice(0, 7) + '-01'),
    },
  }
}

export function updatePreview(data, resource, id, entry, today) {
  const rows = id
    ? data[resource].filter(row => row.id !== id)
    : [...data[resource]]
  if (entry) rows.unshift({ ...entry, id: id || crypto.randomUUID() })
  return previewTotals({ ...data, [resource]: rows }, today)
}

// The caller owns loading/error state. Failed requests never mutate the ledger.
export async function changeTransaction({ preview, data, resource, id, entry, today, send }) {
  if (preview) return updatePreview(data, resource, id, entry, today)
  const path = '/' + resource + (id ? '/' + encodeURIComponent(id) : '')
  await send(path, { method: entry ? (id ? 'PATCH' : 'POST') : 'DELETE', body: entry || undefined })
  return null
}

export function exportRecords(data, preview, today) {
  const pick = (rows, fields) => rows.map(row => Object.fromEntries(fields.map(field => [field, row[field] ?? null])))
  return {
    exported_on: today,
    scope: 'Currently loaded records only; not a full account export',
    fictional_preview: preview,
    income: pick(data.income || [], ['id', 'amount_cents', 'source', 'received_on', 'note']),
    expenses: pick(data.expenses || [], ['id', 'amount_cents', 'category', 'spent_on', 'recurring', 'note']),
    savings: pick(data.savings || [], ['id', 'amount_cents', 'saved_on', 'note']),
  }
}
