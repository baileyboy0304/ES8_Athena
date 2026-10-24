# Dashboard profiles

`devices/es8-gen2/profile.json` and `devices/portal_plus_gen_2/profile.json` are the installable device
definitions. Add further profiles using the same fields: distinct ID/slugs,
shortcut scale and service entries (`id`, `name`, `icon`, `package`, `url`).
The dashboard generator loads these definitions rather than hard-coding app lists.
The USB installer supports only the two named hardware targets.

Home includes a Music Assistant view with a persistent Home button.
`assets/athena-music-card.js` adapts the owner’s existing HA Home Music frame,
using a profile-specific return path and VA screen mode for kiosk height.
`custom/navigation.json` retains the original clock shortcut styling.
`install-ha` copies the frame to `/local/es8-athena/`; `deploy-dashboards` registers
its versioned module resource. Existing Portal resources remain untouched.

Installed pages are Home, TV and the following VA views:

- Your updated **clock** and **weather**, with household navigation removed and
  Home/TV controls added. Clock face, weather layout, day/night styling and shared
  templates come from the saved updated Portal dashboard.
- Standard upstream **alarm, alert, calendar, camera, info, infopic, intent, list,
  locate, music, sports, thermostat, webpage**.

Alternative clock, camera, music and list cards and community YAML contributions
remain in `devices/dashboards/upstream/views/` as references; they are not installed as
duplicate default views. Standard clock/weather originals are retained there too.
Large sample-background collections/community ZIPs are omitted. The pinned commit
and precise copied file list are in `devices/dashboards/upstream/source.json`.

VA blueprint-driven views rely on VA attributes/services. Creating a camera,
calendar, thermostat, sports or locate view does not create the corresponding
HA entities or configure all voice blueprints. Configure those standard VA
features using the upstream documentation as needed.

Install the actual custom card dependencies through HACS/manual resources before
opening the dashboard. The source inventory contains:

| Card/resource | Used for |
|---|---|
| button-card | VA templates and custom clock/weather |
| view-assist-weather-card | Weather |
| calendar-card-pro | Calendar |
| mini-media-player | Music |
| teamtracker-card | Sports, with Team Tracker configured separately |
| layout-card (including horizontal-layout/masonry-layout) | Standard layouts |
| card-mod (mod-card) | Card styling |
| advanced-camera-card | Optional alternative camera YAML |
| View Assist frontend custom elements | Clock rendering, display connection and overlays |

Use View Assist's documented versions/configuration; the repo does not bundle
third-party HACS frontend JavaScript. Asset URLs are rewritten to
`/local/es8-athena/`, populated by `install.py install-ha`. No VA-managed overlay
or custom-overlay file is replaced by the dashboard installer.

Home deliberately uses only three simple buttons. TV keeps the selected
launchers; no-selection gives an explanatory empty state. Use VACAV to open
`app://` / Android intent links; a desktop browser cannot launch those Android
packages. Home/TV remain visible in VA so it is easy to navigate back.

Generated files in `installation-data/generated/PROFILE/` include both JSON and YAML. They can be
imported through a storage dashboard's Raw configuration editor instead of using
the WebSocket installer. The editor should retain the top-level templates and
view paths used by VA blueprints.

Sources: [View Assist dashboard and views](https://github.com/dinki/View-Assist/tree/9a9ad40879543d51fcc86a34ef645e9a356ecc5a/View%20Assist%20dashboard%20and%20views)
and [View Assist documentation](https://dinki.github.io/View-Assist/).
