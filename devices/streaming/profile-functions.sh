#!/system/bin/sh
# Optional owner-managed Android web exceptions, independent of signed payloads.
# Data only: never source the file. Root-only writes; no app or daemon API edits it.
android_profile() {
    p=/data/local/es8-athena-streaming.conf
    ANDROID_WEB=
    [ -e "$p" ] || return 0
    [ ! -L "$p" ] && [ -f "$p" ] || return 1
    case "$(stat -c %u:%a "$p" 2>/dev/null)" in 0:600|0:644) ;; *) return 1;; esac
    case "$(stat -c %u:%a /data/local 2>/dev/null)" in 0:755|0:751|0:750|0:711|0:710|0:701|0:700) ;; *) return 1;; esac
    while IFS='=' read -r k v || [ -n "$k" ]; do
        case "$k" in
            ''|'#'*) continue;;
            web_packages) ANDROID_WEB=$v;;
            *) echo "android profile: unknown key $k" >&2; return 1;;
        esac
    done < "$p"
    # Validate before word splitting (which otherwise expands wildcard tokens).
    case "$ANDROID_WEB" in *[!a-zA-Z0-9_.\ ]*) return 1;; esac
    # Exact tokens only: no glob expansion, traversal or shell expressions.
    for v in $ANDROID_WEB; do
        case "$v" in ''|*[!a-zA-Z0-9_.]*|.*|*..*) return 1;; esac
    done
}

# Called before system writes so the installer makes the selected policy visible.
android_notice() {
    android_profile || return 1
    echo 'Android streaming: optional. No profile/web_packages means no app exceptions.'
    if [ -n "$ANDROID_WEB" ]; then
        echo "Requested streaming web access: $ANDROID_WEB"
        echo 'Only these eligible app UIDs may use TCP 80/443 to any internet host (IPv4/IPv6).'
        echo 'This includes their login, DRM, browser, ads and telemetry traffic, not just video.'
        echo 'UDP/QUIC and other internet ports stay blocked; Alexa/updater blocking stays active.'
        echo 'Missing, system/shared-UID and Alexa/setup/updater apps get no exception.'
    else
        echo 'Streaming web access: NO. Existing EDA network policy is unchanged.'
    fi
    return 0
}

# Re-resolve at every firewall check so uninstall/reinstall cannot authorize a stale UID.
# Reject shared and system UIDs: a package name must grant only that package internet.
android_web_uids() {
    android_profile || return 0
    for package in $ANDROID_WEB; do
        case " $ALEXA_PACKAGES $SETUP_PACKAGES $UPDATE_PACKAGES " in *" $package "*) continue;; esac
        awk -v p="$package" '
            { count[$2]++; if ($1 == p) uid=$2 }
            END { if (uid ~ /^[0-9]+$/ && uid >= 10000 && count[uid] == 1) print uid }
        ' /data/system/packages.list 2>/dev/null
    done | sort -nu
}

android_web_rules() {
    for uid in $(android_web_uids); do
        for port in 80 443; do
            echo "-A hassmic_out -p tcp -m tcp --dport $port -m owner --uid-owner $uid -j RETURN"
        done
    done
}
