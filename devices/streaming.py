"""Optional installed-firewall adaptation. Never edits the bundled EDA source."""
import hashlib
from pathlib import Path
import re
from install import ROOT, save

POLICY = '/data/local/es8-athena-streaming.conf'

def adapted_firewall():
    original = (ROOT / 'echo-dot-assist/scripts/device/lockdown.sh').read_bytes()
    helper = (ROOT / 'devices/streaming/profile-functions.sh').read_bytes()
    anchor = b'WLAN=${WLAN:-wlan0}\n'
    rule = b'    echo "-A hassmic_out -m owner --gid-owner $NET_GID -j RETURN"\n'
    if original.count(anchor) != 1 or original.count(rule) != 1:
        raise RuntimeError('Unsupported upstream firewall shape')
    changed = original.replace(anchor, b'# ES8 Athena optional streaming configuration\n' + helper + b'\n' + anchor)
    changed = changed.replace(rule, rule + b'    android_web_rules\n')
    changed = changed.replace(b'*uid-owner*) echo "!! OTA GUARD NOT ACTIVE', b'*uid-owner*DROP*) echo "!! OTA GUARD NOT ACTIVE')
    return original, changed

def configure(adb, shell, cfg, backup):
    """Adapt only known active/factory scripts; atomically restore on write failure."""
    original, changed = adapted_firewall()
    baseline = hashlib.sha256(original).hexdigest()
    adapted = hashlib.sha256(changed).hexdigest()
    selected = cfg['services']
    candidates = ['/system/hassmic/lockdown.sh', '/data/local/hassmic/lockdown.sh',
                  '/data/local/hassmic/ota/current/lockdown.sh']
    paths = []
    for candidate in candidates:
        if shell('test -f ' + candidate + ' && echo yes || true') != 'yes': continue
        remote = shell('readlink -f ' + candidate)
        if not re.fullmatch(r'/(?:system/hassmic|data/local/hassmic(?:/ota/[A-Za-z0-9_.-]+)?)/lockdown\.sh', remote):
            raise RuntimeError('Unexpected firewall location; stopped: ' + remote)
        if remote in paths: continue
        paths.append(remote)
    if '/system/hassmic/lockdown.sh' not in paths:
        raise RuntimeError('EDA factory firewall missing')
    record = []
    for index, remote in enumerate(paths):
        digest = shell('sha256sum ' + remote).split()[0]
        if digest not in (baseline, adapted):
            raise RuntimeError('Installed firewall differs from pristine checkers or this adapter: ' + remote + '. No firewall files changed.')
        local = backup / f'firewall-{index}.sh'
        adb('pull', remote, str(local))
        if hashlib.sha256(local.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Firewall backup hash mismatch')
        context = shell('ls -Zd ' + remote).split()[0]
        if not re.fullmatch(r'u:object_r:[a-zA-Z0-9_]+:s0', context):
            raise RuntimeError('Unexpected SELinux label')
        record.append(dict(remote=remote, backup=local.name, sha256=digest, context=context))
    policy_exists = shell('test -f ' + POLICY + ' && echo yes || true') == 'yes'
    if policy_exists: adb('pull', POLICY, str(backup / 'streaming-before.conf'))
    save(backup / 'streaming-rollback.json', {'files':record, 'policy_existed':policy_exists})
    if not selected and all(x['sha256'] == baseline for x in record) and not policy_exists:
        print('No streaming selected: installed EDA firewall left unchanged.')
        return
    target = backup / 'firewall-requested.sh'
    target.write_bytes(changed if selected else original)
    adb('push', str(target), '/data/local/tmp/es8-athena-firewall.sh')
    payload = ROOT / 'installation-data/generated' / cfg['profile'] / 'android.conf'
    adb('push', str(payload), '/data/local/tmp/es8-athena-streaming.conf')
    for local, remote in [(target,'/data/local/tmp/es8-athena-firewall.sh'),(payload,'/data/local/tmp/es8-athena-streaming.conf')]:
        if shell('sha256sum '+remote).split()[0] != hashlib.sha256(local.read_bytes()).hexdigest():
            raise RuntimeError('Streaming payload transfer mismatch')
    def replace(stage, dest, context):
        shell('cp -p '+dest+' '+dest+'.es8-new && cat '+stage+' > '+dest+'.es8-new && chown 0:0 '+dest+'.es8-new && chmod 755 '+dest+'.es8-new && chcon '+context+' '+dest+'.es8-new && mv '+dest+'.es8-new '+dest)
    touched = []
    shell('/system/hassmic/otatool remount rw /system')
    try:
        if selected:
            shell('cp /data/local/tmp/es8-athena-streaming.conf '+POLICY+'.new && chown 0:0 '+POLICY+'.new && chmod 600 '+POLICY+'.new && mv '+POLICY+'.new '+POLICY)
        else:
            shell('rm -f '+POLICY)
        for item in record:
            # Refuse a concurrent EDA update after the read-only preparation.
            if shell('sha256sum '+item['remote']).split()[0] != item['sha256']:
                raise RuntimeError('EDA changed during streaming installation')
            touched.append(item)
            replace('/data/local/tmp/es8-athena-firewall.sh',item['remote'],item['context'])
            if shell('sha256sum '+item['remote']).split()[0] != (adapted if selected else baseline):
                raise RuntimeError('Installed firewall hash mismatch')
    except Exception:
        for item in reversed(touched):
            adb('push',str(backup/item['backup']),'/data/local/tmp/es8-athena-firewall-rollback.sh')
            replace('/data/local/tmp/es8-athena-firewall-rollback.sh',item['remote'],item['context'])
        if policy_exists:
            adb('push',str(backup/'streaming-before.conf'),'/data/local/tmp/es8-athena-profile-rollback.conf')
            shell('cp /data/local/tmp/es8-athena-profile-rollback.conf '+POLICY+' && chown 0:0 '+POLICY+' && chmod 600 '+POLICY)
        else: shell('rm -f '+POLICY)
        raise
    finally:
        shell('/system/hassmic/otatool remount ro /system')
    # Existing EDA watcher remains the single firewall owner; reload its script.
    shell('setprop ctl.restart hassmic_fw')
    print('Streaming firewall choice saved. Reboot once, then check playback and EDA firewall status.')
    print('Installed policy was adapted; upstream source/installer are unchanged. Rollback:',backup)
