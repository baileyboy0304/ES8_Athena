# Manual walkthrough

Do one clean install from the agreed unlocked stock baseline. Mark each item
Pass/Fail and record the first confusing instruction. Start with one selected
streaming service, then add the others if preferred; rerun selection, USB apply
and dashboard deploy to keep policy and buttons aligned.

- [ ] Repo checksums pass; no private token/key required by any bundled source.
- [ ] Correct Gen 2 detected; Echo Dot Assist setup completes and survives one reboot.
- [ ] VACAV starts as Home; HA sign-in succeeds; device reconnects on port 26900.
- [ ] HA shows one intended ES8 voice owner; selected pipeline answers a question.
- [ ] Physical microphone mute and Echo Dot Assist native light band behave as expected.
- [ ] Music Assistant plays through the official Music Assistant entity for the physical Sendspin player.
- [ ] VA display ID points to the new VACAV display, not the old pre-wipe UUID.
- [ ] Home's VA, MA and TV buttons reach the correct destinations.
- [ ] Updated clock/weather render; VA Home/TV icons work.
- [ ] Standard VA views render after dependencies and relevant entities are configured.
- [ ] Only selected services appear on TV; no selections produces a clear empty page.
- [ ] Netflix, iPlayer, ITVX and Apple TV/Silk: sign-in, moving picture and sound.
- [ ] During playback, wake → reply → audio restoration works; floating Home returns.
- [ ] Known issue checked: ITVX live audio stops after Home (previous trial did not reliably pass).
- [ ] Keep on and brightness controls work; no Android Settings/SystemUI shortcut.
- [ ] ITVX helper dismisses only its intended warning, if enabled.
- [ ] One reboot retains Home, pairing, streaming choices and required permissions.

Record device firmware, APK versions, HA/MA/VA versions and selected services.
For a failure record: guide step, expected result, actual result, visible error,
whether retry helped. Avoid collecting tokens, transcripts or private screen data.

This repo's preparation uses only local syntax/configuration/checksum and small
installer tests. No live install, wipe, HA dashboard replacement, full application
build, repeated playback tests or endurance tests are required for this packaging pass.
Fresh installation remains unverified until this walkthrough.
