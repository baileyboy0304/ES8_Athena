# Setup: unlocked ES8 Gen 2 → EDA + VACAV + VA

This guide uses the **normal echo-dot-assist installer** and the tested VACAV
upstream prototype. Do not use the separate Athena Assist or Crown Assist projects.
Do not run the EDA or ES8 steps on Portal. Portal only uses steps 1, 5–8 with its profile.

## 1. Configure dashboards and choose optional streaming apps

For the Windows-to-Linux move, complete [Linux handover](LINUX-HANDOVER.md) first.
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

Use the [APK version reference](../devices/APK-VERSIONS.md) to identify the builds
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
python install.py device --serial YOUR_USB_SERIAL --profile es8-gen2 --export-apps
```

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
python install.py device --serial YOUR_USB_SERIAL --profile es8-gen2
python install.py device --serial YOUR_USB_SERIAL --profile es8-gen2 --apply
```

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
(`standard_upstream_eda`). Enter the ES8's address and VACAV port **26900**.
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
and the standard VA card dependencies; [the dashboard inventory](DASHBOARDS.md)
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

Sign into each chosen streaming service on the device. Check [manual acceptance](ACCEPTANCE.md).
Known issue to check explicitly: ITVX live audio may continue after returning Home.
Report the step number and what you saw if anything is unclear; there is no need
for exhaustive automated testing before this walkthrough.
