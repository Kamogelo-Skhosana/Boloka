export function draftImportRows(rows) {
  return rows.map(row => ({ ...row, amount: (row.amount_cents / 100).toFixed(2), included: true }))
}

export function confirmedImportRows(rows) {
  const selected = rows.filter(row => row.included)
  if (!selected.length || selected.length > 10000) throw new Error('invalid_selection')
  return selected.map(row => {
    if (!/^[0-9]+(?:\.[0-9]{1,2})?$/.test(row.amount)) throw new Error('invalid_amount')
    const [whole, fraction = ''] = row.amount.split('.')
    const amount = Number(whole) * 100 + Number(fraction.padEnd(2, '0'))
    const parsedDate = new Date(row.received_on + 'T00:00:00Z')
    if (!Number.isSafeInteger(amount) || amount <= 0 || amount > 2000000000 ||
        !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(row.received_on) ||
        Number.isNaN(parsedDate.getTime()) || parsedDate.toISOString().slice(0, 10) !== row.received_on ||
        (row.source || '').length > 120 || (row.note || '').length > 1000) throw new Error('invalid_row')
    return { amount_cents: amount, source: row.source?.trim() || null,
      received_on: row.received_on, note: row.note?.trim() || null }
  })
}
