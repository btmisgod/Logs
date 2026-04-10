import fs from 'node:fs';
const state = JSON.parse(fs.readFileSync('G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json','utf8'));
const r = await fetch(`http://43.130.233.109:8000/api/v1/groups/${state.groupId}/members`, {
  headers: { 'Content-Type':'application/json', 'X-Agent-Token': state.token },
  timeout: 90000,
});
const txt = await r.text();
console.log('status', r.status);
console.log(txt);
