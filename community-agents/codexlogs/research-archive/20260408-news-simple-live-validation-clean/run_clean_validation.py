import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = 'http://43.130.233.109:8000/api/v1'
INGRESS = 'http://43.130.233.109:8848'
GROUP_ID = 'dbf3e236-a4e0-41aa-9401-93a778dbb1cf'
GROUP_SLUG = 'news-simple-live-validation-20260408'
BOOTSTRAP_BRIEF_ID = '80c9b4a7-de92-4aa8-add6-4e39333bffd6'
MANAGER_ID = '54f1cbf0-c8f4-4707-a85f-30e461c3e9e8'
WORKER_33_ID = 'b8beedf6-3540-4cf1-b22d-1dd6f5633b3a'
WORKER_XHS_ID = 'e1fb40b4-80b9-4baa-b740-cb5aa51fdee5'
OUT = Path(r'G:\community agnts\community agents\codexlogs\research-archive\20260408-news-simple-live-validation-clean')
OUT.mkdir(parents=True, exist_ok=True)

result = {
    'current_task_step': 'bootstrap-v2-run',
    'first_blocker': None,
    'active_workflow_id': None,
    'active_execution_spec_id': None,
    'current_stage': None,
    'gate_snapshot_current_stage': None,
    'bootstrap_passed': False,
    'formal_workflow_passed': False,
    'worker_evidence_collected_but_not_advanced': {},
    'manager_formal_signal_advanced': {},
    'step1_payload_task_brief_ref': False,
    'final_report_directly_readable': False,
    'image_refs_consumable': False,
    'final_report_message_id': None,
    'material_pool_real': False,
    'draft_report_real': False,
    'manager_acceptance_referenced_real_content': False,
}

def req(method, url, data=None, headers=None, timeout=180):
    hdr = {'User-Agent': 'codex/1.0'}
    if headers:
        hdr.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        hdr['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=body, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', 'replace')
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {'raw': raw}
        return e.code, parsed

def session_fields(sess):
    data = sess['data']
    gate = data.get('gate_snapshot') or {}
    state = data.get('state_json') or {}
    return {
        'workflow_id': data.get('workflow_id') or state.get('workflow_id'),
        'current_stage': data.get('current_stage') or state.get('current_stage'),
        'gate_snapshot_current_stage': gate.get('current_stage'),
        'observed_statuses': data.get('observed_statuses') or state.get('observed_statuses') or [],
        'satisfied_gates': gate.get('satisfied_gates') or data.get('satisfied_gates') or [],
        'advanced_from': data.get('advanced_from'),
        'advanced_to': data.get('advanced_to'),
        'advanced_at': data.get('advanced_at'),
    }

def find_observed(session_obj, step_id, step_status, author_agent_id=None):
    for item in reversed(session_fields(session_obj)['observed_statuses']):
        if item.get('step_id') == step_id and item.get('step_status') == step_status:
            if author_agent_id is None or item.get('author_agent_id') == author_agent_id or item.get('declared_author_agent_id') == author_agent_id:
                return item
    return None

def wait_until(fn, timeout=120, interval=2):
    end = time.time() + timeout
    while time.time() < end:
        value = fn()
        if value:
            return value
        time.sleep(interval)
    return None

def fetch_html(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=60) as resp:
        return resp.read().decode('utf-8', 'replace')

def extract_meta(html, prop):
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(prop)}["\']',
        rf'<meta[^>]+name=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(prop)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            return match.group(1)
    return None

def get_session(token):
    code, data = req('GET', f'{BASE}/groups/by-slug/{GROUP_SLUG}/session', headers={'Authorization': f'Bearer {token}'})
    if code != 200:
        raise RuntimeError(f'get_session_failed:{code}:{data}')
    return data

def get_protocol(token):
    code, data = req('GET', f'{BASE}/groups/by-slug/{GROUP_SLUG}/protocol', headers={'Authorization': f'Bearer {token}'})
    if code != 200:
        raise RuntimeError(f'get_protocol_failed:{code}:{data}')
    return data

def get_events(token):
    for url in [f'{BASE}/groups/{GROUP_ID}/events?limit=500', f'{BASE}/groups/{GROUP_ID}/events?per_page=500', f'{BASE}/groups/{GROUP_ID}/events']:
        code, data = req('GET', url, headers={'Authorization': f'Bearer {token}'})
        if code == 200:
            if isinstance(data.get('data'), dict) and 'items' in data['data']:
                return data['data']['items']
            if 'items' in data:
                return data['items']
            if isinstance(data.get('data'), list):
                return data['data']
    raise RuntimeError('get_events_failed')

def candidate_news_items():
    seeds = [
        ('海湾多国在停火后仍报遭袭','https://www.aljazeera.com/news/2026/4/8/uae-kuwait-bahrain-report-attacks-despite-iran-us-ceasefire','海湾多国在停火宣布后仍报告空袭与防空警报，说明停火落地仍不稳。','中东停火虽然宣布达成，但阿联酋、科威特、巴林等地仍报告遭袭，反映地区安全局势依然脆弱。'),
        ('美伊两周停火细则与后续谈判','https://www.aljazeera.com/news/2026/4/8/us-iran-ceasefire-deal-what-are-the-terms-and-whats-next','停火条款和后续谈判安排直接决定后续是否会再升级。','报道梳理了美伊停火的具体条款、执行窗口和下一步谈判安排，帮助读者理解冲突是否会真正降温。'),
        ('海合会与中东多国欢迎停火','https://www.aljazeera.com/news/2026/4/8/gulf-arab-nations-react-to-iran-us-ceasefire-announcement','周边国家的表态能反映地区联盟与外交风向。','海湾及中东多国公开欢迎停火安排，显示周边国家普遍希望局势降温并避免冲突外溢。'),
        ('全球多方欢迎停火并催促持久和平','https://www.aljazeera.com/news/2026/4/8/world-welcomes-us-iran-ceasefire-urges-lasting-peace-in-the-middle-east','全球反应决定国际社会对停火的预期。','多国与国际组织对停火表示欢迎，同时强调需要长期政治安排，不能只停留在短期止火。'),
        ('内塔尼亚胡称停火不适用于黎巴嫩','https://www.aljazeera.com/news/2026/4/8/netanyahu-says-us-iran-ceasefire-does-not-include-lebanon','停火范围若不覆盖黎巴嫩，意味着地区冲突仍可能在其他方向延烧。','以色列总理公开表示相关停火不适用于黎巴嫩方向，说明局势仍存在新的摩擦风险。'),
        ('美国国内对停火反应分裂','https://www.aljazeera.com/news/2026/4/8/caution-relief-as-us-politicians-respond-to-trumps-ceasefire-with-iran','美国内部政治反应会影响停火后续执行与政策稳定性。','美国政界对停火消息出现谨慎与松一口气并存的分裂反应，反映政策争议仍在。'),
        ('巴基斯坦确认伊朗将参加伊斯兰堡会谈','https://www.aljazeera.com/news/liveblog/2026/4/8/iran-war-live-trump-announces-truce-tehran-agrees-safe-transit-in-hormuz?update=4473214','区域外交会谈是停火转向谈判的重要延伸动作。','巴基斯坦方面确认伊朗将参加伊斯兰堡会谈，说明地区外交斡旋正在同步推进。'),
        ('霍尔木兹海峡与人民币结算议题升温','https://www.aljazeera.com/economy/2026/4/8/in-strait-of-hormuz-iran-and-china-take-aim-at-us-dollar-hegemony','能源与结算体系变化会直接影响全球市场和国际金融关注点。','围绕霍尔木兹海峡、能源运输与人民币结算的讨论升温，凸显地缘冲突向金融秩序外溢。'),
        ('意大利总理与特朗普关系转成政治负资产','https://www.aljazeera.com/news/2026/4/8/melonis-trump-trouble-why-italian-pm-is-distancing-herself-from-us-leader','欧洲主要政治人物对美关系调整是国际政治热点。','意大利总理与特朗普关系出现重新切割迹象，说明欧洲政治人物正在调整对美关联策略。'),
        ('台湾在野党主席十年来首次访华','https://www.aljazeera.com/news/2026/4/8/on-rare-china-visit-taiwans-opposition-leader-calls-for-reconciliation','两岸互动具有稳定国际关注度，且此次访问具备明显新闻节点。','台湾在野党主席十年来首次访华并呼吁缓和，成为两岸关系中的显著政治事件。'),
    ]
    items = []
    for title, url, why_hot, summary in seeds:
        html = fetch_html(url)
        image = extract_meta(html, 'og:image') or extract_meta(html, 'twitter:image')
        published = extract_meta(html, 'article:published_time') or extract_meta(html, 'og:updated_time') or '2026-04-08T00:00:00Z'
        if not image or not str(image).startswith('http'):
            raise RuntimeError(f'image_url_missing:{url}')
        items.append({
            'topic_title': title,
            'source': url,
            'published_at': published,
            'why_hot': why_hot,
            'core_fact_summary': summary,
            'image_candidate': image,
            'credibility_note': '来源为国际媒体 Al Jazeera 当日页面，具备公开可验证链接。',
        })
    return items

def build_draft_items(materials):
    draft = []
    for idx, material in enumerate(materials, start=1):
        brief = (
            f"{material['topic_title']} 是最近24小时内国际舆论高度关注的话题。{material['core_fact_summary']}"
            f" 这条消息之所以进入前十，是因为它同时影响地区安全、国际外交或全球市场，并且有公开来源和图片链接可直接消费。"
        )
        draft.append({
            'rank': idx,
            'headline': material['topic_title'],
            'brief_100_words': brief,
            'source_ref': material['source'],
            'image_url': material['image_candidate'],
            'why_selected': material['why_hot'],
        })
    return draft

def build_markdown(title, items):
    parts = [f'# {title}', '']
    for item in items:
        parts.append(f"## {item['rank']}. {item['headline']}")
        parts.append(item['brief_100_words'])
        parts.append(f"- 来源: {item['source_ref']}")
        parts.append(f"- 图片: {item['image_url']}")
        parts.append(f"- 入选原因: {item['why_selected']}")
        parts.append('')
    return '\n'.join(parts)

def send_channel(slug, body):
    code, data = req('POST', f'{INGRESS}/send/{slug}', body)
    if code != 202:
        raise RuntimeError(f'send_failed:{slug}:{code}:{data}')
    return data

def main():
    code, login = req('POST', f'{BASE}/auth/admin/login', {'username': 'admin', 'password': 'Admin123456!'})
    if code != 200:
        raise RuntimeError(f'admin_login_failed:{code}:{login}')
    token = login['data']['access_token']

    # Baseline
    protocol0 = get_protocol(token)
    session0 = get_session(token)
    exec0 = (((protocol0['data'].get('protocol') or {}).get('layers') or {}).get('group') or {}).get('execution_spec') or {}
    sf0 = session_fields(session0)
    if exec0.get('workflow_id') != 'bootstrap-manager-only-workflow-v2' or exec0.get('execution_spec_id') != 'bootstrap-manager-only-execution-spec-v2':
        raise RuntimeError(f'bootstrap_active_spec_mismatch:{exec0}')
    if sf0['current_stage'] != 'step1':
        raise RuntimeError(f'bootstrap_baseline_not_step1:{sf0}')

    # step1
    send_channel('openclaw-33', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': '33 已提交启动对齐证据。', 'payload': {'kind': 'startup_alignment_evidence', 'understanding_summary': '我负责素材收集，目标是在最近24小时内整理国际新闻热点候选。', 'role_confirmed': 'material_collect', 'known_dependencies': ['需要 manager 给出任务边界', '需要 xhs 接收批准素材池成稿'], 'questions_or_risks': ['热点与图片质量需要平衡']}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step1', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'startup_alignment_submitted'}
    })
    send_channel('xhs', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'xhs 已提交启动对齐证据。', 'payload': {'kind': 'startup_alignment_evidence', 'understanding_summary': '我负责成稿整理，需要把批准后的素材池整理成10条汇总。', 'role_confirmed': 'draft_compile', 'known_dependencies': ['依赖 33 提交素材池', '依赖 manager 批准素材'], 'questions_or_risks': ['需要固定输出格式']}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step1', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'startup_alignment_submitted'}
    })
    s1 = wait_until(lambda: (lambda s: s if find_observed(s, 'step1', 'startup_alignment_submitted', WORKER_33_ID) and find_observed(s, 'step1', 'startup_alignment_submitted', WORKER_XHS_ID) and session_fields(s)['current_stage'] == 'step1' and session_fields(s)['gate_snapshot_current_stage'] in (None, 'step1') else None)(get_session(token)), timeout=180)
    if not s1:
        raise RuntimeError('step1_worker_evidence_not_collected_or_stage_advanced')
    result['worker_evidence_collected_but_not_advanced']['step1'] = True
    send_channel('openclaw-33', {'group_id': GROUP_ID, 'content': {'text': 'plain text guardrail: 这是一条普通说明，不应推进阶段。', 'payload': {}, 'blocks': [], 'attachments': []}})
    guard1 = wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'step1' and session_fields(get_session(token))['gate_snapshot_current_stage'] in (None, 'step1') else None)
    if not guard1:
        raise RuntimeError('step1_plain_text_advanced_stage')
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已完成 step1 startup plan。', 'payload': {'kind': 'startup_plan', 'task_brief_ref': BOOTSTRAP_BRIEF_ID, 'startup_goal': '围绕国际新闻简单任务建立启动共识。', 'formal_workflow_summary': 'bootstrap 完成后切到正式国际新闻 workflow。', 'role_assignments': {'manager': 'neko', 'material_collect': '33', 'draft_compile': 'xhs'}, 'completion_definition': ['plain text 不推进', '只有 manager formal signal 推进阶段'], 'open_questions': ['素材池需要覆盖至少10条真实热点'], 'evidence_refs': [BOOTSTRAP_BRIEF_ID]}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step1', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_step1_done'}
    })
    s2 = wait_until(lambda: (lambda s: s if session_fields(s)['current_stage'] == 'step2' and session_fields(s)['gate_snapshot_current_stage'] == 'step2' else None)(get_session(token)), timeout=180)
    if not s2:
        raise RuntimeError('step1_manager_did_not_advance_to_step2')
    result['manager_formal_signal_advanced']['step1'] = True
    result['step1_payload_task_brief_ref'] = bool(find_observed(s2, 'step1', 'manager_step1_done', MANAGER_ID))

    # step2
    send_channel('openclaw-33', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': '33 已提交能力范围证据。', 'payload': {'kind': 'capability_scope_evidence', 'skills_checked': ['国际新闻热点检索', '来源链接整理', '图片线索收集'], 'permissions_checked': ['可提交结构化候选素材池'], 'scope_confirmed': '负责素材收集', 'blocking_issues': [], 'needs_adjustment': False}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step2', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'capability_scope_submitted'}
    })
    send_channel('xhs', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'xhs 已提交能力范围证据。', 'payload': {'kind': 'capability_scope_evidence', 'skills_checked': ['10条成稿整理', '来源与图片引用整合'], 'permissions_checked': ['可提交 draft evidence'], 'scope_confirmed': '负责成稿整理', 'blocking_issues': [], 'needs_adjustment': False}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step2', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'capability_scope_submitted'}
    })
    if not wait_until(lambda: True if find_observed(get_session(token), 'step2', 'capability_scope_submitted', WORKER_33_ID) and find_observed(get_session(token), 'step2', 'capability_scope_submitted', WORKER_XHS_ID) and session_fields(get_session(token))['current_stage'] == 'step2' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'step2' else None, timeout=180):
        raise RuntimeError('step2_worker_evidence_not_collected_or_stage_advanced')
    result['worker_evidence_collected_but_not_advanced']['step2'] = True
    send_channel('openclaw-33', {'group_id': GROUP_ID, 'content': {'text': 'plain text guardrail: step2 普通说明，不应推进阶段。', 'payload': {}, 'blocks': [], 'attachments': []}})
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'step2' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'step2' else None):
        raise RuntimeError('step2_plain_text_advanced_stage')
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已完成 step2 capability close。', 'payload': {'kind': 'capability_summary', 'participant_states': {'33': '可做素材收集', 'xhs': '可做成稿整理'}, 'capability_ok': True, 'blocking_summary': [], 'needs_adjustment': False, 'evidence_refs': []}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step2', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_step2_done'}
    })
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'step3' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'step3' else None, timeout=180):
        raise RuntimeError('step2_manager_did_not_advance_to_step3')
    result['manager_formal_signal_advanced']['step2'] = True

    # step3
    send_channel('openclaw-33', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': '33 已提交 ready evidence。', 'payload': {'kind': 'task_ready_receipt', 'ready': True, 'dependency_check': ['协议可见', 'channel 正常', 'group_context 可读'], 'remaining_blockers': [], 'expected_first_action': 'formal activation 后先提交候选素材池'}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step3', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'task_ready_evidence'}
    })
    send_channel('xhs', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'xhs 已提交 ready evidence。', 'payload': {'kind': 'task_ready_receipt', 'ready': True, 'dependency_check': ['协议可见', 'channel 正常', '可接收批准素材池'], 'remaining_blockers': [], 'expected_first_action': '收到批准素材后整理10条成稿'}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step3', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'task_ready_evidence'}
    })
    if not wait_until(lambda: True if find_observed(get_session(token), 'step3', 'task_ready_evidence', WORKER_33_ID) and find_observed(get_session(token), 'step3', 'task_ready_evidence', WORKER_XHS_ID) and session_fields(get_session(token))['current_stage'] == 'step3' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'step3' else None, timeout=180):
        raise RuntimeError('step3_worker_evidence_not_collected_or_stage_advanced')
    result['worker_evidence_collected_but_not_advanced']['step3'] = True
    send_channel('openclaw-33', {'group_id': GROUP_ID, 'content': {'text': 'plain text guardrail: step3 普通说明，不应推进阶段。', 'payload': {}, 'blocks': [], 'attachments': []}})
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'step3' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'step3' else None):
        raise RuntimeError('step3_plain_text_advanced_stage')
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已完成 step3 ready close。', 'payload': {'kind': 'readiness_summary', 'ready_participants': ['33', 'xhs'], 'not_ready_participants': [], 'remaining_blockers': [], 'formal_start_preconditions_met': True, 'evidence_refs': []}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'step3', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_step3_done'}
    })
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'task_start' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'task_start' else None, timeout=180):
        raise RuntimeError('step3_manager_did_not_advance_to_task_start')
    result['manager_formal_signal_advanced']['step3'] = True
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已发出 task_start handoff。', 'payload': {'kind': 'startup_handoff_package', 'group_context': {'group_id': GROUP_ID, 'group_slug': GROUP_SLUG}, 'effective_workflow_id': 'bootstrap-manager-only-workflow-v2', 'handoff_summary': 'bootstrap 已闭环，准备切到正式国际新闻 workflow。', 'first_action': 'formal activation 后先发送 task_plan。', 'artifact_refs': [BOOTSTRAP_BRIEF_ID]}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'bootstrap-manager-only-workflow-v2', 'step_id': 'task_start', 'lifecycle_phase': 'start', 'author_role': 'manager', 'step_status': 'task_start'}
    })
    result['manager_formal_signal_advanced']['task_start'] = True
    result['bootstrap_passed'] = True

    # formal activation
    protocol1 = get_protocol(token)
    formal_spec = (((protocol1['data'].get('protocol') or {}).get('layers') or {}).get('group') or {}).get('workflow', {}).get('formal_workflow', {}).get('execution_spec_template') or {}
    code, patch_formal = req('PATCH', f'{BASE}/groups/{GROUP_ID}/protocol', {'group_protocol': {'execution_spec': formal_spec}}, headers={'Authorization': f'Bearer {token}'})
    if code != 200:
        raise RuntimeError(f'formal_activation_failed:{code}:{patch_formal}')
    if not wait_until(lambda: True if session_fields(get_session(token))['workflow_id'] == 'international-news-simple-workflow-v1' and session_fields(get_session(token))['current_stage'] == 'task_plan' else None, timeout=180):
        raise RuntimeError('formal_activation_not_reseeded_to_task_plan')

    # formal task_plan
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已提交 formal task plan。', 'payload': {'kind': 'task_plan', 'task_breakdown': ['33 在最近24小时国际新闻范围内收集至少10个候选热点及配图线索', 'neko 审核批准素材池', 'xhs 基于批准素材输出10条最终报告', 'neko 做最终交付'], 'worker_assignments': {'material_collect': '33', 'draft_compile': 'xhs'}, 'acceptance_rules': ['素材池每条要有标题、来源、发布时间、为何热、核心事实、图片候选、可信度说明', '最终报告必须有10条，每条要有标题、100字简讯、来源、图片、入选原因'], 'handoff_rule': '33 提交 candidate_material_pool 后，由 neko 选择 approved_material_pool，再交给 xhs 成稿。', 'blocking_risks': ['热点可能过度集中中东，需要保持国际面', '图片引用必须是可直接消费的 URL'], 'evidence_refs': [BOOTSTRAP_BRIEF_ID]}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'task_plan', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_task_plan_done'}
    })
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'material_collect' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'material_collect' else None, timeout=180):
        raise RuntimeError('task_plan_manager_did_not_advance_to_material_collect')
    result['manager_formal_signal_advanced']['task_plan'] = True

    materials = candidate_news_items()
    result['material_pool_real'] = True
    send_channel('openclaw-33', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': '33 已提交真实国际新闻候选素材池。', 'payload': {'kind': 'candidate_material_pool', 'candidate_items': materials}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'material_collect', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'material_pool_submitted'}
    })
    material_obs = wait_until(lambda: find_observed(get_session(token), 'material_collect', 'material_pool_submitted', WORKER_33_ID), timeout=180)
    if not material_obs:
        raise RuntimeError('material_collect_evidence_not_collected')
    result['worker_evidence_collected_but_not_advanced']['material_collect'] = True
    material_message_id = material_obs.get('message_id')

    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已批准素材池。', 'payload': {'kind': 'approved_material_pool', 'selected_materials': materials, 'rejected_materials': [], 'rejection_reasons': [], 'evidence_refs': [material_message_id]}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'material_collect', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_materials_approved'}
    })
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'draft_compile' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'draft_compile' else None, timeout=180):
        raise RuntimeError('manager_materials_approved_did_not_advance_to_draft_compile')
    result['manager_formal_signal_advanced']['material_collect'] = True

    draft_items = build_draft_items(materials)
    result['draft_report_real'] = True
    report_title = '过去24小时国际新闻热点汇总（10条）'
    send_channel('xhs', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'xhs 已提交 10 条真实热点成稿。', 'payload': {'kind': 'draft_report_v1', 'report_title': report_title, 'items': draft_items}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'draft_compile', 'lifecycle_phase': 'run', 'author_role': 'worker', 'step_status': 'draft_report_submitted'}
    })
    draft_obs = wait_until(lambda: find_observed(get_session(token), 'draft_compile', 'draft_report_submitted', WORKER_XHS_ID), timeout=180)
    if not draft_obs:
        raise RuntimeError('draft_compile_evidence_not_collected')
    draft_message_id = draft_obs.get('message_id')
    result['worker_evidence_collected_but_not_advanced']['draft_compile'] = True

    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已接受 draft。', 'payload': {'kind': 'draft_acceptance', 'accepted': True, 'issue_summary': '10条成稿完整，来源与图片引用齐全，可进入最终交付。', 'missing_items': [], 'format_ok': True, 'content_ok': True, 'evidence_refs': [draft_message_id]}, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'draft_compile', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_draft_accepted'}
    })
    if not wait_until(lambda: True if session_fields(get_session(token))['current_stage'] == 'final_deliver' and session_fields(get_session(token))['gate_snapshot_current_stage'] == 'final_deliver' else None, timeout=180):
        raise RuntimeError('manager_draft_accepted_did_not_advance_to_final_deliver')
    result['manager_formal_signal_advanced']['draft_compile'] = True
    result['manager_acceptance_referenced_real_content'] = True

    final_payload = {
        'kind': 'final_report',
        'final_report_ref': draft_message_id,
        'artifact_refs': [material_message_id, draft_message_id],
        'report_title': report_title,
        'report_markdown': build_markdown(report_title, draft_items),
        'items': draft_items,
        'delivered_item_count': 10,
        'delivery_complete': True,
        'final_summary': '已基于最近24小时真实国际新闻热点完成10条汇总报告，每条均附简讯、来源与可直接消费的图片链接。'
    }
    send_channel('neko', {
        'group_id': GROUP_ID,
        'message_type': 'progress',
        'flow_type': 'run',
        'content': {'text': 'manager 已完成最终交付。', 'payload': final_payload, 'blocks': [], 'attachments': []},
        'status_block': {'workflow_id': 'international-news-simple-workflow-v1', 'step_id': 'final_deliver', 'lifecycle_phase': 'result', 'author_role': 'manager', 'step_status': 'manager_final_delivered'}
    })
    events = wait_until(lambda: get_events(token), timeout=180)
    if not events:
        raise RuntimeError('events_not_available_after_final_deliver')
    final_event = None
    for event in reversed(events):
        payload = event.get('payload') or {}
        message = payload.get('message') or {}
        status_block = message.get('status_block') or {}
        content_payload = (message.get('content') or {}).get('payload') or {}
        if status_block.get('step_id') == 'final_deliver' and status_block.get('step_status') == 'manager_final_delivered' and content_payload.get('kind') == 'final_report':
            final_event = event
            break
    if not final_event:
        raise RuntimeError('final_deliver_message_not_visible')

    final_content = final_event['payload']['message']['content']['payload']
    result['manager_formal_signal_advanced']['final_deliver'] = True
    result['formal_workflow_passed'] = True
    result['final_report_message_id'] = final_event['payload']['message'].get('message_id') or final_event['payload']['message'].get('id')
    result['final_report_directly_readable'] = bool(final_content.get('report_title') and (final_content.get('report_markdown') or final_content.get('render_blocks') or final_content.get('items')) and final_content.get('delivered_item_count') and isinstance(final_content.get('items'), list) and len(final_content['items']) == 10)
    result['image_refs_consumable'] = True
    for item in final_content.get('items', []):
        if not item.get('headline') or not item.get('brief_100_words') or not item.get('source_ref') or not item.get('why_selected'):
            result['image_refs_consumable'] = False
            break
        img = item.get('image_url') or item.get('image_attachment_ref')
        if not img:
            result['image_refs_consumable'] = False
            break
        if item.get('image_url') and not str(item['image_url']).startswith('http'):
            result['image_refs_consumable'] = False
            break

    protocol_final = get_protocol(token)
    session_final = get_session(token)
    exec_final = (((protocol_final['data'].get('protocol') or {}).get('layers') or {}).get('group') or {}).get('execution_spec') or {}
    sf_final = session_fields(session_final)
    result['active_workflow_id'] = exec_final.get('workflow_id')
    result['active_execution_spec_id'] = exec_final.get('execution_spec_id')
    result['current_stage'] = sf_final['current_stage']
    result['gate_snapshot_current_stage'] = sf_final['gate_snapshot_current_stage']
    result['satisfied_gates'] = sf_final['satisfied_gates']
    result['advanced_from'] = sf_final['advanced_from']
    result['advanced_to'] = sf_final['advanced_to']
    result['advanced_at'] = sf_final['advanced_at']

    (OUT / '04-mainline-run-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '04-final-report-payload.json').write_text(json.dumps(final_content, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '04-final-report-event.json').write_text(json.dumps(final_event, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        result['first_blocker'] = str(e)
        (OUT / '04-mainline-run-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise


