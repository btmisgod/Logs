import json
from pathlib import Path

env_path = Path('/root/openclaw-33/workspace/.openclaw/community-agent.env')
bootstrap_path = Path('/root/openclaw-33/workspace/.openclaw/community-agent.bootstrap.json')

replacements = {
    'COMMUNITY_SERVICE_NAME': 'openclaw-community-webhook-openclaw-33.service',
    'COMMUNITY_AGENT_NAME': 'openclaw-33',
    'COMMUNITY_AGENT_SOCKET_PATH': '/root/.openclaw/community-ingress/sockets/openclaw-33-443c3db99818.sock',
    'COMMUNITY_WEBHOOK_PATH': '/webhook/openclaw-33',
    'COMMUNITY_SEND_PATH': '/send/openclaw-33',
    'COMMUNITY_WEBHOOK_PUBLIC_URL': 'http://43.130.233.109:8848/webhook/openclaw-33',
    'COMMUNITY_AGENT_DISPLAY_NAME': 'openclaw-33',
    'COMMUNITY_AGENT_HANDLE': 'openclaw-33',
}

def parse_env(text):
    result = {}
    order = []
    for line in text.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        result[key] = value.strip()
        order.append(key)
    return result, order

raw = env_path.read_text(encoding='utf-8')
values, order = parse_env(raw)
for key, value in replacements.items():
    values[key] = f"'{value}'"
    if key not in order:
        order.append(key)
new_env = '\n'.join(f"{key}={values[key]}" for key in order) + '\n'
env_path.with_suffix('.env.bak-20260410-manager-identity-drift').write_text(raw, encoding='utf-8')
env_path.write_text(new_env, encoding='utf-8')

bootstrap = json.loads(bootstrap_path.read_text(encoding='utf-8'))
bootstrap_before = dict(bootstrap)
bootstrap.update({
    'agent_slug': 'openclaw-33',
    'service_name': 'openclaw-community-webhook-openclaw-33.service',
    'socket_path': '/root/.openclaw/community-ingress/sockets/openclaw-33-443c3db99818.sock',
    'webhook_path': '/webhook/openclaw-33',
    'send_path': '/send/openclaw-33',
})
bootstrap_path.with_suffix('.json.bak-20260410-manager-identity-drift').write_text(json.dumps(bootstrap_before, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
bootstrap_path.write_text(json.dumps(bootstrap, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(json.dumps({'ok': True, 'env_path': str(env_path), 'bootstrap_path': str(bootstrap_path)}, ensure_ascii=False))
