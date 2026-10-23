# APK versions used

Versions read directly from the saved APK manifests on 23 October 2026. These
identify the builds used in the existing trial; they are not a recommendation to
install the latest app or proof that the fresh-install walkthrough has passed.
Users supply their own streaming APKs. None of those APKs are distributed here.

## Echo Show 8 Gen 2 streaming

The target runs Android 9 with 32-bit ARM userspace. Choose builds that include
`armeabi-v7a`; an ARM64-only APK will not work on this target.

| Service | Android package | Version name | Version code | Packaging used |
|---|---|---|---|---|
| Netflix (Echo build) | `com.netflix.mediaclient.echo` | `8.141.2` | `63112` | One APK; includes ARM32 |
| BBC iPlayer | `bbc.iplayer.android` | `5.59.0.37574` | `500037574` | Base APK plus three splits listed below |
| ITVX | `air.ITVMobilePlayer` | `17.7.0` | `1301707000` | One APK; includes ARM32 |
| Apple TV through the existing Silk browser | `com.amazon.cloud9` | `138.16.11.0.7204.244.40` | `1396011040` | Silk browser, one ARM32 APK; no native Apple TV APK used on ES8 |

Silk is already installed on the current ES8. The device installer reuses an
installed app and does not replace it just to match this table. Supply a Silk APK
only if it is missing after the reset and echo-dot-assist installation. Selecting
Apple TV still adds its TV launcher and configures the selected streaming access.

The iPlayer export contains the base APK and these matching splits, all with
version code `500037574`:

- `config.armeabi_v7a`
- `config.en`
- `config.mdpi`

Keep the base and all required splits together in
`installation-data/apks/es8-gen2/iplayer/`; the installer uses `adb install-multiple`.
Do not mix splits from different versions. The other service folders are `netflix`,
`itvx` and `apple_tv` (Silk). Follow [README step 2](../README.md#2-preserve-what-you-need-before-wiping)
for supplying or exporting APKs.

Known trial issue: ITVX live audio can continue after Home. Recording its version
does not mean that issue is resolved. Recheck it during the Linux walkthrough.

## Bundled VACAV builds

Both use package `com.mph1970.vacavision` and are included in this repository.

| Device | Version name | Version code | Bundled file |
|---|---|---|---|
| ES8 Gen 2 | `0.2.3-upstream-prototype.10` | `16` | `VACAV/integration/custom_components/vaca_vision/packages/vision-standard.apk` |
| Portal Plus Gen 2 | `0.2.3-mute-preview.1` | `6` | `VACAV/payloads/portal_plus_gen_2.apk` |

Portal streaming-app versions have not been verified from a saved APK set for this
package. Its profile records launchers only; do not assume the ES8 versions or
Netflix Echo package apply to Portal.
