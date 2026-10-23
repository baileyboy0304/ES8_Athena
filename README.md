# ES8 Athena

Install **echo-dot-assist + VACAV + View Assist** on an Echo Show 8 Gen 2.
A separate **Portal Plus Gen 2** profile is included for VACAV and dashboards.

**This README is the complete installation guide.** Start with preparation below,
then follow steps 1–8 in order. Moving from Windows? The
[Linux handover](docs/LINUX-HANDOVER.md) lists the private files to bring across.

Use the normal echo-dot-assist installer and the bundled VACAV upstream prototype.
Do not use the separate Athena Assist or Crown Assist projects. Do not run EDA or
ES8-specific steps on Portal; Portal uses its own profile in steps 1 and 5–8.

## Additional preparation: unlock files and firmware

Before connecting or wiping the ES8, create a private download folder on your Linux PC:

```sh
mkdir -p "$HOME/ES8-Athena/unlock"
```

Download the following files into that folder, keeping their original filenames:

| File | Where to get it | When needed |
|---|---|---|
| `saiyaku-athena-v1.0.0.zip` | Attachments in the [XDA Athena unlock/root/TWRP thread](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-8-2nd-gen-2021-athena.4804958/) | For a device that still needs unlocking; retain it with your recovery files |
| `boot-root.zip` | Attachments in the same XDA thread | Required for this clean installation, including the policy tool EDA uses |
| `update-kindle-athena-PS75741_user_7080_0036274153604.bin` | The separate [stock firmware download reference linked by EDA](https://ftvdb.com/echo/firmware/com.amazon.athena.android.os/84ffb126664e1a3569404ba61d580e05-36274153604-fire-os-7574-1-ps75741-7080-2026-09-29/) | Required pinned firmware, PS75741.7080N |

If you already unlocked the device, you may already have the XDA archives. Reuse
those files only after checking the hashes below. Unlocking does not establish
that you have this exact stock firmware, a recovery backup, or streaming APK exports.
Do not run the unlock again merely to prepare these downloads. Keep the ZIPs intact;
the unchanged EDA installer handles extraction and the applicable device steps.

After cloning this repository **with submodules**, run these commands from its root
to copy the required downloads to EDA's expected location:

```sh
mkdir -p echo-dot-assist/firmware/athena
cp "$HOME/ES8-Athena/unlock/boot-root.zip" echo-dot-assist/firmware/athena/
cp "$HOME/ES8-Athena/unlock/update-kindle-athena-PS75741_user_7080_0036274153604.bin" echo-dot-assist/firmware/athena/
```

If unlocking is needed, also copy its archive:

```sh
cp "$HOME/ES8-Athena/unlock/saiyaku-athena-v1.0.0.zip" echo-dot-assist/firmware/athena/
```

Check the copied files against the pinned upstream SHA256 values:

```sh
(cd echo-dot-assist/firmware/athena && sha256sum --check <<'SHA256'
741d904f7e2616c70be2c10f3466efb515769632779546a869f5591a6a9c827a  boot-root.zip
7a76fe6f84847c183e617fe6bb0c311faa9ad5ab56803b3a6115fb763c422a1a  update-kindle-athena-PS75741_user_7080_0036274153604.bin
SHA256
)
```

If you copied the unlock archive, check it too:

```sh
(cd echo-dot-assist/firmware/athena && sha256sum --check <<'SHA256'
6d48b4b253fa6cbecb9166c87c0177be09c8a02e5f2efd2bc0d0aec939626218  saiyaku-athena-v1.0.0.zip
SHA256
)
```

Every checked file must report `OK`. Stop on a missing file or mismatch; do not
rename a different firmware build or bypass EDA's verification.

**Also preserve your own device data before a wipe ([step 2 below](#2-preserve-what-you-need-before-wiping)).** A verified TWRP
backup must be made from your ES8 and kept outside this repository. Streaming
APKs must be exported from your existing installation or supplied separately if
you select those services. Neither is included in the XDA unlock downloads.
The first wipe waits until recovery and all required installation inputs are verified.

## 1. Configure dashboards and choose optional streaming apps

For the Windows-to-Linux move, complete [Linux handover](docs/LINUX-HANDOVER.md) first.
Run the device installation on Linux with physical USB access.

Keep the repo in a path **without spaces**. Install Python 3.11+ and Android
platform-tools (`adb` on PATH). In a terminal opened in this repo:

```sh
git submodule update --init echo-dot-assist
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python install.py verify
python install.py choose --profile es8-gen2
python install.py dashboards --profile es8-gen2
```

Streaming is optional. The wizard asks Y/N for Netflix, BBC iPlayer, ITVX and
Apple TV; every answer defaults to No. You can answer No to all four and still
use View Assist and Music Assistant. Run the wizard even without streaming,
because it also saves the dashboard settings described below.
Apple TV uses the existing Silk browser on ES8, not a native Apple TV APK.
With no streaming apps selected, the TV page shows an empty-state message and
the fresh-install streaming firewall adaptation is skipped.
Selected ES8 apps receive EDA firewall TCP 80/443 exceptions to any host, including
advertising and telemetry; Silk's exception covers any website it opens. Other
internet ports and UDP/QUIC stay blocked. No Settings/SystemUI retention is added.

Also enter the intended **VA sensor entity** (not VACAV's display-ID sensor),
weather entity and the actual Music Assistant sidebar path. To get the MA path,
open Music Assistant in HA on your computer and copy everything after the host
and port; it may be an add-on ingress path. The suggested `/music-assistant` is
only a placeholder. Create the VA sensor in step 7, then rerun the wizard if its ID differs.

Default dashboard slugs are `athena-home`, `view-assist`, `athena-tv`. Portal uses
`portal-home`, `view-assist-portal`, `portal-tv`. Use unique slugs if adding another
display. The generated VA dashboard binds to one VA sensor; do not reuse one
generated configuration for several different VA sensors.

Prepared YAML/JSON and `android.conf` are under `installation-data/generated/es8-gen2/`. Local choices
are under `installation-data/choices/es8-gen2.json`. Neither is published.

## 2. Preserve what you need BEFORE wiping

Use the [APK version reference](devices/APK-VERSIONS.md) to identify the builds
used in the trial, including iPlayer's required splits. Streaming APKs are not
bundled. Silk is already installed on the current ES8 and is reused when present;
an APK is only needed if it is missing after the reset and EDA installation.

Do this while the currently working setup is still intact. Keep a verified TWRP
backup of your own device outside this repo, including its matching firmware and
recovery information. Retain EDA update/API keys and MA pairings privately if you
intend to restore identities. A wipe can erase these and all streaming logins.

Export the installed streaming APKs (including split APKs) for personal reinstall:

```sh
adb devices -l
python install.py device --profile es8-gen2 --export-apps
```

`--serial` is optional with exactly one USB ADB device connected. With multiple
USB devices, add `--serial YOUR_USB_SERIAL` using the serial from `adb devices -l`.
Automatic selection uses USB only and stops if it cannot select one device.
This applies to export, inspection and installation commands.

This is read-only on the device. Exports go into ignored `installation-data/apks/es8-gen2/`,
with hashes in `installation-data/es8-gen2-apps.json`. Missing apps are reported as zero APKs;
obtain their compatible ARM32/Android 9 builds before selecting them for install.
An export does not preserve subscriptions, logins or guarantee DRM after a reset.
Do not rename an XAPK/APKM to APK: extract and supply all required split APKs.
Alternatively place each service's APK(s) in `installation-data/apks/es8-gen2/SERVICE_ID/`.
Service IDs are `netflix`, `iplayer`, `itvx`, `apple_tv` (the latter contains Silk).

**The first wipe is deferred until the agent's Linux walkthrough.** The owner has
authorised that first wipe once backup/recovery and installation inputs are ready.
The second wipe, for the owner's own walkthrough, requires a later explicit OK.
This repo has no unattended wipe command. A data-only
reset does not undo old system modifications; start your walkthrough from the
known unlocked stock firmware baseline you intend to support, not a mixed install.
Preserve the unlocked bootloader/recovery. Do not flash Gen 1/Crown images.

## 3. Gather echo-dot-assist prerequisites on Linux

Use a Linux PC with working physical USB access (or properly passed-through USB),
enough space for firmware, build tools and a separate full-device backup; reserve
at least 20 GB for this walkthrough. Install the tools EDA requests. The pinned supported firmware is
**PS75741.7080N**, model `athena` / AEOAT, Android 9 / ARM32.

Read `echo-dot-assist/devices/athena/README.md`. Put the requested files
in `echo-dot-assist/firmware/athena/`:

- `update-kindle-athena-PS75741_user_7080_0036274153604.bin` — pinned stock firmware.
- `boot-root.zip` — the pinned root archive from EDA's linked XDA instructions.
- The unlock archive only if EDA actually needs unlocking; an already unlocked
  device should use its detected existing state. Do not re-unlock just for this repo.

EDA verifies the expected downloads and explains missing tools. Its Athena README
links their sources and `device.conf` holds firmware hashes. Rooting is separate
from unlocking: EDA needs its root prerequisites even on an unlocked device.
Use the normal upstream installer's supported release/source choice. No patched
EDA build is required. If building, the guided installer obtains its pinned Linux NDK.
Do not substitute the older main-branch checkout lacking Athena support.

## 4. Run the developer's echo-dot-assist installer

With the prepared device powered and connected by USB:

```sh
python install.py verify
./echo-dot-assist/scripts/setup.sh athena
```

This runs the upstream script directly; echo-dot-assist owns
root/build/lockdown/network/system installation. Follow its prompts. Do not skip
a failed stage. It can resume after interruption. Its explicit destructive
confirmations still apply; check the target carefully. Use `./echo-dot-assist/scripts/setup.sh athena --dry-run`
to see EDA's sequence, but note upstream dry-run still checks local prerequisites.
There is no root-level `echo-dot-assist/setup.sh` in this upstream branch and no
additional shell wrapper in this package. EDA is shorthand for echo-dot-assist.

After EDA boots, retain USB access. Do not add a separate ESPHome voice owner in
HA for this same ES8: VACAV will own its EDA connection. EDA uses port **26053**.
Keep EDA online updates **off** during the prototype walkthrough. Streaming
exceptions are applied in the next step, once the apps exist.

## 5. Install VACAV and selected streaming apps by USB

Continue on Linux, with private APK exports copied into `installation-data/` as described in
the handover guide. The same Python entry point also supports Windows ADB:

```sh
adb devices -l
python install.py device --profile es8-gen2
python install.py device --profile es8-gen2 --apply
```

These commands select the only connected USB ADB device. Add `--serial YOUR_USB_SERIAL`
if several USB devices are connected. The detected target is shown before installation.

The run without `--apply` inspects prerequisites only. `install.py device` calls
`devices/install-device.py` for you. The apply run reviews the target and installs the bundled VACAV prototype.10 APK, installs missing selected apps, saves
the selected root-owned streaming policy, grants brightness/overlay access and selects
VACAV as Home. Existing app data is retained; incompatible signatures/downgrades
stop instead of uninstalling apps.

When streaming is selected, this stage separately adapts the installed EDA firewall
scripts and writes `/data/local/es8-athena-streaming.conf`. It backs up the original
files and refuses an unexpected installed version. The existing EDA firewall
watcher remains in charge. The `echo-dot-assist/` checkout and its installer remain unchanged.
With no services selected on a fresh install, the firewall is left unchanged.
Reboot once after applying the streaming stage before checking playback.

Two explicit options appear during installation:

- **Floating streaming controls / DUMP:** allows VACAV to inspect bounded active
  window/media-session status so Home, Keep on and Brightness can appear during
  supported playback. Without it, that popup stays hidden. Settings/SystemUI are
  not added back. This is especially useful for returning from TV to VACAV.
- **ITVX compatibility helper:** only if ITVX is selected. Accessibility permission
  lets VACAV dismiss that app's exact English Google Play services warning. It
  does not dismiss sign-in, payment or playback errors. Other enabled accessibility
  services are preserved.

Follow VACAV onboarding and sign into HA on the display. Its HA connection port
is **26900 on Athena**. Do not use the generic 10900 value for this ES8.
Set the initial dashboard to `/athena-home/home` (or your chosen home slug).

**Portal:** use `--profile portal_plus_gen_2` for both commands. The bundled standard Portal
APK uses **10900**. No EDA installation, root/firewall changes, HOME selection or
ES8 popup permissions are applied to Portal. Complete its normal VACAV onboarding.

## 6. Install and configure VACAV in Home Assistant

Install View Assist and Music Assistant using their maintained installation
instructions if absent. Have a working HA Assist pipeline first. The trial used
HA 2026.9.x; newer HA versions remain part of the manual compatibility check.

Mount your HA configuration folder/share on the installer computer, then run:

```sh
python install.py install-ha --ha-config /path/to/ha/config
```

Windows example: `--ha-config "\\HOMEASSISTANT\config"`. The target must contain
`configuration.yaml`. This copies the matching `custom_components/vaca_vision`
including bundled APKs and the dashboard assets under `www/es8-athena/`.
Existing integration files are backed up under this repo's ignored `installation-data/backups/`.
Restart HA. Do not install both this integration and a second copy of the same domain.

Under **Settings → Devices & services → Add integration → VACA_Vision**, connect
to the already installed ES8 app; select **ES8 with upstream EDA (prototype)**
(`standard_upstream_eda`). In the confirmation form, enter a **Device name**,
for example `Kitchen Athena`, before completing pairing. This names the HA
integration and device, and supplies the device name for newly created entities.
You can change it later in VACAV integration options; existing entity IDs and
manual HA device-name overrides are retained. The Android discovery label and
EDA/Sendspin name remain separate. Enter the ES8's address and VACAV port **26900**.
In the EDA fields use port **26053**, and supply its ESPHome Noise PSK if encryption
is enabled (from your EDA setup/settings; leave blank only if not configured).
Keep the secret out of dashboard YAML and Git.

Choose the desired Assist pipeline on the resulting VACAV assistant device.
Use an HA internal HTTP address reachable from the ES8: this pinned EDA revision
does not support native HTTPS reply fetching. That is distinct from browser HA
sign-in, which may use HTTPS.

For music, discover/pair EDA's Sendspin player in MA. In VACAV options choose the
MA integration entry and **MA player ID** (`ma_player_id`, not an HA entity ID).
VACAV exposes its music proxy on the same HA device. Turn **Expose player to Home Assistant** OFF for that EDA player
in Music Assistant before saving VACAV's music mapping; the integration explicitly
rejects a player still exposed separately. This does not disable the MA player.
Avoid a second active voice connection from a separately configured ESPHome integration. VACAV creates an
ESPHome Ignore marker to suppress duplicate discovery; this is expected.
If an existing ESPHome owner blocks setup, first preserve its settings, then remove
that duplicate voice ownership through HA. Do not remove unrelated Dot entries.

For Portal choose its actual role: standard display only, or Display and Dot with
Sendspin if pairing an EDA Dot. The Dot role uses the separately configured native
ESPHome Dot satellite and restores ownership when unpaired; it is not the same-device
ES8 role. Keep Portal's existing pairing if it is already correct.

## 7. Required View Assist settings (manual mapping)

Create/open the VA device in View Assist. Copy the actual IDs from your HA device
pages; never reuse the old pre-wipe display UUID or example sensor names.

| VA setting | ES8 EDA + VACAV value |
|---|---|
| Display device / display ID | **Value** of VACAV's display-device sensor, the `va-…` identifier; not its `sensor.*` entity ID and not the HA registry device ID |
| Microphone device | VACAV's combined `assist_satellite.*` entity |
| Media player | VACAV's combined speaker/music proxy `media_player.*` |
| Music player | The VACAV proxy mapped to EDA's MA Sendspin player |
| Dashboard | `/view-assist` (or the profile's actual VA slug) |
| Home/default view | `/view-assist/clock` or the view field `clock`, according to the VA UI field |
| Weather entity | Your actual `weather.*` entity |
| Ducking | Start at zero in VA; this VACAV/EDA role owns voice/music focus to avoid double attenuation |
| Screen/fullscreen mode | Choose the VA mode appropriate for the display; verify no unwanted HA header/sidebar |
| Voice indicator | Leave VACAV's **Use EDA voice indicator only** on for ES8 |

If the installed VA selector cannot select `assist_satellite.*`, use a VA version
that supports that domain; don't select an unrelated microphone just to continue.
For Portal + Dot, select VACAV's combined Dot satellite and reply Speaker entity;
its music field uses the Portal's MA Sendspin player. Display-only Portal does not
have an ES8 voice satellite to map.

VACAV can install/select the native-only VA overlay once the correct microphone
mapping exists, even if VA is created later. It does **not** create all of these VA
mappings for you. Resolve any VA overlay Repair issue in HA. Keep the normal VA
overlay on Portal. The native-only ES8 option avoids duplicate animated voice bars.

## 8. Install the dashboards

Install the VA frontend/custom elements and required Lovelace cards first, using
the View Assist documentation. The shipped configurations use `custom:button-card`
and the standard VA card dependencies; [the dashboard inventory](docs/DASHBOARDS.md)
lists the detected custom card types. Restart/refresh the frontend after adding
resources. The installer does not silently install HACS packages.

Correct the wizard's VA entity if needed, then:

```sh
python install.py choose --profile es8-gen2
python install.py deploy-dashboards --profile es8-gen2
```

Enter the HA base URL and an administrator's long-lived access token at the hidden
prompt. It is used in memory, not saved. The installer checks your VA/weather
entities, backs up any existing dashboard configs, shows the three target slugs,
and asks before replacing them. Backups are timestamped under `installation-data/backups/`.
Replacing `view-assist` replaces its whole dashboard: choose a new slug if you
want to keep your existing dashboard and set the VA device dashboard accordingly.

Repeat with `--profile portal_plus_gen_2` to install its separate configuration. In VACAV,
set Home/startup dashboard to the corresponding `/...-home/home`.
In VA set its default view to the corresponding `/view-assist.../clock`.

Sign into each chosen streaming service on the device. Check [manual acceptance](docs/ACCEPTANCE.md).
Known issue to check explicitly: ITVX live audio may continue after returning Home.
Report the step number and what you saw if anything is unclear; there is no need
for exhaustive automated testing before this walkthrough.

## Repository layout

```text
ES8_Athena/
├── echo-dot-assist/       unchanged developer checkers branch and installer
├── VACAV/                Android app, HA integration and bundled VACAV APKs
├── devices/
│   ├── es8-gen2/          ES8 profile.json
│   ├── portal_plus_gen_2/ Portal Plus Gen 2 profile.json
│   ├── dashboards/       updated clock/weather and standard View Assist views
│   ├── install-device.py USB helper called by install.py device
│   ├── streaming.py      optional installed-firewall configuration
│   └── streaming/        supporting firewall functions
├── docs/                 setup, recovery, testing and attribution
├── maintenance/          version records, checksums and developer checks
├── installation-data/    your private APKs, choices, output and backups
├── install.py            VACAV/device/dashboard installation entry point
└── requirements.txt      Python dependencies for install.py
```

`installation-data/` contents are excluded from Git except its explanatory README.
Firmware stays in the upstream installer's ignored `echo-dot-assist/firmware/`.
Hidden `.git*` files are Git configuration. `maintenance/` is for maintaining this
package; you do not need to edit it to install. Each support folder has a short README.

## Included dashboards and streaming

Home has three launchers: **View Assist**, **Music Assistant** and **TV**.
VA includes your updated clock/weather plus the standard upstream views, with
Home and TV icons. TV shows only services selected in the Y/N wizard.

ES8 choices are Netflix Echo, BBC iPlayer, ITVX and Apple TV through Silk.
The [APK version reference](devices/APK-VERSIONS.md) lists the exact builds used.
Users supply their own streaming apps; the existing Silk installation is reused.
Portal Plus Gen 2 retains its native launchers, including SStv. Optional streaming
installation adjusts the device's installed firewall; the upstream source and
installer remain unchanged. No streaming selection means no firewall adaptation
on a fresh install.

## Review status

This is a private installation candidate. Limited offline checks pass; the Linux
clean install and owner testing are pending. ITVX live audio continuing after Home
is a known unresolved trial issue. See [validation](docs/VALIDATION.md).

The owner reviewed this layout and approved the private GitHub transfer on
23 October 2026: [baileyboy0304/ES8_Athena](https://github.com/baileyboy0304/ES8_Athena).
Device work waits for Linux; the second wipe requires your later explicit OK. Community
publication follows acceptance. Licences and attribution are in [NOTICE](docs/NOTICE.md).
