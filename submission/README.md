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
| [Judge runbook](../docs/judge-demo.md) | Hosted sign-in, two-account checks and release verification remain #35. |

## Final upload checklist

- [ ] Submit the public repository: <https://github.com/Kamogelo-Skhosana/Boloka>.
- [ ] Upload [`Boloka-pitch.pptx`](Boloka-pitch.pptx), then verify the uploaded
  deck opens and contains all nine slides.
- [ ] Upload a team-signed release APK built from the intended release commit.
  The current checkout contains only a debug APK; it is not a submission build.
  See [`Android release steps`](../docs/android-release.md). The team keystore
  and signing secrets are not available in this workspace, so do not substitute
  a new signing key or submit the debug build as the release artifact.
- [ ] Add the hosted app and judge access through Sonke's appropriate fields.
  Keep passwords and private judge details out of the public repository.
- [ ] Confirm the final Sonke receipt and record the submission time in #44.

Keep account passwords, signing material and private submission fields outside
Git. Only record a successful upload after an actual Sonke confirmation (#44).
