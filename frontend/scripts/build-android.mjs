import { spawnSync } from 'node:child_process'
import { platform } from 'node:os'

const windows = platform() === 'win32'
const result = spawnSync(windows ? 'gradlew.bat' : './gradlew', ['assembleDebug'], {
  cwd: new URL('../android/', import.meta.url),
  stdio: 'inherit',
  shell: windows,
})

if (result.error) throw result.error
process.exit(result.status ?? 1)
