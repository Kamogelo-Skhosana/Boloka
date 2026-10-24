import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { platform } from 'node:os'
import { resolve } from 'node:path'

const windows = platform() === 'win32'
const release = process.argv.includes('--release')
const requiredSigningValues = [
  'ANDROID_KEYSTORE_PATH',
  'ANDROID_KEYSTORE_PASSWORD',
  'ANDROID_KEY_ALIAS',
  'ANDROID_KEY_PASSWORD',
]

if (release) {
  const missing = requiredSigningValues.filter((name) => !process.env[name])
  const keystorePath = process.env.ANDROID_KEYSTORE_PATH
    ? resolve(process.env.ANDROID_KEYSTORE_PATH)
    : null
  if (missing.length || !existsSync(keystorePath || '')) {
    const missingNames = missing.length ? missing.join(', ') : 'an existing ANDROID_KEYSTORE_PATH'
    throw new Error(`Release signing is not configured. Set ${missingNames} without committing the key or passwords.`)
  }
  process.env.ANDROID_KEYSTORE_PATH = keystorePath
}

const result = spawnSync(windows ? 'gradlew.bat' : './gradlew', [release ? 'assembleRelease' : 'assembleDebug'], {
  cwd: new URL('../android/', import.meta.url),
  stdio: 'inherit',
  shell: windows,
})

if (result.error) throw result.error
if (release && result.status === 0) console.log('Signed release APK: android/app/build/outputs/apk/release/app-release.apk')
process.exit(result.status ?? 1)
