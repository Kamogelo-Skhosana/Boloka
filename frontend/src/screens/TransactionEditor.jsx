import { useEffect, useRef, useState } from 'react'
import { today } from '../lib/format'

export default function TransactionEditor({ item, onSave, onCancel, busy, error, tr, amount, dateLabel }) {
  const [value, setValue] = useState(String(item.amount_cents / 100))
  const [label, setLabel] = useState(item.source || item.category || '')
  const [day, setDay] = useState(item.received_on || item.spent_on)
  const [note, setNote] = useState(item.note || '')
  const [recurring, setRecurring] = useState(Boolean(item.recurring))
  const firstInput = useRef(null)
  useEffect(() => { firstInput.current?.focus() }, [])
  const income = item.kind === 'income'
  return <section className="panel form-panel" aria-labelledby="edit-heading">
    <h2 id="edit-heading">{tr('editEntry')}</h2>
    <p>{amount(item.amount_cents)} · {dateLabel(item.date)}</p>
    {error ? <p role="alert">{error}</p> : null}
    <form className="entry-form" onSubmit={event => {
      event.preventDefault()
      const cents = Math.round(Number(value) * 100)
      if (!Number.isSafeInteger(cents) || cents <= 0 || cents > 2000000000) return
      onSave({ amount_cents: cents, [income ? 'source' : 'category']: label.trim() || null,
        [income ? 'received_on' : 'spent_on']: day, note: note.trim() || null,
        ...(!income ? { recurring } : {}) })
    }}>
      <label className="field"><span>{tr('amount')}</span><input ref={firstInput} required type="number" inputMode="decimal" step="0.01" min="0.01" max="20000000" value={value} onChange={e => setValue(e.target.value)} /></label>
      <label className="field"><span>{tr(income ? 'incomeSource' : 'expenseCategory')}</span><input maxLength="120" value={label} onChange={e => setLabel(e.target.value)} /></label>
      <label className="field"><span>{tr(income ? 'receivedDate' : 'expenseDate')}</span><input required type="date" max={income ? today() : undefined} value={day} onChange={e => setDay(e.target.value)} /></label>
      {!income ? <label className="checkbox-field"><input type="checkbox" checked={recurring} onChange={e => setRecurring(e.target.checked)} /><span>{tr('recurring')}</span></label> : null}
      <label className="field"><span>{tr('optionalNote')}</span><input maxLength="1000" value={note} onChange={e => setNote(e.target.value)} /></label>
      <div className="transaction-actions"><button className="button button--primary" type="submit" disabled={busy}>{tr('saveChanges')}</button><button className="button button--outline" type="button" onClick={onCancel} disabled={busy}>{tr('cancel')}</button></div>
    </form>
  </section>
}
