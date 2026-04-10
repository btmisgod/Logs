const payload = {
  group_id: '54b12c32-dbd3-46d8-97ee-22bf8a499709',
  content: { text: 'send-route test from local' },
  message_type: 'analysis'
};
const resp = await fetch('http://127.0.0.1:8848/send/codex-self-onboard-v2', {
  method: 'POST',
  headers: {'content-type': 'application/json'},
  body: JSON.stringify(payload),
  signal: AbortSignal.timeout(10000),
});
console.log('status', resp.status);
console.log(await resp.text());
