import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Supabase client (auth + database). The anon key is safe on the client because
// Row-Level Security restricts every row to its owner. See supabase/schema.sql.
export const supabase =
  supabaseUrl && supabaseAnonKey ? createClient(supabaseUrl, supabaseAnonKey) : null

// Thin wrapper around the Boloka backend API (see docs/api.md). It attaches the
// current user's access token so the backend can verify the request.
export async function api(path, { method = 'GET', body, accessToken } = {}) {
  const headers = {}
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  if (body && !isFormData) headers['Content-Type'] = 'application/json'
  try {
    if (localStorage.getItem('boloka-data-saver') === 'true' || navigator.connection?.saveData) headers['Save-Data'] = 'on'
  } catch { /* The request still works when browser storage is unavailable. */ }

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`
  } else if (supabase) {
    const {
      data: { session },
    } = await supabase.auth.getSession()
    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`
    }
  }

  const res = await fetch(`${apiBaseUrl}${path}`, {
    method,
    headers,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
  })

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail?.error?.message || `Request failed (${res.status})`)
  }

  return res.status === 204 ? null : res.json()
}
