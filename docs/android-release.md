# Android release build

The Capacitor Android project can build a debug APK for local/emulator checks with `npm run mobile:apk` from `frontend/`. A debug APK is not the competition release artifact.

## Team-signed release APK

The release build requires the team's existing Android keystore. The build reads these environment variables and does not store their values in the repository:

- `ANDROID_KEYSTORE_PATH` — path to the team's `.jks` or `.keystore` file.
- `ANDROID_KEYSTORE_PASSWORD` — keystore password.
- `ANDROID_KEY_ALIAS` — release key alias.
- `ANDROID_KEY_PASSWORD` — key password.

Provide the variables through a private local environment or protected CI secrets. Keep the keystore outside the repository; `.gitignore` excludes key files. Do not generate or substitute a new key for the team's established signing identity.

Use Java 21 and the installed Android SDK (`ANDROID_HOME` or a private
`android/local.properties`). On Windows, Android Studio's bundled `jbr` can
provide Java 21 if its reported version matches. The helper resolves the exact
Gradle wrapper path and does not rely on current-directory command lookup.

With the approved signing values available to the build process, run:

```sh
npm run mobile:apk:release
```

The command builds the web assets, syncs Capacitor, and runs Gradle `assembleRelease`. It fails before building if the signing variables or keystore file are missing. The expected output is `android/app/build/outputs/apk/release/app-release.apk` under the frontend directory; generated APKs are ignored by Git.

## Device acceptance still required

Install the release APK on a physical Android device and verify startup, onboarding, language selection, keyboard/screen-reader use, connection loss/recovery, sign-in when team Supabase configuration exists, and the forecast flow. Record the device model, Android version, APK version, and result in the ticket. An emulator install does not satisfy the real-device acceptance criterion.
