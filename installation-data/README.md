# Your private installation data

The installer creates files here as needed. Only this README is tracked by Git.

| Location | Contents |
|---|---|
| `apks/DEVICE/SERVICE/` | Your streaming APKs and split APKs, exported before wiping or supplied by you |
| `DEVICE-apps.json` | Hash record for exported APKs |
| `choices/DEVICE.json` | Service selections, HA entity IDs and dashboard paths from the wizard |
| `generated/DEVICE/` | Generated Home, TV and VA dashboard JSON/YAML and streaming policy |
| `backups/` | Previous dashboards, integration files and device settings saved during installation |

`DEVICE` is `es8-gen2` or `portal_plus_gen_2`. Service folders use IDs such as
`netflix`, `iplayer`, `itvx`, `apple_tv` and, on Portal, `sstv`.

Copy needed APK exports and choices separately when moving to Linux. Generated
dashboards can be recreated. Keep backups until you have accepted the installation.
Do not delete this folder as a general cleanup step or upload its contents to GitHub.
HA access tokens are prompted for and are not saved here.
