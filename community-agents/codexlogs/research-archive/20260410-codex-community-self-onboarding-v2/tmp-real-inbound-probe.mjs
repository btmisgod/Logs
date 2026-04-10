import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawn } from "node:child_process";

const workspaceRoot = "G:/community agnts/community agents";
const skillRoot = path.join(workspaceRoot, "openclaw-for-community", "skills", "CommunityIntegrationSkill");
const serverScript = path.join(skillRoot, "scripts", "community-webhook-server.mjs");
const statePath = path.join(workspaceRoot, ".openclaw", "community-agent-template", "state", "community-webhook-state.json");
const envFile = path.join(workspaceRoot, ".openclaw", "community-agent.env");

const defaults = {
  WORKSPACE_ROOT: workspaceRoot,
  COMMUNITY_TRANSPORT: "http",
  COMMUNITY_WEBHOOK_HOST: "127.0.0.1",
  COMMUNITY_WEBHOOK_PORT: "8848",
  COMMUNITY_WEBHOOK_PATH: "/webhook/codex-pro",
  COMMUNITY_SEND_PATH: "/send/codex-pro",
  COMMUNITY_BASE_URL: "http://43.130.233.109:8000/api/v1",
  COMMUNITY_GROUP_SLUG: "public-lobby",
  COMMUNITY_TEMPLATE_HOME: `${workspaceRoot}\\\.openclaw\\community-agent-template`,
  COMMUNITY_WEBHOOK_PUBLIC_HOST: "127.0.0.1",
  COMMUNITY_WEBHOOK_PUBLIC_URL: "http://127.0.0.1:8848/webhook/codex-pro",
  COMMUNITY_AGENT_NAME: "desktop-codex-pro",
  COMMUNITY_AGENT_HANDLE: "codex-pro",
  COMMUNITY_AGENT_DISPLAY_NAME: "Codex Pro",
  COMMUNITY_AGENT_DESCRIPTION: "Self-onboarding v2 for desktop Codex",
  COMMUNITY_AGENT_IDENTITY: "Codex Pro",
  COMMUNITY_AGENT_TAGLINE: "Desktop Codex handles one community identity and proof loop.",
  COMMUNITY_RESET_STATE_ON_START: "0",
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function request(pathname, method, headers = {}, body = null, port = 8848) {
  return new Promise((resolve) => {
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port,
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
          resolve({ status: res.statusCode, headers: res.headers, body: out });
        });
      },
    );
    req.on("error", (error) => {
      resolve({ status: -1, headers: {}, body: error.message });
    });
    if (body) {
      req.write(body);
    }
    req.end();
  });
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
    const value = line
      .slice(idx + 1)
      .trim()
      .replace(/^['"]|['"]$/g, "");
    if (key) {
      result[key] = value;
    }
  }
  return result;
}

function parseJsonLines(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  return fs
    .readFileSync(filePath, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

async function waitForHealth() {
  for (let i = 0; i < 60; i++) {
    const result = await request("/healthz", "GET", { accept: "application/json" });
    if (result.status === 200) {
      return true;
    }
    await sleep(250);
  }
  return false;
}

async function main() {
  const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
  const fromFile = fs.existsSync(envFile) ? loadEnvFromFile(envFile) : {};
  const serverEnv = {
    ...process.env,
    ...defaults,
    ...fromFile,
    COMMUNITY_WEBHOOK_HOST: "0.0.0.0",
    COMMUNITY_WEBHOOK_PORT: "8848",
  };

  const outPath = path.join(process.cwd(), "tmp-real-inbound-probe-server.out.log");
  const errPath = path.join(process.cwd(), "tmp-real-inbound-probe-server.err.log");
  const outStream = fs.openSync(outPath, "w");
  const errStream = fs.openSync(errPath, "w");
  const serverProc = spawn("node", [serverScript], {
    cwd: skillRoot,
    env: serverEnv,
    stdio: ["ignore", outStream, errStream],
  });

  const stopServer = () => {
    if (!serverProc.killed) {
      serverProc.kill("SIGINT");
    }
    try {
      fs.closeSync(outStream);
      fs.closeSync(errStream);
    } catch {}
  };

  const proof = {
    verified_at: new Date().toISOString(),
    listener_port: defaults.COMMUNITY_WEBHOOK_PORT,
    webhook_path: defaults.COMMUNITY_WEBHOOK_PATH,
    steps: [],
    errors: [],
  };

  try {
    const ready = await waitForHealth();
    proof.steps.push({ name: "server_health", status: ready ? "ok" : "timeout" });
    if (!ready) {
      throw new Error("server did not become ready on /healthz");
    }

    const sendPayload = {
      group_id: state.groupId,
      container: { group_id: state.groupId },
      author: { agent_id: state.agentId },
      extensions: {
        source: "CommunityIntegrationSkill",
      },
      content: {
        text: "real inbound probe: please acknowledge",
        mentions: [],
        metadata: {
          intent: "inform",
          flow_type: "discussion",
          source: "tmp-real-inbound-probe",
        },
      },
      body: {
        text: "real inbound probe: please acknowledge",
        blocks: [],
        attachments: [],
      },
      message_type: "analysis",
      flow_type: "discussion",
      semantics: {
        kind: "analysis",
        intent: "inform",
      },
      routing: {
        mentions: [],
        assignees: [],
      },
    };

    const response = await fetch("http://43.130.233.109:8000/api/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Agent-Token": state.token,
        "X-Community-Skill-Channel": "community-skill-v1",
      },
      body: JSON.stringify(sendPayload),
    });
    const responseText = await response.text();
    proof.steps.push({
      name: "community_send",
      status: response.status,
      body: responseText,
      endpoint: "http://43.130.233.109:8000/api/v1/messages",
      token_present: Boolean(state.token),
    });

    await sleep(30000);

    const logs = parseJsonLines(outPath);
    const webhookEntries = logs.filter((entry) => entry?.ok === true && (entry?.webhook || entry?.event_type));
    const outboundEntries = logs.filter((entry) => entry?.ok === true && entry?.outbound_structured_message === true);
    const outboundReceipt = logs.filter((entry) => entry?.ok === true && entry?.outbound_receipt === true);

    proof.steps.push({
      name: "evidence_capture",
      status: "ok",
      webhook_entries: webhookEntries.length,
      outbound_structured_entries: outboundEntries.length,
      outbound_receipt_entries: outboundReceipt.length,
      sample_webhook_events: webhookEntries.slice(-8).map((entry) => ({
        event_type: entry.event_type,
        category: entry.category,
        handled: entry.handled,
        non_intake: entry.non_intake,
      })),
      sample_outbound_payloads: outboundEntries.slice(-5).map((entry) => ({
        has_thread_id: Boolean(entry.body?.relations?.thread_id),
        has_parent_message_id: Boolean(entry.body?.relations?.parent_message_id),
        thread_id: entry.body?.relations?.thread_id || null,
        parent_message_id: entry.body?.relations?.parent_message_id || null,
      })),
    });

    fs.writeFileSync(
      path.join(process.cwd(), "tmp-real-inbound-probe.json"),
      JSON.stringify(
        {
          ...proof,
          server_logs: {
            out: outPath,
            err: errPath,
          },
        },
        null,
        2,
      ),
      "utf8",
    );

    const statusCounts = {
      webhook: webhookEntries.length,
      outbound: outboundEntries.length,
      outbound_receipt: outboundReceipt.length,
    };
    console.log(JSON.stringify({ status: "ok", statusCounts }, null, 2));
  } catch (error) {
    proof.errors.push(error.message);
    fs.writeFileSync(
      path.join(process.cwd(), "tmp-real-inbound-probe.json"),
      JSON.stringify(
        {
          ...proof,
          server_logs: {
            out: outPath,
            err: errPath,
          },
        },
        null,
        2,
      ),
      "utf8",
    );
    throw error;
  } finally {
    stopServer();
  }
}

main().catch((error) => {
  console.error(`real inbound probe failed: ${error.message}`);
  process.exitCode = 1;
});
