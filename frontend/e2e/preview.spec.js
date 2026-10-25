import { test, expect } from '@playwright/test'
import { readFile } from 'node:fs/promises'
import { translate } from '../src/lib/copy.js'

test('judge preview keeps edits honest, reversible and outside the API', async ({ page }) => {
  const apiRequests = []
  const pageErrors = []
  page.on('pageerror', error => pageErrors.push(error.message))
  await page.route('**/*', route => {
    const url = new URL(route.request().url())
    if (url.pathname.startsWith('/api/') || url.hostname.endsWith('.supabase.co')) {
      apiRequests.push(url.pathname)
      return route.abort()
    }
    return url.hostname === '127.0.0.1' ? route.continue() : route.abort()
  })
  await page.goto('/')
  await page.getByRole('button', { name: 'Explore the sample dashboard', exact: true }).click()
  const balance = async () => Number((await page.locator('.balance-card__value').innerText()).replace(/\D/g, ''))
  const original = await balance()
  await page.getByRole('button', { name: 'Add an entry', exact: true }).click()
  await page.getByLabel('Amount', { exact: true }).fill('100.00')
  await page.getByLabel('Where did it come from?', { exact: true }).fill('Preview QA payout')
  await page.getByRole('button', { name: 'Save income', exact: true }).click()
  await expect.poll(balance).toBe(original + 10000)

  const row = page.locator('.transaction-row').filter({ hasText: 'Preview QA payout' })
  await row.getByRole('button', { name: /^Edit Preview QA payout/ }).click()
  await page.getByLabel('Amount', { exact: true }).fill('200.00')
  await page.getByRole('button', { name: 'Cancel', exact: true }).click()
  await expect.poll(balance).toBe(original + 10000)
  await row.getByRole('button', { name: /^Edit Preview QA payout/ }).click()
  await page.getByLabel('Amount', { exact: true }).fill('200.00')
  await page.getByRole('button', { name: 'Save changes', exact: true }).click()
  await expect.poll(balance).toBe(original + 20000)

  page.once('dialog', dialog => dialog.dismiss())
  await row.getByRole('button', { name: /^Delete Preview QA payout/ }).click()
  await expect(row).toHaveCount(1)
  page.once('dialog', dialog => dialog.accept())
  await row.getByRole('button', { name: /^Delete Preview QA payout/ }).click()
  await expect(row).toHaveCount(0)
  await expect.poll(balance).toBe(original)
  await expect(page.locator('.alert-card')).toContainText('does not recalculate')
  await page.getByRole('button', { name: 'Forecast', exact: true }).click()
  await expect(page.locator('.forecast-summary')).toContainText('does not recalculate')
  await expect(page.getByRole('group', { name: translate('en', 'estimatedIncomeChart', { blocks: 4 }) })).toBeVisible()

  await page.getByRole('button', { name: 'Open account settings', exact: true }).click()
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export loaded entries (JSON)', exact: true }).click()
  const download = await downloadPromise
  const exported = JSON.parse(await readFile(await download.path(), 'utf8'))
  expect(exported.fictional_preview).toBe(true)
  for (const language of ['zu', 'st']) {
    await page.getByRole('combobox').selectOption(language)
    await expect(page.getByText(translate(language, 'translationReview'), { exact: true })).toBeVisible()
    await expect(page.locator('html')).toHaveAttribute('lang', language)
  }
  await page.getByRole('combobox').selectOption('en')
  await page.locator('#high-contrast').check()
  await page.locator('#larger-text').check()
  await expect(page.locator('html')).toHaveAttribute('data-contrast', 'high')
  await expect(page.locator('html')).toHaveAttribute('data-text-size', 'large')
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('data-contrast', 'high')
  await expect(page.locator('html')).toHaveAttribute('data-text-size', 'large')
  await page.getByRole('button', { name: 'Open account settings', exact: true }).click()
  await expect(page.locator('#high-contrast')).toBeChecked()
  await expect(page.locator('#larger-text')).toBeChecked()
  for (const width of [360, 414, 1120]) {
    await page.setViewportSize({ width, height: 812 })
    await page.getByRole('button', { name: 'Home', exact: true }).click()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  }
  expect(apiRequests).toEqual([])
  expect(pageErrors).toEqual([])
})
