# Submission artifact handoff — 25 October 2026

The owner confirmed testing the current APK and uploading it with the
presentation to Sonke; #44 was closed on that report. The issue does not include
a receipt identifier or exact submission time. Generated APKs and the
credential-filled judge guide remain outside Git. Do not upload signing keys or
their password configuration.

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

The owner confirms testing this exact submission APK before upload (#44). The
owner previously identified a Galaxy A15 SM-A155F/DSN on Android 16 for device
acceptance (#31); #44 does not repeat the exact device or individual checks for
this rebuild, so do not claim more detail than the owner reported. The APK uses
the existing certificate and can update the earlier signed app without
uninstalling it.

## Presentation and existing materials

- File: `submission/Boloka-pitch.pptx` (47,825 bytes).
- SHA-256: `35c12d4f7b16c375bdb4e3abd7ed6cb19f3fc78d7ffe78b8517cb44cecc52e21`.
- Nine-slide deck completion is recorded in #39. Recheck the uploaded copy opens.
- Owner already confirmed video and credential-filled judge-guide uploads,
  saving the Lean Canvas and filling in the SSDL. Check intended-judge access
  in Sonke without publishing credentials or private screenshots.
- Web app: <https://boloka.vercel.app>.
- Repository: <https://github.com/Kamogelo-Skhosana/Boloka>.

The owner reports that the APK and slides were uploaded and closed #44. No
receipt identifier or exact time was supplied. Do not state those details as
verified unless the team has a separate confirmation.
