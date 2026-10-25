# Product decisions

- This is a Linux-only Echo Show 8 Gen 2 installation package.
- Echo Dot Assist comes from the developer's checkers branch as an unchanged Git
  submodule. Unlocking, firmware and root instructions belong to that project.
- VACAVision connects the display to View Assist and owns the single Echo Dot
  Assist voice connection. Amazon supplies wake-word detection and audio processing;
  Echo Dot Assist provides Sendspin on the device.
- Streaming services are optional. VACAVision web access is required whenever it
  is installed. The separate installer adapts installed firewall files with backups
  and version checks; upstream source remains unchanged.
- Use the official Music Assistant physical-player entity for View Assist music
  and alerts. Do not route MA actions to the VACAVision proxy.
- Keep the native voice indicator and floating Home/Keep on/Brightness controls.
- ITVX live audio continuing after Home remains a known trial issue.
- The README is the complete user installation guide. Lyrics installation is
  coming soon. Firmware, streaming APK exports, credentials and recovery images
  stay private and outside Git.
- Private repository publication is authorised. Public release and another
  destructive reset require the owner's explicit instruction.

- VACAV is published separately at baileyboy0304/VACAV as a public HACS integration,
  with explicit owner approval. ES8_Athena remains private and pins VACAV as a submodule.

## Integration-owned setup (25 October walkthrough review)

The owner prefers a hands-off, secure setup without Linux HA authentication.
The default wizard therefore writes only non-secret choices to the installed
Android app over USB. The HA integration imports them as proposals and offers an
administrator-only VACAV Setup panel. HA's existing browser session authorizes
View Assist configuration and dashboard changes. No unauthenticated administrative
endpoint, exported HA token, executable device-supplied template or automatic
replacement of an existing dashboard is introduced.

The previous APK certificate is unavailable on Linux. Prototype.11 is signed with
the available Linux key, so old APKs signed with the previous key cannot receive an
in-place update. Keep the live app intact unless its original key is recovered or
an explicit reinstall is chosen. Publish no keystores or private walkthrough data.
