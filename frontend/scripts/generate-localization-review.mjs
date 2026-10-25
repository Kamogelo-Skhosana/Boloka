import { writeFile } from 'node:fs/promises'
import { english } from '../src/lib/strings.js'
import { missingTranslations, translate, translationKeys } from '../src/lib/copy.js'

for (const language of ['zu', 'st']) {
  const missing = missingTranslations(language)
  if (missing.length) throw new Error(`${language} is missing translations: ${missing.join(', ')}`)
}

const escapeCell = value => String(value).replaceAll('|', '\\|').replaceAll('\n', '<br>')
const rows = translationKeys.map(key => `| ${escapeCell(key)} | ${escapeCell(english[key] ?? key)} | ${escapeCell(translate('zu', key))} | ${escapeCell(translate('st', key))} | Fluent review required |`)
const document = `# Localization review inventory

The React screens, accessible labels, charts, confirmations, and action errors have isiZulu and Sesotho draft copy. The catalog has no known English fallback keys. All translations remain unapproved until fluent speakers review them; coverage does not establish language quality.

## Fluent-speaker acceptance

Review financial meanings (recorded net versus available cash, conditional gap, confidence, due costs and savings), action errors, delete confirmation, screen-reader labels, date/currency formatting, and interpolation order. Verify cancellation and destructive actions on a phone. Preserve placeholders and keep CSV column names such as \`amount\`, \`source\`, and \`received_on\` unchanged. Auth-provider/database errors are replaced with catalogued action messages; backend diagnostic prose remains English for API clients.

## Draft translation inventory

| Key | English source | isiZulu draft | Sesotho draft | Review |
| --- | --- | --- | --- | --- |
${rows.join('\n')}

Do not mark issue #28 complete until fluent reviewers approve the financial, safety, and destructive-action flows.
`

await writeFile(new URL('../../docs/localization-review.md', import.meta.url), document)
