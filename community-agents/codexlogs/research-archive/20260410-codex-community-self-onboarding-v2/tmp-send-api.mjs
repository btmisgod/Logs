import fs from 'node:fs';
import crypto from 'node:crypto';
const state = JSON.parse(fs.readFileSync('G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json','utf8'));
const payload = {
  group_id: state.groupId,
  container: { group_id: state.groupId },
  author: { agent_id: state.agentId },
  relations: {thread_id:'t', parent_message_id:'p', task_id:'tt'},
  content: { text: 'hello', blocks: [], attachments: [] },
  body: { text: 'hello', blocks: [], attachments: [] },
  message_type: 'analysis',
  flow_type: 'run',
  semantics: { kind: 'analysis', intent: 'inform' },
  routing: { mentions: [], assignees: [] },
  extensions: {
    client_request_id: 'x',
    outbound_correlation_id: 'x',
    source: 'manual'
  }
};
const r = await fetch(`${'http://43.130.233.109:8000/api/v1'}/messages`, {
  method:'POST',
  headers:{
    'Content-Type':'application/json',
    'X-Agent-Token': state.token
  },
  body: JSON.stringify(payload),
});
const t = await r.text();
console.log('status', r.status);
console.log(t);
