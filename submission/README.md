# Submission preparation

These files are preparation artifacts, not evidence of a completed submission.
The final Sonke upload and receipt are tracked in
[#44](https://github.com/Kamogelo-Skhosana/Boloka/issues/44).

| Artifact | Status and next action |
| --- | --- |
| `Boloka-pitch.pptx` | Nine-slide deck complete under #39. Verify the final uploaded copy opens correctly. |
| [Pitch speaker guide](pitch-content.md) | Supporting speaker context; deck completion is recorded in #39. |
| [Pitch script](hustle-pitch.md) | Preparation script. Owner confirmed video submission; #38 is complete. |
| [Lean Canvas](../docs/lean-canvas.md) | Owner confirmed review and saving in Sonke; #40 is complete. Business and impact claims still require evidence. |
| [Security lifecycle](ssdl-security.md) | Owner confirmed the Sonke SSDL was filled in. This is a recorded assessment, not security certification. |
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

## Owner handoff

Use the [artifact handoff](release-handoff.md) for exact local filenames,
source commit, checksums and signing verification of the prepared release.

1. Open the latest signed APK from the local `output/apk/` directory on the
   Galaxy A15. Confirm startup, sign-in and CSV review/cancel/save behavior on
   this exact build before selecting it for upload. Earlier device acceptance
   does not automatically establish acceptance of a rebuilt artifact.
2. Upload the accepted APK and `submission/Boloka-pitch.pptx` through Sonke's
   submission interface. Verify the resulting filenames and that the uploaded
   presentation opens. Keep generated APKs out of Git.
3. Verify the project overview includes <https://boloka.vercel.app> and
   <https://github.com/Kamogelo-Skhosana/Boloka>. The owner already uploaded the
   credential-filled judge guide and video through Sonke; check that both remain
   available to the intended judges. Do not copy credentials into public text.
4. Complete the final submission action and retain its confirmation. Report
   the submission time, accepted artifact filename/checksum and receipt status
   in #44, excluding credentials and private account information.

A successful build or an uploaded video/guide alone does not establish that
the repository, APK and slides have been submitted. Close #44 after the owner
confirms the complete submission and its receipt.
