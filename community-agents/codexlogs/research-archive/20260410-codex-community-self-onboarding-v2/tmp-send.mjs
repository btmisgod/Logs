import fs from 'node:fs';
import crypto from 'node:crypto';
const state = JSON.parse(fs.readFileSync('G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json', 'utf8'));
const t = new Date().toISOString().replace(/[-:.]/g,'').replace('T','').replace('Z','');
const payload = {
  event: {
    event_type: 'message.posted',
    event_id: `proof-event-disc-${t}`,
    created_at: new Date().toISOString(),
    group_id: state.groupId,
  },
  entity: {
    message: {
      id: `msg-proof-disc-${t}`,
      container: { group_id: state.groupId },
      author: { agent_id: 'external-sender-agent' },
      relations: {
        thread_id: `thread-discussion-${t}`,
        parent_message_id: `parent-discussion-${t}`,
        task_id: `task-discussion-${t}`,
      },
      body: {
        text: 'Test message: @codex-self-onboard-v2£¬please send brief acknowledgement.',
        blocks: [],
        attachments: [],
      },
      message_type: 'analysis',
      semantics: { kind: 'analysis', intent: 'inform' },
      routing: { target: {}, mentions: [], assignees: [] },
      extensions: { source: 'manual-proof-discussion', custom: {} },
      content: {
        text: 'Test message: @codex-self-onboard-v2£¬please send brief acknowledgement.',
        mentions: [],
        metadata: {
          intent: 'inform',
          flow_type: 'discussion',
        },
      },
      flow_type: 'discussion',
    },
  },
};
const body = JSON.stringify(payload);
const sig = crypto.createHmac('sha256', state.webhookSecret).update(body).digest('hex');
const r = await fetch('http://127.0.0.1:8848/webhook/codex-self-onboard-v2', {
  method: 'POST',
  headers: {
    'content-type': 'application/json',
    'x-community-webhook-signature': sig,
  },
  body,
});
const text = await r.text();
console.log('status', r.status);
console.log('body', text);
console.log('sig', sig);
console.log('payloadLength', body.length);
