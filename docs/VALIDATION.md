# Validation — 24 October 2026

## Top-edge flash follow-up — 24 October

- Extended the route-scoped surface styling to HA’s separate header background,
  text, selection bar and border variables. Verified the rendered HA header
  background is `rgb(16, 30, 48)` rather than the default theme colour.
- Repeated the five ES8 dashboard transitions and inspected the top 24 pixel rows
  of all 30 sampled screenshots; no white horizontal loading strip was captured.
- Resource upgrades update the existing style and profile resource entry in place,
  so a cached earlier module cannot prevent the new header rules from applying.

## Cross-dashboard loading background — 24 October

- Replaced the earlier same-dashboard TV workaround. Home, VA and TV again use
  their separate dashboard URLs.
- Added a route-scoped HA frontend resource which keeps the document background
  dark blue while HA replaces dashboard content. The captured Home → VA loading
  gap itself is solid dark blue, rather than white.
- Checked VA → Home, Home → VA, VA → Home again, Home → TV and TV → Home on the
  ES8, with six screenshots per transition. All reached their intended pages;
  no white loading frame was captured. This is sampled verification, not a
  frame-by-frame video measurement. Native initial startup is outside this fix.

## Dashboard correction — 24 October

- Restored the original blue clock navigation style from the owner’s HA dashboard.
- Replaced TV masonry with a single blue panel, one Home button and equally sized
  streaming buttons; verified full labels on the ES8.
- Adapted the existing Music Assistant frame to return to Athena Home. Verified
  authenticated MA rendering and Home return on the ES8.
- Deployment backs up and reads back only Athena’s three dashboards. The shared
  Portal dashboards and their frontend module are unchanged.

## Linux clean-install walkthrough (in progress)

- Restored verified original system/vendor partition images, preserved matching
  unlocked boot/recovery, and formatted userdata/cache. User-installed APKs were
  absent before the new installation.
- Applied the pinned root ZIP from TWRP, then ran the unchanged upstream EDA
  installer at the recorded submodule commit. Source build, firmware probe, Wi-Fi
  setup and the installer's reboot stability check completed successfully.
- Installed VACAV prototype.10 and the supplied Netflix, iPlayer splits, ITVX and
  Silk APKs. Fixed the streaming adapter's busy read-only remount by restarting
  EDA's existing firewall watcher before the remount; the complete apply run passed.
- After reboot, system/vendor were read-only, the EDA firewall watcher was running,
  and all four selected app UIDs had TCP 80/443 rules before the final deny rule.
  VACAV's DUMP permission and ITVX helper persisted.
- Installed the matching HA integration/assets with backups. HA configuration
  check passed. Fixed the device-name schema's unsupported `str.strip` validator;
  after restarting HA, the configuration form rendered successfully.
- Paired the new Garden Athena VACAV device and its EDA Sendspin player. HA's
  assistant connection/TTS test completed, and Music Assistant radio FLAC
  playback started and stopped on the intended device. Camera permission was
  granted with the owner's approval. Streaming sign-ins are deferred by choice.
- Removed the obsolete ES8 VACAV and View Assist registrations for this clean
  reset. Added explicit HA cleanup and recreation order to the README.
- Created and read back Home/VA/TV setup dashboards. The ES8's missing-dashboard
  404 was replaced by the HA login screen; the authenticated desktop browser
  renders the welcome/setup page. Display sign-in must precede VA discovery.
- Twelve repository tests and component checksum verification passed, including
  preserving existing dashboards, safely repeating placeholder preparation and
  refusing VA creation before display discovery. The live creation helper also
  stopped with that explicit sign-in instruction. EDA source
  remains unchanged.

- Restored on-device text entry with official Simple Keyboard 6.8 (release 149),
  verified against its published SHA-256. Android reports the IME selected, bound
  and shown in the HA login field. The stock keyboard trial crashed because its
  system-library access was missing; that trial APK was removed. The device
  installer now supplies the offline keyboard when no selected IME exists.

- The owner completed HA sign-in on the ES8. Created the fresh Garden Athena
  VA device through its normal configuration API with the correct VACAV Assist,
  Music and display ID. Configured its own dashboard, weather and zero ducking;
  the native-only indicator is selected. Corrected VA's restored stale
  `home_screen` attribute through its supported set-state action.
- Generated, installed and read back the final Home, VA and TV dashboards with
  backups. Verified the full-width clock/weather on the ES8 and corrected its
  GMT timezone to Europe/London. Home → VA, VA → Home/TV and Home → Music
  Assistant navigation work on the device; MA shows Garden Athena selected.
- Netflix opens from the actual TV dashboard button without the original auth
  dependency crash. Its protected screen prevents automated visual confirmation
  of the login UI. The installer now restores the exact matching firmware auth
  APK and enables the tablet launcher for the selected Echo Netflix package.
- ITVX reaches its catalogue after manually tapping **OK** on the Google Play
  services warning. A cold-start retry confirmed that the current Back-based
  helper does not reliably dismiss it. A compatible replacement VACAV APK needs
  the original signing key, which is not available on this Linux host. The app
  was not uninstalled and the user's new HA sign-in was preserved.

- Final reboot retained VACAV as Home, HA browser sign-in, Simple Keyboard and
  Europe/London timezone. The Home dashboard rendered without a login prompt;
  EDA processes and the firewall service were running, with system/vendor read-only.

**Still pending:** streaming account sign-ins and DRM/audio playback (deferred by
owner), physical wake/mute checks and the ITVX live-audio-after-Home regression.
ITVX warning automation remains a known failure; manual OK works. Optional VA
calendar/sports/camera views need their own HA entities, resources and blueprints
as described in the dashboard guide. This is basic setup validation, not full
streaming acceptance.

## Original packaging checks

- Four offline dashboard tests passed: complete ES8 view/service generation; no-service
  configuration; Portal package/path isolation; Home/TV navigation on every VA view.
- Installer imports and the `install.py device` helper dispatch passed offline checks.
- Four mocked USB-selection checks cover single-device selection, no/multiple-device
  refusal, explicit serial handling and the public CLI. No device was accessed.
- All 265 bundled VACAV/device files passed SHA256 verification,
  including comparison with staged Git bytes to check Linux checkout consistency.
- `echo-dot-assist/` is a clean Git submodule at `1c00727d332c3b0ee4d13b59f702c78839431694`;
  a live `ls-remote` check matched the developer's current `checkers` branch.
- The separate firewall payload prepared successfully against that upstream source;
  this is a preparation check, not proof of behaviour on the device.
- All manifest paths are included in the staged local Git repository; no ignored
  private/export/backup directory or private key file is staged. The owner approved
  the private GitHub transfer after reviewing this layout.
- The largest bundled file is approximately 49 MB. The earlier targeted
  credential-pattern scan found no matches. Private APK exports remain excluded.
- Read-only ES8 streaming export preserved Netflix (1 APK), iPlayer (4 split APKs),
  ITVX (1 APK), and Silk (1 APK), verified against device hashes. These are local
  private reinstall assets, excluded from Git.

No echo-dot-assist/VACAV rebuild, live installation, HA dashboard write, device wipe, rendered
dashboard QA or end-to-end clean-install test was performed in this packaging pass.
The original trial's acceptance does not establish that this new installer is
fully tested. Repository review and private transfer approval are complete. Next:
the agent's Linux clean install/basic checks followed by the owner's testing.
See `LINUX-HANDOVER.md` for the private files GitHub will not carry.
