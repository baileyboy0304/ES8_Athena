# Validation — 23 October 2026

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

**Not yet accepted end to end:** ES8 HA browser sign-in, fresh View Assist mapping
and final dashboards, streaming account sign-ins, DRM playback and the ITVX
Home/audio regression still need completion. ITVX currently stalls at its splash
after dismissing its Play services warning. Netflix's missing Amazon-auth
dependency was restored from the same original firmware as a user APK; its
initial crash stopped reproducing, but its protected screen is not yet visually
verified. iPlayer and Apple TV reached sign-in. Installed APKs and firewall checks
do not prove playback.

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
