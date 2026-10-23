# Move this candidate to Linux

The Windows preparation does not wipe or install the ES8. The owner reviewed the
layout and approved transfer to the **private** GitHub repository on 23 October 2026.
Continue the device work on Linux. Public release remains a separate later decision.

## 1. Review the installation layout

Open `README.md` for the folder map and `docs/SETUP.md` for the commands.
Device profiles and shared dashboards are under `devices/`; Portal's profile is
`portal_plus_gen_2`. `install.py device` calls the USB helper there.

On GitHub, `echo-dot-assist` appears as a link to its exact upstream commit. It
becomes the complete upstream folder on Linux with `--recurse-submodules`.
Do not use GitHub's Download ZIP: it omits the submodule checkout. Upstream's other
device directories remain because this is an identical upstream tree. Run its
own installer with `./echo-dot-assist/scripts/setup.sh athena`.

## 2. Copy private installation inputs separately

Use a private USB drive or another private transfer. Do not upload these to GitHub:

| From the Windows workspace | Linux destination/use |
|---|---|
| `ES8_Athena/installation-data/apks/es8-gen2/` | Same relative location in the clone; contains exported Netflix, iPlayer splits, ITVX and Silk APKs |
| `ES8_Athena/installation-data/es8-gen2-apps.json` | Same relative location; hashes for those exports |
| `ES8_Athena/installation-data/choices/es8-gen2.json`, if created | Same location, or rerun the selection wizard |
| Any Portal APK exports/choices you want to reuse | Corresponding `installation-data/` folders/files |
| Your verified TWRP backup and recovery notes | Private recovery storage outside the clone |
| The pinned firmware `.bin` and `boot-root.zip`, when acquired | `echo-dot-assist/firmware/athena/` |

Generated `installation-data/generated/` can be recreated. Do not copy Windows `.venv`, build caches,
or toolchains into the Linux environment. HA tokens and Wi-Fi/account credentials
are entered privately when needed; no saved token is required by this repo.

The exported APKs do not contain streaming sign-ins. Sign in again after the wipe.
The stock firmware `.bin` was **not present** during Windows preparation; obtaining
and verifying it remains a prerequisite before the first wipe. Use the download
references and exact hashes in `echo-dot-assist/devices/athena/README.md` and `device.conf`.

## 3. Clone and prepare on Linux

Use a Linux PC with working physical USB, Python 3.11+, Git, `adb`, and sufficient
free storage (at least 20 GB for this walkthrough). On Debian/Ubuntu:

```sh
sudo apt update
sudo apt install git python3 python3-venv python3-pip adb
git clone --recurse-submodules https://github.com/baileyboy0304/ES8_Athena.git
cd ES8_Athena
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python install.py verify
```

Authenticate to GitHub using your usual credential helper (or `gh auth login`
and `gh auth setup-git` if using GitHub CLI). EDA's normal setup checks
its additional Linux tools; follow those prompts before any device reset.

Copy the private inputs from step 2 into place, preserving directory names. Check
that USB ADB sees the intended device:

```sh
adb devices -l
```

If permissions prevent access, resolve Linux USB/udev access before installation.
Do not change the serial to a network address. Keep the Portal disconnected during
the ES8 walkthrough to make device selection unambiguous.

## 4. Continue the same project work

Open this repository in the Linux coding environment. Carry these instructions
forward if the new chat does not have this conversation:

> Read docs/DECISIONS.md, docs/VALIDATION.md and docs/SETUP.md. Continue the
> ES8 Gen 2 EDA + VACAV installation. EDA must stay identical to the developer's
> current checkers branch. Verify recovery and inputs before the authorised first
> wipe to an unlocked baseline. Refresh/check upstream and update the recorded pin
> if needed, then run its unchanged installer. Run VACAV with selected streaming
> apps and its separate optional installed-firewall adaptation. Configure HA using
> normal user setup, correct unclear instructions, and do only basic checks. The
> owner tests further. A second wipe requires the owner's later explicit OK.
> Keep the repo private and conserve usage.

If upstream moved since packaging, inspect the changes before installation:

```sh
git -C echo-dot-assist fetch origin checkers
git -C echo-dot-assist status --short
git -C echo-dot-assist log --oneline HEAD..origin/checkers
```

The maintainer must advance the submodule and `maintenance/source-versions.json` together and check
the streaming adapter against the new firewall. Do not bypass a pin mismatch or
modify EDA source to make the adapter fit. A normal clone intentionally uses the
reviewed commit, rather than silently selecting a different upstream revision.

Proceed with `docs/SETUP.md`. Neither the first wipe nor live installation has
been performed in this Windows packaging pass.
