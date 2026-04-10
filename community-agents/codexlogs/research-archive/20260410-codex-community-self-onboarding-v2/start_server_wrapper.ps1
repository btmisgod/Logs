$ErrorActionPreference = 'Stop'

Set-Location -Path 'G:\community agnts\community agents\openclaw-for-community\skills\CommunityIntegrationSkill'

$env:WORKSPACE_ROOT = 'G:\community agnts\community agents'
$envFile = Join-Path $env:WORKSPACE_ROOT '.openclaw/community-agent.env'

if (Test-Path -Path $envFile) {
  Get-Content -Path $envFile | ForEach-Object {
    if ([string]::IsNullOrWhiteSpace($_) -or $_.TrimStart().StartsWith('#')) {
      return
    }
    $separatorIndex = $_.IndexOf('=')
    if ($separatorIndex -lt 1) {
      return
    }
    $key = $_.Substring(0, $separatorIndex).Trim()
    $rawValue = $_.Substring($separatorIndex + 1).Trim()
    if ([string]::IsNullOrWhiteSpace($key)) {
      return
    }
    if ($rawValue.Length -ge 2 -and (($rawValue.StartsWith("'") -and $rawValue.EndsWith("'")) -or ($rawValue.StartsWith('"') -and $rawValue.EndsWith('"')))) {
      $rawValue = $rawValue.Substring(1, $rawValue.Length - 2)
    }
    Set-Item "env:$key" $rawValue
  }
}

$defaults = @{
  COMMUNITY_TRANSPORT = 'http'
  COMMUNITY_WEBHOOK_HOST = '127.0.0.1'
  COMMUNITY_WEBHOOK_PORT = '8848'
  COMMUNITY_WEBHOOK_PATH = "/webhook/$($env:COMMUNITY_AGENT_HANDLE)"
  COMMUNITY_SEND_PATH = "/send/$($env:COMMUNITY_AGENT_HANDLE)"
  COMMUNITY_BASE_URL = 'http://43.130.233.109:8000/api/v1'
  COMMUNITY_GROUP_SLUG = 'public-lobby'
  COMMUNITY_TEMPLATE_HOME = "$env:WORKSPACE_ROOT\.openclaw\community-agent-template"
  COMMUNITY_WEBHOOK_PUBLIC_HOST = '127.0.0.1'
  COMMUNITY_WEBHOOK_PUBLIC_URL = "http://127.0.0.1:8848/webhook/$($env:COMMUNITY_AGENT_HANDLE)"
  COMMUNITY_AGENT_NAME = 'desktop-codex-self-onboard-v2'
  COMMUNITY_AGENT_HANDLE = 'codex-self-onboard-v2'
  COMMUNITY_AGENT_DISPLAY_NAME = 'Desktop Codex Community Identity'
  COMMUNITY_AGENT_DESCRIPTION = 'Self-onboarding v2 for desktop Codex'
  COMMUNITY_AGENT_IDENTITY = 'Desktop Codex Operator'
  COMMUNITY_AGENT_TAGLINE = 'Desktop Codex handles one community identity and proof loop.'
  COMMUNITY_RESET_STATE_ON_START = '0'
}

foreach ($entry in $defaults.GetEnumerator()) {
  if (-not (Test-Path env:$($entry.Key))) {
    Set-Item "env:$($entry.Key)" $entry.Value
  }
}

if ($env:COMMUNITY_AGENT_HANDLE -and -not $env:COMMUNITY_WEBHOOK_PATH) {
  $env:COMMUNITY_WEBHOOK_PATH = "/webhook/$($env:COMMUNITY_AGENT_HANDLE)"
}
if ($env:COMMUNITY_AGENT_HANDLE -and -not $env:COMMUNITY_SEND_PATH) {
  $env:COMMUNITY_SEND_PATH = "/send/$($env:COMMUNITY_AGENT_HANDLE)"
}
if ($env:COMMUNITY_WEBHOOK_PUBLIC_HOST -and -not $env:COMMUNITY_WEBHOOK_PUBLIC_URL) {
  $env:COMMUNITY_WEBHOOK_PUBLIC_URL = "http://$($env:COMMUNITY_WEBHOOK_PUBLIC_HOST):$($env:COMMUNITY_WEBHOOK_PORT)$($env:COMMUNITY_WEBHOOK_PATH)"
}

node scripts/community-webhook-server.mjs
