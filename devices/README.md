# Device configuration

See [APK versions used](APK-VERSIONS.md) for exact streaming/VACAV versions,
package names and the required iPlayer splits. Streaming apps are supplied by users.

- `es8-gen2/profile.json`: Echo Show 8 Gen 2 launchers and dashboard defaults.
- `dashboards/custom/`: your updated clock/weather and templates.
- `dashboards/upstream/`: pinned standard View Assist views and assets.

The dashboard templates are shared; each device profile generates its own configured
Home, View Assist and TV dashboards in `installation-data/generated/DEVICE/`.

Run `python install.py device ...` from the repository root. It calls
`install-device.py` here to install VACAV and selected streaming apps. On ES8,
`streaming.py` and `streaming/` provide the optional installed-firewall adaptation.
You do not need to run these helper files separately.

`--serial` is optional when exactly one USB ADB device is connected. With several,
pass `--serial YOUR_USB_SERIAL` from `adb devices -l`. Automatic selection uses USB
only, then pins subsequent commands to the detected serial.
