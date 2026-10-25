# Product decisions

These decisions come from the owner's instructions and **Compare release checkers**
chat, read on 23 October 2026. Later owner instructions override these notes.

- EDA is the developer's **current checkers branch**, with a real, unchanged Git
  checkout under `echo-dot-assist/`. No local source patches or replacement EDA installer.
- VACAV uses the existing EDA integration prototype, not the separate Athena Assist
  or Crown Assist setups. EDA owns voice, wake word, Sendspin and the native band.
- Streaming is optional. The **streaming-app installation section** may separately
  adapt the installed firewall policy. It must explain access and not pretend
  that the installed firewall remains stock. On 25 October 2026 the owner also
  approved VACAV web access for external dashboard artwork. The wizard records
  this independently of TV apps; no TV apps and no VACAV web access means no
  adaptation. EDA source remains unchanged.
- No Android Settings/SystemUI/component restoration. The final streaming popup
  is Home, Keep on and Brightness, centred at the top, during supported playback.
- Silk launches fullscreen. ITVX gets its narrowly scoped warning helper.
- One HA assistant device/voice owner. Routine VACAV settings live in HA.
- Native-only VA indicator prevents duplicate dashboard/EDA animations.
- Known unresolved trial issue: ITVX live audio can continue after Home. Do not
  claim full streaming sign-off or hide that issue from the acceptance checklist.

## Owner's requested installation sequence

First finish the package on Windows and ask the owner to inspect it. Only after
that approval, push to a **private** GitHub repository. The owner then moves to
Linux. All device wipe/install work below waits for that move; private APK exports,
firmware and recovery backups must be transferred separately from GitHub.

The owner approved the reviewed layout and private push on 23 October 2026.
Repository: `https://github.com/baileyboy0304/ES8_Athena`.

1. Once prepared, the agent verifies backup/recovery and wipes ES8 to the agreed
   **unlocked baseline**. This first wipe is authorised by the owner.
2. Refresh `echo-dot-assist/` from developer GitHub checkers; prove branch identity/clean tree.
3. Run that unchanged EDA installer.
4. Run VACAV installation including the optional selected streaming apps/firewall.
5. Configure HA through normal supported user setup and correct the instructions.
6. Perform basic checks, then hand the device to the owner for further testing.
7. **Only after the owner's later explicit OK**, wipe again for their own installer
   walkthrough and real-user feedback.

Do not treat step 1 authorisation as permission for step 7. No community publication
until the owner accepts the product. Keep checks economical; do not run broad
inherited suites or repeat device tests without a reason.
