## Double-tap streaming controls — 26 October 2026

Prototype.13 (code 19) removes the single-tap playback trigger. Android’s ten unit
tests, 29 integration tests, 52 installer tests and the release build passed.
Updated Garden Athena from prototype.12 in place. On iPlayer’s sign-in screen,
a single tap left controls hidden and two taps 150 ms apart showed Home, Keep on
and Brightness. The popup then auto-hid. Returned the device to VACAV afterward.
Signed-in video playback was not exercised in this check.

## README and wrapper review — 26 October 2026

Verified the pinned Downloads step always includes the Athena firmware file and
checks the unlocker’s exact v1.0.0 filename/hash when needed. The locally available
v1.1.0 recovery image matches the reset baseline when zero-padded to partition
size; v1.1.1 does not. No current v1.0.0 download was verified (XDA denied access).
The wrapper now explicitly uses device-only inspection and reports the hash checks
before they start. A regression test refuses image checks/restores without an
image directory. The guide documents required MA pairing, the short volume-key
login gesture, player-name matching and the exact announcement option.

# Validation — 25 October 2026

## Device Configure flow — VACAVision 0.5.0

- 29 integration tests and 52 Linux installer tests pass with the project Python
  environment. Tests cover device-bound matching, reading weather from the matched
  View Assist entry, preserving custom VA paths, and the microphone selector.
- Android release build and ten unit tests pass. Prototype.12 (version code 18)
  installed over prototype.11 on Garden Athena with app data and HA sign-in intact.
- The live View Assist manual form offers Garden Athena’s Assist satellite. Name,
  physical Music Assistant player and display selections were filled for screenshots
  and cancelled without creating another View Assist entry.
- HA configuration checks passed before restarting with integration 0.5.0.
- README screenshots show the actual Configure menu and View Assist forms.
- Live dashboard preparation found the existing microphone, display, official MA
  player and VA weather and reached the backup/install confirmation. Cancel was
  verified; existing dashboards and the View Assist entry were preserved.
- This update is an in-place validation. A fresh wipe/install and a new audible
  voice/music test have not been repeated for this release.

# Earlier validation — 24 October 2026

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
  Unrelated dashboards and their frontend module are unchanged.

## Linux clean-install walkthrough (in progress)

- Restored verified original system/vendor partition images, preserved matching
  unlocked boot/recovery, and formatted userdata/cache. User-installed APKs were
  absent before the new installation.
- Applied the pinned root ZIP from TWRP, then ran the unchanged upstream Echo Dot Assist
  installer at the recorded submodule commit. Source build, firmware probe, Wi-Fi
  setup and the installer's reboot stability check completed successfully.
- Installed VACAV prototype.10 and the supplied Netflix, iPlayer splits, ITVX and
  Silk APKs. Fixed the streaming adapter's busy read-only remount by restarting
  Echo Dot Assist's existing firewall watcher before the remount; the complete apply run passed.
- After reboot, system/vendor were read-only, the Echo Dot Assist firewall watcher was running,
  and all four selected app UIDs had TCP 80/443 rules before the final deny rule.
  VACAV's DUMP permission and ITVX helper persisted.
- Installed the matching HA integration/assets with backups. HA configuration
  check passed. Fixed the device-name schema's unsupported `str.strip` validator;
  after restarting HA, the configuration form rendered successfully.
- Paired the new Garden Athena VACAV device and its Echo Dot Assist Sendspin player. HA's
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
  stopped with that explicit sign-in instruction. Echo Dot Assist source
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
  Echo Dot Assist processes and the firewall service were running, with system/vendor read-only.

**Still pending:** streaming account sign-ins and DRM/audio playback (deferred by
owner), physical wake/mute checks and the ITVX live-audio-after-Home regression.
ITVX warning automation remains a known failure; manual OK works. Optional VA
calendar/sports/camera views need their own HA entities, resources and blueprints
as described in the dashboard guide. This is basic setup validation, not full
streaming acceptance.

## Original packaging checks

- Four offline dashboard tests passed: complete ES8 view/service generation; no-service
  configuration; Home/TV navigation on every VA view.
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
Firmware, recovery images and streaming APK exports are private inputs, not supplied through GitHub.

## Music Assistant convention correction — 24 October 2026

The original instructions incorrectly disabled MA's HA exposure and assigned the
VACAV proxy as VA's music player. Both supplied failed traces targeted that proxy.
The instructions now require an available official MA entity before VA setup;
the installer rejects proxies and unavailable MA entities. VACAV 0.2.4 no longer
makes its legacy controls unavailable when MA exposure is enabled.

On Garden Athena, both VA playback fields now reference the official MA physical
player. The MA sync group exposes the physical player and lyrics player.
The original, unmodified group blueprint was temporarily enabled for a test; its
trace selected the physical MA player, found the sync group, and sent Radio 2 to
that group. MA reported both members playing. Pause stopped radio playback (MA
reports idle for this radio source); resume and stop worked, and the original
volume was restored. The owner's listening check confirmed radio sound.
Claude's existing automation copy was re-enabled afterwards, with the original
left disabled, preserving the prior selection without duplicate handlers.

Nineteen offline installer/integration regression tests passed, along with the
installer integrity check. Echo Dot Assist source remains unchanged.

The owner also confirmed the longer announcement tone played and radio resumed
after it. A first quiet half-second tone was not heard, so that attempt was not
counted as success. VA's Use announce setting is now enabled for the official MA
media player; Echo Dot Assist retains voice ownership and VA ducking remains zero. Android
audio diagnostics showed an active output track with no write errors during the
test. Tests ended with playback stopped and the original volume restored.

## Automatic Echo Dot Assist arbitration pairing — 25 October 2026

Garden Athena's VACAV connection previously carried voice without an API key and
without forwarding Echo Dot Assist's pairing tags. HA Tags was already enabled; enabling it
again or adding a second ESPHome voice owner was not the missing step.

VACAV 0.2.5 provisions and privately retains an Echo Dot Assist API key, reconnects encrypted,
and bridges only Echo Dot Assist arbitration tags and their state requests. Existing supplied
keys are retained. Interrupted provisioning reuses the stored pending key rather
than rotating it. The README includes adoption, backup and pairing verification.

Live validation on Garden Athena confirmed encrypted API connections and the
voice subscription. After restarting its voice service to trigger immediate tag
retries, Echo Dot Assist logged that it joined the network using a key from another Echo,
confirmed by Home Assistant; the encrypted diagnostic API reported one arbitration
peer. No manual volume-button pairing or general HA action permission was needed.
The Echo Dot Assist source checkout remains unchanged. Thirty offline regression tests and
`install.py verify` passed. This fixes the pairing gap; it does not establish the
cause of the earlier isolated listening-session stall.

## Guided companion installer — 25 October 2026

`./vacav_setup.sh` now prepares the Python environment and runs the companion wizard.
The upstream installer remains responsible for unlocking and system installation.
The companion wizard reuses operational VA weather and HA timezone, gathers local
APK inputs, installs via the existing USB helper, pauses for HA configuration,
and validates the mappings before dashboard deployment. It saves non-secret
choices/USB progress; HA tokens are not saved.

The readiness validator was run read-only against Garden Athena and passed,
including the VA version's device-registry microphone mapping, matching display,
available official MA player, VA weather and configured Home path. Weather/timezone
inheritance returned the existing weather entity and Europe/London. Offline tests
cover stale IDs, unavailable players/microphones, proxy/group rejection, both
VA microphone identifier formats, and the read-only mode's refusal to install.
This turn did not perform another clean wipe or full live guided installation;
that walkthrough remains for owner review. The README's three images are actual
ES8 captures, displayed at half width; the lyrics image previews a separate existing
lyrics installation and does not claim the wizard installs it.

## HACS and automatic connection setup — 25 October 2026

- Public HACS repository: `baileyboy0304/VACAV`, release `v0.3.2`.
- HACS repository validation and CI pass. The private ES8 repository pins the
  public repository as its `VACAV` submodule; a fresh recursive clone and a later
  submodule update both pass component verification.
- 15 VACAV setup tests and 43 installer/music/pairing tests pass. These cover form
  submission routing, discovery before installer handoff, ambiguous/missing
  players, key fallback, universal-player matching and HA player exposure.
- Downloaded 0.3.2 through the actual HA HACS interface, restarted HA and confirmed
  the loaded integration version. Garden Athena's options show its named MA
  player and save successfully without re-entering the existing encryption key.
- Live MA query confirms exactly one match for the ES8's public Sendspin identity:
  its existing physical universal player. MA supplies neither IP nor MAC for this
  player, so the installer obtains the public identity from the device log and
  supplies it through HA's authenticated preparation endpoint. No private key or
  Sendspin pairing token is extracted by this step.
- Echo Dot Assist source and the Android APK are unchanged by this release.
- The final live three-stage HA preparation request passes, including the setup
  protocol acknowledgement. An independent run of the actual Linux installer
  function extracted the expected device IP and public Sendspin identity over USB.
- Post-update audit: all 20 Garden Athena entity mappings unchanged, Assist
  satellite idle, physical MA player available, and live guided readiness PASS.
  This validation did not perform another wipe or a listening/playback test.

## Walkthrough fixes and integration-owned setup — 25 October 2026

Reviewed the owner's Claude walkthrough and recorded the findings/disposition in
[review notes](REVIEW-2026-10-25.md). The reported live voice/music/navigation/reboot
success belongs to the prior build after workarounds.

For VACAV 0.4.0 / APK prototype.11:

- 23 integration tests, 52 installer/auth/pairing tests and 19 reset tests pass.
- Android release build succeeds; all 10 Android unit tests pass, including
  double-tap timing and the rule excluding VACAV's own foreground window.
- The credential-free main installer is tested to make no HA connection. USB
  choices are strictly allowlisted; dashboard rendering accepts only reviewed
  templates and known service IDs. MA matching tests exclude unrelated players.
- An isolated browser UI test confirmed mapping display, physical-audio gating,
  configuration action, explicit dashboard confirmation, backup-before-write,
  three save/read-back checks and completion. This used a simulated HA API, not
  a live dashboard replacement.
- Read-only inspection of the live MA entity registry confirmed the physical
  player's unique-ID format used by the setup code.
- APK signature verification found a different certificate from prototype.10.
  Both READMEs explain the upgrade constraint. No app was uninstalled and the
  working ES8/HA installation was not replaced during these checks.
- The Echo Dot Assist submodule remains unchanged. The TWRP wrapper and redesigned
  HA setup have not yet had a fresh live installation walkthrough. Physical
  double-tap, signed-in streaming, ITVX helper and mute tests remain to be done.
