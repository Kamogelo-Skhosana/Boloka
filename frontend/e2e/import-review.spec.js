import { test, expect } from '@playwright/test'

test('signed-in import previews, corrects, excludes, cancels and confirms without premature writes', async ({ page }) => {
  const requests = []
  let confirms = 0
  let dashboardLoads = 0
  const rows = Array.from({ length: 21 }, (_, i) => ({ line: i + 2, amount_cents: 1000,
    source: `CSV payout ${i + 1}`, received_on: '2026-10-24', note: null }))
  await page.route('**/*', route => {
    const url = new URL(route.request().url())
    if (url.hostname !== '127.0.0.1') return route.abort()
    if (url.pathname === '/src/lib/client.js') return route.fulfill({ contentType: 'text/javascript', body: `
      const session = { user: { id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', email: 'fixture@example.invalid' }, access_token: 'fixture-token' };
      export const supabase = { auth: { getSession: async () => ({data:{session}}), onAuthStateChange: () => ({data:{subscription:{unsubscribe(){}}}}) } };
      export async function api(path, options={}) {
        const form = options.body instanceof FormData;
        const response = await fetch('/api/v1'+path,{method:options.method||'GET',headers:form?{}:{'Content-Type':'application/json'},body:options.body?(form?options.body:JSON.stringify(options.body)):undefined});
        if(!response.ok) throw new Error('Fixture request failed');
        return response.json();
      }
    ` })
    if (!url.pathname.startsWith('/api/v1/')) return route.continue()
    requests.push(url.pathname)
    if (url.pathname === '/api/v1/dashboard') {
      dashboardLoads += 1
      if (dashboardLoads > 1) return route.fulfill({ status: 502, json: { error: { message: 'Fixture refresh failed' } } })
      return route.fulfill({ json: {
      summary: {}, income: [], expenses: [], savings: [], forecast: { horizon_days: 30, shortfall: { status: 'insufficient_data' }, set_aside: {}, next_steps: ['record_income'], series: [] },
      } })
    }
    if (url.pathname === '/api/v1/income/import/preview') return route.fulfill({ json: { rows, skipped: 1, errors: [{ line: 23, message: 'Invalid amount' }] } })
    if (url.pathname === '/api/v1/income/import/confirm') {
      confirms += 1
      const saved = route.request().postDataJSON().rows
      expect(saved).toHaveLength(20)
      expect(saved[0]).toEqual({ amount_cents: 1234, source: 'Corrected payout', received_on: '2026-10-24', note: null })
      expect(saved.at(-1).amount_cents).toBe(2500)
      expect(saved.some(row => row.source === 'CSV payout 2')).toBe(false)
      if (confirms === 1) return route.fulfill({ status: 502, json: { error: { message: 'Fixture failure' } } })
      return route.fulfill({ json: { imported: 20, skipped: 0, errors: [] } })
    }
    return route.abort()
  })
  await page.goto('/')
  await page.getByRole('button', { name: 'Explore the sample dashboard', exact: true }).click()
  await page.locator('.balance-card').getByRole('button', { name: 'Add an entry', exact: true }).click()
  await page.getByText('Import income from a CSV', { exact: true }).click()
  const upload = async () => {
    await page.locator('input[type=file]').setInputFiles({ name: 'income.csv', mimeType: 'text/csv', buffer: Buffer.from('amount,source,received_on\n10,Test,2026-10-24') })
    await page.getByRole('button', { name: 'Preview CSV without saving', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Review income from CSV', exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Review income from CSV', exact: true })).toBeFocused()
    await page.keyboard.press('Tab')
    await expect(page.locator('.import-review-rows fieldset').first().getByRole('checkbox')).toBeFocused()
  }
  await upload()
  expect(confirms).toBe(0)
  await page.getByRole('button', { name: 'Cancel', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Review income from CSV', exact: true })).toHaveCount(0)
  await expect(page.locator('input[type=file]')).toBeFocused()
  expect(confirms).toBe(0)
  await upload()
  const first = page.locator('.import-review-rows fieldset').first()
  await first.scrollIntoViewIfNeeded()
  await page.screenshot({ path: test.info().outputPath('import-review.png') })
  await first.getByLabel('Amount', { exact: true }).fill('12.34')
  await first.getByLabel('Where did it come from?', { exact: true }).fill('Corrected payout')
  const excluded = page.locator('.import-review-rows fieldset').nth(1)
  await excluded.getByLabel('Amount', { exact: true }).fill('0')
  await excluded.getByRole('checkbox').uncheck()
  await page.getByRole('button', { name: 'Next rows', exact: true }).click()
  await expect(page.locator('.import-review-rows fieldset').getByRole('checkbox')).toBeFocused()
  await page.locator('.import-review-rows fieldset').getByLabel('Amount', { exact: true }).fill('25.00')
  await page.getByRole('button', { name: 'Save 20 selected rows', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('response was lost')
  await expect(page.getByRole('alert')).toBeFocused()
  await expect(page.getByRole('heading', { name: 'Review income from CSV', exact: true })).toBeVisible()
  // The mock guarantees its first attempt did not write; real users must check their records before retrying.
  await page.getByRole('button', { name: 'Save 20 selected rows', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Review income from CSV', exact: true })).toHaveCount(0)
  await expect.poll(() => confirms).toBe(2)
  await expect(page.getByRole('status').filter({ hasText: 'Saved, but the updated records could not be reloaded' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Save 20 selected rows', exact: true })).toHaveCount(0)
  expect(requests).not.toContain('/api/v1/income/import')
})
