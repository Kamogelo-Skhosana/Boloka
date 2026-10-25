import { useEffect, useRef, useState } from 'react'
import { confirmedImportRows, draftImportRows } from '../lib/import-review'

const PAGE_SIZE = 20

export default function IncomeImport({ send, onImported, tr, disabled }) {
  const rowGroup = useRef(null)
  const reviewHeading = useRef(null)
  const fileInput = useRef(null)
  const errorMessage = useRef(null)
  const focusTarget = useRef(null)
  const [review, setReview] = useState(null)
  const [rows, setRows] = useState([])
  const [page, setPage] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (busy) return
    if (error) errorMessage.current?.focus()
    else if (focusTarget.current) {
      const target = focusTarget.current === 'review' ? reviewHeading : fileInput
      target.current?.focus()
      focusTarget.current = null
    }
  }, [review, error, busy])

  async function preview(event) {
    event.preventDefault()
    const file = event.currentTarget.elements.csv.files?.[0]
    if (!file || file.size > 2000000) { setError(tr('chooseACsvFileSmallerThan2Mb')); return }
    setBusy(true)
    setError('')
    try {
      const form = new FormData()
      form.append('file', file)
      const result = await send('/income/import/preview', { method: 'POST', body: form })
      focusTarget.current = 'review'
      setRows(draftImportRows(result.rows))
      setReview({ filename: file.name, skipped: result.skipped, errors: result.errors || [] })
      setPage(0)
    } catch { setError(tr('couldNotImportThatFile')) }
    finally { setBusy(false) }
  }

  function change(index, changes) {
    setRows(current => current.map((row, i) => i === index ? { ...row, ...changes } : row))
    setError('')
  }

  function changePage(next) {
    setPage(next)
    window.requestAnimationFrame(() => rowGroup.current?.querySelector('input')?.focus())
  }

  async function confirm(event) {
    event.preventDefault()
    let prepared
    try { prepared = confirmedImportRows(rows) }
    catch { setError(tr('importReviewInvalid')); return }
    setBusy(true)
    setError('')
    try {
      const result = await send('/income/import/confirm', { method: 'POST', body: { rows: prepared } })
      // Clear after a confirmed write, before refresh, so a refresh failure cannot resubmit.
      const skipped = review.skipped + rows.length - prepared.length
      focusTarget.current = 'upload'
      setReview(null)
      setRows([])
      await onImported({ ...result, skipped })
    } catch { setError(tr('importSaveUncertain')) }
    finally { setBusy(false) }
  }

  const locked = busy || disabled
  const selected = rows.filter(row => row.included).length
  return <section className="income-import" aria-label={tr('reviewIncomeImport')} aria-busy={busy}>
    {error ? <p className="status-message status-message--error" role="alert" tabIndex={-1} ref={errorMessage}>{error}</p> : null}
    {!review ? <form onSubmit={preview} className="import-form">
      <label className="field"><span>{tr('chooseACsvFile')}</span><input ref={fileInput} required name="csv" type="file" accept=".csv,text/csv" disabled={locked} /></label>
      <button className="button button--outline" type="submit" disabled={locked}>{tr('previewIncomeImport')}</button>
    </form> : <form onSubmit={confirm}>
      <h3 ref={reviewHeading} tabIndex={-1}>{tr('reviewIncomeImport')}</h3>
      <p>{review.filename}</p>
      <p>{tr('importReviewHelp')}</p>
      <p role="status">{tr('importSelection', { count: selected, skipped: review.skipped })}</p>
      {review.errors.length ? <section aria-label={tr('csvErrors')}><h4>{tr('csvErrors')}</h4><ol lang="en">{review.errors.map(item => <li key={item.line}>{tr('csvRowError', item)}</li>)}</ol></section> : null}
      <div className="import-review-rows" ref={rowGroup}>{rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).map((row, offset) => {
        const index = page * PAGE_SIZE + offset
        return <fieldset key={index} disabled={locked}>
          <legend>{tr('importCsvLine', { line: row.line })}</legend>
          <label className="import-include"><input type="checkbox" checked={row.included} onChange={event => change(index, { included: event.target.checked })} />{tr('includeImportRow')}</label>
          <label className="field"><span>{tr('amount')}</span><input disabled={!row.included} type="number" min="0.01" max="20000000" step="0.01" inputMode="decimal" required={row.included} value={row.amount} onChange={event => change(index, { amount: event.target.value })} /></label>
          <label className="field"><span>{tr('incomeSource')}</span><input disabled={!row.included} maxLength="120" value={row.source || ''} onChange={event => change(index, { source: event.target.value })} /></label>
          <label className="field"><span>{tr('receivedDate')}</span><input disabled={!row.included} type="date" required={row.included} value={row.received_on} onChange={event => change(index, { received_on: event.target.value })} /></label>
          <label className="field"><span>{tr('optionalNote')}</span><input disabled={!row.included} maxLength="1000" value={row.note || ''} onChange={event => change(index, { note: event.target.value })} /></label>
        </fieldset>
      })}</div>
      <div className="import-review-actions">
        <button type="button" className="button button--outline" disabled={locked || page === 0} onClick={() => changePage(page - 1)}>{tr('importPrevious')}</button>
        <span role="status">{tr('importPage', { page: page + 1, pages: Math.max(1, Math.ceil(rows.length / PAGE_SIZE)) })}</span>
        <button type="button" className="button button--outline" disabled={locked || (page + 1) * PAGE_SIZE >= rows.length} onClick={() => changePage(page + 1)}>{tr('importNext')}</button>
      </div>
      <div className="import-review-actions">
        <button type="submit" className="button button--primary" disabled={locked || !selected}>{tr('confirmIncomeImport', { count: selected })}</button>
        <button type="button" className="button button--outline" disabled={locked} onClick={() => { focusTarget.current = 'upload'; setReview(null); setRows([]); setError('') }}>{tr('cancel')}</button>
      </div>
    </form>}
  </section>
}
