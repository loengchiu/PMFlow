#!/usr/bin/env python3
"""PMFlow Runtime Gate Smoke Test
自生成临时夹具，执行 SKILL.md 逻辑并验证 write-back 行为
用法: python scripts/pmflow-gate-runtime-smoke.py
"""

import os, sys, shutil, tempfile
from datetime import datetime
from pathlib import Path

import yaml

# --- 色彩输出 ---
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
YELLOW = '\033[93m'
WHITE = '\033[97m'
RESET = '\033[0m'

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

passed = 0
failed = 0
results = []


def assert_that(test_name, condition, pass_, detail=''):
    global passed, failed
    results.append({'test': test_name, 'condition': condition, 'pass': pass_, 'detail': detail})
    if pass_:
        passed += 1
        print(f'  {GREEN}PASS{RESET}  {condition}')
    else:
        failed += 1
        print(f'  {RED}FAIL{RESET}  {condition}')
        if detail:
            print(f'         {RED}Detail: {detail}{RESET}')


# ============================================================
# pm-confirm SOP 参考实现 (skills/pm-confirm/SKILL.md)
# ============================================================
def invoke_pm_confirm(fixture_dir):
    """返回 dict: {accepted, message, stage, is_warn}"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    stage = s.get('current_stage', 'uninitialized')
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    if stage == 'uninitialized':
        return {'accepted': False, 'message': 'Project uninitialized', 'stage': stage}

    artifacts = s.get('artifacts') or {}
    stage_artifacts = artifacts.get(stage, []) if artifacts else []
    latest = stage_artifacts[-1] if stage_artifacts else None
    if not latest:
        return {'accepted': False, 'message': f'No artifact for stage {stage}', 'stage': stage}
    artifact_path = fixture_dir / latest
    if not artifact_path.exists():
        return {'accepted': False, 'message': f'Artifact file missing: {latest}', 'stage': stage}

    reviews = s.get('review_results') or []
    review = next((r for r in reviews if r.get('stage') == stage), None)
    if not review:
        return {'accepted': False, 'message': f'No review/self_check for stage {stage}', 'stage': stage}

    reviewed_artifact = review.get('reviewed_artifact')
    reviewed_metadata = review.get('reviewed_metadata')
    if not reviewed_artifact or not reviewed_metadata:
        return {'accepted': False, 'message': 'reviewed_artifact or reviewed_metadata empty', 'stage': stage}
    if reviewed_artifact != latest:
        return {'accepted': False,
                'message': f'reviewed_artifact ({reviewed_artifact}) != latest ({latest}) - stale review',
                'stage': stage}

    verdict = review.get('verdict')
    if verdict == 'fail':
        fail_reasons = review.get('fail_reasons') or []
        return {'accepted': False, 'message': f'verdict=fail: {", ".join(fail_reasons)}', 'stage': stage}

    is_warn = (verdict == 'warn')

    new_conf = {
        'stage': stage, 'artifact': latest, 'confirmed': True,
        'confirmed_at': now, 'confirmed_by': 'PM',
    }
    if s.get('pm_confirmations') is None:
        s['pm_confirmations'] = []
    s['pm_confirmations'].append(new_conf)

    new_baseline = {
        'stage': stage, 'artifact_path': latest, 'confirmed_at': now,
    }
    if s.get('approved_baselines') is None:
        s['approved_baselines'] = []
    s['approved_baselines'].append(new_baseline)

    if is_warn:
        warnings_arr = review.get('warnings') or []
        existing = s.get('open_questions') or []
        qid_base = len(existing) + 1
        for idx, w in enumerate(warnings_arr):
            existing.append({
                'id': f'Q{(qid_base + idx):03d}',
                'question': w, 'status': 'open', 'noted_at': now,
            })
        s['open_questions'] = existing

    stage_map = {'brd': 'uc', 'uc': 'solution', 'solution': 'prototype', 'prototype': 'prd', 'prd': 'prd'}
    cmd_map = {
        'brd': ['/pm-uc', '/pm-brd'], 'uc': ['/pm-solution', '/pm-uc'],
        'solution': ['/pm-proto', '/pm-solution'], 'prototype': ['/pm-prd', '/pm-proto'],
        'prd': [],
    }
    s['current_stage'] = stage_map[stage]
    s['next_allowed_commands'] = cmd_map[stage]

    with open(status_path, 'w', encoding='utf-8') as f:
        yaml.dump(s, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    if stage == 'prd':
        msg = 'PRD confirmed - main chain complete'
    else:
        msg = f'Confirmed {stage} -> {stage_map[stage]}'
    if is_warn:
        msg += ' (warn - risks recorded to open_questions)'
    return {'accepted': True, 'message': msg, 'stage': stage, 'is_warn': is_warn}


# ============================================================
# prd-writer §2.1 baseline check (24 条件)
# ============================================================
def prd_writer_pre_check(fixture_dir):
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    stage = s.get('current_stage')
    failures = []
    if stage != 'prd':
        return {'passed': False, 'failures': [f'current_stage is {stage}, not prd']}

    for pre_stage in ('brd', 'uc', 'solution', 'prototype'):
        arts = (s.get('artifacts') or {}).get(pre_stage, []) or []
        latest = arts[-1] if arts else None

        confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == pre_stage]
        conf = confs[0] if confs else None
        if not conf or not conf.get('confirmed'):
            failures.append(f'{pre_stage}: not confirmed in pm_confirmations')
            continue
        if conf.get('artifact') != latest:
            failures.append(f'{pre_stage}: pm_confirmations.artifact ({conf.get("artifact")}) != artifacts latest ({latest})')
        bls = [b for b in (s.get('approved_baselines') or []) if b.get('stage') == pre_stage]
        bl = bls[0] if bls else None
        if not bl:
            failures.append(f'{pre_stage}: missing in approved_baselines')
        elif bl.get('artifact_path') != latest:
            failures.append(f'{pre_stage}: approved_baselines.artifact_path ({bl.get("artifact_path")}) != artifacts latest ({latest})')
        revs = [r for r in (s.get('review_results') or []) if r.get('stage') == pre_stage]
        rev = revs[0] if revs else None
        if rev and rev.get('verdict') == 'fail':
            failures.append(f'{pre_stage}: review verdict is fail')
        if rev and rev.get('reviewed_artifact') != latest:
            failures.append(f'{pre_stage}: reviewed_artifact ({rev.get("reviewed_artifact")}) != artifacts latest ({latest})')
        if rev:
            meta_path = fixture_dir / rev['reviewed_metadata']
            if not meta_path.exists():
                failures.append(f'{pre_stage}: reviewed_metadata file missing: {rev.get("reviewed_metadata")}')

    return {'passed': len(failures) == 0, 'failures': failures}


# ============================================================
# 夹具生成器 — 每种场景自建目录和文件
# ============================================================
def make_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def write_status(fixture_dir, data):
    sp = fixture_dir / '.pmflow'
    make_dir(sp)
    with open(sp / 'status.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def make_artifact(fixture_dir, rel_path, content=''):
    fp = fixture_dir / rel_path
    make_dir(fp.parent)
    fp.write_text(content or f'# placeholder: {rel_path}\n', encoding='utf-8')


def make_meta(fixture_dir, rel_path):
    fp = fixture_dir / rel_path
    make_dir(fp.parent)
    fp.write_text('', encoding='utf-8')


# --- Fixture 1: fail blocking ---
def setup_fail_fixture():
    d = Path(tempfile.mkdtemp(prefix='pmflow-fail-'))
    t = '2026-04-30T10:00:00'
    write_status(d, {
        'project_name': 'Runtime-fail阻断',
        'current_stage': 'solution',
        'next_allowed_commands': ['/pm-solution-review', '/pm-solution'],
        'artifacts': {
            'brd': ['output/brd/brd-note-fail.md'],
            'uc': ['output/uc/uc-note-fail.md'],
            'solution': ['output/solution/solution-note-fail.md'],
        },
        'approved_baselines': [
            {'stage': 'brd', 'artifact_path': 'output/brd/brd-note-fail.md', 'confirmed_at': t},
            {'stage': 'uc', 'artifact_path': 'output/uc/uc-note-fail.md', 'confirmed_at': t},
        ],
        'open_questions': [],
        'pm_confirmations': [
            {'stage': 'brd', 'artifact': 'output/brd/brd-note-fail.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'uc', 'artifact': 'output/uc/uc-note-fail.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
        ],
        'review_results': [
            {'stage': 'brd', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/brd/brd-note-fail.md',
             'reviewed_metadata': '.pmflow/metadata/brd/brd-fail.yaml'},
            {'stage': 'uc', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/uc/uc-note-fail.md',
             'reviewed_metadata': '.pmflow/metadata/uc/uc-fail.yaml'},
            {'stage': 'solution', 'check_type': 'reviewer_check', 'verdict': 'fail',
             'fail_reasons': ['方案缺少安全审计日志设计', '未定义审批超时后的降级策略'],
             'warnings': [], 'checked_at': t, 'reviewer': 'solution-reviewer',
             'reviewed_artifact': 'output/solution/solution-note-fail.md',
             'reviewed_metadata': '.pmflow/metadata/solution/solution-fail.yaml'},
        ],
    })
    make_artifact(d, 'output/brd/brd-note-fail.md')
    make_artifact(d, 'output/uc/uc-note-fail.md')
    make_artifact(d, 'output/solution/solution-note-fail.md')
    for m in ('brd/brd-fail', 'uc/uc-fail', 'solution/solution-fail'):
        make_meta(d, f'.pmflow/metadata/{m}.yaml')
    return d


# --- Fixture 2: warn + open_questions ---
def setup_warn_fixture():
    d = Path(tempfile.mkdtemp(prefix='pmflow-warn-'))
    t = '2026-04-30T10:00:00'
    write_status(d, {
        'project_name': 'Runtime-warn风险记录',
        'current_stage': 'uc',
        'next_allowed_commands': ['/pm-confirm', '/pm-uc'],
        'artifacts': {
            'brd': ['output/brd/brd-note-warn.md'],
            'uc': ['output/uc/uc-note-warn.md'],
        },
        'approved_baselines': [
            {'stage': 'brd', 'artifact_path': 'output/brd/brd-note-warn.md', 'confirmed_at': t},
        ],
        'open_questions': [
            {'id': 'Q001', 'question': '10万阈值是否包含10万本身？', 'status': 'open', 'noted_at': t},
        ],
        'pm_confirmations': [
            {'stage': 'brd', 'artifact': 'output/brd/brd-note-warn.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
        ],
        'review_results': [
            {'stage': 'brd', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/brd/brd-note-warn.md',
             'reviewed_metadata': '.pmflow/metadata/brd/brd-warn.yaml'},
            {'stage': 'uc', 'check_type': 'self_check', 'verdict': 'warn', 'fail_reasons': [],
             'warnings': ['部分异常路径（网络超时、并发冲突）尚未详细讨论', '移动端审批场景的交互细节待确认'],
             'checked_at': t, 'reviewed_artifact': 'output/uc/uc-note-warn.md',
             'reviewed_metadata': '.pmflow/metadata/uc/uc-warn.yaml'},
        ],
    })
    make_artifact(d, 'output/brd/brd-note-warn.md')
    make_artifact(d, 'output/uc/uc-note-warn.md')
    for m in ('brd/brd-warn', 'uc/uc-warn'):
        make_meta(d, f'.pmflow/metadata/{m}.yaml')
    return d


# --- Fixture 3: stale review ---
def setup_stale_review_fixture():
    d = Path(tempfile.mkdtemp(prefix='pmflow-stale-'))
    t = '2026-04-30T10:00:00'
    write_status(d, {
        'project_name': 'Runtime-审查过期',
        'current_stage': 'solution',
        'next_allowed_commands': ['/pm-solution-review', '/pm-solution'],
        'artifacts': {
            'brd': ['output/brd/brd-note-stale.md'],
            'uc': ['output/uc/uc-note-stale.md'],
            'solution': ['output/solution/solution-note-stale.md', 'output/solution/solution-note-stale-v2.md'],
        },
        'approved_baselines': [
            {'stage': 'brd', 'artifact_path': 'output/brd/brd-note-stale.md', 'confirmed_at': t},
            {'stage': 'uc', 'artifact_path': 'output/uc/uc-note-stale.md', 'confirmed_at': t},
        ],
        'open_questions': [],
        'pm_confirmations': [
            {'stage': 'brd', 'artifact': 'output/brd/brd-note-stale.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'uc', 'artifact': 'output/uc/uc-note-stale.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
        ],
        'review_results': [
            {'stage': 'brd', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/brd/brd-note-stale.md',
             'reviewed_metadata': '.pmflow/metadata/brd/brd-stale.yaml'},
            {'stage': 'uc', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/uc/uc-note-stale.md',
             'reviewed_metadata': '.pmflow/metadata/uc/uc-stale.yaml'},
            {'stage': 'solution', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'solution-reviewer',
             'reviewed_artifact': 'output/solution/solution-note-stale.md',
             'reviewed_metadata': '.pmflow/metadata/solution/solution-stale.yaml'},
        ],
    })
    make_artifact(d, 'output/brd/brd-note-stale.md')
    make_artifact(d, 'output/uc/uc-note-stale.md')
    make_artifact(d, 'output/solution/solution-note-stale.md')
    make_artifact(d, 'output/solution/solution-note-stale-v2.md')
    for m in ('brd/brd-stale', 'uc/uc-stale', 'solution/solution-stale'):
        make_meta(d, f'.pmflow/metadata/{m}.yaml')
    return d


# --- Fixture 4: baseline mismatch ---
def setup_baseline_mismatch_fixture():
    d = Path(tempfile.mkdtemp(prefix='pmflow-baseline-'))
    t = '2026-04-30T10:00:00'
    write_status(d, {
        'project_name': 'Runtime-基线不一致',
        'current_stage': 'prd',
        'next_allowed_commands': ['/pm-prd-review', '/pm-prd'],
        'artifacts': {
            'brd': ['output/brd/brd-note-baseline.md'],
            'uc': ['output/uc/uc-note-baseline.md'],
            'solution': ['output/solution/solution-note-baseline.md'],
            'prototype': ['output/prototype/prototype-note-baseline.md'],
        },
        'approved_baselines': [
            {'stage': 'brd', 'artifact_path': 'output/brd/brd-note-baseline.md', 'confirmed_at': t},
            {'stage': 'uc', 'artifact_path': 'output/uc/uc-note-baseline.md', 'confirmed_at': t},
            # 故意指向不存在的 OLD 文件
            {'stage': 'solution', 'artifact_path': 'output/solution/solution-note-baseline-OLD.md', 'confirmed_at': t},
            {'stage': 'prototype', 'artifact_path': 'output/prototype/prototype-note-baseline.md', 'confirmed_at': t},
        ],
        'open_questions': [],
        'pm_confirmations': [
            {'stage': 'brd', 'artifact': 'output/brd/brd-note-baseline.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'uc', 'artifact': 'output/uc/uc-note-baseline.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'solution', 'artifact': 'output/solution/solution-note-baseline.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'prototype', 'artifact': 'output/prototype/prototype-note-baseline.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
        ],
        'review_results': [
            {'stage': 'brd', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/brd/brd-note-baseline.md',
             'reviewed_metadata': '.pmflow/metadata/brd/brd-baseline.yaml'},
            {'stage': 'uc', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/uc/uc-note-baseline.md',
             'reviewed_metadata': '.pmflow/metadata/uc/uc-baseline.yaml'},
            {'stage': 'solution', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'solution-reviewer',
             'reviewed_artifact': 'output/solution/solution-note-baseline.md',
             'reviewed_metadata': '.pmflow/metadata/solution/solution-baseline.yaml'},
            {'stage': 'prototype', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'prototype-reviewer',
             'reviewed_artifact': 'output/prototype/prototype-note-baseline.md',
             'reviewed_metadata': '.pmflow/metadata/prototype/prototype-baseline.yaml'},
        ],
    })
    make_artifact(d, 'output/brd/brd-note-baseline.md')
    make_artifact(d, 'output/uc/uc-note-baseline.md')
    make_artifact(d, 'output/solution/solution-note-baseline.md')
    make_artifact(d, 'output/prototype/prototype-note-baseline.md')
    for m in ('brd/brd-baseline', 'uc/uc-baseline', 'solution/solution-baseline', 'prototype/prototype-baseline'):
        make_meta(d, f'.pmflow/metadata/{m}.yaml')
    return d


# --- Fixture 5: PRD endpoint ---
def setup_prd_endpoint_fixture():
    d = Path(tempfile.mkdtemp(prefix='pmflow-prd-endpoint-'))
    t = '2026-04-30T14:00:00'
    write_status(d, {
        'project_name': 'Runtime-PRD终点确认',
        'current_stage': 'prd',
        'next_allowed_commands': ['/pm-confirm', '/pm-prd'],
        'artifacts': {
            'brd': ['output/brd/brd-note-ep.md'],
            'uc': ['output/uc/uc-note-ep.md'],
            'solution': ['output/solution/solution-note-ep.md'],
            'prototype': ['output/prototype/prototype-note-ep.md'],
            'prd': ['output/prd/prd-ep.md'],
        },
        'approved_baselines': [
            {'stage': 'brd', 'artifact_path': 'output/brd/brd-note-ep.md', 'confirmed_at': t},
            {'stage': 'uc', 'artifact_path': 'output/uc/uc-note-ep.md', 'confirmed_at': t},
            {'stage': 'solution', 'artifact_path': 'output/solution/solution-note-ep.md', 'confirmed_at': t},
            {'stage': 'prototype', 'artifact_path': 'output/prototype/prototype-note-ep.md', 'confirmed_at': t},
        ],
        'open_questions': [
            {'id': 'Q001', 'question': '10万阈值是否包含10万本身？', 'status': 'open', 'noted_at': t},
        ],
        'pm_confirmations': [
            {'stage': 'brd', 'artifact': 'output/brd/brd-note-ep.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'uc', 'artifact': 'output/uc/uc-note-ep.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'solution', 'artifact': 'output/solution/solution-note-ep.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
            {'stage': 'prototype', 'artifact': 'output/prototype/prototype-note-ep.md', 'confirmed': True,
             'confirmed_at': t, 'confirmed_by': 'PM'},
        ],
        'review_results': [
            {'stage': 'brd', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/brd/brd-note-ep.md',
             'reviewed_metadata': '.pmflow/metadata/brd/brd-ep.yaml'},
            {'stage': 'uc', 'check_type': 'self_check', 'verdict': 'pass', 'fail_reasons': [],
             'warnings': [], 'checked_at': t, 'reviewed_artifact': 'output/uc/uc-note-ep.md',
             'reviewed_metadata': '.pmflow/metadata/uc/uc-ep.yaml'},
            {'stage': 'solution', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'solution-reviewer',
             'reviewed_artifact': 'output/solution/solution-note-ep.md',
             'reviewed_metadata': '.pmflow/metadata/solution/solution-ep.yaml'},
            {'stage': 'prototype', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'prototype-reviewer',
             'reviewed_artifact': 'output/prototype/prototype-note-ep.md',
             'reviewed_metadata': '.pmflow/metadata/prototype/prototype-ep.yaml'},
            {'stage': 'prd', 'check_type': 'reviewer_check', 'verdict': 'pass',
             'fail_reasons': [], 'warnings': [], 'checked_at': t, 'reviewer': 'prd-reviewer',
             'reviewed_artifact': 'output/prd/prd-ep.md',
             'reviewed_metadata': '.pmflow/metadata/prd/prd-ep.yaml'},
        ],
    })
    make_artifact(d, 'output/brd/brd-note-ep.md')
    make_artifact(d, 'output/uc/uc-note-ep.md')
    make_artifact(d, 'output/solution/solution-note-ep.md')
    make_artifact(d, 'output/prototype/prototype-note-ep.md')
    make_artifact(d, 'output/prd/prd-ep.md')
    for m in ('brd/brd-ep', 'uc/uc-ep', 'solution/solution-ep', 'prototype/prototype-ep', 'prd/prd-ep'):
        make_meta(d, f'.pmflow/metadata/{m}.yaml')
    return d


# ============================================================
# 辅助
# ============================================================
def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def read_raw(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================
# TEST 1: fail blocks /pm-confirm
# ============================================================
def test1_fail_block():
    print(f'\n{CYAN}========================================{RESET}')
    print(f'{CYAN}  TEST 1: fail blocking /pm-confirm{RESET}')
    print(f'{CYAN}========================================{RESET}')
    d = setup_fail_fixture()
    status_path = d / '.pmflow' / 'status.yaml'
    before = read_raw(status_path)
    result = invoke_pm_confirm(d)
    after_raw = read_raw(status_path)
    after = read_yaml(status_path)

    print(f'  Command: /pm-confirm')
    print(f'  Result:  {result["message"]}')
    assert_that('fail-block', 'pm-confirm rejected (accepted=False)', not result['accepted'],
                f'accepted={result["accepted"]}')
    assert_that('fail-block', 'rejection reason mentions fail', 'fail' in result['message'],
                result['message'])
    assert_that('fail-block', 'current_stage remains solution', after['current_stage'] == 'solution')
    sol_confs = [c for c in (after.get('pm_confirmations') or []) if c.get('stage') == 'solution']
    assert_that('fail-block', 'pm_confirmations has NO solution entry', len(sol_confs) == 0,
                f'count={len(sol_confs)}')
    assert_that('fail-block', 'status.yaml NOT modified (before == after)', before == after_raw,
                'rejection must not write back')
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 2: warn records to open_questions
# ============================================================
def test2_warn_record():
    print(f'\n{CYAN}========================================{RESET}')
    print(f'{CYAN}  TEST 2: warn + open_questions{RESET}')
    print(f'{CYAN}========================================{RESET}')
    d = setup_warn_fixture()
    status_path = d / '.pmflow' / 'status.yaml'
    before = read_yaml(status_path)
    before_oq_count = len(before.get('open_questions') or [])
    result = invoke_pm_confirm(d)
    after = read_yaml(status_path)

    print(f'  Command: /pm-confirm')
    print(f'  Result:  {result["message"]}')
    assert_that('warn-record', 'pm-confirm accepted', result['accepted'], result['message'])
    assert_that('warn-record', 'current_stage uc -> solution', after['current_stage'] == 'solution',
                f'actual: {after["current_stage"]}')
    cmds = after.get('next_allowed_commands') or []
    assert_that('warn-record', 'next_allowed_commands = [/pm-solution, /pm-uc]',
                cmds == ['/pm-solution', '/pm-uc'], f'actual: {cmds}')
    uc_confs = [c for c in (after.get('pm_confirmations') or []) if c.get('stage') == 'uc']
    assert_that('warn-record', 'pm_confirmations has uc entry', len(uc_confs) > 0,
                f'count={len(uc_confs)}')
    uc_bls = [b for b in (after.get('approved_baselines') or []) if b.get('stage') == 'uc']
    assert_that('warn-record', 'approved_baselines has uc entry', len(uc_bls) > 0,
                f'count={len(uc_bls)}')
    after_oq_count = len(after.get('open_questions') or [])
    assert_that('warn-record', 'open_questions increased (+2 warnings)',
                after_oq_count == before_oq_count + 2,
                f'before={before_oq_count}, after={after_oq_count}')
    assert_that('warn-record', 'review_results unchanged',
                len(after.get('review_results') or []) == 2, 'uc + brd only')
    assert_that('warn-record', 'artifacts unchanged',
                len(after.get('artifacts', {}).get('uc', [])) == 1)
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 3: stale review rejection
# ============================================================
def test3_stale_review():
    print(f'\n{CYAN}========================================{RESET}')
    print(f'{CYAN}  TEST 3: stale review rejection{RESET}')
    print(f'{CYAN}========================================{RESET}')
    d = setup_stale_review_fixture()
    status_path = d / '.pmflow' / 'status.yaml'
    before = read_raw(status_path)
    result = invoke_pm_confirm(d)
    after_raw = read_raw(status_path)
    after = read_yaml(status_path)

    print(f'  Command: /pm-confirm')
    print(f'  Result:  {result["message"]}')
    assert_that('stale-review', 'pm-confirm rejected', not result['accepted'],
                f'accepted={result["accepted"]}')
    assert_that('stale-review', 'rejection reason mentions stale',
                'stale' in result['message'].lower() or '!=' in result['message'],
                result['message'])
    assert_that('stale-review', 'current_stage remains solution', after['current_stage'] == 'solution')
    sol_confs = [c for c in (after.get('pm_confirmations') or []) if c.get('stage') == 'solution']
    assert_that('stale-review', 'pm_confirmations has NO solution entry', len(sol_confs) == 0,
                f'count={len(sol_confs)}')
    assert_that('stale-review', 'status.yaml NOT modified', before == after_raw)
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 4: baseline mismatch blocks PRD
# ============================================================
def test4_baseline_mismatch():
    print(f'\n{CYAN}========================================{RESET}')
    print(f'{CYAN}  TEST 4: baseline mismatch blocks PRD{RESET}')
    print(f'{CYAN}========================================{RESET}')
    d = setup_baseline_mismatch_fixture()
    status_path = d / '.pmflow' / 'status.yaml'
    before = read_raw(status_path)
    check = prd_writer_pre_check(d)
    after_raw = read_raw(status_path)

    blocked_text = 'BLOCKED' if not check['passed'] else 'ALLOWED'
    print(f'  Command: /pm-prd (pre-check phase)')
    print(f'  Result:  {blocked_text}')
    print(f'  Failures: {"; ".join(check["failures"])}')
    assert_that('baseline-mismatch', 'prd-writer pre-check BLOCKED', not check['passed'],
                f'passed={check["passed"]}')
    assert_that('baseline-mismatch', 'failure mentions solution',
                'solution' in ' '.join(check['failures']).lower(),
                '; '.join(check['failures']))
    assert_that('baseline-mismatch', 'failure mentions approved_baselines or artifact_path',
                'approved_baselines' in ' '.join(check['failures']) or 'artifact_path' in ' '.join(check['failures']),
                '; '.join(check['failures']))
    assert_that('baseline-mismatch', 'only 1 stage fails (no false positives)',
                len(check['failures']) == 1,
                f'total failures: {len(check["failures"])}')
    assert_that('baseline-mismatch', 'status.yaml NOT modified', before == after_raw,
                'pre-check failure must not write')
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 5: PRD endpoint confirm
# ============================================================
def test5_prd_endpoint():
    print(f'\n{CYAN}========================================{RESET}')
    print(f'{CYAN}  TEST 5: PRD endpoint confirm{RESET}')
    print(f'{CYAN}========================================{RESET}')
    d = setup_prd_endpoint_fixture()
    status_path = d / '.pmflow' / 'status.yaml'
    result = invoke_pm_confirm(d)
    after = read_yaml(status_path)

    print(f'  Command: /pm-confirm')
    print(f'  Result:  {result["message"]}')
    assert_that('prd-endpoint', 'pm-confirm accepted', result['accepted'], result['message'])
    assert_that('prd-endpoint', "current_stage STAYS prd (terminal)", after['current_stage'] == 'prd',
                f"actual: {after['current_stage']}")
    cmds = after.get('next_allowed_commands') or []
    assert_that('prd-endpoint', 'next_allowed_commands = [] (empty)', len(cmds) == 0,
                f'actual: {cmds}')
    prd_confs = [c for c in (after.get('pm_confirmations') or []) if c.get('stage') == 'prd']
    assert_that('prd-endpoint', 'pm_confirmations has prd entry', len(prd_confs) > 0,
                f'count={len(prd_confs)}')
    prd_bls = [b for b in (after.get('approved_baselines') or []) if b.get('stage') == 'prd']
    assert_that('prd-endpoint', 'approved_baselines has prd entry', len(prd_bls) > 0,
                f'count={len(prd_bls)}')
    assert_that('prd-endpoint', 'message says main chain complete',
                'main chain complete' in result['message'] or 'complete' in result['message'],
                result['message'])
    assert_that('prd-endpoint', 'no fix/change/review-pack/export in commands',
                not any(w in ' '.join(cmds) for w in ('fix', 'change', 'review-pack', 'export')))
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    test1_fail_block()
    test2_warn_record()
    test3_stale_review()
    test4_baseline_mismatch()
    test5_prd_endpoint()

    print(f'\n{MAGENTA}========================================{RESET}')
    print(f'{MAGENTA}  Runtime Smoke Summary{RESET}')
    print(f'{MAGENTA}========================================{RESET}')
    print(f'  {GREEN}PASS : {passed}{RESET}')
    pc = RED if failed > 0 else GREEN
    print(f'  {pc}FAIL : {failed}{RESET}')
    print(f'  {WHITE}TOTAL: {passed + failed}{RESET}')
    print()

    if failed > 0:
        print(f'{RED}Failures:{RESET}')
        for r in results:
            if not r['pass']:
                print(f'  {RED}[{r["test"]}] {r["condition"]}{RESET}')
                if r['detail']:
                    print(f'    {YELLOW}-> {r["detail"]}{RESET}')
        print(f'\n{RED}P0/P1 issues detected - see details above.{RESET}')
        sys.exit(1)
    else:
        print(f'{GREEN}All runtime gate tests passed.{RESET}')
        sys.exit(0)
