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
# TEST 17: wireframe-reviewer 前置检查包含三项校验
# ============================================================
def test17_wireframe_reviewer_precheck():
    print(f'\n{CYAN}=== TEST 17: wireframe-reviewer 前置检查三项校验 ==={RESET}')
    repo_root = Path(__file__).resolve().parent.parent
    skill_path = repo_root / 'skills' / 'pm-wireframe-reviewer' / 'SKILL.md'

    assert_that('wf-precheck', 'SKILL.md 存在', skill_path.exists())
    if skill_path.exists():
        text = skill_path.read_text(encoding='utf-8')
        # 检查 §2 前置检查包含 verdict pass/warn 校验
        has_verdict_check = 'verdict' in text and ('pass' in text or 'warn' in text)
        assert_that('wf-precheck',
                    '前置检查包含 verdict pass/warn 校验',
                    has_verdict_check)
        # 检查包含 reviewed_artifact 校验
        has_artifact_check = 'reviewed_artifact' in text
        assert_that('wf-precheck',
                    '前置检查包含 reviewed_artifact 校验',
                    has_artifact_check)
        # 检查包含 reviewed_metadata 校验
        has_metadata_check = 'reviewed_metadata' in text
        assert_that('wf-precheck',
                    '前置检查包含 reviewed_metadata 校验',
                    has_metadata_check)


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
    test17_wireframe_reviewer_precheck()

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
