import test from 'node:test'
import assert from 'node:assert/strict'
import { createPreview } from '../src/lib/sample.js'
import { changeTransaction, exportRecords, updatePreview } from '../src/lib/transactions.js'

import { loadAccountData } from '../src/lib/account-data.js'

const day = '2026-10-24'

test('preview create/edit/delete update ledger totals without sending data or changing the reference forecast', async () => {
  const original = createPreview(day)
  const snapshot = structuredClone(original)
  const entry = { amount_cents: 10000, source: 'Test payout', received_on: day }
  const added = await changeTransaction({ preview: true, data: original, resource: 'income', entry, today: day,
    send: () => assert.fail('Preview must never call the API') })
  assert.equal(added.summary.balance_cents, original.summary.balance_cents + 10000)
  assert.equal(added.summary.this_week_income_cents, original.summary.this_week_income_cents + 10000)
  assert.deepEqual(added.forecast, original.forecast)
  const edited = updatePreview(added, 'income', added.income[0].id, { ...entry, amount_cents: 20000 }, day)
  assert.equal(edited.summary.this_week_income_cents, original.summary.this_week_income_cents + 20000)
  const removed = updatePreview(edited, 'income', added.income[0].id, null, day)
  assert.deepEqual(removed.summary, original.summary)
  assert.deepEqual(original, snapshot)
})

test('future expenses do not reduce recorded net until their due date; corrections and removal stay consistent', () => {
  const data = createPreview(day)
  const future = updatePreview(data, 'expenses', null, { amount_cents: 5000, spent_on: '2026-10-25' }, day)
  assert.equal(future.summary.balance_cents, data.summary.balance_cents)
  const paid = updatePreview(future, 'expenses', future.expenses[0].id, { amount_cents: 5000, spent_on: day }, day)
  assert.equal(paid.summary.balance_cents, data.summary.balance_cents - 5000)
  assert.equal(updatePreview(paid, 'expenses', paid.expenses[0].id, null, day).summary.balance_cents, data.summary.balance_cents)
})

test('savings totals exclude other months and future entries', () => {
  const data = createPreview(day)
  for (const date of ['2026-09-24', '2026-10-25']) {
    const next = updatePreview(data, 'savings', null, { amount_cents: 5000, saved_on: date }, day)
    assert.equal(next.summary.set_aside_progress_cents, data.summary.set_aside_progress_cents)
  }
})

test('failed account mutation leaves records intact; account edit and delete use the correct routes', async () => {
  const data = createPreview(day)
  const before = structuredClone(data)
  await assert.rejects(changeTransaction({ preview: false, data, resource: 'expenses', id: 'id', entry: null,
    send: async () => { throw new Error('offline') } }), /offline/)
  assert.deepEqual(data, before)
  const calls = []
  const send = async (...args) => calls.push(args)
  await changeTransaction({ preview: false, resource: 'income', id: 'id', entry: { amount_cents: 500 }, send })
  await changeTransaction({ preview: false, resource: 'expenses', id: 'id', entry: null, send })
  assert.equal(calls[0][0], '/income/id')
  assert.equal(calls[0][1].method, 'PATCH')
  assert.equal(calls[1][0], '/expenses/id')
  assert.equal(calls[1][1].method, 'DELETE')
})

test('loaded-record export identifies its scope and fiction, and excludes auth data', () => {
  const data = createPreview(day)
  data.income[0].access_token = 'must-not-export'
  const exported = exportRecords(data, true, day)
  assert.equal(exported.fictional_preview, true)
  assert.match(exported.scope, /not a full account export/)
  assert.equal(JSON.stringify(exported).includes('must-not-export'), false)
  assert.equal(Object.hasOwn(exported, 'forecast'), false)
})


test('account refresh uses one request and only falls back for a missing route', async () => {
  const data = { summary: {}, forecast: {}, income: [], expenses: [], savings: [] }
  const calls = []
  assert.equal(await loadAccountData(async (path, options) => {
    calls.push(path)
    assert.equal(options.accessToken, 'caller-token')
    return data
  }, 'caller-token'), data)
  assert.deepEqual(calls, ['/dashboard'])

  for (const status of [401, 403, 500, 502, 503, undefined]) {
    const failed = []
    const error = Object.assign(new Error('Unavailable'), { status })
    await assert.rejects(loadAccountData(async path => { failed.push(path); throw error }, 'caller-token'), error)
    assert.deepEqual(failed, ['/dashboard'])
  }
  const legacy = []
  const fallback = await loadAccountData(async path => {
    legacy.push(path)
    if (path === '/dashboard') throw Object.assign(new Error('Not found'), { status: 404 })
    if (path === '/summary' || path === '/forecast') return data[path.slice(1)]
    return { items: [{ id: path }] }
  }, 'caller-token')
  assert.deepEqual(legacy, ['/dashboard', '/summary', '/forecast', '/income', '/expenses', '/savings'])
  assert.deepEqual(fallback.income, [{ id: '/income' }])
  assert.deepEqual(fallback.expenses, [{ id: '/expenses' }])
  assert.deepEqual(fallback.savings, [{ id: '/savings' }])
})


test('upcoming costs include day 30 once, exclude today and do not repeat recurring history', async () => {
  const { upcomingCosts } = await import('../src/lib/dashboard.js')
  const rows = [
    { id: 'old', spent_on: '2026-10-01', amount_cents: 9000, recurring: true },
    { id: 'today', spent_on: '2026-10-25', amount_cents: 5000 },
    { id: 'last', spent_on: '2026-11-24', amount_cents: 2000, recurring: true },
    { id: 'outside', spent_on: '2026-11-25', amount_cents: 7000 },
    { id: 'next', spent_on: '2026-10-26', amount_cents: 1000 },
  ]
  const snapshot = structuredClone(rows)
  assert.deepEqual(upcomingCosts(rows, '2026-10-25'), { entries: [rows[4], rows[2]], totalCents: 3000 })
  assert.deepEqual(rows, snapshot)
  assert.deepEqual(upcomingCosts([], '2026-10-25'), { entries: [], totalCents: 0 })
})


test('import review preserves input, applies edits, excludes rows and strips ownership', async () => {
  const { draftImportRows, confirmedImportRows } = await import('../src/lib/import-review.js')
  const original = [{ amount_cents: 1234, source: 'Original', received_on: '2026-10-24', note: 'Note', line: 2, user_id: 'untrusted' }]
  const drafts = draftImportRows(original)
  assert.equal(drafts[0].amount, '12.34')
  drafts[0].amount = '0.01'
  drafts[0].source = 'Corrected'
  drafts.push({ included: false, amount: 'bad', received_on: 'bad' })
  assert.deepEqual(confirmedImportRows(drafts), [{ amount_cents: 1, source: 'Corrected', received_on: '2026-10-24', note: 'Note' }])
  assert.equal(original[0].amount_cents, 1234)
  for (const amount of ['0', '-1', 'NaN', '1.001', '1e2', '20000000.01']) {
    assert.throws(() => confirmedImportRows([{ ...drafts[0], amount }]))
  }
  assert.throws(() => confirmedImportRows([{ ...drafts[0], received_on: '2026-02-30' }]))
  assert.throws(() => confirmedImportRows(drafts.map(row => ({ ...row, included: false }))))
})
