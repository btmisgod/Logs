Set-Location -Path "G:\community agnts\community agents\openclaw-for-community\skills\CommunityIntegrationSkill"
$env:WORKSPACE_ROOT = 'G:\community agnts\community agents'
Get-Content 'G:\community agnts\community agents\.openclaw\community-agent.env' | ForEach-Object {
  if ($_ -match '^(.*?)=(.*)$') {
    $k = $matches[1]
    $v = $matches[2].Trim("'", '"')
    Set-Item env:$k $v
  }
}
node "G:\community agnts\community agents\openclaw-for-community\skills\CommunityIntegrationSkill\scripts\community-webhook-server.mjs"
