import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, supabase } from './lib/client'

const sample = {
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
}

const money = new Intl.NumberFormat('en-ZA', {
  style: 'currency',
  currency: 'ZAR',
  minimumFractionDigits: 2,
})

const dateLabel = (value, options = { day: 'numeric', month: 'short' }) => {
  if (!value) return 'Not available'
  const date = new Date(value + 'T12:00:00')
  return Number.isNaN(date.getTime())
    ? 'Not available'
    : new Intl.DateTimeFormat('en-ZA', options).format(date)
}

const amount = (cents = 0) => money.format(Number(cents || 0) / 100)
const today = () => {
  const now = new Date()
  return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-')
}

function Brand({ compact = false }) {
  return (
    <a className={'brand' + (compact ? ' brand--compact' : '')} href="#home" aria-label="Boloka home">
      <span className="brand__mark" aria-hidden="true">b</span>
      <span className="brand__word">boloka</span>
    </a>
  )
}

function Icon({ name }) {
  const paths = {
    home: <><path d="m3 10 9-7 9 7" /><path d="M5 9v11h14V9M9 20v-6h6v6" /></>,
    add: <><path d="M12 5v14M5 12h14" /></>,
    forecast: <><path d="M3 18h18M5 15l4-5 4 3 6-8" /><path d="M17 5h2v2" /></>,
    savings: <><rect x="3" y="6" width="18" height="14" rx="3" /><path d="M3 10h18M7 16h4" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.8 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.8-1l-1.7.7-1.4-2.4 1.4-1.1a7 7 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.8-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.8 1l1.7-.7 1.4 2.4-1.4 1.1a7 7 0 0 1 0 2Z" /></>,
  }
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
      {paths[name]}
    </svg>
  )
}

function Metric({ label, value, hint, tone = '' }) {
  return (
    <article className={'metric-card ' + tone}>
      <p className="eyebrow">{label}</p>
      <p className="metric-card__value">{value}</p>
      {hint ? <p className="metric-card__hint">{hint}</p> : null}
    </article>
  )
}

function App() {
  const [session, setSession] = useState(null)
  const [authReady, setAuthReady] = useState(!supabase)
  const [page, setPage] = useState('home')
  const [data, setData] = useState(sample)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [authMode, setAuthMode] = useState('signin')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [entryKind, setEntryKind] = useState('income')
  const [entryAmount, setEntryAmount] = useState('')
  const [entryLabel, setEntryLabel] = useState('')
  const [entryDate, setEntryDate] = useState(today)
  const [recurring, setRecurring] = useState(false)
  const pageTitleRef = useRef(null)

  const preview = !session
  const profileName = session?.user?.email?.split('@')[0] || 'friend'
  const shortfall = data.forecast?.shortfall

  const refresh = useCallback(async () => {
    if (!session) return
    setLoading(true)
    setMessage('')
    try {
      const [summary, forecast, income, expenses] = await Promise.all([
        api('/summary'),
        api('/forecast'),
        api('/income'),
        api('/expenses'),
      ])
      setData({
        summary,
        forecast,
        income: income.items || [],
        expenses: expenses.items || [],
      })
    } catch (error) {
      setMessage(error.message || 'We could not load your money picture. Try again.')
    } finally {
      setLoading(false)
    }
  }, [session])

  useEffect(() => {
    if (!supabase) return undefined
    supabase.auth.getSession()
      .then(({ data: authData }) => setSession(authData.session))
      .catch(() => setMessage('We could not check your account. Check your connection and reload.'))
      .finally(() => setAuthReady(true))
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      setAuthReady(true)
    })
    return () => listener.subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (session) {
      setData({
        summary: { balance_cents: 0, this_week_income_cents: 0, set_aside_progress_cents: 0, set_aside_target_cents: 0, next_shortfall: null },
        forecast: { confidence: 'low', horizon_days: 30, predicted_income_cents: 0, predicted_expenses_cents: 0, shortfall: { likely: false, date: null, amount_cents: 0 }, set_aside: { weekly_cents: 0, reason: 'Add entries to see a set-aside suggestion.' }, explanation: 'Add income and expense entries to build your estimate.', series: [] },
        income: [],
        expenses: [],
      })
      refresh()
    } else {
      setData(sample)
    }
  }, [session, refresh])

  const transactions = useMemo(() => [
    ...(data.income || []).map((item) => ({ ...item, kind: 'income', date: item.received_on, label: item.source || 'Income' })),
    ...(data.expenses || []).map((item) => ({ ...item, kind: 'expense', date: item.spent_on, label: item.category || 'Expense' })),
  ].sort((a, b) => (b.date || '').localeCompare(a.date || '')).slice(0, 5), [data])

  async function signIn(event) {
    event.preventDefault()
    if (!supabase) return
    setLoading(true)
    setMessage('')
    try {
      const result = authMode === 'signup'
        ? await supabase.auth.signUp({ email: authEmail, password: authPassword })
        : await supabase.auth.signInWithPassword({ email: authEmail, password: authPassword })
      if (result.error) setMessage(result.error.message)
      else if (authMode === 'signup' && !result.data.session) {
        setMessage('Check your inbox to confirm your email, then sign in.')
        setAuthMode('signin')
      } else {
        setMessage('You’re signed in. Your private money picture is ready.')
        setPage('home')
      }
    } catch {
      setMessage('We could not reach sign-in. Check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  async function signOut() {
    if (!supabase) return
    const { error } = await supabase.auth.signOut()
    setMessage(error ? error.message : 'You have been signed out.')
    setData(sample)
  }

  async function saveEntry(event) {
    event.preventDefault()
    const cents = Math.round(Number(entryAmount) * 100)
    if (!Number.isFinite(cents) || cents < 1) {
      setMessage('Enter an amount greater than R0.00.')
      return
    }
    const entry = entryKind === 'income'
      ? { amount_cents: cents, source: entryLabel.trim(), received_on: entryDate }
      : { amount_cents: cents, category: entryLabel.trim(), spent_on: entryDate, recurring }
    setLoading(true)
    setMessage('')
    try {
      if (session) {
        await api('/' + (entryKind === 'income' ? 'income' : 'expenses'), { method: 'POST', body: entry })
        await refresh()
        setMessage('Entry saved to your account.')
      } else {
        const id = 'preview-' + Date.now()
        setData((current) => {
          const next = { ...current, income: [...current.income], expenses: [...current.expenses], summary: { ...current.summary } }
          if (entryKind === 'income') {
            next.income.unshift({ ...entry, id })
            next.summary.balance_cents += cents
          } else {
            next.expenses.unshift({ ...entry, id })
            next.summary.balance_cents -= cents
          }
          return next
        })
        setMessage('Added to this sample preview only. Sign in to save entries to your account.')
      }
      setEntryAmount('')
      setEntryLabel('')
      setRecurring(false)
      setPage('home')
    } catch (error) {
      setMessage(error.message || 'Could not save this entry. Try again.')
    } finally {
      setLoading(false)
    }
  }

  async function importCsv(event) {
    event.preventDefault()
    const formElement = event.currentTarget
    const file = formElement.elements.csv.files?.[0]
    if (!file || !session) {
      setMessage('Sign in and choose a CSV file to import income.')
      return
    }
    if (file.size > 2 * 1024 * 1024) {
      setMessage('Choose a CSV file smaller than 2 MB.')
      return
    }
    const form = new FormData()
    form.append('file', file)
    setLoading(true)
    setMessage('')
    try {
      const result = await api('/income/import', { method: 'POST', body: form })
      await refresh()
      setMessage('Imported ' + result.imported + ' entries. ' + result.skipped + ' rows were skipped.')
      formElement.reset()
    } catch (error) {
      setMessage(error.message || 'Could not import that file.')
    } finally {
      setLoading(false)
    }
  }

  function navigate(nextPage) {
    setPage(nextPage)
    setMessage('')
    window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
    window.requestAnimationFrame(() => pageTitleRef.current?.focus({ preventScroll: true }))
  }

  if (!authReady) {
    return (
      <div className="app-shell">
        <a className="skip-link" href="#main-content">Skip to main content</a>
        <header className="topbar"><Brand /></header>
        <main id="main-content" className="main-layout">
          <p className="eyebrow">YOUR MONEY, WITH A PLAN</p>
          <h1 className="loading-heading" tabIndex="-1">Getting your money picture ready.</h1>
          <p className="loading-line" role="status"><span className="spinner" aria-hidden="true" /> Checking your account securely…</p>
        </main>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <header className="topbar" id="home">
        <Brand />
        <div className="topbar__right">
          {preview ? <span className="preview-pill"><span aria-hidden="true" />Sample preview</span> : null}
          <button className="avatar-button" type="button" onClick={() => navigate('settings')} aria-label="Open account settings">
            {session ? profileName.slice(0, 1).toUpperCase() : <Icon name="settings" />}
          </button>
        </div>
      </header>

      {preview ? (
        <div className="preview-notice" role="note">
          <span><strong>Sample preview.</strong> Numbers are fictional and changes are saved only in this browser session.</span>
          {supabase ? <button className="text-button" onClick={() => navigate('settings')} type="button">Sign in to your account <span aria-hidden="true">↗</span></button> : null}
        </div>
      ) : null}

      <main id="main-content" className="main-layout">
        <div className="page-heading">
          <div>
            <p className="eyebrow">YOUR MONEY, WITH A PLAN</p>
            <h1 ref={pageTitleRef} tabIndex="-1">{page === 'home' ? 'A little more breathing room.' : page === 'add' ? 'Put it on the books.' : page === 'forecast' ? 'See what’s coming.' : page === 'savings' ? 'Build your buffer.' : page === 'settings' ? 'Your account.' : 'Your money.'}</h1>
            <p className="page-heading__sub">{page === 'home' ? 'Small moves today can make a tight week easier.' : page === 'add' ? 'Keep the picture honest: add money as it comes and goes.' : page === 'forecast' ? 'A guide from your entries, never a promise.' : page === 'savings' ? 'A steady set-aside can soften an uneven month.' : page === 'settings' ? 'Your data belongs to you.' : ''}</p>
          </div>
          <p className="date-chip"><span className="status-dot" aria-hidden="true" /> Updated {dateLabel(new Date().toISOString().slice(0, 10), { day: 'numeric', month: 'long' })}</p>
        </div>

        {message ? <div className="status-message" role="status" aria-live="polite">{message}<button type="button" aria-label="Dismiss message" onClick={() => setMessage('')}>×</button></div> : null}
        {loading ? <p className="loading-line" role="status"><span className="spinner" aria-hidden="true" /> Updating your money picture…</p> : null}

        {page === 'home' ? (
          <>
            <section className="hero-grid" aria-label="Your money overview">
              <article className="balance-card">
                <div className="balance-card__top">
                  <p className="eyebrow">RECORDED BALANCE</p>
                  <span className="balance-card__icon" aria-hidden="true">↗</span>
                </div>
                <p className="balance-card__value">{amount(data.summary?.balance_cents)}</p>
                <p className="balance-card__caption">From income and expenses you’ve logged</p>
                <button type="button" className="button button--light" onClick={() => navigate('add')}><Icon name="add" /> Add an entry</button>
                <div className="balance-card__orb" aria-hidden="true" />
              </article>

              <article className={'alert-card' + (shortfall?.likely ? '' : ' alert-card--clear')}>
                <div className="alert-card__top"><span className="alert-icon" aria-hidden="true">{shortfall?.likely ? '!' : '✓'}</span><p className="eyebrow">{shortfall?.likely ? 'A HEADS-UP' : 'LOOKING STEADY'}</p></div>
                <h2>{shortfall?.likely ? 'That week could get tight.' : 'No gap showing right now.'}</h2>
                <p className="alert-card__text">{shortfall?.likely ? 'The estimate sees a possible gap around ' + dateLabel(shortfall.date) + '.' : 'Keep logging income and bills so the estimate can keep up.'}</p>
                <div className="alert-card__bottom">
                  <div><span className="eyebrow">ESTIMATED GAP</span><strong>{shortfall?.likely ? amount(shortfall.amount_cents) : '—'}</strong></div>
                  <button type="button" className="button button--dark" onClick={() => navigate('forecast')}>See the forecast <span aria-hidden="true">→</span></button>
                </div>
              </article>
            </section>

            <section className="metrics-grid" aria-label="Recent money">
              <Metric label="This week" value={amount(data.summary?.this_week_income_cents)} hint="Income you’ve recorded" />
              <Metric label="Set aside each week" value={amount(data.forecast?.set_aside?.weekly_cents)} hint="A suggestion, not a guarantee" tone="metric-card--accent" />
              <Metric label="Forecast confidence" value={(data.forecast?.confidence || 'low').toUpperCase()} hint="More history can improve the estimate" />
            </section>

            <section className="content-grid">
              <article className="panel transactions-panel">
                <div className="panel__heading">
                  <div><p className="eyebrow">THE LATEST</p><h2>Money moves</h2></div>
                  <button type="button" className="text-button" onClick={() => navigate('add')}>Add one <span aria-hidden="true">↗</span></button>
                </div>
                {transactions.length ? (
                  <ul className="transaction-list">
                    {transactions.map((item) => (
                      <li className="transaction-row" key={item.id}>
                        <span className={'transaction-icon transaction-icon--' + item.kind} aria-hidden="true">{item.kind === 'income' ? '↑' : '↓'}</span>
                        <span className="transaction-row__label"><strong>{item.label}</strong><small>{dateLabel(item.date)}</small></span>
                        <span className={'transaction-row__amount transaction-row__amount--' + item.kind}>{item.kind === 'income' ? '+' : '−'}{amount(item.amount_cents)}</span>
                      </li>
                    ))}
                  </ul>
                ) : <div className="empty-state"><span aria-hidden="true">✳</span><h3>Your story starts here.</h3><p>Add income or a bill to get a picture that’s yours.</p><button type="button" className="button button--outline" onClick={() => navigate('add')}>Add your first entry</button></div>}
              </article>

              <article className="panel nudge-panel">
                <span className="nudge-icon" aria-hidden="true">✳</span>
                <p className="eyebrow">ONE SMALL MOVE</p>
                <h2>Give your next week a head start.</h2>
                <p>Set aside a little when a payout lands. It can make a slower week feel less sudden.</p>
                <button type="button" className="button button--outline" onClick={() => navigate('savings')}>See your buffer <span aria-hidden="true">→</span></button>
              </article>
            </section>
          </>
        ) : null}

        {page === 'add' ? (
          <section className="panel form-panel">
            <div className="panel__heading">
              <div><p className="eyebrow">QUICK ENTRY</p><h2>What moved?</h2></div>
            </div>
            <div className="segmented" role="group" aria-label="Entry type">
              <button type="button" aria-pressed={entryKind === 'income'} className={entryKind === 'income' ? 'is-active' : ''} onClick={() => { setEntryKind('income'); setEntryLabel('') }}>Money in</button>
              <button type="button" aria-pressed={entryKind === 'expense'} className={entryKind === 'expense' ? 'is-active' : ''} onClick={() => { setEntryKind('expense'); setEntryLabel('') }}>Money out</button>
            </div>
            <form className="entry-form" onSubmit={saveEntry}>
              <label className="field field--amount"><span>Amount</span><span className="amount-input"><span aria-hidden="true">R</span><input required inputMode="decimal" type="number" min="0.01" step="0.01" max="20000000" value={entryAmount} onChange={(event) => setEntryAmount(event.target.value)} placeholder="0.00" aria-describedby="amount-help" /></span><small id="amount-help">Use rands and cents, for example 150.00</small></label>
              <label className="field"><span>{entryKind === 'income' ? 'Where did it come from?' : 'What was it for?'}</span><input required maxLength="120" value={entryLabel} onChange={(event) => setEntryLabel(event.target.value)} placeholder={entryKind === 'income' ? 'Delivery shift, market order…' : 'Transport, rent…'} /></label>
              <label className="field"><span>{entryKind === 'income' ? 'Date received' : 'Date paid'}</span><input required type="date" max={today()} value={entryDate} onChange={(event) => setEntryDate(event.target.value)} /></label>
              {entryKind === 'expense' ? <div className="checkbox-field"><input id="recurring-expense" type="checkbox" checked={recurring} onChange={(event) => setRecurring(event.target.checked)} /><label htmlFor="recurring-expense"><strong>It comes around regularly</strong><small>For example, rent or a monthly phone bill</small></label></div> : null}
              <div className="form-note"><span aria-hidden="true">🔒</span> Your entries stay private to your account. Preview entries are not uploaded.</div>
              <button type="submit" className="button button--primary button--wide" disabled={loading}>Save {entryKind === 'income' ? 'income' : 'expense'} <span aria-hidden="true">→</span></button>
            </form>
            <details className="import-details">
              <summary>Import income from a CSV</summary>
              <p>Use columns <code>amount</code>, <code>source</code>, and <code>received_on</code>. Dates must use YYYY-MM-DD.</p>
              {session ? <form onSubmit={importCsv} className="import-form"><label className="field"><span>Choose a CSV file</span><input required name="csv" type="file" accept=".csv,text/csv" /></label><button className="button button--outline" type="submit" disabled={loading}>Import income</button></form> : <p className="muted-note">Sign in to import entries to your account.</p>}
            </details>
          </section>
        ) : null}

        {page === 'forecast' ? (
          <section className="forecast-page">
            <article className="panel forecast-summary">
              <div className="panel__heading"><div><p className="eyebrow">NEXT {data.forecast?.horizon_days || 30} DAYS</p><h2>{shortfall?.likely ? 'Plan for a possible lean week.' : 'Your estimate looks balanced.'}</h2></div><span className="confidence-pill">Confidence: {data.forecast?.confidence || 'low'}</span></div>
              <p className="forecast-explanation">{data.forecast?.explanation}</p>
              <div className="forecast-totals">
                <div><span className="eyebrow">EXPECTED INCOME</span><strong>{amount(data.forecast?.predicted_income_cents)}</strong></div>
                <div><span className="eyebrow">KNOWN COSTS</span><strong>{amount(data.forecast?.predicted_expenses_cents)}</strong></div>
                <div className="forecast-totals__gap"><span className="eyebrow">POSSIBLE GAP</span><strong>{shortfall?.likely ? amount(shortfall.amount_cents) : 'None seen'}</strong></div>
              </div>
              {shortfall?.likely ? <div className="set-aside-callout"><span className="set-aside-callout__icon" aria-hidden="true">↗</span><div><strong>{amount(data.forecast?.set_aside?.weekly_cents)} a week could help build a buffer.</strong><p>{data.forecast?.set_aside?.reason}</p></div></div> : null}
              <p className="disclaimer">This is an estimate from the entries you’ve recorded. It is not financial advice and cannot guarantee what you’ll earn or spend.</p>
            </article>
            <article className="panel chart-panel">
              <div className="panel__heading"><div><p className="eyebrow">WEEK BY WEEK</p><h2>Income outlook</h2></div><span className="chart-key"><span aria-hidden="true" /> Estimated income</span></div>
              <ol className="income-chart" aria-label="Estimated weekly income">
                {(data.forecast?.series || []).map((week, index) => {
                  const values = data.forecast.series.map((item) => item.upper_cents || item.predicted_income_cents || item.amount_cents || 0)
                  const max = Math.max(...values, 1)
                  const value = week.predicted_income_cents ?? week.amount_cents ?? 0
                  const lower = week.lower_cents ?? Math.round(value * 0.5)
                  const upper = week.upper_cents ?? Math.round(value * 1.5)
                  return <li key={week.week_start} className="income-chart__week"><span className="income-chart__amount">{amount(value)}</span><div className="income-chart__track" aria-hidden="true"><span className="income-chart__range" style={{ bottom: (lower / max * 100) + '%', height: Math.max(3, (upper - lower) / max * 100) + '%' }} /><span className="income-chart__bar" style={{ height: Math.max(2, value / max * 100) + '%' }} /></div><span className="income-chart__date">Week {index + 1}<small>{dateLabel(week.week_start)}</small><span className="sr-only">Estimated range {amount(lower)} to {amount(upper)}</span></span></li>
                })}
              </ol>
              <p className="chart-note">The shaded band shows a possible range. Real income can land above or below this estimate.</p>
            </article>
          </section>
        ) : null}

        {page === 'savings' ? (
          <section className="panel savings-panel">
            <p className="eyebrow">YOUR WEEKLY BUFFER</p>
            <h2>A small cushion, built at your pace.</h2>
            <p className="savings-panel__lead">From the current estimate, setting aside <strong>{amount(data.forecast?.set_aside?.weekly_cents)}</strong> each week could help cover the next possible gap.</p>
            <div className="buffer-progress"><div><span>Progress tracker</span><span>Not yet connected</span></div><div className="progress-track" aria-hidden="true"><span /></div></div>
            <p className="muted-note">A savings tracker is not live yet. We won’t show a progress number until real set-aside entries can be tracked.</p>
            <button type="button" className="button button--primary" onClick={() => navigate('add')}>Log a payout <span aria-hidden="true">→</span></button>
          </section>
        ) : null}

        {page === 'settings' ? (
          <section className="panel settings-panel">
            <div className="settings-avatar" aria-hidden="true">{session ? profileName.slice(0, 1).toUpperCase() : 'b'}</div>
            <p className="eyebrow">ACCOUNT & PRIVACY</p>
            <h2>{session ? 'Good to see you, ' + profileName + '.' : 'Your money stays yours.'}</h2>
            {supabase ? session ? <><p className="settings-email">{session.user.email}</p><button type="button" className="button button--outline" onClick={signOut}>Sign out</button></> : (
              <form className="auth-form" onSubmit={signIn}>
                <p>{authMode === 'signup' ? 'Create an account to save your entries privately.' : 'Sign in to see your private dashboard.'}</p>
                <label className="field"><span>Email address</span><input required type="email" autoComplete="email" value={authEmail} onChange={(event) => setAuthEmail(event.target.value)} /></label>
                <label className="field"><span>Password</span><input required type="password" minLength="8" autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'} value={authPassword} onChange={(event) => setAuthPassword(event.target.value)} /></label>
                <button type="submit" className="button button--primary button--wide" disabled={loading}>{authMode === 'signup' ? 'Create account' : 'Sign in'}</button>
                <button type="button" className="text-button auth-toggle" onClick={() => setAuthMode(authMode === 'signup' ? 'signin' : 'signup')}>{authMode === 'signup' ? 'Already have an account? Sign in' : 'New to Boloka? Create an account'}</button>
              </form>
            ) : <p className="settings-email">Account sign-in will be available when the team connects the Supabase project.</p>}
            <div className="privacy-note"><strong>Private by design</strong><p>Boloka never asks for your bank password. Your entries are protected by account sign-in and row-level security.</p></div>
          </section>
        ) : null}
      </main>

      <nav className="bottom-nav" aria-label="Main navigation">
        {[
          ['home', 'Home', 'home'],
          ['add', 'Add', 'add'],
          ['forecast', 'Forecast', 'forecast'],
          ['savings', 'Savings', 'savings'],
        ].map(([target, label, icon]) => (
          <button key={target} type="button" onClick={() => navigate(target)} className={page === target ? 'nav-item is-current' : 'nav-item'} aria-current={page === target ? 'page' : undefined}>
            <Icon name={icon} /><span>{label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}

export default App
