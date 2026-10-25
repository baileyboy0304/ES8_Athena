# Reset ES8 Gen 2 to the unlocked TWRP baseline

This standalone folder resets **Echo Show 8 2nd generation (2021), `athena`**, using
our reviewed original PS75741.7080N images and TWRP **3.7.0_9-0**. It is not a bootloader-unlock or generic firmware-flashing tool.

“TWRP baseline” means original system/vendor, empty user data/internal storage and
cache, with the existing unlocked boot and TWRP recovery retained. There is no
universal “TWRP default firmware”. **Stock firmware APKs remain**; all user-installed
APKs, VACAV, streaming sign-ins, Wi-Fi settings and internal-storage files are erased.
Restoring system/vendor also removes Echo Dot Assist and the installed root/firewall changes.
The script stops in TWRP: it does not reboot into stock Fire OS or reinstall root.

## Inputs

Use Linux, Python 3.10+ and Android platform-tools (`adb`). No pip packages or Echo Dot Assist
checkout are needed. Keep USB and power connected throughout the restore.

Provide these four **raw, full partition images**, uncompressed, in a private folder:

- `boot-original.img`
- `recovery-original.img`
- `system-original.img`
- `vendor-original.img`

These are the previously verified original images from the reviewed recovery backup. They are not included in GitHub. `baseline.json` pins
all four sizes and SHA256 hashes from that reviewed backup. Other image sets and
TWRP versions are deliberately rejected; do not edit the hashes merely to bypass
a mismatch. The boot/recovery files are checked as recovery prerequisites but
**never flashed**. The connected device's boot/recovery must already match them.

Before resetting, export any APKs you need to reinstall and save anything you want
from the device. An APK export does not preserve account sign-ins. The script does
not create a backup of the working installation.

Keep the recovery images in a private folder outside the checkout.

## 1. Check local images without contacting the ES8

Run from the repository root (replace the directory for your machine):

```sh
python3 reset-es8/reset_es8.py \
  --backup-dir /path/to/private/recovery-images \
  --check-files
```

This reads/hashes local files only. It is safe while the ES8 is still running.

## 2. Prepare recovery and perform a read-only device check

When you are ready for downtime, connect the intended ES8 by USB, inspect
`adb devices -l`, and boot it into TWRP. From working, authorised Android ADB:

```sh
adb -d reboot recovery
```

Wait for TWRP to finish starting. Do not allow TWRP to mount system/vendor again
while the reset is running. Then run the command **without** `--apply`:

```sh
python3 reset-es8/reset_es8.py \
  --backup-dir /path/to/private/recovery-images
```

With no `--serial`, the script selects the single connected USB device, prints its
serial and uses that serial for every subsequent check and write. It stops if USB
selection is ambiguous or unavailable. To select one of several USB devices, add
`--serial YOUR_USB_SERIAL` (and use `adb -s YOUR_USB_SERIAL` for the reboot).

This verifies the USB connection, device serial, Athena identity, root recovery,
TWRP version, distinct partition mappings, all image sizes/hashes, partition sizes,
and the unchanged boot/recovery hashes. It makes no writes and does not reboot.
A mismatch stops the process; inspect it instead of bypassing the check.

## 3. Reset — destructive, only when you are ready

```sh
python3 reset-es8/reset_es8.py \
  --backup-dir /path/to/private/recovery-images \
  --apply
```

An interactive terminal is required. After the compatibility checks pass, type the
confirmation shown, using the selected serial:

```text
ERASE YOUR_USB_SERIAL
```

The script then:

1. Rechecks the device and opens a private timestamped report.
2. Unmounts system/vendor and restores only those two partitions, checking each
   full partition SHA256 after writing. It never writes boot, recovery, preloader,
   bootloader, NVRAM or other unlock/device-specific partitions.
3. Formats `/data`, including internal storage, and checks that no user files or
   application data remain. Only empty recovery-created directories, layout metadata
   and TWRP's own preferences are permitted.
4. Wipes cache and checks for unexpected remaining top-level contents.
5. Rechecks boot/recovery hashes and remains in TWRP.

Reports are in `reset-es8/reports/` (ignored by Git), or use `--report-dir` for a
private location. A failed/interrupted run is **not** a successful reset. Leave the
ES8 in TWRP and inspect the failed stage before attempting recovery or another run.
Do not disconnect USB or reboot following a partition-write failure.

## 4. Clean up the old HA registrations, then reinstall

This script does **not** alter Home Assistant or Music Assistant. Follow the main
[README's HA cleanup instructions](../README.md#clear-this-devices-ha-registrations-as-part-of-a-clean-reset)
to remove only this ES8's obsolete View Assist and VACAV entries and any obsolete
MA pairing. Preserve other devices, shared dashboards and providers. Recreate the
entries at the documented installation steps, after VACAV/HA browser sign-in.

Continue with the main [installation guide](../README.md), including its root
prerequisite and the unchanged Echo Dot Assist installer. The reset script does not perform
any part of the new installation.

## Validation status

The earlier live reset used this same reviewed partition-image restore procedure.
This standalone script has **not** been applied to the live ES8. Its local image
check passed against the private recovery files; automated tests simulate success,
confirmation rejection, wrong devices, corrupted images and interrupted/failing
stages. No destructive live validation is implied.

```sh
python3 -m unittest discover -s reset-es8/tests -q
```
