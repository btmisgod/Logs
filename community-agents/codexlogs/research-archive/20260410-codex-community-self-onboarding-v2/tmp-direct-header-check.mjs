import fs from 'node:fs';
import crypto from 'node:crypto';
const state = JSON.parse(fs.readFileSync('G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json','utf8'));
const payload = {
  group_id: state.groupId,
  container: { group_id: state.groupId },
  author: { agent_id: state.agentId },
  relations: { thread_id: crypto.randomUUID(), parent_message_id: null, task_id: null },
  content: { text: 'direct header test from node', blocks: [], attachments: [] },
  body: { text: 'direct header test from node', blocks: [], attachments: [] },
  message_type: 'analysis',
  flow_type: 'run',
  semantics: { kind: 'analysis', intent: 'inform' },
  routing: { mentions: [], assignees: [] },
  extensions: {
    client_request_id: crypto.randomUUID(),
    outbound_correlation_id: crypto.randomUUID(),
    source: 'CommunityIntegrationSkill',
  },
};
const r = await fetch('http://43.130.233.109:8000/api/v1/messages', {
  method:'POST',
  headers:{
    'Content-Type':'application/json',
    'X-Agent-Token': state.token,
    'X-Community-Skill-Channel':'community-skill-v1'
  },
  body: JSON.stringify(payload),
});
const text = await r.text();
console.log('status', r.status);
console.log(text);
