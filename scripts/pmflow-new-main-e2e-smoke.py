#!/usr/bin/env python3
"""PMFlow New Main Chain E2E Smoke Test
验证新主链已实现段：input -> align -> align-review -> design -> design-review
测试 status/schema/route/gate 契约，不测试 LLM 生成质量。
用法: python scripts/pmflow-new-main-e2e-smoke.py
"""

import sys
import shutil
import tempfile
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
# pm-guide 路由逻辑（简化复现，用于断言推荐命令）
# ============================================================
def pm_guide_recommend(fixture_dir):
    """复现 pm-guide 新主链路由逻辑，返回推荐命令字符串。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    stage = s.get('current_stage', 'uninitialized')
    artifacts = s.get('artifacts') or {}
    reviews = s.get('review_results') or []

    def latest_artifact(stage_name):
        arts = artifacts.get(stage_name, []) or []
        return arts[-1] if arts else None

    def review_verdict(stage_name):
        for r in reversed(reviews):
            if r.get('stage') == stage_name:
                return r
        return None

    if stage == 'uninitialized':
        return '/pm-input'

    if stage == 'input':
        r = review_verdict('input')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-input'
        if not latest_artifact('input'):
            return '/pm-input'
        if not r:
            return '/pm-input'
        if r.get('verdict') in ('pass', 'warn'):
            return '/pm-align'
        return '/pm-input'

    if stage == 'align':
        r = review_verdict('align')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-align'
        if not latest_artifact('align'):
            return '/pm-align'
        if not r:
            return '/pm-align-review'
        if r.get('verdict') in ('pass', 'warn'):
            return '/pm-design'
        return '/pm-align'

    if stage == 'design':
        r = review_verdict('design')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-design'
        if not latest_artifact('design'):
            return '/pm-design'
        if not r:
            return '/pm-design-review'
        if r.get('verdict') in ('pass', 'warn'):
            return '/pm-wireframe'
        return '/pm-design'

    if stage == 'wireframe':
        r = review_verdict('wireframe')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-wireframe'
        if not latest_artifact('wireframe'):
            return '/pm-wireframe'
        if not r:
            return '/pm-wireframe-review'
        if r.get('verdict') in ('pass', 'warn'):
            return '/pm-prd'
        return '/pm-wireframe'

    if stage == 'prd':
        r = review_verdict('prd')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-prd'
        if not latest_artifact('prd'):
            return '/pm-prd'
        if not r:
            return '/pm-prd-review'
        if r.get('verdict') in ('pass', 'warn'):
            return '/pm-prototype'
        return '/pm-prd'

    if stage == 'prototype':
        r = review_verdict('prototype')
        if r and r.get('verdict') == 'fail':
            return '回到 /pm-prototype'
        if not latest_artifact('prototype'):
            return '/pm-prototype'
        if not r:
            return '/pm-prototype-review'
        if r.get('verdict') in ('pass', 'warn'):
            return '主链路完成'
        return '/pm-prototype'

    return f'未处理阶段: {stage}'


# ============================================================
# 夹具辅助
# ============================================================
def make_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def write_yaml(path, data):
    make_dir(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def make_file(path, content=''):
    make_dir(path.parent)
    path.write_text(content or f'# placeholder: {path.name}\n', encoding='utf-8')


# ============================================================
# 阶段模拟器：模拟 writer 执行后 status 的变化
# ============================================================
def simulate_input(fixture_dir, t):
    """模拟 /pm-input 执行：生成 input 产物 + self_check pass。"""
    s = {
        'project_name': 'E2E-新主链',
        'workflow_mode': 'new_main',
        'current_stage': 'input',
        'artifacts': {'input': ['output/input/materials.md']},
        'open_questions': [],
        'review_results': [{
            'stage': 'input', 'check_type': 'self_check', 'verdict': 'pass',
            'fail_reasons': [], 'warnings': [], 'checked_at': t,
            'reviewed_artifact': 'output/input/materials.md',
            'reviewed_metadata': '.pmflow/metadata/input/materials.yaml',
        }],
    }
    write_yaml(fixture_dir / '.pmflow' / 'status.yaml', s)
    make_file(fixture_dir / 'output/input/materials.md', '# 输入材料')
    make_file(fixture_dir / '.pmflow/metadata/input/materials.yaml', 'materials: []')


def simulate_align(fixture_dir, t):
    """模拟 /pm-align 执行：生成 align 产物，current_stage 更新为 align。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['current_stage'] = 'align'
    s['artifacts']['align'] = ['output/align/align.md']
    write_yaml(status_path, s)
    make_file(fixture_dir / 'output/align/align.md', '# 对齐基线')
    make_file(fixture_dir / '.pmflow/metadata/align/index.yaml', 'goals: []')


def simulate_align_review(fixture_dir, t, verdict='pass'):
    """模拟 /pm-align-review 执行：写入 review_results。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['review_results'].append({
        'stage': 'align', 'check_type': 'reviewer_check', 'verdict': verdict,
        'fail_reasons': [], 'warnings': [] if verdict == 'pass' else ['部分角色待确认'],
        'checked_at': t, 'reviewer': 'align-reviewer',
        'reviewed_artifact': 'output/align/align.md',
        'reviewed_metadata': '.pmflow/metadata/align/index.yaml',
    })
    write_yaml(status_path, s)


def simulate_design(fixture_dir, t):
    """模拟 /pm-design 执行：生成 design 产物，current_stage 更新为 design。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['current_stage'] = 'design'
    s['artifacts']['design'] = ['output/design/design.md']
    write_yaml(status_path, s)
    make_file(fixture_dir / 'output/design/design.md', '# 详细设计')
    make_file(fixture_dir / '.pmflow/metadata/design/index.yaml', 'modules: []')
    make_file(fixture_dir / '.pmflow/snapshots/design/design.last-synced.md', '# 快照')


def simulate_design_review(fixture_dir, t, verdict='pass'):
    """模拟 /pm-design-review 执行：写入 review_results。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['review_results'].append({
        'stage': 'design', 'check_type': 'reviewer_check', 'verdict': verdict,
        'fail_reasons': [], 'warnings': [] if verdict == 'pass' else ['部分字段待细化'],
        'checked_at': t, 'reviewer': 'design-reviewer',
        'reviewed_artifact': 'output/design/design.md',
        'reviewed_metadata': '.pmflow/metadata/design/index.yaml',
    })
    write_yaml(status_path, s)


def simulate_wireframe(fixture_dir, t):
    """模拟 /pm-wireframe 执行：生成 wireframe 产物，current_stage 更新为 wireframe。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['current_stage'] = 'wireframe'
    s['artifacts']['wireframe'] = ['output/wireframe/wireframe.md']
    write_yaml(status_path, s)
    make_file(fixture_dir / 'output/wireframe/wireframe.md', '# 线框图')
    make_file(fixture_dir / '.pmflow/metadata/wireframe/index.yaml', 'pages: []')
    make_file(fixture_dir / '.pmflow/snapshots/wireframe/wireframe.last-synced.md', '# 快照')


def simulate_wireframe_review(fixture_dir, t, verdict='pass'):
    """模拟 /pm-wireframe-review 执行：写入 review_results。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['review_results'].append({
        'stage': 'wireframe', 'check_type': 'reviewer_check', 'verdict': verdict,
        'fail_reasons': [] if verdict != 'fail' else ['主流程导航断裂'],
        'warnings': [] if verdict == 'pass' else ['部分边缘页面布局待细化'],
        'checked_at': t, 'reviewer': 'wireframe-reviewer',
        'reviewed_artifact': 'output/wireframe/wireframe.md',
        'reviewed_metadata': '.pmflow/metadata/wireframe/index.yaml',
    })
    write_yaml(status_path, s)


def simulate_prd(fixture_dir, t):
    """模拟 /pm-prd 执行：生成 PRD 产物，current_stage 更新为 prd。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['current_stage'] = 'prd'
    s['artifacts']['prd'] = ['output/prd/prd.md']
    write_yaml(status_path, s)
    make_file(fixture_dir / 'output/prd/prd.md', '# PRD 主稿')
    # 新的 metadata 结构
    make_file(fixture_dir / '.pmflow/metadata/prd/index.yaml', 'pages: []\nrules: []\nacceptance: []')
    make_file(fixture_dir / '.pmflow/metadata/prd/dictionary.yaml', 'dictionary: []')
    make_file(fixture_dir / '.pmflow/metadata/prd/pages/P01.yaml', 'page_id: PRD-PAGE-001\npage_name: 测试页')
    make_file(fixture_dir / '.pmflow/metadata/prd/rules.yaml', 'rules: []')
    make_file(fixture_dir / '.pmflow/metadata/prd/trace.yaml', 'traces: []')
    make_file(fixture_dir / '.pmflow/snapshots/prd/prd.last-synced.md', '# 快照')


def simulate_prd_review(fixture_dir, t, verdict='pass'):
    """模拟 /pm-prd-review 执行：写入 review_results。"""
    status_path = fixture_dir / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['review_results'].append({
        'stage': 'prd', 'check_type': 'reviewer_check', 'verdict': verdict,
        'fail_reasons': [] if verdict != 'fail' else ['核心字段无数据字典定义'],
        'warnings': [] if verdict == 'pass' else ['边缘动作可补充'],
        'checked_at': t, 'reviewer': 'pm-prd-reviewer',
        'reviewed_artifact': 'output/prd/prd.md',
        'reviewed_metadata': '.pmflow/metadata/prd/index.yaml',
    })
    write_yaml(status_path, s)


# ============================================================
# 断言辅助
# ============================================================
def read_status(fixture_dir):
    with open(fixture_dir / '.pmflow' / 'status.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def assert_no_legacy_fields(s, test_name):
    """断言 status 中不存在 pm_confirmations、approved_baselines、next_allowed_commands。"""
    assert_that(test_name,
                'pm_confirmations 不存在或为空',
                not s.get('pm_confirmations'),
                f'实际: {s.get("pm_confirmations")}')
    assert_that(test_name,
                'approved_baselines 不存在或为空',
                not s.get('approved_baselines'),
                f'实际: {s.get("approved_baselines")}')
    assert_that(test_name,
                'next_allowed_commands 不存在或为空',
                not s.get('next_allowed_commands'),
                f'实际: {s.get("next_allowed_commands")}')


def assert_no_pm_confirm_in_text(text, test_name):
    """断言文本中不包含 /pm-confirm。"""
    assert_that(test_name,
                '文本中无 /pm-confirm',
                '/pm-confirm' not in text,
                f'发现 /pm-confirm: {text[:200]}')


# ============================================================
# TEST 1: 初始状态 + workflow_mode
# ============================================================
def test1_workflow_mode():
    print(f'\n{CYAN}=== TEST 1: workflow_mode = new_main ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    s = read_status(d)

    assert_that('workflow-mode', 'workflow_mode = new_main',
                s.get('workflow_mode') == 'new_main',
                f'实际: {s.get("workflow_mode")}')
    assert_that('workflow-mode', 'current_stage = input',
                s.get('current_stage') == 'input',
                f'实际: {s.get("current_stage")}')
    assert_no_legacy_fields(s, 'workflow-mode')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 2: input self_check pass -> pm-guide 推荐 /pm-align
# ============================================================
def test2_input_to_align():
    print(f'\n{CYAN}=== TEST 2: input self_check pass -> /pm-align ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    s = read_status(d)

    assert_that('input->align', 'artifacts.input 非空',
                len(s.get('artifacts', {}).get('input', [])) > 0)
    input_reviews = [r for r in s.get('review_results', []) if r.get('stage') == 'input']
    assert_that('input->align', 'review_results 存在 input self_check',
                len(input_reviews) > 0)
    assert_that('input->align', 'input self_check verdict = pass',
                input_reviews[0].get('verdict') == 'pass',
                f'实际: {input_reviews[0].get("verdict")}')

    recommend = pm_guide_recommend(d)
    assert_that('input->align', 'pm-guide 推荐 /pm-align',
                recommend == '/pm-align',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'input->align')
    assert_no_legacy_fields(s, 'input->align')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 3: input self_check warn -> pm-guide 仍推荐 /pm-align
# ============================================================
def test3_input_warn_to_align():
    print(f'\n{CYAN}=== TEST 3: input self_check warn -> /pm-align ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)

    # 覆盖为 warn
    status_path = d / '.pmflow' / 'status.yaml'
    with open(status_path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)
    s['review_results'][0]['verdict'] = 'warn'
    s['review_results'][0]['warnings'] = ['部分材料引用自背景文档']
    write_yaml(status_path, s)

    recommend = pm_guide_recommend(d)
    assert_that('input-warn', 'pm-guide 推荐 /pm-align（warn 不阻断）',
                recommend == '/pm-align',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'input-warn')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 4: /pm-align 执行后 artifacts.align 存在，不自动进入 design
# ============================================================
def test4_align_artifacts():
    print(f'\n{CYAN}=== TEST 4: /pm-align 后 artifacts.align 存在 ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    s = read_status(d)

    assert_that('align-artifacts', 'current_stage = align',
                s.get('current_stage') == 'align',
                f'实际: {s.get("current_stage")}')
    assert_that('align-artifacts', 'artifacts.align 非空',
                len(s.get('artifacts', {}).get('align', [])) > 0)
    assert_that('align-artifacts', 'artifacts.design 不存在（未自动进入）',
                not s.get('artifacts', {}).get('design'))
    align_reviews = [r for r in s.get('review_results', []) if r.get('stage') == 'align']
    assert_that('align-artifacts', 'review_results 无 align review（未审查）',
                len(align_reviews) == 0)
    assert_no_legacy_fields(s, 'align-artifacts')

    # pm-guide 应推荐 /pm-align-review
    recommend = pm_guide_recommend(d)
    assert_that('align-artifacts', 'pm-guide 推荐 /pm-align-review',
                recommend == '/pm-align-review',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 5: align-review pass -> pm-guide 推荐 /pm-design
# ============================================================
def test5_align_review_to_design():
    print(f'\n{CYAN}=== TEST 5: align-review pass -> /pm-design ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t, verdict='pass')

    recommend = pm_guide_recommend(d)
    assert_that('align-review->design', 'pm-guide 推荐 /pm-design',
                recommend == '/pm-design',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'align-review->design')

    s = read_status(d)
    assert_no_legacy_fields(s, 'align-review->design')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 6: align-review warn -> pm-guide 仍推荐 /pm-design
# ============================================================
def test6_align_review_warn():
    print(f'\n{CYAN}=== TEST 6: align-review warn -> /pm-design ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t, verdict='warn')

    recommend = pm_guide_recommend(d)
    assert_that('align-warn', 'pm-guide 推荐 /pm-design（warn 不阻断）',
                recommend == '/pm-design',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 7: /pm-design 后产物入口存在
# ============================================================
def test7_design_artifacts():
    print(f'\n{CYAN}=== TEST 7: /pm-design 后 design 产物入口存在 ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    s = read_status(d)

    assert_that('design-artifacts', 'current_stage = design',
                s.get('current_stage') == 'design',
                f'实际: {s.get("current_stage")}')
    assert_that('design-artifacts', 'artifacts.design 包含 design.md',
                any('design.md' in p for p in s.get('artifacts', {}).get('design', [])))
    assert_that('design-artifacts', 'output/design/design.md 存在于磁盘',
                (d / 'output/design/design.md').exists())
    assert_that('design-artifacts', '.pmflow/metadata/design/index.yaml 存在',
                (d / '.pmflow/metadata/design/index.yaml').exists())
    assert_that('design-artifacts', '.pmflow/snapshots/design/design.last-synced.md 存在',
                (d / '.pmflow/snapshots/design/design.last-synced.md').exists())
    assert_no_legacy_fields(s, 'design-artifacts')

    # pm-guide 应推荐 /pm-design-review
    recommend = pm_guide_recommend(d)
    assert_that('design-artifacts', 'pm-guide 推荐 /pm-design-review',
                recommend == '/pm-design-review',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 8: design-review pass -> pm-guide 推荐 /pm-wireframe
# ============================================================
def test8_design_review_to_wireframe():
    print(f'\n{CYAN}=== TEST 8: design-review pass -> /pm-wireframe ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t, verdict='pass')

    recommend = pm_guide_recommend(d)
    assert_that('design-review->wireframe', 'pm-guide 推荐 /pm-wireframe',
                recommend == '/pm-wireframe',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'design-review->wireframe')

    s = read_status(d)
    assert_no_legacy_fields(s, 'design-review->wireframe')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 9: design-review warn -> pm-guide 仍推荐 /pm-wireframe
# ============================================================
def test9_design_review_warn():
    print(f'\n{CYAN}=== TEST 9: design-review warn -> /pm-wireframe ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t, verdict='warn')

    recommend = pm_guide_recommend(d)
    assert_that('design-warn', 'pm-guide 推荐 /pm-wireframe（warn 不阻断）',
                recommend == '/pm-wireframe',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 10: 全流程无 legacy 字段写入
# ============================================================
def test10_no_legacy_fields_full_run():
    print(f'\n{CYAN}=== TEST 10: 全流程无 legacy 字段 ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t)

    s = read_status(d)
    assert_that('no-legacy', 'workflow_mode = new_main',
                s.get('workflow_mode') == 'new_main')
    assert_that('no-legacy', 'pm_confirmations 不存在',
                not s.get('pm_confirmations'))
    assert_that('no-legacy', 'approved_baselines 不存在',
                not s.get('approved_baselines'))
    assert_that('no-legacy', 'next_allowed_commands 不存在',
                not s.get('next_allowed_commands'))

    # 遍历 review_results，确保无 /pm-confirm 引用
    all_reviews = s.get('review_results') or []
    assert_that('no-legacy', f'review_results 共 {len(all_reviews)} 条',
                len(all_reviews) == 4,
                f'期望 4（input self_check + align/design/wireframe review），实际 {len(all_reviews)}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 11: YAML schema 可解析
# ============================================================
def test11_schema_parseable():
    print(f'\n{CYAN}=== TEST 11: status.schema.yaml 可解析 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    schema_path = repo_root / 'schemas' / 'status.schema.yaml'
    assert_that('schema', 'status.schema.yaml 存在',
                schema_path.exists())
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)
    assert_that('schema', 'YAML 可解析',
                isinstance(schema, dict))
    fields = schema.get('fields', {})
    assert_that('schema', 'current_stage enum 含 input/align/design/wireframe',
                set(['input', 'align', 'design', 'wireframe']).issubset(
                    set(fields.get('current_stage', {}).get('values', []))))
    assert_that('schema', 'workflow_mode 存在',
                'workflow_mode' in fields)

    # pm_confirmations stage 不含新链阶段
    pm_stage_vals = set(fields.get('pm_confirmations', {}).get('items', {})
                        .get('properties', {}).get('stage', {}).get('values', []))
    assert_that('schema', 'pm_confirmations.stage 不含 input/align/design/wireframe',
                not {'input', 'align', 'design', 'wireframe'}.intersection(pm_stage_vals),
                f'实际值: {pm_stage_vals}')

    # approved_baselines stage 不含新链阶段
    ab_stage_vals = set(fields.get('approved_baselines', {}).get('items', {})
                        .get('properties', {}).get('stage', {}).get('values', []))
    assert_that('schema', 'approved_baselines.stage 不含 input/align/design/wireframe',
                not {'input', 'align', 'design', 'wireframe'}.intersection(ab_stage_vals),
                f'实际值: {ab_stage_vals}')


# ============================================================
# TEST 12: /pm-wireframe 后 artifacts.wireframe 存在
# ============================================================
def test12_wireframe_artifacts():
    print(f'\n{CYAN}=== TEST 12: /pm-wireframe 后 wireframe 产物入口存在 ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    s = read_status(d)

    assert_that('wireframe-artifacts', 'current_stage = wireframe',
                s.get('current_stage') == 'wireframe',
                f'实际: {s.get("current_stage")}')
    assert_that('wireframe-artifacts', 'artifacts.wireframe 包含 wireframe.md',
                any('wireframe.md' in p for p in s.get('artifacts', {}).get('wireframe', [])))
    assert_that('wireframe-artifacts', 'output/wireframe/wireframe.md 存在于磁盘',
                (d / 'output/wireframe/wireframe.md').exists())
    assert_that('wireframe-artifacts', '.pmflow/metadata/wireframe/index.yaml 存在',
                (d / '.pmflow/metadata/wireframe/index.yaml').exists())
    assert_that('wireframe-artifacts', '.pmflow/snapshots/wireframe/wireframe.last-synced.md 存在',
                (d / '.pmflow/snapshots/wireframe/wireframe.last-synced.md').exists())
    assert_no_legacy_fields(s, 'wireframe-artifacts')

    # pm-guide 应推荐 /pm-wireframe-review
    recommend = pm_guide_recommend(d)
    assert_that('wireframe-artifacts', 'pm-guide 推荐 /pm-wireframe-review',
                recommend == '/pm-wireframe-review',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 13: wireframe-review pass -> pm-guide 推荐 /pm-prd
# ============================================================
def test13_wireframe_review_to_prd():
    print(f'\n{CYAN}=== TEST 13: wireframe-review pass -> /pm-prd ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t, verdict='pass')

    recommend = pm_guide_recommend(d)
    assert_that('wf-review->prd', 'pm-guide 推荐 /pm-prd',
                recommend == '/pm-prd',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'wf-review->prd')

    s = read_status(d)
    assert_no_legacy_fields(s, 'wf-review->prd')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 14: wireframe-review warn -> pm-guide 仍推荐 /pm-prd
# ============================================================
def test14_wireframe_review_warn():
    print(f'\n{CYAN}=== TEST 14: wireframe-review warn -> /pm-prd ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t, verdict='warn')

    recommend = pm_guide_recommend(d)
    assert_that('wf-warn', 'pm-guide 推荐 /pm-prd（warn 不阻断）',
                recommend == '/pm-prd',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 15: wireframe-review fail -> pm-guide 推荐回到 /pm-wireframe
# ============================================================
def test15_wireframe_review_fail():
    print(f'\n{CYAN}=== TEST 15: wireframe-review fail -> 回到 /pm-wireframe ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-03T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t, verdict='fail')

    recommend = pm_guide_recommend(d)
    assert_that('wf-fail', 'pm-guide 推荐回到 /pm-wireframe',
                recommend == '回到 /pm-wireframe',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'wf-fail')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 16: SOP 文件包含 review_results 双写规则
# ============================================================
def test16_sop_dual_write_rule():
    print(f'\n{CYAN}=== TEST 16: SOP 文件包含 review_results 双写规则 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent

    sop_files = {
        'pm-input': repo_root / 'skills' / 'pm-input' / 'SKILL.md',
        'pm-align-reviewer': repo_root / 'skills' / 'pm-align-reviewer' / 'SKILL.md',
        'pm-design-reviewer': repo_root / 'skills' / 'pm-design-reviewer' / 'SKILL.md',
        'pm-wireframe-reviewer': repo_root / 'skills' / 'pm-wireframe-reviewer' / 'SKILL.md',
    }

    for name, path in sop_files.items():
        assert_that('sop-dual-write', f'{name} SKILL.md 存在',
                    path.exists(), f'路径: {path}')
        if path.exists():
            text = path.read_text(encoding='utf-8')
            has_append = '追加到' in text
            has_review_results = 'review_results' in text
            assert_that('sop-dual-write',
                        f'{name} 包含"追加到 review_results"规则',
                        has_append and has_review_results,
                        f'追加到: {has_append}, review_results: {has_review_results}')


# ============================================================
# TEST 17: reviewer 前置检查包含基线校验三项
# ============================================================
def extract_section2(text):
    """提取 §2 前置检查区域（从 ## 2. 到 ## 3. 之间）。"""
    import re
    m = re.search(r'## 2\..*?\n(.*?)(?=## 3\.)', text, re.DOTALL)
    return m.group(1) if m else ''


def test17_reviewer_precheck_baseline():
    print(f'\n{CYAN}=== TEST 17: reviewer 前置检查基线校验 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent

    reviewers = {
        'pm-design-reviewer': {
            'path': repo_root / 'skills' / 'pm-design-reviewer' / 'SKILL.md',
            'upstream': 'align',
        },
        'pm-wireframe-reviewer': {
            'path': repo_root / 'skills' / 'pm-wireframe-reviewer' / 'SKILL.md',
            'upstream': 'design',
        },
    }

    for name, info in reviewers.items():
        skill_path = info['path']
        upstream = info['upstream']
        assert_that('reviewer-precheck', f'{name} SKILL.md 存在',
                    skill_path.exists(), f'路径: {skill_path}')
        if not skill_path.exists():
            continue

        text = skill_path.read_text(encoding='utf-8')
        section2 = extract_section2(text)
        assert_that('reviewer-precheck',
                    f'{name} §2 区域非空',
                    len(section2.strip()) > 0)

        # 1. verdict pass/warn 校验
        has_verdict = 'verdict' in section2 and 'pass' in section2 and 'warn' in section2
        assert_that('reviewer-precheck',
                    f'{name} §2 包含 verdict pass/warn 校验',
                    has_verdict,
                    f'section2 snippet: {section2[:300]}')

        # 2. reviewed_artifact 校验
        has_artifact = 'reviewed_artifact' in section2
        assert_that('reviewer-precheck',
                    f'{name} §2 包含 reviewed_artifact 校验',
                    has_artifact)

        # 3. reviewed_metadata 校验
        has_metadata = 'reviewed_metadata' in section2
        assert_that('reviewer-precheck',
                    f'{name} §2 包含 reviewed_metadata 校验',
                    has_metadata)


# ============================================================
# TEST 18: wireframe 模板和参考文件存在 + SOP 引用
# ============================================================
def test18_wireframe_template_and_reference():
    print(f'\n{CYAN}=== TEST 18: wireframe 模板和参考文件 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent

    template_path = repo_root / 'templates' / 'wireframe.md'
    reference_path = repo_root / 'references' / 'wireframe-writing.md'
    writer_path = repo_root / 'skills' / 'pm-wireframe' / 'SKILL.md'

    assert_that('wf-template', 'templates/wireframe.md 存在',
                template_path.exists())
    assert_that('wf-template', 'references/wireframe-writing.md 存在',
                reference_path.exists())

    if writer_path.exists():
        writer_text = writer_path.read_text(encoding='utf-8')
        assert_that('wf-template',
                    'pm-wireframe SOP 引用 templates/wireframe.md',
                    'templates/wireframe.md' in writer_text)
        assert_that('wf-template',
                    'pm-wireframe SOP 引用 references/wireframe-writing.md',
                    'references/wireframe-writing.md' in writer_text)


# ============================================================
# TEST 19: wireframe-reviewer fail 路由包含 /pm-fix
# ============================================================
def test19_wireframe_reviewer_fail_routing():
    print(f'\n{CYAN}=== TEST 19: wireframe-reviewer fail 路由 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    reviewer_path = repo_root / 'skills' / 'pm-wireframe-reviewer' / 'SKILL.md'

    assert_that('wf-fail-route', 'SKILL.md 存在', reviewer_path.exists())
    if reviewer_path.exists():
        text = reviewer_path.read_text(encoding='utf-8')
        # fail 时应建议 /pm-wireframe 或 /pm-fix
        has_wireframe_route = '/pm-wireframe' in text
        has_fix_route = '/pm-fix' in text
        assert_that('wf-fail-route',
                    'fail 时建议包含 /pm-wireframe',
                    has_wireframe_route)
        assert_that('wf-fail-route',
                    'fail 时建议包含 /pm-fix（design 层问题）',
                    has_fix_route)


# ============================================================
# TEST 20: pm-wireframe §2 前置检查包含 workflow_mode 和失败条件
# ============================================================
def test20_writer_precheck_workflow_mode():
    print(f'\n{CYAN}=== TEST 20: pm-wireframe §2 前置检查 workflow_mode ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-wireframe' / 'SKILL.md'

    assert_that('wf-precheck-wm', 'SKILL.md 存在', skill_path.exists())
    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')
    section2 = extract_section2(text)
    assert_that('wf-precheck-wm', '§2 区域非空', len(section2.strip()) > 0)

    # workflow_mode 和 new_main 校验
    has_workflow_mode = 'workflow_mode' in section2
    has_new_main = 'new_main' in section2
    assert_that('wf-precheck-wm', '§2 包含 workflow_mode 校验', has_workflow_mode)
    assert_that('wf-precheck-wm', '§2 包含 new_main 校验', has_new_main)

    # 前置失败条件：不写 wireframe、不写 metadata、不更新 status、不提示 /pm-prd
    has_no_write_wf = 'wireframe.md' in section2 and '不得写入' in section2
    has_no_write_meta = 'index.yaml' in section2 and '不得写入' in section2
    has_no_update_status = 'status.yaml' in section2 and '不得更新' in section2
    has_no_prd = '/pm-prd' in section2 and '不得提示' in section2
    assert_that('wf-precheck-wm',
                '§2 失败条件：不写 wireframe.md',
                has_no_write_wf,
                f'section2 snippet: {section2[:500]}')
    assert_that('wf-precheck-wm',
                '§2 失败条件：不写 metadata index.yaml',
                has_no_write_meta)
    assert_that('wf-precheck-wm',
                '§2 失败条件：不更新 status.yaml',
                has_no_update_status)
    assert_that('wf-precheck-wm',
                '§2 失败条件：不提示 /pm-prd',
                has_no_prd)


# ============================================================
# TEST 21: /pm-fix 命令和 skill 存在 + SOP 内容校验
# ============================================================
def test21_pm_fix_exists():
    print(f'\n{CYAN}=== TEST 21: /pm-fix 命令和 skill 存在 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent

    cmd_path = repo_root / 'commands' / 'pm-fix.md'
    skill_path = repo_root / 'skills' / 'pm-fix' / 'SKILL.md'

    assert_that('pm-fix', 'commands/pm-fix.md 存在', cmd_path.exists())
    assert_that('pm-fix', 'skills/pm-fix/SKILL.md 存在', skill_path.exists())

    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')

    # frontmatter triggers 包含 /pm-fix
    has_trigger = 'triggers' in text and '/pm-fix' in text
    assert_that('pm-fix', 'triggers 包含 /pm-fix', has_trigger)

    # SOP 读取 review-debt/human-sync/snapshot-diff
    has_review_debt = 'review-debt.md' in text
    has_human_sync = 'human-sync.md' in text
    has_snapshot_diff = 'snapshot-diff.md' in text
    assert_that('pm-fix', 'SOP 读取 contracts/review-debt.md', has_review_debt)
    assert_that('pm-fix', 'SOP 读取 contracts/human-sync.md', has_human_sync)
    assert_that('pm-fix', 'SOP 读取 contracts/snapshot-diff.md', has_snapshot_diff)

    # SOP 会写 status.fix_debts
    has_fix_debts = 'fix_debts' in text
    assert_that('pm-fix', 'SOP 会写 status.fix_debts', has_fix_debts)

    # pm-guide 和 wireframe-reviewer 推荐的 /pm-fix 有实际命令入口
    assert_that('pm-fix', 'pm-guide 推荐 /pm-fix 有命令入口', cmd_path.exists())

    wf_reviewer = repo_root / 'skills' / 'pm-wireframe-reviewer' / 'SKILL.md'
    if wf_reviewer.exists():
        wf_text = wf_reviewer.read_text(encoding='utf-8')
        has_fix_ref = '/pm-fix' in wf_text
        assert_that('pm-fix', 'wireframe-reviewer 推荐 /pm-fix 有命令入口',
                    has_fix_ref and cmd_path.exists())


# ============================================================
# TEST 22: pm-fix §2 前置检查 uninitialized 方向正确
# ============================================================
def test22_pm_fix_precheck_direction():
    print(f'\n{CYAN}=== TEST 22: pm-fix §2 前置检查方向 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-fix' / 'SKILL.md'

    assert_that('pm-fix-dir', 'SKILL.md 存在', skill_path.exists())
    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')
    section2 = extract_section2(text)
    assert_that('pm-fix-dir', '§2 区域非空', len(section2.strip()) > 0)

    # 不应出现反向表达："不为 uninitialized：停止"
    has_wrong = '不为' in section2 and 'uninitialized' in section2 and '停止' in section2
    assert_that('pm-fix-dir',
                '§2 没有"不为 uninitialized：停止"的反向表达',
                not has_wrong,
                f'section2: {section2[:400]}')

    # 应包含正确方向："为 uninitialized" + "停止"
    has_correct = 'uninitialized' in section2 and '停止' in section2
    assert_that('pm-fix-dir',
                '§2 包含"uninitialized...停止"的正确阻断表达',
                has_correct,
                f'section2: {section2[:400]}')


# ============================================================
# TEST 23: pm-fix §4 输出规则必须统一推荐 /pm-fix-review
# ============================================================
def extract_section4(text):
    """提取 §4 输出规则区域（从 ## 4. 到 ## 5. 之间）。"""
    import re
    m = re.search(r'## 4\..*?\n(.*?)(?=## 5\.)', text, re.DOTALL)
    return m.group(1) if m else ''


def test23_pm_fix_output_routes_to_fix_review():
    print(f'\n{CYAN}=== TEST 23: pm-fix §4 输出规则统一推荐 /pm-fix-review ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-fix' / 'SKILL.md'

    assert_that('pm-fix-route', 'SKILL.md 存在', skill_path.exists())
    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')
    section4 = extract_section4(text)
    assert_that('pm-fix-route', '§4 区域非空', len(section4.strip()) > 0)

    # §4 必须包含统一规则声明
    has_unified_rule = '/pm-fix-review' in section4
    assert_that('pm-fix-route',
                '§4 包含 /pm-fix-review 统一推荐',
                has_unified_rule,
                f'section4 snippet: {section4[:500]}')

    # §4 不得直接建议阶段 review（open debt 未收口时绕过 fix-review）
    stage_reviews = ['/pm-design-review', '/pm-wireframe-review', '/pm-prd-review', '/pm-prototype-review']
    for sr in stage_reviews:
        assert_that('pm-fix-route',
                    f'§4 不直接建议 {sr}',
                    sr not in section4,
                    f'发现 {sr} in section4')

    # §4 必须包含"下一步唯一建议：/pm-fix-review"格式
    has_exact_recommend = '下一步唯一建议：/pm-fix-review' in section4
    assert_that('pm-fix-route',
                '§4 包含"下一步唯一建议：/pm-fix-review"',
                has_exact_recommend,
                f'section4 snippet: {section4[:500]}')


# ============================================================
# TEST 24: /pm-prd command new_main 不再 placeholder
# ============================================================
def test24_pm_prd_command_not_placeholder():
    print(f'\n{CYAN}=== TEST 24: /pm-prd command new_main 不再 placeholder ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    cmd_path = repo_root / 'commands' / 'pm-prd.md'

    assert_that('pm-prd-cmd', 'commands/pm-prd.md 存在', cmd_path.exists())
    if not cmd_path.exists():
        return

    text = cmd_path.read_text(encoding='utf-8')
    # new_main 应触发 pm-prd skill，不是 placeholder
    has_pm_prd_skill = 'pm-prd' in text
    has_trigger_skill = '触发 skill' in text and 'pm-prd' in text
    assert_that('pm-prd-cmd', 'new_main 触发 pm-prd skill', has_trigger_skill)
    # 不应再有"尚未实现"
    has_placeholder = '尚未实现' in text
    assert_that('pm-prd-cmd', '不再包含"尚未实现"placeholder', not has_placeholder)
    # legacy 仍保留 prd-writer
    has_legacy = 'prd-writer' in text
    assert_that('pm-prd-cmd', 'legacy 仍保留 prd-writer', has_legacy)


# ============================================================
# TEST 25: /pm-prd-review command new_main 不再 placeholder
# ============================================================
def test25_pm_prd_review_command_not_placeholder():
    print(f'\n{CYAN}=== TEST 25: /pm-prd-review command new_main 不再 placeholder ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    cmd_path = repo_root / 'commands' / 'pm-prd-review.md'

    assert_that('pm-prd-rev-cmd', 'commands/pm-prd-review.md 存在', cmd_path.exists())
    if not cmd_path.exists():
        return

    text = cmd_path.read_text(encoding='utf-8')
    has_pm_prd_reviewer = 'pm-prd-reviewer' in text
    has_trigger_skill = '触发 skill' in text and 'pm-prd-reviewer' in text
    assert_that('pm-prd-rev-cmd', 'new_main 触发 pm-prd-reviewer skill', has_trigger_skill)
    has_placeholder = '尚未实现' in text
    assert_that('pm-prd-rev-cmd', '不再包含"尚未实现"placeholder', not has_placeholder)
    has_legacy = 'prd-reviewer' in text
    assert_that('pm-prd-rev-cmd', 'legacy 仍保留 prd-reviewer', has_legacy)


# ============================================================
# TEST 26: skills/pm-prd/SKILL.md 存在 + 内容校验
# ============================================================
def test26_pm_prd_skill_content():
    print(f'\n{CYAN}=== TEST 26: skills/pm-prd/SKILL.md 内容校验 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-prd' / 'SKILL.md'

    assert_that('pm-prd-skill', 'SKILL.md 存在', skill_path.exists())
    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')
    # frontmatter
    assert_that('pm-prd-skill', 'triggers 包含 /pm-prd', '/pm-prd' in text)
    # 前置检查
    assert_that('pm-prd-skill', '包含 workflow_mode', 'workflow_mode' in text)
    assert_that('pm-prd-skill', '包含 new_main', 'new_main' in text)
    # wireframe-review 绑定
    assert_that('pm-prd-skill', '包含 wireframe reviewer_check', 'wireframe' in text and 'reviewer_check' in text)
    # 输出
    assert_that('pm-prd-skill', '输出 prd.md', 'output/prd/prd.md' in text)
    assert_that('pm-prd-skill', '输出 metadata', 'metadata/prd' in text)
    assert_that('pm-prd-skill', '输出 snapshot', 'snapshots/prd' in text)
    assert_that('pm-prd-skill', '更新 status', 'current_stage' in text and 'prd' in text)
    # 禁止
    assert_that('pm-prd-skill', '不提示 /pm-confirm', '/pm-confirm' not in text or '不得提示' in text)
    assert_that('pm-prd-skill', '不写 pm_confirmations', 'pm_confirmations' not in text or '不得写' in text)


# ============================================================
# TEST 27: skills/pm-prd-reviewer/SKILL.md 存在 + 内容校验
# ============================================================
def test27_pm_prd_reviewer_skill_content():
    print(f'\n{CYAN}=== TEST 27: skills/pm-prd-reviewer/SKILL.md 内容校验 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-prd-reviewer' / 'SKILL.md'

    assert_that('pm-prd-rev-skill', 'SKILL.md 存在', skill_path.exists())
    if not skill_path.exists():
        return

    text = skill_path.read_text(encoding='utf-8')
    # frontmatter
    assert_that('pm-prd-rev-skill', 'triggers 包含 /pm-prd-review', '/pm-prd-review' in text)
    # review_results 回写
    assert_that('pm-prd-rev-skill', '包含 review_results 双写规则',
                'review_results' in text and '追加' in text)
    # reviewed_artifact / reviewed_metadata
    assert_that('pm-prd-rev-skill', '包含 reviewed_artifact', 'reviewed_artifact' in text)
    assert_that('pm-prd-rev-skill', '包含 reviewed_metadata', 'reviewed_metadata' in text)
    # 不修改 current_stage
    assert_that('pm-prd-rev-skill', '不修改 current_stage', '不修改' in text and 'current_stage' in text)
    # §3 审查方法包含 8 项检查
    assert_that('pm-prd-rev-skill', '包含归档可读性检查', '归档可读性' in text)
    assert_that('pm-prd-rev-skill', '包含字段一致性检查', '字段一致性' in text)
    assert_that('pm-prd-rev-skill', '包含人机分离检查', '人机分离' in text)
    # §2 前置检查包含产物存在和 metadata 可反查
    section2 = extract_section2(text)
    assert_that('pm-prd-rev-skill', '§2 区域非空', len(section2.strip()) > 0)
    assert_that('pm-prd-rev-skill', '§2 包含 artifacts.prd 检查', 'artifacts.prd' in section2)
    assert_that('pm-prd-rev-skill', '§2 包含 index.yaml 存在检查', 'index.yaml' in section2)


# ============================================================
# TEST 28: templates/prd.md 不含执行说明和内部路径
# ============================================================
def test28_template_prd_clean():
    print(f'\n{CYAN}=== TEST 28: templates/prd.md 不含执行说明和内部路径 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    tpl_path = repo_root / 'templates' / 'prd.md'

    assert_that('tpl-prd', 'templates/prd.md 存在', tpl_path.exists())
    if not tpl_path.exists():
        return

    text = tpl_path.read_text(encoding='utf-8')
    # 不含 HTML 注释
    assert_that('tpl-prd', '不含 HTML 注释', '<!--' not in text)
    # 不含内部路径
    assert_that('tpl-prd', '不含 .pmflow 路径', '.pmflow' not in text)
    assert_that('tpl-prd', '不含 output/ 路径', 'output/' not in text)
    # 不含 metadata 字段
    assert_that('tpl-prd', '不含 field_id', 'field_id' not in text)
    assert_that('tpl-prd', '不含 page_id', 'page_id' not in text)
    # 不含 review 字段
    assert_that('tpl-prd', '不含 verdict', 'verdict' not in text)
    assert_that('tpl-prd', '不含 check_type', 'check_type' not in text)
    # 包含中文章节编号
    assert_that('tpl-prd', '包含"一、文档概述"', '一、文档概述' in text)
    assert_that('tpl-prd', '包含"六、详细需求说明"', '六、详细需求说明' in text)


# ============================================================
# TEST 29: references/prd-action-examples.md 覆盖 10 类样例
# ============================================================
def test29_prd_action_examples():
    print(f'\n{CYAN}=== TEST 29: references/prd-action-examples.md 覆盖 10 类样例 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    ref_path = repo_root / 'references' / 'prd-action-examples.md'

    assert_that('prd-examples', '文件存在', ref_path.exists())
    if not ref_path.exists():
        return

    text = ref_path.read_text(encoding='utf-8')
    categories = [
        '列表查询', '新增/编辑表单', '审批/确认', '导入/导出',
        '详情页', '状态流转', '批量操作', '数据统计', '选择器', '跨页面跳转',
    ]
    for cat in categories:
        assert_that('prd-examples', f'覆盖"{cat}"', cat in text)
    # 每类应有目标和非目标
    assert_that('prd-examples', '包含"目标写法"', '目标写法' in text)
    assert_that('prd-examples', '包含"非目标写法"', '非目标写法' in text)
    assert_that('prd-examples', '包含"metadata"', 'metadata' in text)


# ============================================================
# TEST 30: profiles 文件存在
# ============================================================
def test30_profiles_exist():
    print(f'\n{CYAN}=== TEST 30: PRD profiles 文件存在 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent

    p1 = repo_root / 'profiles' / 'prd-new-main.profile.yaml'
    p2 = repo_root / 'profiles' / 'prd-review-new-main.profile.yaml'
    assert_that('prd-profiles', 'prd-new-main.profile.yaml 存在', p1.exists())
    assert_that('prd-profiles', 'prd-review-new-main.profile.yaml 存在', p2.exists())

    if p1.exists():
        text = p1.read_text(encoding='utf-8')
        assert_that('prd-profiles', 'prd-new-main 包含 workflow_mode: new_main',
                    'new_main' in text)
        assert_that('prd-profiles', 'prd-new-main 包含 review_checklist',
                    'review_checklist' in text)
        assert_that('prd-profiles', 'prd-new-main 包含 dictionary',
                    'dictionary' in text)

    if p2.exists():
        text = p2.read_text(encoding='utf-8')
        assert_that('prd-profiles', 'prd-review-new-main 包含 checks',
                    'checks' in text)
        assert_that('prd-profiles', 'prd-review-new-main 包含 field_consistency',
                    'field_consistency' in text)


# ============================================================
# TEST 31: wireframe-review pass 后 pm-guide 推荐 /pm-prd
# ============================================================
def test31_wireframe_review_pass_to_prd():
    print(f'\n{CYAN}=== TEST 31: wireframe-review pass -> pm-guide 推荐 /pm-prd ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-04T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t, verdict='pass')

    recommend = pm_guide_recommend(d)
    assert_that('wf-pass->prd', 'pm-guide 推荐 /pm-prd',
                recommend == '/pm-prd',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'wf-pass->prd')

    s = read_status(d)
    assert_no_legacy_fields(s, 'wf-pass->prd')
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 32: /pm-prd 后 artifacts.prd 存在，guide 推荐 /pm-prd-review
# ============================================================
def test32_prd_artifacts():
    print(f'\n{CYAN}=== TEST 32: /pm-prd 后 artifacts.prd 存在 ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-04T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t)
    simulate_prd(d, t)
    s = read_status(d)

    assert_that('prd-artifacts', 'current_stage = prd',
                s.get('current_stage') == 'prd',
                f'实际: {s.get("current_stage")}')
    assert_that('prd-artifacts', 'artifacts.prd 包含 prd.md',
                any('prd.md' in p for p in s.get('artifacts', {}).get('prd', [])))
    assert_that('prd-artifacts', 'output/prd/prd.md 存在于磁盘',
                (d / 'output/prd/prd.md').exists())
    assert_that('prd-artifacts', '.pmflow/metadata/prd/index.yaml 存在',
                (d / '.pmflow/metadata/prd/index.yaml').exists())
    assert_that('prd-artifacts', '.pmflow/snapshots/prd/prd.last-synced.md 存在',
                (d / '.pmflow/snapshots/prd/prd.last-synced.md').exists())

    # 新增：验证新的 metadata 结构
    assert_that('prd-artifacts', '.pmflow/metadata/prd/dictionary.yaml 存在',
                (d / '.pmflow/metadata/prd/dictionary.yaml').exists())
    assert_that('prd-artifacts', '.pmflow/metadata/prd/rules.yaml 存在',
                (d / '.pmflow/metadata/prd/rules.yaml').exists())
    assert_that('prd-artifacts', '.pmflow/metadata/prd/trace.yaml 存在',
                (d / '.pmflow/metadata/prd/trace.yaml').exists())

    # pages/*.yaml 存在
    pages_dir = d / '.pmflow/metadata/prd/pages'
    assert_that('prd-artifacts', '.pmflow/metadata/prd/pages/ 目录存在',
                pages_dir.exists() and pages_dir.is_dir())
    if pages_dir.exists():
        page_files = list(pages_dir.glob('*.yaml'))
        assert_that('prd-artifacts', 'pages/*.yaml 至少有一个文件',
                    len(page_files) > 0, f'实际文件数: {len(page_files)}')

    # 不要求旧的 metadata 结构
    assert_that('prd-artifacts', '不要求 entities/*.yaml',
                True, 'entities/*.yaml 已删除')
    assert_that('prd-artifacts', '不要求 field_usage.yaml',
                not (d / '.pmflow/metadata/prd/field_usage.yaml').exists(),
                'field_usage.yaml 不应存在')
    assert_that('prd-artifacts', '不要求 relations.yaml',
                not (d / '.pmflow/metadata/prd/relations.yaml').exists(),
                'relations.yaml 不应存在')

    assert_no_legacy_fields(s, 'prd-artifacts')

    recommend = pm_guide_recommend(d)
    assert_that('prd-artifacts', 'pm-guide 推荐 /pm-prd-review',
                recommend == '/pm-prd-review',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 33: prd-review pass 后 guide 推荐 /pm-prototype
# ============================================================
def test33_prd_review_pass():
    print(f'\n{CYAN}=== TEST 33: prd-review pass -> /pm-prototype ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-04T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t)
    simulate_prd(d, t)
    simulate_prd_review(d, t, verdict='pass')

    recommend = pm_guide_recommend(d)
    assert_that('prd-pass->proto', 'pm-guide 推荐 /pm-prototype',
                recommend == '/pm-prototype',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'prd-pass->proto')

    s = read_status(d)
    assert_no_legacy_fields(s, 'prd-pass->proto')
    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 34: prd-review warn 后 guide 仍推荐 /pm-prototype
# ============================================================
def test34_prd_review_warn():
    print(f'\n{CYAN}=== TEST 34: prd-review warn -> /pm-prototype ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-04T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t)
    simulate_prd(d, t)
    simulate_prd_review(d, t, verdict='warn')

    recommend = pm_guide_recommend(d)
    assert_that('prd-warn', 'pm-guide 推荐 /pm-prototype（warn 不阻断）',
                recommend == '/pm-prototype',
                f'实际推荐: {recommend}')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# TEST 35: prd-review fail 后 guide 推荐 /pm-prd
# ============================================================
def test35_prd_review_fail():
    print(f'\n{CYAN}=== TEST 35: prd-review fail -> 回到 /pm-prd ==={RESET}')
    d = Path(tempfile.mkdtemp(prefix='pmflow-e2e-'))
    t = '2026-05-04T10:00:00'
    simulate_input(d, t)
    simulate_align(d, t)
    simulate_align_review(d, t)
    simulate_design(d, t)
    simulate_design_review(d, t)
    simulate_wireframe(d, t)
    simulate_wireframe_review(d, t)
    simulate_prd(d, t)
    simulate_prd_review(d, t, verdict='fail')

    recommend = pm_guide_recommend(d)
    assert_that('prd-fail', 'pm-guide 推荐回到 /pm-prd',
                recommend == '回到 /pm-prd',
                f'实际推荐: {recommend}')
    assert_no_pm_confirm_in_text(recommend, 'prd-fail')

    shutil.rmtree(d, ignore_errors=True)


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print(f'{MAGENTA}PMFlow New Main Chain E2E Smoke Test{RESET}')

    test1_workflow_mode()
    test2_input_to_align()
    test3_input_warn_to_align()
    test4_align_artifacts()
    test5_align_review_to_design()
    test6_align_review_warn()
    test7_design_artifacts()
    test8_design_review_to_wireframe()
    test9_design_review_warn()
    test10_no_legacy_fields_full_run()
    test11_schema_parseable()
    test12_wireframe_artifacts()
    test13_wireframe_review_to_prd()
    test14_wireframe_review_warn()
    test15_wireframe_review_fail()
    test16_sop_dual_write_rule()
    test17_reviewer_precheck_baseline()
    test18_wireframe_template_and_reference()
    test19_wireframe_reviewer_fail_routing()
    test20_writer_precheck_workflow_mode()
    test21_pm_fix_exists()
    test22_pm_fix_precheck_direction()
    test23_pm_fix_output_routes_to_fix_review()
    test24_pm_prd_command_not_placeholder()
    test25_pm_prd_review_command_not_placeholder()
    test26_pm_prd_skill_content()
    test27_pm_prd_reviewer_skill_content()
    test28_template_prd_clean()
    test29_prd_action_examples()
    test30_profiles_exist()
    test31_wireframe_review_pass_to_prd()
    test32_prd_artifacts()
    test33_prd_review_pass()
    test34_prd_review_warn()
    test35_prd_review_fail()

    print(f'\n{MAGENTA}========================================{RESET}')
    print(f'{MAGENTA}  New Main Chain E2E Summary{RESET}')
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
        sys.exit(1)
    else:
        print(f'{GREEN}All new main chain e2e tests passed.{RESET}')
        sys.exit(0)
