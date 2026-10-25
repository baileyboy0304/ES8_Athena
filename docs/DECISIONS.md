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

- VACAV is published separately at baileyboy0304/VACAV as a public HACS integration,
  with explicit owner approval. ES8_Athena remains private and pins VACAV as a submodule.

## User-managed View Assist setup (25 October 2026)

The Linux wizard installs the app and selected streaming services. It sends the
chosen name, dashboard destinations and public Sendspin identity over USB.
VACAV connects the existing voice and music services automatically.

The user creates the View Assist device through its normal Add device form.
VACAV extends older View Assist microphone selectors to include its satellites;
it does not write View Assist entries or configuration. The README names each
field and explains how to identify this Echo’s entities.

Example dashboards are an optional action under the VACAV device’s Configure
menu. An administrator opens the device-specific installer, which reads that
View Assist device’s weather and player settings. The installer uses HA’s normal
WebSocket dashboard APIs, backs up existing configurations, and requires explicit
confirmation before replacement. Completion shows the View Assist dashboard paths
for the user to enter. The dashboard installer is not registered in the sidebar.

The APK uses the Linux signing certificate starting with prototype.11. Preserve
that key for future builds. Updates from prototype.10 require its original key or
a deliberate app reinstall with private backups.
