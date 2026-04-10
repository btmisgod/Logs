$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$baseApi = 'http://43.130.233.109:8000/api/v1'
$baseIngress = 'http://43.130.233.109:8848'
$groupId = '8d9d8e44-54b2-4279-aab2-0a6d9ce851b2'
$groupSlug = 'news-test'
$workflowId = 'news-five-role-workflow-v1'
$results = [ordered]@{
  started_at = (Get-Date -Format o)
  group_id = $groupId
  group_slug = $groupSlug
  steps = @()
}

function Add-Step($name, $data) {
  $results.steps += [pscustomobject]@{ name = $name; data = $data }
}

function Get-AdminToken() {
  $body = @{ username='admin'; password='Admin123456!' } | ConvertTo-Json
  $resp = Invoke-RestMethod -Uri "$baseApi/auth/admin/login" -Method Post -ContentType 'application/json' -Body $body
  return $resp.data.access_token
}

function Get-Session([string]$token) {
  $headers = @{ Authorization = "Bearer $token" }
  return (Invoke-RestMethod -Uri "$baseApi/groups/by-slug/$groupSlug/session" -Headers $headers -Method Get).data
}

function Get-Events([string]$token, [int]$limit=200) {
  $headers = @{ Authorization = "Bearer $token" }
  return (Invoke-RestMethod -Uri "$baseApi/groups/$groupId/events?limit=$limit" -Headers $headers -Method Get).data.items
}

function Send-AgentMessage([string]$slug, $payload) {
  $json = $payload | ConvertTo-Json -Depth 30
  try {
    $resp = Invoke-WebRequest -Uri "$baseIngress/send/$slug" -Method Post -ContentType 'application/json' -Body $json -UseBasicParsing -ErrorAction Stop
    return @{ status = [int]$resp.StatusCode; body = ($resp.Content | ConvertFrom-Json) }
  } catch {
    $resp = $_.Exception.Response
    if ($resp) {
      $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
      $body = $reader.ReadToEnd()
      throw "send/$slug failed: HTTP $([int]$resp.StatusCode) body=$body"
    }
    throw
  }
}

function Assert-Stage([string]$token, [string]$expected, [string]$label) {
  Start-Sleep -Seconds 2
  $session = Get-Session $token
  if ($session.current_stage -ne $expected) {
    throw "$label expected stage '$expected' but got '$($session.current_stage)'"
  }
  return $session
}

function BasePayload([string]$flowType, [string]$messageType, [string]$text, [hashtable]$contentPayload, [hashtable]$statusBlock, [string]$cycleId, [int]$cycleIndex) {
  return @{
    group_id = $groupId
    flow_type = $flowType
    message_type = $messageType
    content = @{
      text = $text
      payload = $contentPayload
      blocks = @()
      attachments = @()
    }
    status_block = $statusBlock
    routing = @{ target=@{}; mentions=@() }
    relations = @{}
    extensions = @{ cycle_id = $cycleId; cycle_index = $cycleIndex; workflow_id = $workflowId; source = 'branch-a-two-cycle-run' }
  }
}

function Run-Cycle([string]$token, [string]$cycleId, [int]$cycleIndex, [hashtable]$data) {
  $managerId = 'b8beedf6-3540-4cf1-b22d-1dd6f5633b3a'
  $worker33Id = '8a8c144a-1efb-4c01-8084-f7bb45e33106'
  $workerXhsId = 'a734a7b8-1fe1-4779-a92b-f4f5268b4a95'
  $editorId = 'b5eff68e-0497-466f-9a74-734bcbb177b7'
  $testerId = '738e280d-af02-4618-85ed-2fd5fe4ab4b4'

  $cycle = [ordered]@{ cycle_id = $cycleId; cycle_index = $cycleIndex; checkpoints = @() }

  $startPayload = BasePayload 'start' 'decision' $data.start_text @{
    kind = 'cycle_start_command'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    workflow_id = $workflowId
    cycle_goal = $data.cycle_goal
  } @{
    workflow_id = $workflowId
    step_id = 'cycle_baseline_ready'
    lifecycle_phase = 'start'
    author_agent_id = $managerId
    author_role = 'manager'
    step_status = 'cycle_start'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='cycle_start_send'; result=(Send-AgentMessage 'openclaw-33' $startPayload) }
  $cycle.checkpoints += @{ step='cycle_start_stage'; session=(Assert-Stage $token 'material_collect' 'cycle_start') }

  $worker33Payload = BasePayload 'run' 'analysis' $data.worker33_text @{
    kind = 'candidate_material_pool'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    lane = 'worker-33'
    items = $data.worker33_items
  } @{
    workflow_id = $workflowId
    step_id = 'material_collect'
    lifecycle_phase = 'run'
    author_agent_id = $worker33Id
    author_role = 'worker'
    step_status = 'material_collect_submitted'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='worker33_send'; result=(Send-AgentMessage 'openclaw-33-worker-33' $worker33Payload) }
  $cycle.checkpoints += @{ step='worker33_stage'; session=(Assert-Stage $token 'material_collect' 'worker33 evidence') }

  $workerXhsPayload = BasePayload 'run' 'analysis' $data.workerXhs_text @{
    kind = 'candidate_material_pool'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    lane = 'worker-xhs'
    items = $data.workerXhs_items
  } @{
    workflow_id = $workflowId
    step_id = 'material_collect'
    lifecycle_phase = 'run'
    author_agent_id = $workerXhsId
    author_role = 'worker'
    step_status = 'material_collect_submitted'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='workerXhs_send'; result=(Send-AgentMessage 'openclaw-33-worker-xhs' $workerXhsPayload) }
  $cycle.checkpoints += @{ step='workerXhs_stage'; session=(Assert-Stage $token 'material_collect' 'worker-xhs evidence') }

  $managerCollectDone = BasePayload 'result' 'decision' $data.material_done_text @{
    kind = 'approved_material_pool'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    selected_materials = $data.selected_materials
    rejected_materials = @()
    evidence_refs = @('worker33-material-pool', 'workerXhs-material-pool')
  } @{
    workflow_id = $workflowId
    step_id = 'material_collect'
    lifecycle_phase = 'done'
    author_agent_id = $managerId
    author_role = 'manager'
    step_status = 'material_collect_done'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='material_done_send'; result=(Send-AgentMessage 'openclaw-33' $managerCollectDone) }
  $cycle.checkpoints += @{ step='material_done_stage'; session=(Assert-Stage $token 'editorial_review' 'material_collect done') }

  $editorPayload = BasePayload 'run' 'summary' $data.editor_text @{
    kind = 'draft_report_v1'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    report_title = $data.report_title
    items = $data.report_items
    report_markdown = $data.report_markdown
  } @{
    workflow_id = $workflowId
    step_id = 'editorial_review'
    lifecycle_phase = 'run'
    author_agent_id = $editorId
    author_role = 'editor'
    step_status = 'editorial_review_submitted'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='editor_send'; result=(Send-AgentMessage 'openclaw-33-editor' $editorPayload) }
  $cycle.checkpoints += @{ step='editor_stage'; session=(Assert-Stage $token 'editorial_review' 'editor evidence') }

  $managerEditorialDone = BasePayload 'result' 'decision' $data.editor_done_text @{
    kind = 'editorial_acceptance'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    accepted = $true
    evidence_refs = @('draft_report_v1')
    summary = $data.editor_acceptance_summary
  } @{
    workflow_id = $workflowId
    step_id = 'editorial_review'
    lifecycle_phase = 'done'
    author_agent_id = $managerId
    author_role = 'manager'
    step_status = 'editorial_review_done'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='editor_done_send'; result=(Send-AgentMessage 'openclaw-33' $managerEditorialDone) }
  $cycle.checkpoints += @{ step='editor_done_stage'; session=(Assert-Stage $token 'qa_validation' 'editorial_review done') }

  $testerPayload = BasePayload 'run' 'review' $data.tester_text @{
    kind = 'qa_validation_report'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    checklist = $data.tester_checklist
    verdict = 'pass'
    issues = @()
  } @{
    workflow_id = $workflowId
    step_id = 'qa_validation'
    lifecycle_phase = 'run'
    author_agent_id = $testerId
    author_role = 'tester'
    step_status = 'qa_validation_submitted'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='tester_send'; result=(Send-AgentMessage 'openclaw-33-tester' $testerPayload) }
  $cycle.checkpoints += @{ step='tester_stage'; session=(Assert-Stage $token 'qa_validation' 'qa evidence') }

  $managerQaDone = BasePayload 'result' 'decision' $data.qa_done_text @{
    kind = 'qa_acceptance'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    accepted = $true
    summary = $data.qa_acceptance_summary
  } @{
    workflow_id = $workflowId
    step_id = 'qa_validation'
    lifecycle_phase = 'done'
    author_agent_id = $managerId
    author_role = 'manager'
    step_status = 'qa_validation_done'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='qa_done_send'; result=(Send-AgentMessage 'openclaw-33' $managerQaDone) }
  $cycle.checkpoints += @{ step='qa_done_stage'; session=(Assert-Stage $token 'final_delivery' 'qa_validation done') }

  $finalPayload = BasePayload 'result' 'summary' $data.final_text @{
    kind = 'final_report'
    cycle_id = $cycleId
    cycle_index = $cycleIndex
    report_title = $data.report_title
    final_summary = $data.final_summary
    items = $data.report_items
    report_markdown = $data.report_markdown
  } @{
    workflow_id = $workflowId
    step_id = 'final_delivery'
    lifecycle_phase = 'done'
    author_agent_id = $managerId
    author_role = 'manager'
    step_status = 'cycle_final_delivered'
    related_message_id = $cycleId
  } $cycleId $cycleIndex
  $cycle.checkpoints += @{ step='final_send'; result=(Send-AgentMessage 'openclaw-33' $finalPayload) }
  $cycle.checkpoints += @{ step='final_stage'; session=(Assert-Stage $token 'cycle_baseline_ready' 'final_delivery done') }

  return $cycle
}

$token = Get-AdminToken
Add-Step 'baseline_session' (Get-Session $token)

$cycle1 = @{
  start_text = '第 1 轮正式启动：围绕中东停火、乌克兰前线和全球市场波动完成新闻采集。'
  cycle_goal = '完成第 1 轮国际热点新闻采集、编辑、质检与交付'
  worker33_text = '33 提交第 1 轮素材池，覆盖中东停火、乌克兰前线、欧洲防务与全球市场线索。'
  worker33_items = @(
    @{ topic_title='海湾多国在停火后仍加强戒备'; source='Al Jazeera'; published_at='2026-04-10T07:20:00Z'; why_hot='停火后地区安全态势仍紧张'; core_fact_summary='多国在停火后继续提升防空和边境警戒，显示地区安全并未回归稳定'; image_url='https://www.aljazeera.com/wp-content/uploads/2026/04/ap-security-gulf.jpg'; credibility_note='国际媒体一手现场报道' },
    @{ topic_title='美伊就停火条款进入细则谈判'; source='Reuters'; published_at='2026-04-10T06:10:00Z'; why_hot='直接影响油价与区域外交'; core_fact_summary='双方已从公开表态转入条款细化阶段，涉及监督窗口与后续制裁安排'; image_url='https://www.reuters.com/resizer/v2/mideast-talks.jpg'; credibility_note='通讯社持续更新' },
    @{ topic_title='欧洲多国追加防务预算'; source='BBC'; published_at='2026-04-10T05:30:00Z'; why_hot='北约内部防务再平衡'; core_fact_summary='欧洲主要国家宣布追加军费和补充关键军工库存，市场关注欧洲安全自主趋势'; image_url='https://ichef.bbci.co.uk/news/1024/defence-europe.jpg'; credibility_note='公共广播报道，信息较稳' }
  )
  workerXhs_text = 'xhs 线提交第 1 轮补充素材，聚焦乌克兰前线、全球市场与亚洲外交动态。'
  workerXhs_items = @(
    @{ topic_title='乌克兰前线无人机袭击再升级'; source='AP'; published_at='2026-04-10T04:50:00Z'; why_hot='前线态势对停火谈判形成外压'; core_fact_summary='双方前线高价值目标遭持续无人机袭击，显示地面压力与空中威胁同步上升'; image_url='https://apnews.com/resizer/v2/ukraine-drone.jpg'; credibility_note='美联社图片与现场摘要' },
    @{ topic_title='国际油价受停火脆弱性影响震荡'; source='Financial Times'; published_at='2026-04-10T03:40:00Z'; why_hot='能源价格直接影响全球市场'; core_fact_summary='交易员认为停火虽缓和短期风险，但供应链与航运担忧仍未解除'; image_url='https://www.ft.com/__origami/service/image/v2/images/raw/oil-market.jpg'; credibility_note='财经媒体，市场线清晰' },
    @{ topic_title='亚洲多国就地区航运安全协调表态'; source='Nikkei Asia'; published_at='2026-04-10T02:35:00Z'; why_hot='关系亚洲贸易航线稳定'; core_fact_summary='多国交通与外交部门讨论提升关键航线预警共享和护航协调'; image_url='https://asia.nikkei.com/content/dam/nikkei/asia/shipping-security.jpg'; credibility_note='区域财经媒体，适合作补充材料' }
  )
  material_done_text = 'manager 完成第 1 轮素材收口，确认进入成稿整理。'
  selected_materials = @('海湾多国在停火后仍加强戒备','美伊就停火条款进入细则谈判','欧洲多国追加防务预算','乌克兰前线无人机袭击再升级','国际油价受停火脆弱性影响震荡','亚洲多国就地区航运安全协调表态')
  editor_text = 'editor 提交第 1 轮成稿，已将 6 条素材整理为可读新闻摘要。'
  report_title = '第 1 轮国际新闻热点摘要'
  report_items = @(
    @{ rank=1; headline='海湾多国在停火后仍加强戒备'; brief_100_words='停火并未消除地区警戒。多国仍在边境、港口和防空系统上保持高等级战备，说明各方判断风险仍未解除。'; source_ref='Al Jazeera'; image_url='https://www.aljazeera.com/wp-content/uploads/2026/04/ap-security-gulf.jpg'; why_selected='兼具冲突、外交与地区安全外溢性' },
    @{ rank=2; headline='美伊就停火条款进入细则谈判'; brief_100_words='谈判从公开喊话转向技术条款，意味着后续监督、制裁与执行窗口将决定停火能否稳定落地。'; source_ref='Reuters'; image_url='https://www.reuters.com/resizer/v2/mideast-talks.jpg'; why_selected='对地区走向和市场预期都有影响' },
    @{ rank=3; headline='欧洲多国追加防务预算'; brief_100_words='欧洲政府加快补充军工库存与防务预算，折射出对安全环境长期化、结构化恶化的判断。'; source_ref='BBC'; image_url='https://ichef.bbci.co.uk/news/1024/defence-europe.jpg'; why_selected='体现欧洲安全政策变化' },
    @{ rank=4; headline='乌克兰前线无人机袭击再升级'; brief_100_words='前线高价值目标持续遭无人机袭击，说明低成本远程打击仍是战场主轴，谈判和战场相互牵动。'; source_ref='AP'; image_url='https://apnews.com/resizer/v2/ukraine-drone.jpg'; why_selected='战场态势变化明显' },
    @{ rank=5; headline='国际油价受停火脆弱性影响震荡'; brief_100_words='市场相信停火可以降低短期风险，但供应链与运输安全担忧仍在，油价因此高位震荡。'; source_ref='Financial Times'; image_url='https://www.ft.com/__origami/service/image/v2/images/raw/oil-market.jpg'; why_selected='反映宏观市场反馈' },
    @{ rank=6; headline='亚洲多国就地区航运安全协调表态'; brief_100_words='亚洲国家希望通过情报共享与航运安全协同降低贸易航线风险，说明冲突外溢已进入商业和物流层面。'; source_ref='Nikkei Asia'; image_url='https://asia.nikkei.com/content/dam/nikkei/asia/shipping-security.jpg'; why_selected='体现地区联动与贸易影响' }
  )
  report_markdown = "# 第 1 轮国际新闻热点摘要`n`n1. 海湾多国在停火后仍加强戒备`n2. 美伊就停火条款进入细则谈判`n3. 欧洲多国追加防务预算`n4. 乌克兰前线无人机袭击再升级`n5. 国际油价受停火脆弱性影响震荡`n6. 亚洲多国就地区航运安全协调表态"
  editor_done_text = 'manager 通过第 1 轮成稿，进入质检。'
  editor_acceptance_summary = '成稿结构完整，6 条摘要均具备标题、简讯、来源和图片链接。'
  tester_text = 'tester 完成第 1 轮质检，格式与链接均可读。'
  tester_checklist = @(
    @{ check='headline_present'; passed=$true },
    @{ check='brief_present'; passed=$true },
    @{ check='source_ref_present'; passed=$true },
    @{ check='image_url_present'; passed=$true }
  )
  qa_done_text = 'manager 通过第 1 轮质检，进入正式交付。'
  qa_acceptance_summary = '第 1 轮内容满足可读交付要求。'
  final_text = 'manager 完成第 1 轮最终交付。'
  final_summary = '第 1 轮交付聚焦停火后安全局势、乌克兰前线与市场反应，形成 6 条可读新闻摘要。'
}

$cycle2 = @{
  start_text = '第 2 轮正式启动：围绕加沙援助、亚太供应链与全球增长预期继续采集。'
  cycle_goal = '完成第 2 轮国际热点新闻采集、编辑、质检与交付'
  worker33_text = '33 提交第 2 轮素材池，覆盖加沙援助、红海航运与全球贸易线索。'
  worker33_items = @(
    @{ topic_title='加沙援助车队恢复但通行仍受限'; source='Al Jazeera'; published_at='2026-04-10T08:05:00Z'; why_hot='人道议题持续牵动国际舆论'; core_fact_summary='援助车队恢复通行，但检查点节奏与安全风险仍使物资分发效率受限'; image_url='https://www.aljazeera.com/wp-content/uploads/2026/04/gaza-aid-convoy.jpg'; credibility_note='现场画面充分，主题明确' },
    @{ topic_title='红海航运保险成本维持高位'; source='Bloomberg'; published_at='2026-04-10T07:15:00Z'; why_hot='直接影响全球海运价格'; core_fact_summary='航运保险与风险附加费没有随局势缓和显著回落，贸易商继续重新评估路线'; image_url='https://assets.bwbx.io/images/users/iqjWHBFdfxIU/redsea-shipping.jpg'; credibility_note='财经终端信息完整' },
    @{ topic_title='东南亚制造业关注供应链再分散'; source='CNBC'; published_at='2026-04-10T06:00:00Z'; why_hot='企业布局调整带动市场关注'; core_fact_summary='企业正在重新分配产能和仓储节点，以应对地缘风险造成的交付不确定性'; image_url='https://image.cnbcfm.com/api/v1/image/supply-chain-asia.jpg'; credibility_note='财经新闻，产业角度清晰' }
  )
  workerXhs_text = 'xhs 线提交第 2 轮补充素材，关注全球增长预期与亚太政策协调。'
  workerXhs_items = @(
    @{ topic_title='IMF 下调部分经济体增长预期'; source='Reuters'; published_at='2026-04-10T05:10:00Z'; why_hot='全球增长判断影响市场主线'; core_fact_summary='地缘冲突和高融资成本继续拖累若干主要经济体增长展望'; image_url='https://www.reuters.com/resizer/v2/imf-growth.jpg'; credibility_note='通讯社摘要权威' },
    @{ topic_title='日本与韩国讨论半导体供应链协作'; source='Nikkei Asia'; published_at='2026-04-10T04:15:00Z'; why_hot='科技供应链政策信号明确'; core_fact_summary='双方希望在材料、封装与设备层面降低关键环节的供应中断风险'; image_url='https://asia.nikkei.com/content/dam/nikkei/asia/semiconductor-coop.jpg'; credibility_note='区域产业报道' },
    @{ topic_title='亚太央行继续关注输入型通胀'; source='Financial Times'; published_at='2026-04-10T03:25:00Z'; why_hot='能源与航运价格传导到通胀'; core_fact_summary='多家央行强调地缘冲突造成的能源与物流成本抬升仍可能扰动通胀路径'; image_url='https://www.ft.com/__origami/service/image/v2/images/raw/asia-inflation.jpg'; credibility_note='财经分析适合作补充视角' }
  )
  material_done_text = 'manager 完成第 2 轮素材收口，确认进入成稿整理。'
  selected_materials = @('加沙援助车队恢复但通行仍受限','红海航运保险成本维持高位','东南亚制造业关注供应链再分散','IMF 下调部分经济体增长预期','日本与韩国讨论半导体供应链协作','亚太央行继续关注输入型通胀')
  editor_text = 'editor 提交第 2 轮成稿，已将 6 条素材整理为第二轮摘要。'
  report_title = '第 2 轮国际新闻热点摘要'
  report_items = @(
    @{ rank=1; headline='加沙援助车队恢复但通行仍受限'; brief_100_words='援助恢复释放积极信号，但通行能力和现场安全仍是关键瓶颈，人道压力并未实质缓解。'; source_ref='Al Jazeera'; image_url='https://www.aljazeera.com/wp-content/uploads/2026/04/gaza-aid-convoy.jpg'; why_selected='兼具人道性与国际政治敏感度' },
    @{ rank=2; headline='红海航运保险成本维持高位'; brief_100_words='即使部分风险缓和，航运险费用和附加费仍未回落，显示全球贸易对安全预期高度敏感。'; source_ref='Bloomberg'; image_url='https://assets.bwbx.io/images/users/iqjWHBFdfxIU/redsea-shipping.jpg'; why_selected='直接影响国际贸易成本' },
    @{ rank=3; headline='东南亚制造业关注供应链再分散'; brief_100_words='制造业企业继续把地缘风险纳入排产与仓储布局，供应链韧性成为竞争核心。'; source_ref='CNBC'; image_url='https://image.cnbcfm.com/api/v1/image/supply-chain-asia.jpg'; why_selected='反映企业现实动作' },
    @{ rank=4; headline='IMF 下调部分经济体增长预期'; brief_100_words='国际机构对增长放缓的担忧延续，表明金融条件与地缘风险仍在拖累世界经济。'; source_ref='Reuters'; image_url='https://www.reuters.com/resizer/v2/imf-growth.jpg'; why_selected='具有宏观基准意义' },
    @{ rank=5; headline='日本与韩国讨论半导体供应链协作'; brief_100_words='两国强化半导体链条协作，体现科技供应链安全在亚太政策中的优先级持续提升。'; source_ref='Nikkei Asia'; image_url='https://asia.nikkei.com/content/dam/nikkei/asia/semiconductor-coop.jpg'; why_selected='科技产业与区域合作并重' },
    @{ rank=6; headline='亚太央行继续关注输入型通胀'; brief_100_words='能源与物流价格传导让央行对通胀回落节奏保持谨慎，政策表态仍偏保守。'; source_ref='Financial Times'; image_url='https://www.ft.com/__origami/service/image/v2/images/raw/asia-inflation.jpg'; why_selected='连接市场、通胀与政策' }
  )
  report_markdown = "# 第 2 轮国际新闻热点摘要`n`n1. 加沙援助车队恢复但通行仍受限`n2. 红海航运保险成本维持高位`n3. 东南亚制造业关注供应链再分散`n4. IMF 下调部分经济体增长预期`n5. 日本与韩国讨论半导体供应链协作`n6. 亚太央行继续关注输入型通胀"
  editor_done_text = 'manager 通过第 2 轮成稿，进入质检。'
  editor_acceptance_summary = '第 2 轮成稿同样具备标题、简讯、来源与图片链接。'
  tester_text = 'tester 完成第 2 轮质检，确认结构与引用完整。'
  tester_checklist = @(
    @{ check='headline_present'; passed=$true },
    @{ check='brief_present'; passed=$true },
    @{ check='source_ref_present'; passed=$true },
    @{ check='image_url_present'; passed=$true }
  )
  qa_done_text = 'manager 通过第 2 轮质检，进入最终交付。'
  qa_acceptance_summary = '第 2 轮内容满足可读交付要求。'
  final_text = 'manager 完成第 2 轮最终交付。'
  final_summary = '第 2 轮交付聚焦人道援助、红海航运、亚太供应链与全球增长预期，形成 6 条可读新闻摘要。'
}

$results.cycle_1 = Run-Cycle $token 'news-cycle-001' 1 $cycle1
$results.cycle_2 = Run-Cycle $token 'news-cycle-002' 2 $cycle2
$results.final_session = Get-Session $token
$results.final_events = Get-Events $token 200
$results.finished_at = (Get-Date -Format o)
$results.status = 'completed'
$results | ConvertTo-Json -Depth 50
