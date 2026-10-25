# Submission artifact handoff — 25 October 2026

This is preparation for #44, not a Sonke submission receipt. Generated APKs and
the credential-filled judge guide remain outside Git. Do not upload signing
keys or their password configuration.

## Candidate Android artifact

- Local file: `output/apk/Boloka-1.0-submission.apk`
- Source commit: `defcc2d70aee48f53b4e3e0b9f69341925335ff7` (includes #91's import-focus fix).
- Size: 3,420,519 bytes.
- SHA-256: `87067a0e6ae8b77a745e416636940ba033a5aa757cf80e94d0f5f943cbe34888`.
- Signing certificate SHA-256: `f937de473f61cd98febbbd294d1a7d88d083060c896c71ee27362c2cfa43af30`.

`npm run mobile:apk:release` completed successfully with the existing private
team key, and Android `apksigner verify --print-certs` accepted the resulting
APK. The certificate matches the earlier release identity. The source commit's
backend, PostgreSQL RLS and frontend CI checks passed before packaging.

The owner previously accepted earlier builds on Galaxy A15 SM-A155F/DSN,
Android 16, and confirmed the full judge flow. This exact rebuilt artifact has
not yet received owner device acceptance. Install it over the prior signed app
and check startup, sign-in and CSV review/cancel/save before upload. Do not
uninstall merely to test an update; keep account-backed records intact.

## Presentation and existing materials

- File: `submission/Boloka-pitch.pptx` (47,825 bytes).
- SHA-256: `35c12d4f7b16c375bdb4e3abd7ed6cb19f3fc78d7ffe78b8517cb44cecc52e21`.
- Nine-slide deck completion is recorded in #39. Recheck the uploaded copy opens.
- Owner already confirmed video and credential-filled judge-guide uploads,
  saving the Lean Canvas and filling in the SSDL. Check intended-judge access
  in Sonke without publishing credentials or private screenshots.
- Web app: <https://boloka.vercel.app>.
- Repository: <https://github.com/Kamogelo-Skhosana/Boloka>.

Follow the [final upload checklist](README.md#final-upload-checklist). After the
accepted APK and slides are uploaded and the final submission action succeeds,
record the actual receipt/time in #44. Keep #44 open until that confirmation.
