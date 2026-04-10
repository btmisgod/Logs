import fs from 'node:fs';
import crypto from 'node:crypto';
const state = JSON.parse(fs.readFileSync('G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json', 'utf8'));
const payload = {
  event: {
    event_type: 'message.posted',
    event_id: `proof-event-${crypto.randomUUID()}`,
    created_at: new Date().toISOString(),
    group_id: state.groupId,
    actor_agent_id: crypto.randomUUID(),
  },
  entity: {
    message: {
      group_id: state.groupId,
      author: { agent_id: crypto.randomUUID() },
      container: { group_id: state.groupId },
      relations: {
        thread_id: crypto.randomUUID(),
      },
      body: {
        text: 'final proof ping no id: @codex-self-onboard-v2 please send a short ack',
        blocks: [],
        attachments: [],
      },
      content: {
        text: 'final proof ping no id: @codex-self-onboard-v2 please send a short ack',
        metadata: {
          intent: 'inform',
          flow_type: 'discussion',
        },
      },
      semantics: {
        kind: 'analysis',
        intent: 'inform',
      },
      message_type: 'analysis',
      flow_type: 'discussion',
      routing: {
        target: {},
        mentions: [],
        assignees: [],
      },
      extensions: {
        source: 'final-proof-discussion-no-id',
      },
    },
  },
};
const body = JSON.stringify(payload);
const sig = crypto.createHmac('sha256', state.webhookSecret).update(body).digest('hex');
const response = await fetch('http://127.0.0.1:8848/webhook/codex-self-onboard-v2', {
  method: 'POST',
  headers: {
    'content-type': 'application/json',
    'x-community-webhook-signature': sig,
  },
  body,
});
const text = await response.text();
fs.writeFileSync('G:/community agnts/community agents/codexlogs/research-archive/20260410-codex-community-self-onboarding-v2/last-webhook-body.json', body);
fs.writeFileSync('G:/community agnts/community agents/codexlogs/research-archive/20260410-codex-community-self-onboarding-v2/last-webhook-signature.txt', sig);
fs.writeFileSync('G:/community agnts/community agents/codexlogs/research-archive/20260410-codex-community-self-onboarding-v2/last-webhook-response.json', text);
console.log(JSON.stringify({ status: response.status, body: text, signature: sig, eventId: payload.event.event_id }));
