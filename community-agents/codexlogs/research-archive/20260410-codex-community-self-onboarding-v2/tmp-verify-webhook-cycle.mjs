import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawn } from "node:child_process";

const workspaceRoot = "G:/community agnts/community agents";
const skillRoot = path.join(workspaceRoot, "openclaw-for-community", "skills", "CommunityIntegrationSkill");
const envFile = path.join(workspaceRoot, ".openclaw", "community-agent.env");
const serverScript = path.join(skillRoot, "scripts", "community-webhook-server.mjs");
const statePath = path.join(workspaceRoot, ".openclaw", "community-agent-template", "state", "community-webhook-state.json");

const defaults = {
  COMMUNITY_TRANSPORT: "http",
  COMMUNITY_WEBHOOK_HOST: "127.0.0.1",
  COMMUNITY_WEBHOOK_PORT: "8848",
  COMMUNITY_WEBHOOK_PATH: "/webhook/codex-pro",
  COMMUNITY_SEND_PATH: "/send/codex-pro",
  COMMUNITY_BASE_URL: "http://43.130.233.109:8000/api/v1",
  COMMUNITY_GROUP_SLUG: "public-lobby",
  COMMUNITY_TEMPLATE_HOME: `${workspaceRoot}\\.openclaw\\community-agent-template`,
  COMMUNITY_WEBHOOK_PUBLIC_HOST: "127.0.0.1",
  COMMUNITY_WEBHOOK_PUBLIC_URL: "http://127.0.0.1:8848/webhook/codex-pro",
  COMMUNITY_AGENT_NAME: "desktop-codex-self-onboard-v2",
  COMMUNITY_AGENT_HANDLE: "codex-pro",
  COMMUNITY_AGENT_DISPLAY_NAME: "Codex Pro",
  COMMUNITY_AGENT_DESCRIPTION: "Self-onboarding v2 for desktop Codex",
  COMMUNITY_AGENT_IDENTITY: "Codex Pro",
  COMMUNITY_AGENT_TAGLINE: "Desktop Codex handles one community identity and proof loop.",
  COMMUNITY_RESET_STATE_ON_START: "0",
};

function readJson(file, fallback = null) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return fallback;
  }
}

function loadEnvFromFile(file) {
  const data = fs.readFileSync(file, "utf8");
  const result = {};
  for (const raw of data.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    const idx = line.indexOf("=");
    if (idx < 0) {
      continue;
    }
    const key = line.slice(0, idx).trim();
    const value = line.slice(idx + 1).trim().replace(/^["']|["']$/g, "");
    if (key) {
      result[key] = value;
    }
  }
  return result;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function request(pathname, method, headers = {}, body = null) {
  return new Promise((resolve) => {
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port: Number(defaults.COMMUNITY_WEBHOOK_PORT),
        path: pathname,
        method,
        headers,
      },
      (res) => {
        let out = "";
        res.setEncoding("utf8");
        res.on("data", (chunk) => {
          out += chunk;
        });
        res.on("end", () => {
          resolve({ status: res.statusCode, body: out, headers: res.headers });
        });
      },
    );
    req.on("error", (error) => {
      resolve({ status: -1, body: error.message, headers: {} });
    });
    if (body) {
      req.write(body);
    }
    req.end();
  });
}

function makeEvent(name, eventType, hasParent, groupId, state) {
  const eventId = `test-${name}-${Date.now()}`;
  return {
    event: {
      event_type: eventType,
      event_id: eventId,
      created_at: new Date().toISOString(),
      group_id: groupId,
      actor_agent_id: crypto.randomUUID(),
    },
    entity: {
      message: {
        id: `m-${name}-${Date.now()}`,
        group_id: groupId,
        author: { agent_id: crypto.randomUUID() },
        container: { group_id: groupId },
        relations: {
          thread_id: `t-${Date.now()}-${name}`,
          ...(hasParent ? { parent_message_id: `p-${Date.now()}-${name}` } : {}),
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
          client_request_id: crypto.randomUUID(),
          outbound_correlation_id: crypto.randomUUID(),
        },
      },
    },
  };
}

function makeSignedPost(pathname, event, signatureSecret) {
  const raw = JSON.stringify(event);
  const signature = crypto.createHmac("sha256", signatureSecret).update(raw).digest("hex");
  return request(pathname, "POST", {
    "content-type": "application/json",
    "x-community-webhook-signature": signature,
  }, raw);
}

async function main() {
  const state = readJson(statePath);
  const stateSecret = state?.webhookSecret;
  if (!stateSecret) {
    throw new Error("No webhookSecret in state file");
  }

  const fromFile = loadEnvFromFile(envFile);
  const serverEnv = {
    ...process.env,
    WORKSPACE_ROOT: workspaceRoot,
    ...defaults,
    ...fromFile,
  };

  const serverLogPath = path.join(process.cwd(), "tmp-verify-webhook-cycle-server.log");
  const serverErrPath = path.join(process.cwd(), "tmp-verify-webhook-cycle-server.err");
  const outStream = fs.openSync(serverLogPath, "a");
  const errStream = fs.openSync(serverErrPath, "a");

  const serverProc = spawn("node", [serverScript], {
    cwd: skillRoot,
    env: serverEnv,
    stdio: ["ignore", outStream, errStream],
  });

  const stopServer = async () => {
    if (!serverProc.killed) {
      serverProc.kill("SIGINT");
      await sleep(500);
      if (!serverProc.killed) {
        serverProc.kill();
      }
    }
    fs.closeSync(outStream);
    fs.closeSync(errStream);
  };

  try {
    let ready = false;
    for (let i = 0; i < 60; i++) {
      const health = await request("/healthz", "GET", { accept: "application/json" });
      if (health.status === 200) {
        ready = true;
        break;
      }
      await sleep(250);
    }
    if (!ready) {
      throw new Error("server not ready on /healthz within 15s");
    }

    const results = [];
    const health = await request("/healthz", "GET", { accept: "application/json" });
    results.push({ name: "healthz", status: health.status, body: health.body });

    const groupId = state.groupId;
    const webhookPath = defaults.COMMUNITY_WEBHOOK_PATH;

    const root = makeEvent("root-posted", "message.posted", false, groupId, state);
    results.push({
      name: "root-posted",
      ...(await makeSignedPost(webhookPath, root, stateSecret)),
    });

    const reply = makeEvent("reply-posted", "message.posted", true, groupId, state);
    results.push({
      name: "reply-posted",
      ...(await makeSignedPost(webhookPath, reply, stateSecret)),
    });

    const receipt = makeEvent("outbound-receipt", "message.accepted", false, groupId, state);
    results.push({
      name: "outbound-receipt",
      ...(await makeSignedPost(webhookPath, receipt, stateSecret)),
    });

    const unknown = makeEvent("unhandled-event", "message.deleted", false, groupId, state);
    const unknownRaw = JSON.stringify(unknown);
    const unknownSig = crypto.createHmac("sha256", stateSecret).update(unknownRaw).digest("hex");
    const unknownResult = await request(webhookPath, "POST", {
      "content-type": "application/json",
      "x-community-webhook-signature": unknownSig,
    }, unknownRaw);
    results.push({ name: "unknown-event", ...unknownResult });

    const badSigRaw = JSON.stringify(makeEvent("bad-signature", "message.posted", false, groupId, state));
    const badSig = crypto.randomBytes(32).toString("hex");
    const bad = await request(webhookPath, "POST", {
      "content-type": "application/json",
      "x-community-webhook-signature": badSig,
    }, badSigRaw);
    results.push({ name: "bad-signature", ...bad });

    const wrongPath = await request("/webhook/does-not-exist", "POST", { "content-type": "application/json" }, "{}");
    results.push({ name: "wrong-path", ...wrongPath });

    const sendPath = defaults.COMMUNITY_SEND_PATH;
    const emptySendBody = await request(sendPath, "POST", { "content-type": "application/json" }, "{}");
    results.push({ name: "send-path-empty-body", ...emptySendBody });

    console.log(JSON.stringify(results, null, 2));

    const proof = {
      verified_at: new Date().toISOString(),
      results,
      server: {
        webhookPath: defaults.COMMUNITY_WEBHOOK_PATH,
        sendPath: defaults.COMMUNITY_SEND_PATH,
        host: defaults.COMMUNITY_WEBHOOK_HOST,
        port: defaults.COMMUNITY_WEBHOOK_PORT,
      },
      note: "Each webhook test except bad-signature/404 should return 202 and trigger receive path logs; 422 indicates outbound contract block not receive path.",
    };
    fs.writeFileSync(path.join(process.cwd(), "community-webhook-verification-proof.json"), JSON.stringify(proof, null, 2));
  } finally {
    await stopServer();
  }
}

main().catch((error) => {
  console.error(`verification failed: ${error.message}`);
  process.exit(1);
});
