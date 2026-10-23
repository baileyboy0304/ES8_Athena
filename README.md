# ES8 Athena

Install **echo-dot-assist + VACAV + View Assist** on an Echo Show 8 Gen 2.
A separate **Portal Plus Gen 2** profile is included for VACAV and dashboards.

**Start with [the installation guide](docs/SETUP.md).** Moving from Windows?
Read [the Linux handover](docs/LINUX-HANDOVER.md) first.

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

**Also preserve your own device data before a wipe ([setup step 2](docs/SETUP.md#2-preserve-what-you-need-before-wiping)).** A verified TWRP
backup must be made from your ES8 and kept outside this repository. Streaming
APKs must be exported from your existing installation or supplied separately if
you select those services. Neither is included in the XDA unlock downloads.
The first wipe waits until recovery and all required installation inputs are verified.

Then follow [the installation guide](docs/SETUP.md) in order.

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

## Which installer do I run?

On Linux, from this repository's root, follow the guide in order:

1. **echo-dot-assist:** `./echo-dot-assist/scripts/setup.sh athena`
2. **Configure dashboards and choose optional streaming apps:**
   `python install.py choose --profile es8-gen2`
   Answer Y/N for Netflix, BBC iPlayer, ITVX and Apple TV. All default to No;
   choosing none is supported. Run this wizard even without streaming, because
   it also saves your View Assist sensor, weather entity and dashboard paths.
3. **VACAV and selected streaming apps:**
   `python install.py device --profile es8-gen2 --apply`
4. **Home Assistant and dashboards:** continue with steps 6–8 of the setup guide.

The developer puts the installer in `scripts/setup.sh`; there is no upstream
`echo-dot-assist/setup.sh`. We keep that layout unchanged and provide no replacement
shell installer. In the guide, **EDA** is simply shorthand for echo-dot-assist.

`install.py device` calls `devices/install-device.py` for you. Without `--apply`
it inspects the device only. **`--serial` is optional when exactly one USB ADB
device is connected.** With several USB devices, add `--serial YOUR_USB_SERIAL`;
find it with `adb devices -l`. Automatic selection ignores network ADB and emulators.
Use `--profile portal_plus_gen_2` for Portal Plus Gen 2;
**do not run echo-dot-assist on Portal**. `python install.py --help` lists commands.

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
