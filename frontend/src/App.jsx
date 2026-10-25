import React, { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, supabase } from './lib/client'
import { supportedLanguages, translate as t } from './lib/copy'
import { createPreview } from './lib/sample'
import { updatePreview, changeTransaction, exportRecords } from './lib/transactions'
import TransactionList from './components/TransactionList'
import ForecastExplanation from './components/ForecastExplanation'
import TransactionEditor from './screens/TransactionEditor'
import { emptyAccountData } from './lib/account-data'
import { formatMoney, formatDate, today } from './lib/format'

const ForecastChart = lazy(() => import('./components/ForecastChart.jsx'))


const currentLanguage = () => {
  try {
    const saved = localStorage.getItem('boloka-language')
    return ['en', 'zu', 'st'].includes(saved) ? saved : 'en'
  } catch { return 'en' }
}

const dashboardStepActions = {
  record_income: { copyKey: 'nextRecordIncome', target: 'income' },
  add_upcoming_costs: { copyKey: 'nextAddCosts', target: 'expense' },
  review_overlapping_costs: { copyKey: 'nextReviewCosts', target: 'forecast' },
  check_available_cash: { copyKey: 'nextCheckCash', target: 'forecast' },
}

function dashboardNextAction(forecast) {
  const nextStep = forecast?.next_steps?.find(step => dashboardStepActions[step])
  if (nextStep) return dashboardStepActions[nextStep]

  if (forecast?.shortfall?.status === 'planning_gap') {
    return { copyKey: 'nextReviewGap', target: 'forecast' }
  }
  if (forecast?.shortfall?.status === 'no_gap_in_estimate') {
    return { copyKey: 'nextReviewEstimate', target: 'forecast' }
  }
  return { copyKey: 'nextRecordIncome', target: 'income' }
}

function Brand({ compact = false, language = 'en' }) {
  const tr = (key, vars) => t(language, key, vars)
  return (
    <a className={'brand' + (compact ? ' brand--compact' : '')} href="#home" aria-label={tr('bolokaHome')}>
      <span className="brand__mark" aria-hidden="true">b</span>
      <span className="brand__word">{tr('boloka')}</span>
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
  const [editingEntry, setEditingEntry] = useState(null)
  const [editError, setEditError] = useState('')
  const [showAllTransactions, setShowAllTransactions] = useState(false)
  const requestVersion = useRef(0)
  const activeUser = useRef(null)
  const [cashInput, setCashInput] = useState('')
  const [session, setSession] = useState(null)
  const [authReady, setAuthReady] = useState(!supabase)
  const [page, setPage] = useState(() => {
    try { return localStorage.getItem('boloka-onboarding-complete') ? 'home' : 'onboarding' } catch { return 'onboarding' }
  })
  const [data, setData] = useState(() => createPreview(today()))
  const [loading, setLoading] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)
  const [loadError, setLoadError] = useState(false)
  const [message, setMessage] = useState('')
  const [csvErrors, setCsvErrors] = useState([])
  const [online, setOnline] = useState(typeof navigator === 'undefined' ? true : navigator.onLine)
  const [language, setLanguage] = useState(currentLanguage)
  const [dataSaver, setDataSaver] = useState(() => {
    try { return localStorage.getItem('boloka-data-saver') === 'true' || Boolean(navigator.connection?.saveData) } catch { return false }
  })
  const [highContrast, setHighContrast] = useState(() => {
    try { return localStorage.getItem('boloka-high-contrast') === 'true' } catch { return false }
  })
  const [largerText, setLargerText] = useState(() => {
    try { return localStorage.getItem('boloka-larger-text') === 'true' } catch { return false }
  })
  const [authMode, setAuthMode] = useState('signin')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [entryKind, setEntryKind] = useState('income')
  const [entryAmount, setEntryAmount] = useState('')
  const [entryLabel, setEntryLabel] = useState('')
  const [entryDate, setEntryDate] = useState(today)
  const [recurring, setRecurring] = useState(false)
  const [savingAmount, setSavingAmount] = useState('')
  const [savingNote, setSavingNote] = useState('')
  const [savingDate, setSavingDate] = useState(today)
  const pageTitleRef = useRef(null)

  const tr = (key, vars) => t(language, key, vars)
  const amount = cents => formatMoney(cents, language)
  const dateLabel = (value, options) => formatDate(value, language, options)
  const preview = !session
  const profileName = session?.user?.email?.split('@')[0] || 'friend'
  const shortfall = data.forecast?.shortfall
  const hasGap = !preview && shortfall?.status === 'planning_gap'
  const homeAction = preview ? null : dashboardNextAction(data.forecast)
  const cashExplanation = data.forecast?.available_balance_cents != null ? tr('cashScenarioUsed', { amount: amount(data.forecast.available_balance_cents) }) : tr('cashAssumption')

  useEffect(() => {
    const updateOnline = () => setOnline(navigator.onLine)
    window.addEventListener('online', updateOnline)
    window.addEventListener('offline', updateOnline)
    return () => {
      window.removeEventListener('online', updateOnline)
      window.removeEventListener('offline', updateOnline)
    }
  }, [])

  useEffect(() => {
    document.documentElement.lang = language === 'zu' ? 'zu' : language === 'st' ? 'st' : 'en'
    try { localStorage.setItem('boloka-language', language) } catch { /* Language still works for this session. */ }
  }, [language])

  useEffect(() => {
    document.documentElement.dataset.contrast = highContrast ? 'high' : 'normal'
    try { localStorage.setItem('boloka-high-contrast', String(highContrast)) } catch { /* Preference still works for this session. */ }
  }, [highContrast])

  useEffect(() => {
    document.documentElement.dataset.textSize = largerText ? 'large' : 'normal'
    try { localStorage.setItem('boloka-larger-text', String(largerText)) } catch { /* Preference still works for this session. */ }
  }, [largerText])

  function completeOnboarding() {
    try { localStorage.setItem('boloka-onboarding-complete', 'true') } catch { /* Continue without local persistence. */ }
  }

  function changeDataSaver(enabled) {
    setDataSaver(enabled)
    try { localStorage.setItem('boloka-data-saver', String(enabled)) } catch { /* Preference remains active for this session. */ }
  }

  const refresh = useCallback(async () => {
    if (!session || activeUser.current !== session.user.id) return false
    const version = ++requestVersion.current
    setLoading(true)
    setLoadError(false)
    setMessage('')
    try {
      const [summary, forecast, income, expenses, savings] = await Promise.all([
        api('/summary', { accessToken: session.access_token }),
        api('/forecast', { accessToken: session.access_token }),
        api('/income', { accessToken: session.access_token }),
        api('/expenses', { accessToken: session.access_token }),
        api('/savings', { accessToken: session.access_token }),
      ])
      if (version !== requestVersion.current) return false
      setData({
        summary,
        forecast,
        income: income.items || [],
        expenses: expenses.items || [],
        savings: savings.items || [],
      })
      setCashInput('')
      return true
    } catch {
      if (version !== requestVersion.current) return false
      setLoadError(true)
      return false
    } finally {
      if (version === requestVersion.current) { setLoading(false); setHasLoaded(true) }
    }
  }, [session])

  useEffect(() => {
    if (!supabase) return undefined
    supabase.auth.getSession()
      .then(({ data: authData }) => {
        if (requestVersion.current) return
        activeUser.current = authData.session?.user.id || null
        setData(authData.session ? emptyAccountData() : createPreview(today()))
        setSession(authData.session)
      })
      .catch(() => setMessage(tr('weCouldNotCheckYourAccountCheckYour')))
      .finally(() => setAuthReady(true))
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      requestVersion.current += 1
      const identity = nextSession?.user.id || null
      if (identity !== activeUser.current) {
        setData(nextSession ? emptyAccountData() : createPreview(today()))
        setEditingEntry(null)
        setEntryAmount('')
        setEntryLabel('')
        setSavingAmount('')
        setSavingNote('')
        setCsvErrors([])
        setAuthPassword('')
        setCashInput('')
      }
      activeUser.current = identity
      setSession(nextSession)
      setAuthReady(true)
    })
    return () => listener.subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (session) {
      setHasLoaded(false)
      setData(emptyAccountData())
      refresh()
    } else {
      setData(createPreview(today()))
      setHasLoaded(true)
    }
  }, [session, refresh])

  const transactions = useMemo(() => [
    ...(data.income || []).map((item) => ({ ...item, kind: 'income', date: item.received_on, label: item.source || tr('income') })),
    ...(data.expenses || []).map((item) => ({ ...item, kind: 'expense', date: item.spent_on, label: item.category || tr('expense') })),
  ].sort((a, b) => (b.date || '').localeCompare(a.date || '')), [data, language])

  async function signIn(event) {
    event.preventDefault()
    if (!supabase) return
    setLoading(true)
    setMessage('')
    try {
      const result = authMode === 'signup'
        ? await supabase.auth.signUp({ email: authEmail, password: authPassword })
        : await supabase.auth.signInWithPassword({ email: authEmail, password: authPassword })
      if (result.error) setMessage(tr('signInFailed'))
      else if (authMode === 'signup' && !result.data.session) {
        setMessage(tr('checkYourInboxToConfirmYourEmailThen'))
        setAuthMode('signin')
      } else {
        setMessage(tr('youReSignedInYourPrivateMoneyPicture'))
        setPage('home')
      }
    } catch {
      setMessage(tr('weCouldNotReachSignInCheckYour'))
    } finally {
      setLoading(false)
    }
  }

  async function signOut() {
    if (!supabase) return
    requestVersion.current += 1
    const { error } = await supabase.auth.signOut()
    setMessage(error ? tr('signOutFailed') : tr('youHaveBeenSignedOut'))
    if (!error) {
      setData(createPreview(today()))
      setPage('home')
    }
  }

  async function saveEntry(event) {
    event.preventDefault()
    const cents = Math.round(Number(entryAmount) * 100)
    if (!Number.isSafeInteger(cents) || cents < 1 || cents > 2000000000) {
      setMessage(tr('enterAnAmountGreaterThanR000'))
      return
    }
    const entry = entryKind === 'income'
      ? { amount_cents: cents, source: entryLabel.trim(), received_on: entryDate }
      : { amount_cents: cents, category: entryLabel.trim(), spent_on: entryDate, recurring }
    setLoading(true)
    setMessage('')
    try {
      if (session) {
        if (!online) throw new Error(tr('youAreOfflineReconnectBeforeSavingToYour'))
        await api('/' + (entryKind === 'income' ? 'income' : 'expenses'), { method: 'POST', body: entry, accessToken: session.access_token })
        if (activeUser.current !== session.user.id) return
        await refresh()
        setMessage(tr('entrySavedToYourAccount'))
      } else {
        completeOnboarding()
        setData(current => updatePreview(current, entryKind === 'income' ? 'income' : 'expenses', null, entry, today()))
        setMessage(tr('addedToThisSamplePreviewOnlySignIn'))
      }
      completeOnboarding()
      setEntryAmount('')
      setEntryLabel('')
      setRecurring(false)
      setPage('home')
    } catch {
      setMessage(tr('couldNotSaveThisEntryTryAgain'))
    } finally {
      setLoading(false)
    }
  }

  async function saveContribution(event) {
    event.preventDefault()
    const cents = Math.round(Number(savingAmount) * 100)
    if (!Number.isSafeInteger(cents) || cents < 1) {
      setMessage(tr('enterAnAmountGreaterThanR000'))
      return
    }
    const contribution = { amount_cents: cents, saved_on: savingDate, note: savingNote.trim() || null }
    setLoading(true)
    setMessage('')
    try {
      if (session) {
        if (!online) throw new Error(tr('youAreOfflineReconnectBeforeSavingThisContribution'))
        await api('/savings', { method: 'POST', body: contribution, accessToken: session.access_token })
        if (activeUser.current !== session.user.id) return
        await refresh()
        setMessage(tr('yourSetAsideWasAddedToThisMonth'))
      } else {
        setData(current => updatePreview(current, 'savings', null, contribution, today()))
        setMessage(tr('addedToThisSamplePreviewOnlySignIn2'))
      }
      setSavingAmount('')
      setSavingNote('')
    } catch {
      setMessage(tr('couldNotSaveThatSetAsideTryAgain'))
    } finally {
      setLoading(false)
    }
  }

  async function removeContribution(item) {
    if (!window.confirm(tr('confirmDelete', { label: item.note || tr('navSavings'), amount: amount(item.amount_cents), date: dateLabel(item.saved_on) }))) return
    try {
      if (session) {
        if (!online) throw new Error(tr('youAreOfflineReconnectBeforeRemovingThisContribution'))
        await api('/savings/' + encodeURIComponent(item.id), { method: 'DELETE', accessToken: session.access_token })
        if (activeUser.current !== session.user.id) return
        await refresh()
      } else {
        setData(current => updatePreview(current, 'savings', item.id, null, today()))
      }
      setMessage(tr('setAsideRemoved'))
    } catch {
      setMessage(tr('couldNotRemoveThatSetAsideTryAgain'))
    }
  }

  async function importCsv(event) {
    event.preventDefault()
    setCsvErrors([])
    const formElement = event.currentTarget
    const file = formElement.elements.csv.files?.[0]
    if (!file || !session) {
      setMessage(tr('signInAndChooseACsvFileTo'))
      return
    }
    if (file.size > 2 * 1024 * 1024) {
      setMessage(tr('chooseACsvFileSmallerThan2Mb'))
      return
    }
    const form = new FormData()
    form.append('file', file)
    setLoading(true)
    setMessage('')
    try {
      if (!online) throw new Error(tr('youAreOfflineReconnectBeforeImportingToYour'))
      const result = await api('/income/import', { method: 'POST', body: form, accessToken: session.access_token })
      if (activeUser.current !== session.user.id) return
      await refresh()
      setMessage(tr('importResult', result))
      setCsvErrors(result.errors || [])
      formElement.reset()
    } catch {
      setMessage(tr('couldNotImportThatFile'))
    } finally {
      setLoading(false)
    }
  }

  async function changeEntry(item, entry) {
    const resource = item.kind === 'income' ? 'income' : 'expenses'
    if (!entry && !window.confirm(tr('confirmDelete', { label: item.label, amount: amount(item.amount_cents), date: dateLabel(item.date) }))) return
    setLoading(true)
    setEditError('')
    try {
      if (session && !online) throw new Error(tr('offlineBody'))
      const next = await changeTransaction({ preview, data, resource, id: item.id, entry, today: today(),
        send: (path, options) => api(path, { ...options, accessToken: session?.access_token }) })
      if (session && activeUser.current !== session.user.id) return
      if (next) setData(next)
      else if (!await refresh()) { setEditingEntry(null); setMessage(tr('savedReloadFailed')); return }
      setEditingEntry(null)
      window.requestAnimationFrame(() => pageTitleRef.current?.focus())
      setMessage(tr(entry ? 'entryCorrected' : 'entryDeleted'))
    } catch {
      const text = tr('entryChangeFailed')
      setEditError(text)
      setMessage(text)
    } finally { setLoading(false) }
  }

  async function applyCashScenario(event) {
    event.preventDefault()
    if (preview) return
    const cents = cashInput === '' ? null : Math.round(Number(cashInput) * 100)
    const version = requestVersion.current
    setLoading(true)
    try {
      const forecast = await api('/forecast/scenario', { method: 'POST', body: { available_balance_cents: cents }, accessToken: session.access_token })
      if (version === requestVersion.current) setData(current => ({ ...current, forecast }))
    } catch { setMessage(tr('cashScenarioFailed')) }
    finally { setLoading(false) }
  }

  function downloadRecords() {
    const blob = new Blob([JSON.stringify(exportRecords(data, preview, today()), null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'boloka-records-' + today() + '.json'
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  function navigate(nextPage) {
    setEditingEntry(null)
    setEditError('')
    if (page === 'onboarding' && nextPage !== 'onboarding') completeOnboarding()
    setPage(nextPage)
    setMessage('')
    window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
    window.requestAnimationFrame(() => pageTitleRef.current?.focus({ preventScroll: true }))
  }

  if (!authReady) {
    return (
      <div className="app-shell">
        <a className="skip-link" href="#main-content">{tr('skipToMainContent')}</a>
        <header className="topbar"><Brand language={language} /></header>
        <main id="main-content" className="main-layout">
          <p className="eyebrow">{t(language, 'onboardingEyebrow')}</p>
          <h1 className="loading-heading" tabIndex="-1">{tr('gettingYourMoneyPictureReady')}</h1>
          <p className="loading-line" role="status"><span className="spinner" aria-hidden="true" /> {tr('checkingYourAccountSecurely')}</p>
        </main>
      </div>
    )
  }

  return (
    <div className={'app-shell' + (page === 'onboarding' ? ' app-shell--onboarding' : '') + (page === 'add' ? ' app-shell--entry' : '')}>
      <a className="skip-link" href="#main-content">{tr('skipToMainContent')}</a>
      <header className="topbar" id="home">
        <Brand language={language} />
        <div className="topbar__right">
          {preview ? <span className="preview-pill"><span aria-hidden="true" />{t(language, 'previewLabel')}</span> : null}
          <button className="avatar-button" type="button" onClick={() => navigate('settings')} aria-label={tr('openAccountSettings')}>
            {session ? profileName.slice(0, 1).toUpperCase() : <Icon name="settings" />}
          </button>
        </div>
      </header>

      {preview ? (
        <div className="preview-notice" role="note">
          <span>{t(language, 'previewNotice')}</span>
          {supabase ? <button className="text-button" onClick={() => navigate('settings')} type="button">{tr('signInToYourAccount')} <span aria-hidden="true">↗</span></button> : null}
        </div>
      ) : null}

      <main id="main-content" className="main-layout">
        {language !== 'en' ? <p className="connection-banner" lang="en">{tr('translationReview')}</p> : null}
        {!online ? <div className="connection-banner" role="status"><strong>{t(language, 'offlineTitle')}</strong> {t(language, 'offlineBody')}</div> : null}
        {online && !preview && page === 'home' && !hasLoaded ? <section className="panel dashboard-skeleton" aria-label={tr('loadingDashboard')} aria-busy="true"><span className="skeleton skeleton--wide" /><span className="skeleton" /><span className="skeleton" /><p className="sr-only" role="status">{tr('loadingYourMoneyPicture')}</p></section> : null}
        {online && loadError && session ? <div className="error-banner" role="alert"><span>{tr('weCouldnTRefreshYourAccountData')}</span><button type="button" className="button button--outline" onClick={refresh} disabled={loading}>{t(language, 'retry')}</button></div> : null}
        {page !== 'onboarding' ? <div className="page-heading">
          <div>
            <p className="eyebrow">{t(language, 'onboardingEyebrow')}</p>
            <h1 ref={pageTitleRef} tabIndex="-1">{page === 'home' ? t(language, 'homeTitle') : page === 'add' ? t(language, 'addTitle') : page === 'forecast' ? t(language, 'forecastTitle') : page === 'savings' ? t(language, 'savingsTitle') : page === 'settings' ? t(language, 'settingsTitle') : t(language, 'onboardingTitle')}</h1>
            <p className="page-heading__sub">{page === 'home' ? t(language, 'homeSubtitle') : page === 'add' ? t(language, 'addSubtitle') : page === 'forecast' ? t(language, 'forecastSubtitle') : page === 'savings' ? t(language, 'savingsSubtitle') : page === 'settings' ? t(language, 'settingsSubtitle') : ''}</p>
          </div>
          <p className="date-chip"><span className="status-dot" aria-hidden="true" /> {tr('recordedDates')}</p>
        </div> : null}

        {message ? <div className="status-message" role="status" aria-live="polite">{message}<button type="button" aria-label={tr('dismissMessage')} onClick={() => setMessage('')}>×</button></div> : null}
        {loading ? <p className="loading-line" role="status"><span className="spinner" aria-hidden="true" /> {tr('updatingYourMoneyPicture')}</p> : null}

        {page === 'onboarding' ? (
          <section className="panel onboarding-panel" aria-labelledby="onboarding-title">
            <p className="eyebrow">{t(language, 'onboardingEyebrow')}</p>
            <h2 id="onboarding-title">{t(language, 'onboardingTitle')}</h2>
            <p className="onboarding-panel__lead">{tr('planningIntro')}</p>
            <ol className="onboarding-steps">
              <li><span aria-hidden="true">1</span>{t(language, 'onboardingStepOne')}</li>
              <li><span aria-hidden="true">2</span>{t(language, 'onboardingStepTwo')}</li>
              <li><span aria-hidden="true">3</span>{t(language, 'onboardingStepThree')}</li>
            </ol>
            <div className="onboarding-actions">
              <button type="button" className="button button--primary" onClick={() => { setEntryKind('income'); setPage('add') }}>{t(language, 'onboardingStart')} <span aria-hidden="true">→</span></button>
              <button type="button" className="button button--outline" onClick={() => { completeOnboarding(); setPage('home') }}>{t(language, 'onboardingPreview')}</button>
              {supabase ? <button type="button" className="text-button" onClick={() => { completeOnboarding(); setPage('settings') }}>{t(language, 'onboardingSignIn')}</button> : null}
            </div>
          </section>
        ) : null}

        {editingEntry ? <TransactionEditor key={editingEntry.id} item={editingEntry} onSave={entry => changeEntry(editingEntry, entry)} onCancel={() => { const id = 'entry-edit-' + editingEntry.kind + editingEntry.id; setEditingEntry(null); setEditError(''); window.requestAnimationFrame(() => document.getElementById(id)?.focus()) }} busy={loading} error={editError} tr={tr} amount={amount} dateLabel={dateLabel} /> : null}

        {page === 'home' && !editingEntry ? (
          <>
            <section className="hero-grid" aria-label={tr('yourMoneyOverview')}>
              <article className="balance-card">
                <div className="balance-card__top">
                  <p className="eyebrow">{tr('recordedBalance')}</p>
                  <span className="balance-card__icon" aria-hidden="true">↗</span>
                </div>
                <p className="balance-card__value">{amount(data.summary?.balance_cents)}</p>
                <p className="balance-card__caption">{tr('fromIncomeAndExpensesYouVeLogged')}</p>
                <button type="button" className="button button--light" onClick={() => navigate('add')}><Icon name="add" /> {t(language, 'addEntry')}</button>
                <div className="balance-card__orb" aria-hidden="true" />
              </article>

              <article className={'alert-card' + (hasGap ? '' : ' alert-card--clear')}>
                <div className="alert-card__top"><span className="alert-icon" aria-hidden="true">{hasGap ? '!' : '✓'}</span><p className="eyebrow">{tr('planningEstimate')}</p></div>
                <h2>{preview ? tr('sampleRecommendation') : hasGap ? tr('conditionalGap') : tr('checkInputs')}</h2>
                <p className="alert-card__text">{preview ? tr('sampleForecastStatic') : cashExplanation}</p>
                <div className="alert-card__bottom">
                  <div><span className="eyebrow">{tr('estimatedGap')}</span><strong>{hasGap ? amount(shortfall.amount_cents) : '—'}</strong></div>
                  <button type="button" className="button button--dark" onClick={() => navigate('forecast')}>{t(language, 'showForecast')} <span aria-hidden="true">→</span></button>
                </div>
              </article>
            </section>

            <section className="metrics-grid" aria-label={tr('recentMoney')}>
              <Metric label={tr('thisWeek')} value={amount(data.summary?.this_week_income_cents)} hint={tr('incomeYouVeRecorded')} />
              <Metric label={tr('setAsideEachWeek')} value={!preview && shortfall?.status === 'insufficient_data' ? tr('notEstablished') : amount(data.forecast?.set_aside?.weekly_cents)} hint={tr(preview ? 'sampleReference' : 'conditionalSuggestion')} tone="metric-card--accent" />
              <Metric label={tr('forecastConfidence')} value={tr('unvalidated')} hint={tr('incompleteHistory')} />
            </section>

            <section className="content-grid">
              <article className="panel transactions-panel">
                <div className="panel__heading">
                  <div><p className="eyebrow">{tr('theLatest')}</p><h2>{tr('moneyMoves')}</h2></div>
                  <button type="button" className="text-button" onClick={() => navigate('add')}>{tr('addOne')} <span aria-hidden="true">↗</span></button>
                </div>
                {transactions.length ? (
                  <>
                    <TransactionList items={showAllTransactions ? transactions : transactions.slice(0, 5)} amount={amount} dateLabel={dateLabel} tr={tr} busy={loading} onEdit={item => { setEditingEntry(item); setEditError('') }} onDelete={item => changeEntry(item, null)} />
                    <button type="button" className="text-button" onClick={() => setShowAllTransactions(value => !value)}>{tr(showAllTransactions ? 'showRecent' : 'showLoadedEntries')}</button>
                  </>
                ) : <div className="empty-state"><span aria-hidden="true">✳</span><h3>{tr('yourStoryStartsHere')}</h3><p>{tr('addIncomeOrABillToGetA')}</p><button type="button" className="button button--outline" onClick={() => navigate('add')}>{t(language, 'firstEntry')}</button></div>}
              </article>

              <article className="panel nudge-panel">
                <span className="nudge-icon" aria-hidden="true">✳</span>
                <p className="eyebrow">{tr('oneSmallMove')}</p>
                <h2>{tr(homeAction ? 'startNextSteps' : 'giveYourNextWeekAHeadStart')}</h2>
                <p>{tr(homeAction?.copyKey || 'setAsideALittleWhenAPayoutLands')}</p>
                <button type="button" className="button button--outline" onClick={() => {
                  if (homeAction?.target === 'income' || homeAction?.target === 'expense') {
                    setEntryKind(homeAction.target)
                    navigate('add')
                  } else if (homeAction) navigate('forecast')
                  else navigate('savings')
                }}>{homeAction?.target === 'income' || homeAction?.target === 'expense' ? tr('addEntry') : homeAction ? tr('showForecast') : tr('seeYourBuffer')} <span aria-hidden="true">→</span></button>
              </article>
            </section>
          </>
        ) : null}

        {page === 'add' ? (
          <section className="panel form-panel">
            <div className="panel__heading">
              <div><p className="eyebrow">{tr('quickEntry')}</p><h2>{tr('whatMoved')}</h2></div>
            </div>
            <div className="segmented" role="group" aria-label={tr('entryType')}>
              <button type="button" aria-pressed={entryKind === 'income'} className={entryKind === 'income' ? 'is-active' : ''} onClick={() => { setEntryKind('income'); setEntryLabel('') }}>{tr('moneyIn')}</button>
              <button type="button" aria-pressed={entryKind === 'expense'} className={entryKind === 'expense' ? 'is-active' : ''} onClick={() => { setEntryKind('expense'); setEntryLabel('') }}>{tr('moneyOut')}</button>
            </div>
            <form className="entry-form" onSubmit={saveEntry}>
              <label className="field field--amount"><span id="entry-amount-label">{t(language, 'amount')}</span><span className="amount-input"><span aria-hidden="true">R</span><input required inputMode="decimal" type="number" min="0.01" step="0.01" max="20000000" value={entryAmount} onChange={(event) => setEntryAmount(event.target.value)} placeholder="0.00" aria-labelledby="entry-amount-label" aria-describedby="amount-help" /></span><small id="amount-help">{tr('useRandsAndCentsForExample15000')}</small></label>
              <label className="field"><span>{entryKind === 'income' ? t(language, 'incomeSource') : t(language, 'expenseCategory')}</span><input required maxLength="120" value={entryLabel} onChange={(event) => setEntryLabel(event.target.value)} placeholder={entryKind === 'income' ? tr('deliveryShiftMarketOrder') : tr('transportRent')} /></label>
              <label className="field"><span>{entryKind === 'income' ? t(language, 'receivedDate') : t(language, 'expenseDate')}</span><input required type="date" max={entryKind === 'income' ? today() : undefined} value={entryDate} onChange={(event) => setEntryDate(event.target.value)} /></label>
              {entryKind === 'expense' ? <p className="muted-note">{tr('dateHelp')}</p> : null}
              {entryKind === 'expense' ? <div className="checkbox-field"><input id="recurring-expense" type="checkbox" checked={recurring} onChange={(event) => setRecurring(event.target.checked)} /><label htmlFor="recurring-expense"><strong>{t(language, 'recurring')}</strong><small>{tr('forExampleRentOrAMonthlyPhoneBill')}</small></label></div> : null}
              <div className="form-note"><span aria-hidden="true">🔒</span> {tr('yourEntriesStayPrivateToYourAccountPreview')}</div>
              <button type="submit" className="button button--primary button--wide" disabled={loading}>{entryKind === 'income' ? t(language, 'saveIncome') : t(language, 'saveExpense')} <span aria-hidden="true">→</span></button>
            </form>
            <details className="import-details">
              <summary>{tr('importIncomeFromACsv')}</summary>
              <p>{tr('csvInstructions')}</p>
              <p>{tr('csvImportLimits')}</p>
              {csvErrors.length ? <section aria-label={tr('csvErrors')}><h3>{tr('csvErrors')}</h3><ol lang="en">{csvErrors.map(error => <li key={error.line}>{t('en', 'csvRowError', error)}</li>)}</ol></section> : null}
              {session ? <form onSubmit={importCsv} className="import-form"><label className="field"><span>{tr('chooseACsvFile')}</span><input required name="csv" type="file" accept=".csv,text/csv" /></label><button className="button button--outline" type="submit" disabled={loading}>{tr('importIncome')}</button></form> : <p className="muted-note">{tr('signInToImportEntriesToYourAccount')}</p>}
            </details>
          </section>
        ) : null}

        {page === 'forecast' ? (
          <section className="forecast-page">
            <article className="panel forecast-summary">
              <div className="panel__heading"><div><p className="eyebrow">{tr('forecastPeriod', { days: data.forecast?.horizon_days || 30 })}</p><h2>{preview ? tr('sampleRecommendation') : tr('planningEstimate')}</h2></div><span className="confidence-pill">{tr('unvalidated')}</span></div>
              <p className="forecast-explanation">{preview ? tr('sampleForecastStatic') : tr('forecastMethod', { weeks: data.forecast?.history_weeks || 0, days: data.forecast?.expense_history_days || 0 })}</p>
              {!preview ? <ForecastExplanation forecast={data.forecast} language={language} /> : null}
              {!preview ? <form className="cash-scenario" onSubmit={applyCashScenario}><label className="field"><span>{tr('cashScenario')}</span><input type="number" min="0" max="20000000" step="0.01" inputMode="decimal" value={cashInput} onChange={event => setCashInput(event.target.value)} /></label><p>{tr('cashScenarioHelp')}</p><button type="submit" className="button button--outline" disabled={loading}>{tr('applyCashScenario')}</button></form> : null}
              {!preview && data.forecast?.costs_overlap_possible ? <p role="note" className="muted-note">{tr('spendingOverlap')}</p> : null}
              <ul className="forecast-assumptions"><li>{data.forecast?.available_balance_cents != null ? tr('cashScenarioUsed', { amount: amount(data.forecast.available_balance_cents) }) : tr('cashAssumption')}</li><li>{tr('spendingAssumption')}</li><li>{tr('recurringAssumption')}</li><li>{tr('forecastTiming')}</li><li>{tr('incompleteHistory')}</li></ul>
              <div className="forecast-totals">
                <div><span className="eyebrow">{tr('expectedIncome')}</span><strong>{!preview && !data.forecast?.income_estimate_available ? tr('notEstablished') : amount(data.forecast?.predicted_income_cents)}</strong></div>
                <div><span className="eyebrow">{tr('knownCosts')}</span><strong>{amount(data.forecast?.predicted_expenses_cents)}</strong></div>
                <div className="forecast-totals__gap"><span className="eyebrow">{tr('possibleGap')}</span><strong>{hasGap ? amount(shortfall.amount_cents) : tr('notEstablished')}</strong></div>
              </div>
              {hasGap ? <div className="set-aside-callout"><span className="set-aside-callout__icon" aria-hidden="true">↗</span><div><strong>{amount(data.forecast?.set_aside?.weekly_cents)} {tr('aWeekCouldHelpBuildABuffer')}</strong><p>{cashExplanation}</p></div></div> : null}
              <p className="disclaimer">{tr('thisIsAnEstimateFromTheEntriesYou')}</p>
            </article>
            <article className="panel chart-panel">
              <div className="panel__heading"><div><p className="eyebrow">{tr('weekByWeek')}</p><h2>{tr('incomeOutlook')}</h2></div><span className="chart-key"><span aria-hidden="true" /> {tr('estimatedIncome')}</span></div>
              {dataSaver ? <ol className="forecast-list" aria-label={tr('estimatedWeeklyIncome')}>
                {(data.forecast?.series || []).map((week, index) => <li key={week.week_start}><strong>{tr('weekNumber', { number: index + 1 })}</strong><span>{dateLabel(week.week_start)}</span><span>{amount(week.predicted_income_cents ?? week.amount_cents ?? 0)}</span></li>)}
              </ol> : data.forecast?.series?.length ? <Suspense fallback={<div className="chart-loading" role="status">{tr('loadingForecastChart')}</div>}><ForecastChart series={data.forecast.series} formatAmount={amount} formatDate={dateLabel} tr={tr} reducedMotion={window.matchMedia('(prefers-reduced-motion: reduce)').matches} /></Suspense> : <div className="empty-state chart-empty"><h3>{tr('noEstimateYet')}</h3><p>{tr('addIncomeEntriesToCreateAWeeklyOutlook')}</p><button type="button" className="button button--outline" onClick={() => navigate('add')}>{t(language, 'firstEntry')}</button></div>}
              {!dataSaver && data.forecast?.series?.length ? <ol className="forecast-list forecast-list--accessible" aria-label={tr('weeklyForecastValues')}>
                {data.forecast.series.map((week, index) => <li key={week.week_start}><strong>{tr('weekNumber', { number: index + 1 })}</strong><span>{dateLabel(week.week_start)}</span><span>{amount(week.predicted_income_cents ?? week.amount_cents ?? 0)}</span></li>)}
              </ol> : null}
              <p className="chart-note">{tr('chartAssumption')}</p>
            </article>
          </section>
        ) : null}

        {page === 'savings' ? (
          <section className="panel savings-panel">
            <p className="eyebrow">{tr('yourWeeklyBuffer')}</p>
            <h2>{tr('aSmallCushionBuiltAtYourPace')}</h2>
            <p className="savings-panel__lead">{preview ? tr('sampleForecastStatic') : tr('conditionalSuggestion')} <strong>{!preview && shortfall?.status === 'insufficient_data' ? tr('notEstablished') : amount(data.forecast?.set_aside?.weekly_cents)}</strong></p>
            <div className="buffer-progress"><p>{tr('recordedThisMonth')}: <strong>{amount(data.summary?.set_aside_progress_cents || 0)}</strong></p><p>{tr('savingsNotCash')}</p></div>
            <form className="contribution-form" onSubmit={saveContribution}>
              <h3>{tr('recordMoneyYouVePutAside')}</h3>
              <label className="field field--amount"><span>{tr('amount')}</span><span className="amount-input"><span aria-hidden="true">R</span><input required inputMode="decimal" type="number" min="0.01" step="0.01" max="20000000" value={savingAmount} onChange={(event) => setSavingAmount(event.target.value)} placeholder="0.00" /></span></label>
              <label className="field"><span>{tr('dateSetAside')}</span><input required type="date" max={today()} value={savingDate} onChange={(event) => setSavingDate(event.target.value)} /></label>
              <label className="field"><span>{tr('optionalNote')}</span><input maxLength="120" value={savingNote} onChange={(event) => setSavingNote(event.target.value)} placeholder={tr('bufferEmergencyFund')} /></label>
              <button type="submit" className="button button--primary" disabled={loading}>{tr('addToMyBuffer')} <span aria-hidden="true">→</span></button>
            </form>
            <h3 className="contribution-list-heading">{tr('recentSetAsides')}</h3>
            {(data.savings || []).length ? <ul className="contribution-list">{data.savings.slice(0, 8).map((item) => <li key={item.id}><span><strong>{amount(item.amount_cents)}</strong><small>{dateLabel(item.saved_on)}{item.note ? ' · ' + item.note : ''}</small></span><button type="button" className="text-button" onClick={() => removeContribution(item)} aria-label={tr('removeContributionLabel', { amount: amount(item.amount_cents), date: dateLabel(item.saved_on) })}>{tr('remove')}</button></li>)}</ul> : <p className="muted-note">{tr('noSetAsidesRecordedYetYouCanStart')}</p>}
          </section>
        ) : null}

        {page === 'settings' ? (
          <section className="panel settings-panel">
            <div className="settings-avatar" aria-hidden="true">{session ? profileName.slice(0, 1).toUpperCase() : 'b'}</div>
            <p className="eyebrow">{tr('accountPrivacy')}</p>
            <h2>{session ? tr('greeting', { name: profileName }) : t(language, 'accountTitle')}</h2>
            <div className="settings-preferences">
              <label className="field"><span>{t(language, 'language')}</span><select value={language} onChange={(event) => setLanguage(event.target.value)}>{supportedLanguages.map((item) => <option key={item.code} value={item.code}>{item.label}</option>)}</select></label>
              <div className="checkbox-field preference-toggle"><input id="data-saver" type="checkbox" checked={dataSaver} onChange={(event) => changeDataSaver(event.target.checked)} /><label htmlFor="data-saver"><strong>{t(language, 'dataSaver')}</strong><small>{tr('useSmallerTextOnlyForecastVisualsAndAsk')}</small></label></div>
              <div className="checkbox-field preference-toggle"><input id="high-contrast" type="checkbox" checked={highContrast} onChange={(event) => setHighContrast(event.target.checked)} /><label htmlFor="high-contrast"><strong>{tr('highContrast')}</strong><small>{tr('highContrastHelp')}</small></label></div>
              <div className="checkbox-field preference-toggle"><input id="larger-text" type="checkbox" checked={largerText} onChange={(event) => setLargerText(event.target.checked)} /><label htmlFor="larger-text"><strong>{tr('largerText')}</strong><small>{tr('largerTextHelp')}</small></label></div>
            </div>
            {supabase ? session ? <><p className="settings-email">{session.user.email}</p><button type="button" className="button button--outline" onClick={signOut}>{tr('signOut')}</button></> : (
              <form className="auth-form" onSubmit={signIn}>
                <p>{authMode === 'signup' ? tr('createAnAccountToSaveYourEntriesPrivately') : tr('signInToSeeYourPrivateDashboard')}</p>
                <label className="field"><span>{t(language, 'email')}</span><input required type="email" autoComplete="email" value={authEmail} onChange={(event) => setAuthEmail(event.target.value)} /></label>
                <label className="field"><span>{t(language, 'password')}</span><input required type="password" minLength="8" autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'} value={authPassword} onChange={(event) => setAuthPassword(event.target.value)} /></label>
                <button type="submit" className="button button--primary button--wide" disabled={loading}>{authMode === 'signup' ? t(language, 'createAccount') : t(language, 'signIn')}</button>
                <button type="button" className="text-button auth-toggle" onClick={() => setAuthMode(authMode === 'signup' ? 'signin' : 'signup')}>{authMode === 'signup' ? tr('alreadyHaveAnAccountSignIn') : tr('newToBolokaCreateAnAccount')}</button>
              </form>
            ) : <p className="settings-email">{tr('accountSignInWillBeAvailableWhenThe')}</p>}
            <div className="privacy-note"><h3>{tr('dataControls')}</h3><button type="button" className="button button--outline" onClick={downloadRecords} disabled={loading || (!preview && loadError)}>{tr('exportLoaded')}</button><p>{tr('exportScope')}</p><p>{tr('deleteAccountDecision')}</p></div>
            <div className="privacy-note"><strong>{t(language, 'privateTitle')}</strong><p>{tr('bolokaNeverAsksForYourBankPasswordYour')}</p></div>
          </section>
        ) : null}

        {page === 'home' ? <aside className="panel safety-panel" aria-labelledby="safety-heading"><span className="eyebrow">{tr('safety')}</span><h2 id="safety-heading">{t(language, 'scamTitle')}</h2><p>{t(language, 'scamBody')}</p></aside> : null}
      </main>

      {page !== 'onboarding' ? <nav className="bottom-nav" aria-label={tr('mainNavigation')}>
        {[
          ['home', t(language, 'navHome'), 'home'],
          ['add', t(language, 'navAdd'), 'add'],
          ['forecast', t(language, 'navForecast'), 'forecast'],
          ['savings', t(language, 'navSavings'), 'savings'],
        ].map(([target, label, icon]) => (
          <button key={target} type="button" onClick={() => navigate(target)} className={page === target ? 'nav-item is-current' : 'nav-item'} aria-current={page === target ? 'page' : undefined}>
            <Icon name={icon} /><span>{label}</span>
          </button>
        ))}
      </nav> : null}
    </div>
  )
}

export default App
