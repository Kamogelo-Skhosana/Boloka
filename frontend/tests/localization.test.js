import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Linter } from 'eslint'
import { translate, missingTranslations, translationKeys } from '../src/lib/copy.js'
import { formatMoney } from '../src/lib/format.js'

test('locale fallbacks and complete interpolation remain explicit', () => {
  assert.equal(translate('en', 'confirmDelete', { label: 'Rent', amount: 'R500', date: '25 Oct' }), 'Delete Rent, R500, dated 25 Oct? This cannot be undone.')
  assert.equal(translate('zu', 'navHome'), 'Ikhaya')
  assert.equal(translate('st', 'navHome'), 'Lehae')
  for (const language of ['zu', 'st']) {
    assert.deepEqual(missingTranslations(language).sort(), [
      'homeOverview', 'homeIntro', 'homeUpcomingTitle', 'homeUpcomingHelp',
      'homeNoUpcoming', 'homeRecordedLabel', 'homeRecordedHelp',
    ].sort()) // Deliberate English fallback pending fluent review of new home copy.
    for (const key of translationKeys) {
      const englishPlaceholders = [...translate('en', key).matchAll(/\{(\w+)\}/g)].map((match) => match[1]).sort()
      const translatedPlaceholders = [...translate(language, key).matchAll(/\{(\w+)\}/g)].map((match) => match[1]).sort()
      assert.deepEqual(translatedPlaceholders, englishPlaceholders, `${language}.${key} placeholders`)
    }
  }
  assert.match(formatMoney(150000), /1[,.\s\u00a0]?500/)
  assert.equal(formatMoney(150000).includes('150k'), false)
  for (const language of ['en', 'zu', 'st']) {
    const label = translate(language, 'estimatedIncomeChart', { blocks: 5 })
    assert.match(label, /5/)
    assert.doesNotMatch(label, /weeks|dibeke|masonto/i)
  }
})

test('main screen JSX and accessible labels do not bypass the copy catalog', () => {
  const linter = new Linter()
  const rule = { create(context) {
    return {
      JSXText(node) {
        if (/[A-Za-z]{2}/.test(node.value)) context.report({ node, message: 'Use a translation key' })
      },
      JSXAttribute(node) {
        if (['aria-label', 'title', 'placeholder', 'label', 'hint'].includes(node.name.name) &&
            node.value?.type === 'Literal' && /[A-Za-z]{2}/.test(node.value.value)) {
          context.report({ node, message: 'Use a translation key for accessible and visible copy' })
        }
      },
    }
  } }
  for (const path of ['App.jsx', 'components/TransactionList.jsx', 'screens/TransactionEditor.jsx', 'components/ForecastChart.jsx']) {
    const source = readFileSync(new URL('../src/' + path, import.meta.url), 'utf8')
    const messages = linter.verify(source, [{ languageOptions: { parserOptions: { ecmaFeatures: { jsx: true } } },
      plugins: { copy: { rules: { keys: rule } } }, rules: { 'copy/keys': 'error' } }])
    assert.deepEqual(messages, [], path)
    for (const match of source.matchAll(/(?:tr\(|t\(language, )'([^']+)'/g)) {
      assert.ok(translationKeys.includes(match[1]), 'Missing copy: ' + match[1])
    }
  }
})
