# View Assist on Echo Show 8 Gen 2

### View Assist homepage — clock page

<img src="docs/images/es8-clock.png" alt="View Assist clock on the Echo Show 8 Gen 2" width="640">

### Mediaplayer with lyrics (coming soon)

<img src="docs/images/es8-lyrics.png" alt="Music player with artwork and lyrics on the Echo Show" width="640">

### Streaming services support

<img src="docs/images/es8-tv.png" alt="Netflix, BBC iPlayer, ITVX and Apple TV launchers" width="640">

Turn an **Amazon Echo Show 8 Gen 2 (2021, Athena)** into a Home Assistant Assist
voice satellite with visual feedback from **View Assist**. It uses Amazon's
wake-word engine and audio front end (AFE) for microphone processing.

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

## Prerequisites

- A Linux PC with physical USB access, Git, Android platform-tools (`adb`),
  Python **3.11+** and its venv package. Keep the checkout path free of spaces.
  Allow at least **8 GB** free space. The pinned Echo Dot Assist version builds
  from source, downloading an Android NDK of about **1 GB** plus build tools.
  Its installer offers to install missing tools, including `brotli`, using sudo.
- **View Assist already installed and operational in Home Assistant**, including
  its frontend resources and a working Assist pipeline. This guide adds an Echo
  Show to your existing setup.
  See [View Assist documentation](https://dinki.github.io/View-Assist/) if needed.
- Music Assistant server and its official HA integration already operational.
  This setup uses its physical Echo Show player for music and announcements.
- The dashboard card dependencies, including `custom:button-card`, from
  [the dashboard inventory](docs/DASHBOARDS.md).
- An existing Home Assistant administrator browser session for **VACAV Setup**.
  The Linux installer needs no HA login, password, MFA code or access token.
- Your own compatible streaming APKs if you choose those services. The wizard
  asks for their folder and installs them; proprietary APKs are not bundled or
  automatically downloaded. See [tested versions](devices/APK-VERSIONS.md).

Preserve device data, recovery backups and streaming APKs before following any
upstream operation that wipes data. APK exports do not preserve account sign-ins.

## 1. Run the Echo Dot Assist installer — unlock and install

Clone this repository with its upstream installer:

```sh
git clone --recurse-submodules https://github.com/baileyboy0304/ES8_Athena.git
cd ES8_Athena
```

For an existing checkout, update its linked components before continuing:

```sh
git pull
git submodule update --init --recursive
```

Follow the **Echo Show 8 Gen 2 / Athena** instructions in
[Echo Dot Assist's checkers guide](https://github.com/Gamer92000/echo-dot-assist/tree/checkers),
including its downloads and prerequisites, then run:

```sh
./echo-dot-assist/scripts/setup.sh athena
```

**That installer handles unlocking, firmware, rooting and Echo Dot Assist
installation.** Its pinned version requires **`saiyaku-athena-v1.0.0.zip`** with
the exact checksum in its Athena guide. A newer `v1.1.x` archive is not a drop-in
replacement; do not rename it or bypass the checksum. Follow the pinned guide’s
download requirements for a device that still needs unlocking.

**Already unlocked and sitting in TWRP after our reset?** Use this command instead
of the upstream command above, after placing the guide’s `boot-root.zip` in
`echo-dot-assist/firmware/athena/`:

```sh
./echo_setup.sh
```

This checks the USB model, recovery and root ZIP checksum, asks before rooting,
then boots the rooted system and starts the unchanged upstream installer afresh.
Choose **Keep it as it is** when it detects the rooted Echo. It does not need the
unlocker ZIP in this state. An unlocked but unrooted Echo in TWRP does **not** get
that prompt from the unmodified installer’s initial Downloads step.

The companion installer checks for Athena firmware `PS75741.7080N` and stops on a
different build. After a reset, enter your Wi-Fi SSID and password when the Echo
Dot Assist installer asks. Do not complete Amazon’s touchscreen/Alexa setup.

**Does cloning fetch the latest checkers code? No.** It fetches the exact upstream
commit recorded by this repository, from the checkers branch. The branch setting
in `.gitmodules` does not make a normal clone follow the latest tip. This keeps
our checks and firewall adaptation matched to the reviewed upstream version.
Updating that revision is a maintainer task followed by compatibility checks.

**Ignore the ESPHome “Add device” instruction on Echo Dot Assist’s done-screen.**
For this combined setup, VACAVision owns the voice connection;
there should be only one voice owner for this Echo Show. Keep existing ESPHome
entries for other devices. If this Echo Show already has one, preserve its API
key/settings before removing that duplicate ownership.

Echo Dot Assist installs and runs Sendspin and supplies the Music Assistant
pairing token. Pair the player in Music Assistant; VACAVision will enable its
exposure to HA. View Assist's device mappings are completed during the HA handoff.

To log into the Echo Dot Assist settings page, choose **Ask the Echo**, then press
both volume buttons together and release within about **one second**. Athena has
no action button. Holding both for two seconds invokes Echo pairing instead.
Back up `echo-dot-assist/secrets/update.key`; it signs device updates. The secrets
folder also contains your Wi-Fi credentials—keep it private.

Keep automatic Echo Dot Assist updates off while using this candidate's
installed-firewall adaptation. Retain USB access for the next step.

## 2. Install VACAVision and your selected streaming apps

In HA, open **HACS → ⋮ → Custom repositories**, add
`https://github.com/baileyboy0304/VACAV` as an **Integration**, then download
**VACAVision 0.4.0 or later** and restart HA. The recursive clone also fetches the
tested VACAV app/source revision.

From this repository’s root:

```sh
./vacav_setup.sh
```

**Updating an older VACAV APK:** this build uses the Linux signing key. An older
APK signed with the previous key cannot be updated in place. The installer stops
on Android’s signature mismatch and never uninstalls it automatically. Preserve
the working installation until you can use the original signing key or deliberately
reinstall VACAV and sign into HA on the display again. Fresh installs are unaffected.

The wizard asks for the device name, dashboard names and Y/N for Netflix, BBC
iPlayer, ITVX and Apple TV. Use unique dashboard names for each additional display.
It installs VACAVision and the selected apps, prepares the keyboard, Home app and
permissions, and offers a reboot. It waits for Android, Wi-Fi and VACAVision to
start rather than immediately trying to connect.

When an app is missing, choose the folder containing its APK files. Keep each
service’s files in its own folder, including all matching splits. **Apple TV needs
a Silk browser APK after a clean reset**; there is no native Apple TV APK here.
See [tested APK versions](devices/APK-VERSIONS.md).

Answer **Yes** to floating controls if you want Home, Keep on and Brightness over
other apps. A single tap during recognised playback shows the controls; a double
tap can show them on sign-in/browsing screens too. Android passes these taps to
the underlying app, so a player may also seek. The popup hides after five seconds
and does not appear over VACAVision itself. The DUMP permission is used to identify
the foreground window. For ITVX, answer **Yes** to the exact Google-services-warning
helper if you want that known warning dismissed automatically; cookie choices and
account sign-in still need your input.

On the ES8, allow VACAVision’s camera and photos/media/files permission prompts.
These prompts are separate from the voice microphone supplied by Echo Dot Assist.
The app may show **Waiting for connection** until the next step.

VACAVision always receives TCP 80/443 web access for artwork and embedded content.
Selected streaming apps receive the same access, including advertising/telemetry;
other internet ports and UDP/QUIC remain blocked. The installer backs up and checks
the installed firewall before adapting it.

The wizard writes **non-secret choices** into VACAVision’s private app folder over
USB: device name, dashboard names, selected services and public Sendspin identity.
It does not send HA passwords, access tokens or encryption keys to the Echo. These
choices are proposals; adding the device and replacing dashboards still require
your existing HA administrator session.

Choices and USB progress stay in ignored `installation-data/`. Run the same
command to resume. After Linux setup finishes, continue in HA—there is no terminal
HA login and no need to return to the terminal to install dashboards.

## 3. Add the Echo in Home Assistant

Pair this Echo’s Sendspin player in Music Assistant using the pairing token on
the Echo Dot Assist done-screen or settings page (`http://DEVICE_IP:28931/`).
Reuse an existing valid pairing. VACAVision enables that physical player’s exposure
to HA automatically. Echo Dot Assist runs Sendspin; VACAVision’s own engine stays
disabled in this role.

### Connect Home Assistant to VACAVision

**1. Add the discovered device.** Open **Settings → Devices & services**.
Under **Discovered**, select **Add** on the **VACA_Vision** card.

<img src="docs/images/setup/00-discovered-device.png" alt="VACA_Vision discovered card with Add button" width="618">

If you already have VACA_Vision devices, you can also open the integration and
select **Add** on its **Discovered** row.

<img src="docs/images/setup/01-discovered-integration.png" alt="Discovered VACA_Vision device within the integration page" width="593">

**2. Confirm the device name**, then select **Submit**. The Echo Show role and voice connection are selected automatically. VACAVision connects
the matching Music Assistant player and exposes it to Home Assistant.

<img src="docs/images/setup/02-confirm-discovered.png" alt="Add this Echo Show: confirm the device name and submit" width="313">

<details>
<summary>If the Echo Show does not appear under Discovered</summary>

Check that VACAVision is running and HA can reach the Echo Show's IP address.
If VACA_Vision was previously ignored, show ignored integrations and stop ignoring
that discovery. Keep this Echo’s separate ESPHome discovery ignored.
Select **Add integration**, search for `VACA`, and choose **VACA_Vision**.
If you already have the integration, open it and select **Add device**.

<img src="docs/images/setup/01-select-integration.png" alt="Add integration search results: choose VACA_Vision" width="338">

Choose **Connect an installed device by IP address**.

<img src="docs/images/setup/03-connect-menu.png" alt="Connect VACAVision menu with the IP-address connection option" width="314">

Enter the Echo Show's IP address shown by Echo Dot Assist and select **Submit**.
If **Vision port** is shown, leave it blank for automatic detection; only enter
a port for a custom installation. The screenshot shows the usual Echo Show port,
`26900`.

<img src="docs/images/setup/04-manual-address.png" alt="Enter the Echo Show IP address; Vision port can be left blank" width="311">

Confirm the device name and select **Submit**.

<img src="docs/images/setup/05-confirm-manual.png" alt="Confirm the device name after connecting by IP address" width="314">

Continue with selecting the voice assistant below.

</details>

VACAVision reads the choices from the Echo, including its public Sendspin identity.
This also matches MA universal players that do not report their IP address.
The initial page is HA’s built-in dashboard (`/lovelace/0`), so no unfinished
dashboard path needs to exist before browser sign-in.

If more than one player matches, or its address is unavailable, select this Echo
Show from the named player list. If no player is available, the form tells you to
pair it in Music Assistant and retry. You do not need to find a player ID.

For a new Echo, the API encryption key is created automatically and stored
privately in HA. A known key is checked before reuse. If a reset Echo rejects it,
VACAVision checks the same hardware identity and initial-provisioning state before
restoring the key. Network failures never trigger provisioning. Only an Echo secured with an unknown key
asks for that existing key, available from Echo Dot Assist's settings or original
setup records. The installer does not print keys; back up HA's configuration.

**3. Select the voice assistant.** Open the new VACAVision device in HA and choose
its Assist pipeline. HA may guide you through a connection test and ask you to
say “Alexa” twice. If the first test runs before the voice connection is ready,
wait for the satellite to become available, then retry. For spoken replies, HA's internal URL must be an HTTP
address reachable from the Echo Show; this version of Echo Dot Assist cannot
fetch those replies over HTTPS.

### Sign into Home Assistant on the Echo Show

Now use **the Echo Show's touchscreen**. When VACAVision displays the Home
Assistant sign-in page, enter your HA username and password there. This signs
in the display's browser so it can open your dashboards. The integration
connection above does not perform this browser sign-in.

After signing in, the display opens HA’s built-in dashboard. This lets View Assist
discover the browser display ID. HA supplies the Android timezone after connection.
Existing Athena dashboards remain untouched until you approve replacement below.

## 4. Finish in the HA “VACAV Setup” sidebar page

Open **VACAV Setup** in the HA sidebar and select this Echo Show. If it was added
before this update, select **Read installer choices from Echo** after running the
new Linux installer; you do not need to remove the working integration.

1. **Refresh connections.** The page shows this device’s microphone, display ID and
   official Music Assistant physical-player entity. If something is unavailable,
   follow the displayed instruction and refresh after it connects.
2. Check the weather selection, inherited from an existing View Assist device
   where possible. The Music Assistant sidebar path is detected automatically;
   if blank, open Music Assistant from HA’s sidebar and copy the path after the
   host/port (often `/<addon-id>_music_assistant`).
3. Select **Configure View Assist**. The integration creates a **View Assist device
   with display** using this Echo’s microphone/display and the same official MA
   player for music and alerts. This handles VA versions whose UI picker excludes
   VACAV satellites. It sets weather, announce on, ducking zero and this device’s
   Home, Music, Intent and List dashboard paths. It reuses a correctly mapped
   existing VA device rather than creating a duplicate.
4. Wait for VA to reload, then **Refresh connections** again. Select **Install
   dashboards**, review the three destination names and confirm replacement.
   Existing dashboard configurations are backed up to a private HA `.storage`
   file whose path is shown. Each saved dashboard is read back and checked.

The integration serves the included dashboard assets itself: no mounted HA folder,
manual asset copying or extra command is required. `custom:button-card` and your
existing View Assist frontend must already be installed.

The Home page links to View Assist, Music Assistant in a frame with a Home button,
and TV. The TV page shows the selected services. A tap on the clock can enable VA
hold mode; tap the hand icon again to return to normal mode.

**Check on the Echo itself:** ask a voice question and play music. Confirm both
come from this Echo, not another device. Sign into each streaming service, answer
ITVX’s cookie prompt, and test picture, sound, floating Home controls and mute.
A “Playing…” reply alone is not proof of audio playback. **Known issue:** ITVX live
audio can continue after returning Home. Lyrics installation is **coming soon**.

For repeat readiness checks, reopen **VACAV Setup → Refresh connections**.
`./vacav_setup.sh --check-ha` points to that page without contacting HA.
See [reruns and backups](docs/RECOVERY.md).

### Clear this device’s HA registrations as part of a clean reset

The [reset tool](reset-es8/README.md) wipes the Echo, not HA. For a clean reinstall:

- Remove only this Echo’s old **View Assist** and **VACA_Vision** entries under
  **Settings → Devices & services**. Do not remove unrelated devices.
- In **Music Assistant → Settings → Players**, remove its stale/unavailable player
  through its menu. Pair the reset Echo again. Check any sync group that contained
  the old player and replace only that member; preserve lyrics players and other
  devices.
- Keep its ESPHome discovery ignored. VACAVision owns this Echo’s voice connection.
- Keep shared dashboards. Existing Athena dashboards can also remain: the setup
  page backs them up before an explicitly confirmed replacement.
- Update to VACAVision **0.4.0** before adding the reset Echo. Stored keys are now
  checked and reset adoption is handled automatically; do not delete arbitrary
  `.storage` files. An explicitly identified `.old-pre-reset` backup from the old
  workaround is no longer used, but is not removed by the installer.

## Project files and status

`vacav_setup.sh` is the guided entry point; `install.py` retains individual commands for
maintenance. `echo-dot-assist/` is the unchanged upstream installer; `VACAV/`
contains the app/integration; `devices/` contains the ES8 profile and dashboards.
Private inputs, generated files and backups stay in ignored `installation-data/`.

This is an installation candidate under owner review. The October walkthrough
passed voice/music, navigation and reboot after workarounds; the revised integrated
setup flow requires its own walkthrough. See
[validation](docs/VALIDATION.md), [manual checks](docs/ACCEPTANCE.md) and
[licences/attribution](docs/NOTICE.md).
