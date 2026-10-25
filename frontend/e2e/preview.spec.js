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
    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      offenders: [...document.body.querySelectorAll('*')]
        .map(element => ({
          selector: `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ''}${element.className && typeof element.className === 'string' ? `.${element.className.trim().replace(/\s+/g, '.')}` : ''}`,
          left: Math.round(element.getBoundingClientRect().left),
          right: Math.round(element.getBoundingClientRect().right),
        }))
        .filter(element => element.left < -1 || element.right > innerWidth + 1)
        .slice(0, 8),
    }))
    expect(overflow.scrollWidth, `Horizontal overflow at ${width}px: ${JSON.stringify(overflow.offenders)}`).toBeLessThanOrEqual(width)
  }
  expect(apiRequests).toEqual([])
  expect(pageErrors).toEqual([])
})

test('entry save action stays above mobile navigation and can be keyboard reached', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 })
  await page.goto('/')
  await page.getByRole('button', { name: 'Explore the sample dashboard', exact: true }).click()
  await page.getByRole('button', { name: 'Add an entry', exact: true }).click()

  const save = page.getByRole('button', { name: 'Save income', exact: true })
  const nav = page.locator('.bottom-nav')
  const initial = await page.evaluate(() => {
    const button = [...document.querySelectorAll('button')].find(element => element.textContent.includes('Save income'))
    const navigation = document.querySelector('.bottom-nav')
    const rect = button.getBoundingClientRect()
    const navRect = navigation.getBoundingClientRect()
    const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2)
    return { buttonBottom: rect.bottom, navTop: navRect.top, hitIsSave: hit === button || button.contains(hit) }
  })
  expect(initial.buttonBottom).toBeLessThanOrEqual(initial.navTop)
  expect(initial.hitIsSave).toBe(true)

  await save.focus()
  const focused = await page.evaluate(() => {
    const button = document.activeElement.getBoundingClientRect()
    const navTop = document.querySelector('.bottom-nav').getBoundingClientRect().top
    return { buttonBottom: button.bottom, navTop }
  })
  expect(focused.buttonBottom).toBeLessThanOrEqual(focused.navTop)
  await expect(nav).toBeVisible()
})


test('home prioritizes dated costs and keeps preview planning separate', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Explore the sample dashboard', exact: true }).click()
  await page.setViewportSize({ width: 360, height: 900 })
  await page.getByRole('button', { name: 'Open account settings', exact: true }).click()
  await page.locator('#larger-text').check()
  await page.locator('#high-contrast').check()
  await page.getByRole('button', { name: 'Home', exact: true }).click()
  await expect(page.locator('.upcoming-costs')).toContainText('No upcoming costs recorded')
  // Navigation scrolls smoothly; assert the settled hit target, not an intermediate frame.
  await expect.poll(() => page.getByRole('button', { name: 'Add a bill you know is coming.', exact: true }).evaluate(button => {
    const rect = button.getBoundingClientRect()
    const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2)
    const navTop = document.querySelector('.bottom-nav').getBoundingClientRect().top
    return { hitIsButton: hit === button || button.contains(hit), aboveNav: rect.bottom <= navTop, buttonTop: rect.top, buttonBottom: rect.bottom, navTop }
  })).toMatchObject({ hitIsButton: true, aboveNav: true })
  await expect(page.locator('.balance-card')).toContainText('not your available cash or bank balance')
  await expect(page.locator('.home-metrics')).not.toContainText('Set aside each week')
  await page.getByRole('button', { name: 'Add a bill you know is coming.', exact: true }).click()
  await page.getByLabel('Amount', { exact: true }).fill('125.00')
  await page.getByLabel('What was it for?', { exact: true }).fill('Test upcoming electricity')
  const date = page.getByLabel('Date paid or due', { exact: true })
  const tomorrow = new Date((await date.inputValue()) + 'T00:00:00Z')
  tomorrow.setUTCDate(tomorrow.getUTCDate() + 1)
  await date.fill(tomorrow.toISOString().slice(0, 10))
  await page.getByRole('button', { name: 'Save expense', exact: true }).click()
  await page.getByRole('button', { name: 'Home', exact: true }).click()
  await expect(page.locator('.upcoming-costs li')).toContainText('Test upcoming electricity')
  await expect(page.locator('.upcoming-costs__total')).toContainText('125')
  await expect(page.locator('.alert-card')).toContainText('does not recalculate')
})
