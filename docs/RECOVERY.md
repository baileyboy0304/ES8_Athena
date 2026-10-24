# Recovery and reruns

Stop at the first failing step; keep its output and the timestamped backup path.
Do not try another device family's installer. Run the developer's echo-dot-assist
installer directly for its system work; follow its Athena recovery guidance.

## Dashboards

`installation-data/backups/dashboards-TIMESTAMP/SLUG.json` stores the old dashboard metadata and
`config`. In HA open the affected dashboard's Raw configuration editor and restore
the `config` value (JSON is valid YAML). A null config means that dashboard did
not previously exist; delete only that newly created dashboard via HA if reverting.
Each dashboard is saved/read back separately: if the third fails, the first two
may already be installed. The backup covers all three before any save.

## VACAV HA integration

Stop HA, move the newly installed `custom_components/vaca_vision` aside, restore
the backed-up folder from `installation-data/backups/ha-TIMESTAMP/vaca_vision`, then restart HA.
Do not restore `.storage` wholesale. New installations without an older integration
can remove this integration via HA and remove its folder with HA stopped.
The old integration backup may contain device configuration supplied by you; keep
all backups private. The `www/es8-athena` assets can remain without affecting VA.

## Streaming profile and Android grants

The device installer records installed script paths, hashes and SELinux labels in
`installation-data/backups/device-TIMESTAMP/streaming-rollback.json`, alongside the saved firewall
scripts and (if present) `streaming-before.conf`. Keep this folder private.
The policy is `/data/local/es8-athena-streaming.conf`, owned by root with mode 0600.
Do not remove the EDA firewall itself to fix playback.

For the supported return to the pinned stock firewall, choose No for every service
and rerun `python install.py device --serial YOUR_USB_SERIAL --profile es8-gen2 --apply`.
It restores the original scripts from the unchanged `echo-dot-assist/` checkout and removes
its policy, provided the installed scripts still match this adapter or that original.
It stops on an unknown version. Reboot once. A write failure attempts to restore
the saved script/policy state; preserve the error and backups if recovery also fails.

Selecting fewer services and rerunning USB apply replaces the profile and removes
their internet exceptions; it does not uninstall their APKs or delete logins.
Rerun dashboard deployment to remove those buttons too. A normal data wipe can
erase the profile; reapply the saved choices afterwards.

To revoke floating-window inspection:

```sh
adb -s YOUR_USB_SERIAL shell pm revoke com.mph1970.vacavision android.permission.DUMP
```

To disable the ITVX helper, remove only
`com.mph1970.vacavision/com.msp1974.vacompanion.utils.ItvxWarningService` from the
colon-separated `enabled_accessibility_services` secure setting. Retain other
services. `before.json` records the original state; do not overwrite newer unrelated
settings with an old snapshot. If the removed helper was the only service, restore
the original global accessibility-enabled value. Revoke overlay/WRITE_SETTINGS
only if you want to remove those VACAV capabilities as well.

Android APK updates must keep the signer and cannot normally downgrade. Do not
uninstall just to bypass an error without accepting loss of app data/sign-ins.
Exporting streaming APKs does not back up those apps' private data.

## EDA system recovery

Consult the pinned EDA Athena README for `scripts/install-system.sh --uninstall`
and its limitations. The [standalone ES8 reset tool](../reset-es8/README.md) packages the previously
used original-image restore procedure, with preflight and read-back checks.
The new script itself has not been run destructively. It requires the exact
reviewed private raw images and leaves the device in TWRP; it is not a generic
TWRP Restore-menu backup importer.
EDA's stock-component removal includes Android Settings and SystemUI; their
absence is expected. VACAV's Home/Keep on/Brightness panel supplies the agreed controls.
If the display is blank, use USB to open VACAV's activity or inspect EDA's status;
do not run a different recovery installer or flash Crown files.
