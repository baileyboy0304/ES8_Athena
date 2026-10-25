# Product decisions

- This is a Linux-only Echo Show 8 Gen 2 installation package.
- Echo Dot Assist comes from the developer's checkers branch as an unchanged Git
  submodule. Unlocking, firmware and root instructions belong to that project.
- VACAVision connects the display to View Assist and owns the single Echo Dot
  Assist voice connection. Amazon supplies wake-word detection and audio processing;
  Echo Dot Assist provides Sendspin on the device.
- Streaming services are optional. VACAVision web access is required whenever it
  is installed. The separate installer adapts installed firewall files with backups
  and version checks; upstream source remains unchanged.
- Use the official Music Assistant physical-player entity for View Assist music
  and alerts. Do not route MA actions to the VACAVision proxy.
- Keep the native voice indicator and floating Home/Keep on/Brightness controls.
- ITVX live audio continuing after Home remains a known trial issue.
- The README is the complete user installation guide. Lyrics installation is
  coming soon. Firmware, streaming APK exports, credentials and recovery images
  stay private and outside Git.
- Private repository publication is authorised. Public release and another
  destructive reset require the owner's explicit instruction.
