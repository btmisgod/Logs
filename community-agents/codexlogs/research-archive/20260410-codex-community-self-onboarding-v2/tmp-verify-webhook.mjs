import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";

const statePath = "G:/community agnts/community agents/.openclaw/community-agent-template/state/community-webhook-state.json";
const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
const secret = state.webhookSecret;
const groupId = state.groupId;

const webhook = new URL("http://127.0.0.1:8848/webhook/codex-pro");

async function post(path, { method, headers = {}, body } = {}) {
  return new Promise((resolve) => {
    const req = http.request(
      {
        method,
        hostname: webhook.hostname,
        port: webhook.port,
        path,
        headers: Object.assign({ "content-type": "application/json" }, headers),
      },
      (res) => {
        let out = "";
        res.setEncoding("utf8");
        res.on("data", (chunk) => {
          out += chunk;
        });
        res.on("end", () => {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: out,
            path,
            method,
          });
        });
      },
    );
    req.on("error", (error) => {
      resolve({ status: -1, body: error.message, path, method, headers });
    });
    if (body) {
      req.write(body);
    }
    req.end();
  });
}

function makeEvent(name, eventType, hasParent = false) {
  const now = new Date().toISOString();
  const msgId = `m-${name}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
  const event = {
    event: {
      event_type: eventType,
      event_id: `test-${name}-${Date.now()}`,
      created_at: now,
      group_id: groupId,
      actor_agent_id: crypto.randomUUID(),
    },
    entity: {
      message: {
        id: msgId,
        group_id: groupId,
        author: { agent_id: crypto.randomUUID() },
        container: { group_id: groupId },
        relations: {
          thread_id: `t-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
          ...(hasParent ? { parent_message_id: `p-${Date.now()}-${Math.random().toString(16).slice(2, 8)}` } : {}),
        },
        body: {
          text: `verification ${name}`,
          blocks: [],
          attachments: [],
        },
        content: {
          text: `verification ${name}`,
          metadata: {
            intent: "inform",
            flow_type: "discussion",
          },
        },
        semantics: {
          kind: "analysis",
          intent: "inform",
        },
        message_type: "analysis",
        flow_type: "discussion",
        routing: {
          target: {},
          mentions: [],
          assignees: [],
        },
        extensions: {
          source: "manual-verification",
        },
      },
    },
  };
  return event;
}

async function run() {
  const results = [];
  results.push(await post("/healthz", { method: "GET", headers: { accept: "application/json" } }));

  const cases = [
    { name: "root-posted", eventType: "message.posted", hasParent: false },
    { name: "reply-posted", eventType: "message.posted", hasParent: true },
    { name: "outbound-receipt", eventType: "message.accepted", hasParent: false },
  ];

  for (const testCase of cases) {
    const payload = makeEvent(testCase.name, testCase.eventType, testCase.hasParent);
    const raw = JSON.stringify(payload);
    const sig = crypto.createHmac("sha256", secret).update(raw).digest("hex");
    const result = await post(webhook.pathname, {
      method: "POST",
      headers: {
        "x-community-webhook-signature": sig,
      },
      body: raw,
    });
    results.push({ name: testCase.name, ...result });
  }

  const badPayload = makeEvent("bad-signature", "message.posted", false);
  const badBody = JSON.stringify(badPayload);
  const badSig = crypto.randomBytes(32).toString("hex");
  const badRes = await post(webhook.pathname, {
    method: "POST",
    headers: {
      "x-community-webhook-signature": badSig,
    },
    body: badBody,
  });
  results.push({ name: "bad-signature", ...badRes });

  const noSig = await post(webhook.pathname, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: badBody,
  });
  results.push({ name: "no-signature", ...noSig });

  const wrongPath = await post("/webhook/not-your-path", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-community-webhook-signature": badSig,
    },
    body: badBody,
  });
  results.push({ name: "wrong-path", ...wrongPath });

  const validSendPayload = {
    text: "verification send probe",
    group_id: state.groupId,
    container: { group_id: state.groupId },
    author: { agent_id: state.agentId },
    relations: { thread_id: `send-${Date.now()}` },
    flow_type: "analysis",
    content: { text: "verification send probe", mentions: [], metadata: { intent: "inform", flow_type: "analysis" } },
    body: { text: "verification send probe", blocks: [], attachments: [] },
    semantics: { kind: "analysis", intent: "inform" },
    routing: { mentions: [], assignees: [] },
    message_type: "analysis",
    source: "test",
  };
  const sendPath = "/send/codex-pro";
  const sendRes = await post(sendPath, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(validSendPayload),
  });
  results.push({ name: "send-path", ...sendRes });

  console.log(JSON.stringify(results, null, 2));
}

run().catch((error) => {
  console.error(`FAIL: ${error.message}`);
  process.exit(1);
});
