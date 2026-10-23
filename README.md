# ES8 Athena

Install **echo-dot-assist + VACAV + View Assist** on an Echo Show 8 Gen 2.
A separate **Portal Plus Gen 2** profile is included for VACAV and dashboards.

**Start with [the installation guide](docs/SETUP.md).** Moving from Windows?
Read [the Linux handover](docs/LINUX-HANDOVER.md) first.

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
2. **Choose services:** `python install.py choose --profile es8-gen2`
3. **VACAV and selected streaming apps:**
   `python install.py device --profile es8-gen2 --serial YOUR_USB_SERIAL --apply`
4. **Home Assistant and dashboards:** continue with steps 6–8 of the setup guide.

The developer puts the installer in `scripts/setup.sh`; there is no upstream
`echo-dot-assist/setup.sh`. We keep that layout unchanged and provide no replacement
shell installer. In the guide, **EDA** is simply shorthand for echo-dot-assist.

`install.py device` calls `devices/install-device.py` for you. Without `--apply`
it inspects the device only. Use `--profile portal_plus_gen_2` for Portal Plus Gen 2;
**do not run echo-dot-assist on Portal**. `python install.py --help` lists commands.

## Included dashboards and streaming

Home has three launchers: **View Assist**, **Music Assistant** and **TV**.
VA includes your updated clock/weather plus the standard upstream views, with
Home and TV icons. TV shows only services selected in the Y/N wizard.

ES8 choices are Netflix Echo, BBC iPlayer, ITVX and Apple TV through Silk.
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
