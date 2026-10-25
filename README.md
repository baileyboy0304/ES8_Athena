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
- **View Assist already installed and operational in Home Assistant**, including
  its frontend resources and a working Assist pipeline. This guide adds an Echo
  Show to your existing setup.
  See [View Assist documentation](https://dinki.github.io/View-Assist/) if needed.
- Music Assistant server and its official HA integration already working if you
  want the music/announcement setup described here. The current guided flow checks
  both player mappings before installing the example dashboards.
- The dashboard card dependencies, including `custom:button-card`, from
  [the dashboard inventory](docs/DASHBOARDS.md).
- An HA administrator long-lived access token for the guided checks and dashboard
  setup. Enter it at the hidden prompt; the installer does not save it.
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

Follow the **Echo Show 8 Gen 2 / Athena** instructions in
[Echo Dot Assist's checkers guide](https://github.com/Gamer92000/echo-dot-assist/tree/checkers),
including its downloads and prerequisites, then run:

```sh
./echo-dot-assist/scripts/setup.sh athena
```

**That installer handles unlocking, firmware, rooting and Echo Dot Assist
installation.** If already unlocked, follow its detected-device prompts; there is
no separate unlock procedure here. The current companion installer checks for
Athena firmware `PS75741.7080N` and stops on a different build.

**Does cloning fetch the latest checkers code? No.** It fetches the exact upstream
commit recorded by this repository, from the checkers branch. The branch setting
in `.gitmodules` does not make a normal clone follow the latest tip. This keeps
our checks and firewall adaptation matched to the reviewed upstream version.
Updating that revision is a maintainer task followed by compatibility checks.

At the end, Echo Dot Assist shows HA and Music Assistant instructions. For this
combined setup, **leave the separate ESPHome voice-entry step to VACAVision below**;
there should be only one voice owner for this Echo Show. Keep existing ESPHome
entries for other devices. If this Echo Show already has one, preserve its API
key/settings before removing that duplicate ownership.

Echo Dot Assist installs and runs Sendspin and supplies the Music Assistant
pairing token. Music Assistant discovers the player, but pairing, **Expose player
to Home Assistant**, and View Assist's entity mappings still need to be completed
in HA/MA. They are not configured automatically by the upstream installer.

Keep automatic Echo Dot Assist updates off while using this candidate's
installed-firewall adaptation. Retain USB access for the next step.

## 2. Start the guided VACAVision installer

From this repository's root, run:

```sh
./vacav_setup.sh
```

This prepares the Python environment and starts the guided setup.

The wizard:

1. Connects to HA and checks that View Assist is already operational.
2. Reuses the weather entity from an existing View Assist device and the timezone
   from HA. The HA timezone is also applied to Android.
3. Asks Y/N for Netflix, BBC iPlayer, ITVX and Apple TV. Apple TV uses Silk.
   It reuses installed apps and asks for your APK folder when selected apps are
   missing. Include all required split APKs together.
4. Asks for dashboard names and the existing Music Assistant sidebar path.
   Use unique names for each additional display. It creates missing landing pages
   so first sign-in reaches a setup page rather than a 404, leaving existing
   dashboards untouched at this stage.
5. Checks the connected USB Echo Show, reviews the changes and installs VACAVision
   and your selected apps. It prepares the keyboard, timezone, Home selection and
   display permissions, with Y/N prompts for floating streaming controls and the
   ITVX warning helper. It offers a reboot.
6. Offers to copy the matching HA integration and frontend files through your
   mounted HA configuration folder. If that folder is not accessible from Linux,
   it tells you which files to copy into HA instead.
7. **Pauses and tells you exactly what to finish in HA**, as listed below.

VACAVision always receives its required web access for artwork and embedded
content. Selected streaming apps also receive TCP 80/443 access, including any
web advertising/telemetry. Other internet ports and UDP/QUIC remain blocked.
The installer backs up and checks the installed firewall files before adapting them.

Choices and USB progress are saved under ignored `installation-data/`. If you
stop, run **the same `./vacav_setup.sh` command** and choose to resume. It rechecks USB
prerequisites and lets you retain a completed USB installation. HA credentials are
requested again, not stored. Answer No at the HA pause to finish another day.

## 3. While the installer waits: finish this device in HA

You are adding/configuring **one device in your existing View Assist setup**.
Leave the installer waiting, complete these steps, then return to it.

### Prepare the Music Assistant player

Complete this before adding VACAVision: its connection form needs the Echo Show's
Music Assistant player ID.

If you paired the Echo's Sendspin player during Echo Dot Assist setup, reuse it.
Otherwise pair it using the token supplied by Echo Dot Assist. In that player's
Music Assistant settings, enable **Expose player to Home Assistant**. Wait for its
player entity to appear in HA under the **Music Assistant integration**.
Keep the player's **Music Assistant player ID** for the voice and music settings below.

On this ES8, **Echo Dot Assist runs the Sendspin player**. VACAVision's built-in
Sendspin engine is disabled in this role. Use the official MA physical-player
entity for View Assist playback.

### Connect Home Assistant to VACAVision

Restart HA after the installer has copied the integration files. These steps let
HA control the app and use the Echo Show's microphone and speaker for Assist.

**1. Add the discovered device.** Open **Settings → Devices & services** in HA.
Look under **Discovered** for your Echo Show's **VACA_Vision** card and select
**Add** on the **VACA_Vision** card. The screenshot also shows the Echo's
ESPHome discovery card; use the VACA_Vision card for this setup.

<img src="docs/images/setup/00-discovered-device.png" alt="HA Discovered section with separate ESPHome and VACA_Vision cards; select Add on VACA_Vision" width="640">

Continue with the device role and landing page below.

<details>
<summary>If the Echo Show does not appear under Discovered</summary>

Check that VACAVision is running on the Echo Show and that HA can reach its IP
address. Then select **Add integration**, search for `VACA`, and select
**VACA_Vision**.

<img src="docs/images/setup/01-select-integration.png" alt="Search results showing the VACA_Vision integration" width="460">

Select **Connect an installed device by IP address**.

<img src="docs/images/setup/02-connect-installed.png" alt="VACA_Vision menu with Connect an installed device by IP address" width="460">

Enter your Echo Show's IP address and change **Vision port** to **26900**, then
select **Submit**. Use the address printed by your installer.

<img src="docs/images/setup/03-address-port.png" alt="Connect an installed Vision app: device address and port 26900" width="460">

</details>

**2. Set the device role and landing page.** Enter the device name. Under
**Device role**, select **ES8 with upstream EDA (prototype)** — this is the current
screen label for Echo Dot Assist. Set **Initial dashboard path** to the landing
page printed by the installer, normally `/athena-home/home`. Select **Submit**.

<img src="docs/images/setup/04-role-dashboard.png" alt="New-device setup showing the ES8 upstream role and initial dashboard path" width="460">

**3. Connect voice and music.** Fill in the following fields and select **Submit**.

| Field shown on screen | What to enter |
|---|---|
| Use EDA voice indicator only | Leave checked to use the Echo Show's native listening indicator. |
| Music Assistant server | Select your Music Assistant integration. |
| EDA Sendspin player ID | Enter this Echo Show's **Music Assistant player ID**. The example `upfae92cea` belongs to the pictured device. This field does not take a `media_player.…` HA entity ID. |
| EDA API port | **26053** — Echo Dot Assist's voice connection. |
| EDA encryption key | If Echo Dot Assist already has an API encryption key, enter that key. For a new device with no key, leave blank to let the integration set up encryption. |

<img src="docs/images/setup/05-voice-music.png" alt="New-device voice and music settings: Music Assistant server, player ID, API port and encryption key" width="460">

HA checks the voice connection and the Music Assistant player before completing
setup. If it reports that the player is missing or not exposed, correct that
player's Music Assistant settings and retry.

**4. Select the voice assistant.** Open the new VACAVision device in HA and choose
the Assist pipeline in its assistant selector. For spoken replies, HA's internal
URL must be an HTTP address reachable from the Echo Show; this version of Echo
Dot Assist cannot fetch those replies over HTTPS.

### Sign into Home Assistant on the Echo Show

Now use **the Echo Show's touchscreen**. When VACAVision displays the Home
Assistant sign-in page, enter your HA username and password there. This signs
in the display's browser so it can open your dashboards. The integration
connection above does not perform this browser sign-in.

After signing in, the display should open the landing page created by the
installer. View Assist can then discover its display ID. Continue with the
View Assist device mapping below before returning to the installer to replace
the landing page with the finished dashboards.

### View Assist device mapping

Add or configure this Echo Show in View Assist using its actual new identifiers:

| Setting | Value |
|---|---|
| Display | **Value** of VACAVision's display sensor, starting `va-`; not its entity ID |
| Microphone | This VACAVision device's `assist_satellite.*` entity |
| Media player / alerts | Official MA entity for the physical Echo Show Sendspin player |
| Music player | The same official MA physical-player entity |
| Dashboard | Wizard's VA path, normally `/view-assist-athena` |
| Home/default view | Wizard's clock path, normally `/view-assist-athena/clock` |
| Weather | Set through this VA device's existing weather options |
| Use announce | Enabled for compatible announcement blueprints |
| Ducking | Start at zero; Echo Dot Assist/VACAVision handle voice/music focus |
| Display mode | Fullscreen/kiosk as appropriate; native voice indicator enabled |

If your VA version's picker excludes VACAVision, the optional helper
`python install.py create-view-assist --profile es8-gen2` uses VA's normal
configuration API. Run it in another terminal using `.venv/bin/python` instead of
`python` if your virtual environment is not activated. Then configure that VA
device's dashboard, weather and default view normally. Do not create a duplicate
if the device already exists.

Confirm that a spoken Assist request receives a reply and that music actually
plays on **this Echo Show**. A spoken “Playing…” response alone is not proof.

## 4. Return to the installer — check and install dashboards

Answer **Yes** when asked whether the HA steps are finished, then select this
Echo Show's View Assist sensor. The installer checks:

- View Assist sensor is available.
- Its microphone is an available VACAVision Assist satellite.
- The display ID and microphone belong to the same VACAVision device.
- Music and alerts use the same available official MA entity, not the VACAVision
  proxy or an MA sync-group entity.
- Its VA weather entity is available and its Home path matches the planned clock.

If a check fails, the installer explains what to correct and waits for you to
retry. It also asks you to confirm voice and music playback on the Echo Show.

Once the checks pass, the wizard reads the VA weather setting, backs up existing
dashboard configurations, lists the three targets and asks before installing them.

The resulting Home page links to View Assist, Music Assistant in a frame with a
Home button, and TV. The TV page shows only selected services. Sign into those
services on the Echo Show, then test picture, sound and the floating Home control.
**Known issue:** ITVX live audio can continue after returning Home.
Lyrics installation is **coming soon**.

For a read-only repeat of the HA checks, use `./vacav_setup.sh --check-ha`.
For recovery, see [reruns and backups](docs/RECOVERY.md). The separate
[reset tool](reset-es8/README.md) is only for an explicitly requested clean reset;
a normal install or upgrade does not require it. A clean reset also needs removal
of only this device's stale VA/VACAVision entries and invalidated MA pairing.

## Project files and status

`vacav_setup.sh` is the guided entry point; `install.py` retains individual commands for
maintenance. `echo-dot-assist/` is the unchanged upstream installer; `VACAV/`
contains the app/integration; `devices/` contains the ES8 profile and dashboards.
Private inputs, generated files and backups stay in ignored `installation-data/`.

This is an installation candidate under owner review. See
[validation](docs/VALIDATION.md), [manual checks](docs/ACCEPTANCE.md) and
[licences/attribution](docs/NOTICE.md).
