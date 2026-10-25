# Submission preparation

These files are preparation artifacts, not evidence of a completed submission.
The final Sonke upload and receipt are tracked in
[#44](https://github.com/Kamogelo-Skhosana/Boloka/issues/44).

| Artifact | Status and next action |
| --- | --- |
| `Boloka-pitch.pptx` | Updated nine-slide deck with corrected forecast limits, architecture and judge-access guidance; hosted demo access and team review remain unverified. |
| [Pitch speaker guide](pitch-content.md) | Speaker context and remaining live verification for #39. |
| [Pitch script](hustle-pitch.md) | Script and shot list only; actual recording/upload remains #38. |
| [Lean Canvas](../docs/lean-canvas.md) | Hypothesis draft; team review and transfer into Sonke remain #40. |
| [Security lifecycle](ssdl-security.md) | Repository-grounded engineering assessment; security-owner approval and transfer into any required Sonke template remain. Not certification. |
| [Judge runbook](../docs/judge-demo.md) | Owner confirmed the judge demo flow passed and #35 is closed. Final Sonke upload and receipt remain tracked separately in #44. |

## Final upload checklist

- [ ] Submit the public repository: <https://github.com/Kamogelo-Skhosana/Boloka>.
- [ ] Upload [`Boloka-pitch.pptx`](Boloka-pitch.pptx), then verify the uploaded
  deck opens and contains all nine slides.
- [ ] Upload the existing team-signed release APK through the team's private
  handoff. The owner reports that the APK was built, signature-verified, and
  accepted on a Galaxy A15 running Android 16 (#31); the private APK is
  intentionally not committed to this checkout. Do not generate a different
  signing key. If a rebuild is needed, follow the existing-key procedure in
  [`Android release steps`](../docs/android-release.md) and confirm the artifact
  uses the established certificate.
- [ ] Add the hosted app and judge access through Sonke's appropriate fields.
  Keep passwords and private judge details out of the public repository.
- [ ] Confirm the final Sonke receipt and record the submission time in #44.

Keep account passwords, signing material and private submission fields outside
Git. Only record a successful upload after an actual Sonke confirmation (#44).
