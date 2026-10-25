# View Assist on Echo Show 8 Gen 2

![View Assist clock on the Echo Show 8 Gen 2](docs/images/es8-clock.png)

*Music player with lyrics — coming soon.*

![TV dashboard with Netflix, BBC iPlayer, ITVX and Apple TV launchers](docs/images/es8-tv.png)

Turn an **Amazon Echo Show 8 Gen 2 (2021, Athena)** into a Home Assistant Assist
voice satellite with visual feedback from **View Assist**. It uses Amazon's
wake-word engine and audio front end (AFE) for microphone processing.
This is a **Linux-only installation guide**.

The setup has three parts:

- **[Echo Dot Assist](https://github.com/Gamer92000/echo-dot-assist/tree/checkers)**
  provides the Amazon wake word, audio processing, Assist voice connection and
  Sendspin audio on the Echo Show. Install its **checkers** branch first.
- **VACAVision** provides the display companion and Home Assistant integration for
  [View Assist](https://dinki.github.io/View-Assist/).
  View Assist's development repository is [dinki/View-Assist](https://github.com/dinki/View-Assist).
  VACAVision is inspired by **MSP1974** and his
  [View Assist Companion App](https://github.com/msp1974/ViewAssistCompanionApp).
  This variant replaces the companion's microWakeWord approach with Amazon's
  wake word through Echo Dot Assist.
- **Optional streaming and example dashboards** add launchers for Netflix,
  BBC iPlayer, ITVX and Apple TV, alongside Home, clock/weather and other
  View Assist views. Apple TV opens in Silk; the other services use Android apps.
  You supply the streaming apps and sign into your own accounts.

The bundled app and Home Assistant integration appear as **VACA_Vision** in
Home Assistant. Commands and folders use `VACAV`.

## Before you start: unlock the Echo Show

For unlocking, use only the maintained **Echo Show 8 Gen 2 / Athena** instructions
in [Echo Dot Assist's checkers branch](https://github.com/Gamer92000/echo-dot-assist/tree/checkers).
Follow its links and requirements for firmware, rooting, recovery and downloads.
This repository does not provide a separate unlock procedure.

**Already unlocked? [Jump to step 1: install Echo Dot Assist](#1-install-echo-dot-assist).**
An unlocked bootloader does not mean rooting and firmware prerequisites can be
skipped: follow the upstream installer's checks for your device's current state.

Have a Linux PC with physical USB access, Git, Android platform-tools (`adb`),
Python **3.11 or later** with its venv package, and room for firmware and backups.
Keep the checkout path free of spaces. Preserve anything you need from the device
before following an upstream operation that clears data, including recovery
backups and streaming APKs. Streaming sign-ins are not preserved by APK exports.

## 1. Install Echo Dot Assist

Clone this repository, including its upstream installer:

```sh
git clone --recurse-submodules https://github.com/baileyboy0304/ES8_Athena.git
cd ES8_Athena
adb devices -l
```

Connect the intended Echo Show by USB. Read the
[upstream Athena guide](https://github.com/Gamer92000/echo-dot-assist/blob/checkers/devices/athena/README.md),
obtain its required downloads, and follow its Linux prerequisites. Then run:

```sh
./echo-dot-assist/scripts/setup.sh athena
```

The `echo-dot-assist/` submodule is an unchanged, recorded revision of the
**checkers** branch. It owns firmware, root, networking and system installation.
Follow its prompts for the existing unlocked state; stop if a stage fails.
Do not repeat unlocking just because the device is already unlocked.

**Finish this step with Echo Dot Assist running and USB access working.**
The bundled VACAVision installer currently checks for model `athena` and firmware
`PS75741.7080N`; it stops on a different build. Keep Echo Dot Assist automatic
updates off while using this candidate's installed-firewall adaptation.

For this combined setup, **do not add a separate ESPHome voice connection for the
same Echo Show**. VACAVision will own that connection in step 4. Other Echo devices
can retain their normal ESPHome integrations.

## 2. Prepare Home Assistant and the setup pages

Have a working **Home Assistant Assist pipeline**, and install:

- **View Assist**, following its [setup documentation](https://dinki.github.io/View-Assist/).
- **Music Assistant server and its Home Assistant integration**, following the
  [Music Assistant installation guide](https://www.music-assistant.io/integration/installation/).
- View Assist's required frontend resources and `custom:button-card`.
  [Dashboard dependencies](docs/DASHBOARDS.md) lists the cards used here.

In the Linux checkout, create the Python environment. Use your installed Python
3.11+ command if it differs from this example:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python install.py verify
python install.py choose --profile es8-gen2
python install.py dashboards --profile es8-gen2
python install.py prepare-dashboards --profile es8-gen2
```

The choices wizard asks for:

- Optional streaming services — answer **No** to all if you only want voice,
  music and View Assist.
- Your weather entity and timezone, for example `weather.home` and `Europe/London`.
- A planned View Assist sensor ID. You will replace this with the actual ID in
  step 7 after creating the View Assist device.
- Your Music Assistant sidebar path. Open Music Assistant in HA and copy the path
  after the host and port; `/music-assistant` is only a placeholder.
- Dashboard names. The defaults are `athena-home`, `view-assist-athena` and
  `athena-tv`. Use different names for each additional display.

`prepare-dashboards` asks for the HA URL and an administrator's long-lived access
token at a hidden prompt. It does not save the token. It creates missing setup
pages and leaves existing dashboards alone. This gives the display a working
landing page before View Assist is configured, avoiding a 404 during first sign-in.

Choices and generated files stay in ignored `installation-data/` folders.
Run later commands from this checkout with the virtual environment activated.

## 3. Install VACAVision and optional streaming apps

The VACAVision APK is bundled. Streaming APKs are **not** bundled. For each selected
service, place compatible Android 9 / ARM32 APKs here:

```text
installation-data/apks/es8-gen2/netflix/
installation-data/apks/es8-gen2/iplayer/
installation-data/apks/es8-gen2/itvx/
installation-data/apks/es8-gen2/apple_tv/
```

The last folder is for Silk if it is missing; the existing Silk installation is
reused. Include every required split APK for iPlayer. Do not rename an XAPK/APKM
archive to APK. See [tested app versions](devices/APK-VERSIONS.md).
If exporting from an existing working device, do so **before** any wipe:
`python install.py device --profile es8-gen2 --export-apps`.

Inspect first, then install:

```sh
python install.py device --profile es8-gen2
python install.py device --profile es8-gen2 --apply
```

With one USB device, selection is automatic. With several, append
`--serial YOUR_USB_SERIAL` from `adb devices -l`. Check the displayed target.
The first command makes no device changes; the second asks before applying them.

The installer installs VACAVision and missing selected apps, selects VACAVision
as Home, applies the timezone and prepares its display permissions. It installs
Simple Keyboard if no working keyboard is selected, so HA sign-in is possible.
For the exported Echo Netflix app, it also restores the matching authentication
APK from the firmware extracted by the upstream installer.

**VACAVision web access is always enabled when installed**, including when no TV
apps are selected, so external artwork can load. Selected streaming apps also
receive TCP 80/443 internet access. This separately adapts the device's installed
firewall, with backups and version checks; the Echo Dot Assist source remains
unchanged. Silk and dashboard websites can use that web access, including their
advertising/telemetry requests. Other internet ports and UDP/QUIC remain blocked.

The installer also offers:

- **Floating streaming controls**: Home, Keep on and Brightness when supported
  video playback is detected. This is how you return from streaming to the display.
- **ITVX compatibility helper**, when ITVX is selected: handles its specific
  Google Play services warning. It does not handle sign-in or playback errors.

Reboot once after installation. Complete VACAVision's on-screen onboarding and
allow the camera/microphone permissions if you want those functions. Check that
tapping a text field opens the keyboard. Then continue with HA pairing below.

## 4. Connect VACAVision to Home Assistant

Mount or otherwise make your HA configuration folder accessible from Linux.
The folder must contain `configuration.yaml`. Install the matching integration:

```sh
python install.py install-ha --ha-config /path/to/ha/config
```

This copies `custom_components/vaca_vision` and the dashboard assets, backing up
existing files under `installation-data/backups/`. **Restart Home Assistant.**

Open **Settings → Devices & services → Add integration → VACA_Vision**:

1. Select the **ES8 with upstream Echo Dot Assist** role. Older builds abbreviate
   the upstream name in this label; the role identifier is `standard_upstream_eda`.
2. Enter a friendly **Device name**, such as `Garden Athena`.
3. Enter the Echo Show's IP address, VACAVision port **26900**, and Echo Dot Assist
   port **26053**.
4. If Echo Dot Assist already has an API encryption key, supply it. Otherwise
   leave it blank: VACAVision provisions and privately stores a key automatically.
5. Set **Home/startup dashboard** to `/athena-home/home`, or the home path prepared
   in step 2. Select your intended Assist pipeline.

Use an internal HA HTTP address reachable by the Echo Show for Assist replies;
this pinned Echo Dot Assist version does not fetch native replies over HTTPS.
The display's browser sign-in is separate and may use HTTPS.

**Sign into HA on the Echo Show itself.** You should see the setup page. This also
registers the display for View Assist. Pairing the integration does not sign in
the display browser. If the page is missing, rerun `prepare-dashboards` with the
matching names, then use the VACAVision device's **Refresh dashboard** button.

The integration loads HA Tags and forwards the authenticated pairing tags needed
for Echo arbitration. Check **Settings → Tags** for recent scans and the Echo Dot
Assist arbitration page for peers without a missing-key warning. A retry after
previous failures can take up to five minutes. No separate ESPHome voice owner
or general HA-action permission is needed. An ESPHome Ignore marker for this
Echo Show is expected. Back up HA's configuration, including private `.storage`,
which holds the generated key.

## 5. Connect the music player

In Music Assistant, pair the Echo Show's **Sendspin player** and give it the
friendly device name. In that player's settings, turn **Expose player to Home
Assistant** on. Wait for its available `media_player.*` entity under the official
**Music Assistant integration**. Test play, stop and volume from Music Assistant.

In VACAVision options select your Music Assistant integration and the **MA player
ID**. This is Music Assistant's player ID, not an HA entity ID.

For View Assist's playback settings in the next step, use the official **Music
Assistant entity for the physical Echo Show player**. Do not select the VACAVision
music proxy or import that proxy back into Music Assistant through its HA player
provider. Entity names can retain an old hardware name; check which integration
owns the entity rather than judging by its name.

**Lyrics support: coming soon.** The installer does not set up a lyrics server.
If you already use a separate lyrics player, add it and the physical Sendspin
player to an MA sync group and expose both members and the group to HA. Keep
View Assist's music setting on the physical player; group-aware blueprints can
then find its group through `group_members`.

## 6. Create the View Assist device

Once the Echo Show is signed into HA, create its device under
**Settings → Devices & services → Add integration → View Assist**. Select a
display-and-audio device and use the same friendly name as VACAVision.

Use the new device's actual identifiers:

| View Assist setting | Value |
|---|---|
| Display device / display ID | The **value** of VACAVision's display-device sensor, starting `va-`; not the sensor entity ID |
| Microphone device | VACAVision's combined `assist_satellite.*` entity |
| Media player (playback/alerts) | Official Music Assistant entity for the physical Sendspin player |
| Music player | The same official Music Assistant physical-player entity |
| Dashboard | `/view-assist-athena`, or your chosen dashboard name |
| Home/default view | `/view-assist-athena/clock` (use `clock` if the field asks only for the view name) |
| Weather | Your `weather.*` entity |
| Use announce | Enabled, so compatible blueprints interrupt and resume music for alerts |
| Ducking | Start at zero; VACAVision and Echo Dot Assist handle voice/music focus |
| Screen mode | Fullscreen/kiosk mode appropriate for this display |

Leave VACAVision's native Echo Dot Assist voice indicator enabled to avoid
showing two listening bars.

If your View Assist version's picker does not include VACAVision or
`assist_satellite.*`, use its normal configuration API through this helper:

```sh
python install.py create-view-assist --profile es8-gen2
```

It asks for the HA URL/token and the mapping above, validates it and reviews it
before creating the device. It does not patch View Assist or delete existing
devices. If the display ID is not found, complete the on-display HA sign-in in
step 4 first. After creation, set dashboard/default-view and weather options in
the new View Assist entry's **Configure** menu.

Copy the new **View Assist sensor entity ID** for the next step. Do not copy an old
pre-reset display ID or sensor. Resolve any View Assist overlay Repair issue;
VACAVision can select the native-only overlay after the microphone mapping exists.

## 7. Install the example dashboards and check the result

Rerun the choices wizard, replacing the planned sensor ID with the actual View
Assist sensor from step 6. Keep the same dashboard names:

```sh
python install.py choose --profile es8-gen2
python install.py deploy-dashboards --profile es8-gen2
```

Enter the HA URL/token when asked. Deployment validates the entities, backs up
existing dashboard configurations, lists its targets and asks before replacing
them. Backups are in `installation-data/backups/`. Use unique names if you want
to preserve other dashboards.

Home links to View Assist, Music Assistant in a frame with a Home button, and TV.
The TV page includes only the streaming services you selected. View Assist
provides the clock/weather and standard views. Sign into your selected streaming
services on the Echo Show.

Check the following before considering setup complete:

- The clock appears, Home/TV navigation works, and Music Assistant has a Home button.
- The Amazon wake word starts Assist and a spoken request receives a reply.
- A radio request plays **on this Echo Show**; pause, stop and volume control it.
  A spoken “Playing…” response by itself does not prove playback succeeded.
- An alert interrupts music and music resumes as intended.
- Selected streaming apps open and play, and the floating Home control returns
  to VACAVision. **Known issue:** ITVX live audio may continue after returning Home.
- Artwork loads when using an external music/lyrics dashboard. Missing artwork
  can mean VACAVision's required firewall rules were not applied.

If a View Assist version restores an old Home path, check the sensor's
`home_screen` attribute. Correct that satellite only using **View Assist: Set
state or attributes**, with `home_screen: /view-assist-athena/clock` (or your path).
Do not change the shared Master Configuration to fix one display.

## Resetting or updating an existing installation

A fresh installation does **not** require this repository's reset tool.
For an intentional return to the unlocked baseline, see the separate
[ES8 reset tool](reset-es8/README.md). It erases apps and user data and requires
verified recovery images and explicit confirmation.

As part of a clean reset, back up HA and remove only this Echo Show's old
**View Assist** and **VACA_Vision** entries, plus an obsolete Sendspin pairing if
invalidated by the wipe. Preserve shared configuration and other devices.
Recreate them in steps 4–6; do not reuse stale display IDs. A device wipe alone
does not clean up HA registrations.

For a routine upgrade, retain the existing entries and sign-ins. Do not uninstall
VACAVision to bypass an APK signing-key mismatch. See [recovery and reruns](docs/RECOVERY.md).

## Project files

| Folder | Purpose |
|---|---|
| `echo-dot-assist/` | Unchanged upstream checkers source and installer |
| `VACAV/` | VACAVision app, bundled APK and HA integration |
| `devices/es8-gen2/` | Echo Show profile and streaming launchers |
| `devices/dashboards/` | Example dashboards and frontend assets |
| `installation-data/` | Private app exports, choices, generated files and backups; ignored by Git |
| `reset-es8/` | Separate, explicitly requested baseline reset tool |
| `maintenance/` | Version records, component checksums and maintainer checks |

This remains an installation candidate under owner review.
See [validation notes](docs/VALIDATION.md), [manual checks](docs/ACCEPTANCE.md) and
[licences and attribution](docs/NOTICE.md).
