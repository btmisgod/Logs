const payload = {
  group_id: '54b12c32-dbd3-46d8-97ee-22bf8a499709',
  content: { text: `route test ${Date.now()} with unique` },
  message_type: 'analysis',
};
const start = Date.now();
try {
  const resp = await fetch('http://127.0.0.1:8848/send/codex-self-onboard-v2', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(90000),
  });
  const txt = await resp.text();
  console.log('status', resp.status);
  console.log('timeMs', Date.now()-start);
  console.log('body', txt);
} catch (error) {
  console.log('send-route failed', error.name, error.message);
  console.log('timeMs', Date.now()-start);
}
