import { supabase } from './lib/client'

// Placeholder shell for the Boloka dashboard. Real screens (onboarding, auth,
// dashboard, add income/expense, forecast, savings) land in later tickets.
// See docs/design.md for the screen list and visual direction.
export default function App() {
  const connected = Boolean(supabase)

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <div className="flex items-center gap-3 mb-4">
        <span className="grid place-items-center w-11 h-11 rounded-full bg-accent text-ink font-extrabold text-xl">
          B
        </span>
        <h1 className="text-4xl font-extrabold tracking-tight">Boloka</h1>
      </div>

      <p className="text-warn font-semibold text-lg">Save, before you have to.</p>

      <p className="text-muted mt-6 max-w-sm">
        Cash-flow forecasting for people with irregular incomes. This is the app
        shell. Screens are built from the tickets in the backlog.
      </p>

      <p className="text-muted mt-8 text-sm">
        Supabase client: {connected ? 'configured' : 'not configured (set .env)'}
      </p>
    </div>
  )
}
