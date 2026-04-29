#!/usr/bin/env python3
"""PMFlow Boundary Gate Smoke Test
对 4 个边界场景的 status.yaml 做静态断言，验证 verdict/gate 边界行为
用法: python scripts/pmflow-gate-boundary-smoke.py
"""

import sys
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
TEST_DIR = REPO_ROOT / 'test'

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
# 1. boundary-fail: verdict=fail 阻断 pm-confirm
# ============================================================
def test_boundary_fail():
    print(f'\n{CYAN}=== boundary-fail: verdict=fail blocking ==={RESET}')
    path = TEST_DIR / 'boundary-fail' / '.pmflow' / 'status.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    assert_that('boundary-fail', 'current_stage = solution',
                s['current_stage'] == 'solution',
                f"actual: {s['current_stage']}")

    sol_reviews = [r for r in (s.get('review_results') or []) if r.get('stage') == 'solution']
    sol_review = sol_reviews[0] if sol_reviews else None
    assert_that('boundary-fail', 'review_results has solution entry',
                sol_review is not None,
                'no stage=solution in review_results')

    if sol_review:
        assert_that('boundary-fail', 'verdict = fail',
                    sol_review['verdict'] == 'fail',
                    f"actual verdict: {sol_review['verdict']}")
        assert_that('boundary-fail', 'check_type = reviewer_check',
                    sol_review['check_type'] == 'reviewer_check',
                    f"actual check_type: {sol_review['check_type']}")
        fr = sol_review.get('fail_reasons') or []
        assert_that('boundary-fail', 'fail_reasons non-empty (>=1)',
                    len(fr) >= 1,
                    f'count: {len(fr)}')

        artifacts = s.get('artifacts') or {}
        sol_arts = artifacts.get('solution', []) or []
        latest = sol_arts[-1] if sol_arts else None
        reviewed = sol_review.get('reviewed_artifact')
        assert_that('boundary-fail', 'reviewed_artifact matches latest artifact',
                    reviewed == latest,
                    f'reviewed: {reviewed}, latest: {latest}')

    sol_confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == 'solution']
    assert_that('boundary-fail', 'pm_confirmations has NO solution entry (confirm blocked)',
                len(sol_confs) == 0,
                'solution confirmation exists but should have been blocked by fail verdict')


# ============================================================
# 2. boundary-warn: verdict=warn, open_questions recorded
# ============================================================
def test_boundary_warn():
    print(f'\n{CYAN}=== boundary-warn: verdict=warn + open_questions ==={RESET}')
    path = TEST_DIR / 'boundary-warn' / '.pmflow' / 'status.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    assert_that('boundary-warn', 'current_stage = uc',
                s['current_stage'] == 'uc',
                f"actual: {s['current_stage']}")

    uc_reviews = [r for r in (s.get('review_results') or []) if r.get('stage') == 'uc']
    uc_review = uc_reviews[0] if uc_reviews else None
    assert_that('boundary-warn', 'review_results has uc entry',
                uc_review is not None,
                'no stage=uc in review_results')

    if uc_review:
        assert_that('boundary-warn', 'verdict = warn',
                    uc_review['verdict'] == 'warn',
                    f"actual verdict: {uc_review['verdict']}")
        warns = uc_review.get('warnings') or []
        assert_that('boundary-warn', 'warnings non-empty (>=1)',
                    len(warns) >= 1,
                    f'count: {len(warns)}')

        artifacts = s.get('artifacts') or {}
        uc_arts = artifacts.get('uc', []) or []
        latest_uc = uc_arts[-1] if uc_arts else None
        assert_that('boundary-warn', 'reviewed_artifact matches artifacts.uc latest',
                    uc_review.get('reviewed_artifact') == latest_uc,
                    f"reviewed: {uc_review.get('reviewed_artifact')}, latest: {latest_uc}")

    oq = s.get('open_questions') or []
    assert_that('boundary-warn', 'open_questions has existing entries',
                len(oq) >= 1,
                f'count: {len(oq)}')

    brd_confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == 'brd']
    uc_confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == 'uc']
    assert_that('boundary-warn', 'brd confirmed, uc NOT confirmed (awaiting PM confirm)',
                len(brd_confs) > 0 and len(uc_confs) == 0,
                f'brd: {len(brd_confs) > 0}, uc: {len(uc_confs) > 0}')


# ============================================================
# 3. boundary-stale-review: reviewed_artifact mismatch
# ============================================================
def test_boundary_stale_review():
    print(f'\n{CYAN}=== boundary-stale-review: review-artifact mismatch ==={RESET}')
    path = TEST_DIR / 'boundary-stale-review' / '.pmflow' / 'status.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    artifacts = s.get('artifacts') or {}
    sol_arts = artifacts.get('solution', []) or []
    assert_that('boundary-stale-review', 'artifacts.solution has >=2 versions',
                len(sol_arts) >= 2,
                f'count: {len(sol_arts)}')

    latest = sol_arts[-1] if sol_arts else None
    assert_that('boundary-stale-review', 'latest artifact is v2',
                'v2' in (latest or ''),
                f'latest: {latest}')

    sol_reviews = [r for r in (s.get('review_results') or []) if r.get('stage') == 'solution']
    sol_review = sol_reviews[0] if sol_reviews else None
    if sol_review:
        ra = sol_review.get('reviewed_artifact', '')
        assert_that('boundary-stale-review', 'reviewed_artifact points to v1 (stale)',
                    'stale-test.md' in ra and 'v2' not in ra,
                    f'reviewed_artifact: {ra}')

    if sol_review and latest:
        mismatch = sol_review.get('reviewed_artifact') != latest
        assert_that('boundary-stale-review', 'reviewed_artifact != latest artifact (MUST reject confirm)',
                    mismatch,
                    f"reviewed: {sol_review.get('reviewed_artifact')}, latest: {latest}")

    if sol_review:
        assert_that('boundary-stale-review', 'verdict = pass (testing mismatch, not fail)',
                    sol_review.get('verdict') == 'pass',
                    f"actual verdict: {sol_review.get('verdict')}")

    sol_confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == 'solution']
    assert_that('boundary-stale-review', 'pm_confirmations has NO solution entry',
                len(sol_confs) == 0,
                'solution should not be confirmed with stale review')


# ============================================================
# 4. boundary-baseline-mismatch: approved_baselines mismatch
# ============================================================
def test_boundary_baseline_mismatch():
    print(f'\n{CYAN}=== boundary-baseline-mismatch: baseline path mismatch ==={RESET}')
    path = TEST_DIR / 'boundary-baseline-mismatch' / '.pmflow' / 'status.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        s = yaml.safe_load(f)

    assert_that('boundary-baseline-mismatch', 'current_stage = prd',
                s['current_stage'] == 'prd',
                f"actual: {s['current_stage']}")

    artifacts = s.get('artifacts') or {}
    sol_arts = artifacts.get('solution', []) or []
    latest_sol = sol_arts[-1] if sol_arts else None
    assert_that('boundary-baseline-mismatch', 'artifacts.solution has latest artifact',
                latest_sol is not None,
                f'latest: {latest_sol}')

    sol_bls = [b for b in (s.get('approved_baselines') or []) if b.get('stage') == 'solution']
    sol_bl = sol_bls[0] if sol_bls else None
    assert_that('boundary-baseline-mismatch', 'approved_baselines has solution entry',
                sol_bl is not None,
                'no stage=solution in approved_baselines')

    if sol_bl:
        assert_that('boundary-baseline-mismatch', 'baseline artifact_path points to OLD file',
                    'OLD' in (sol_bl.get('artifact_path') or ''),
                    f"artifact_path: {sol_bl.get('artifact_path')}")

    if sol_bl and latest_sol:
        mismatch = sol_bl.get('artifact_path') != latest_sol
        assert_that('boundary-baseline-mismatch', 'baseline artifact_path != artifacts.solution latest (MUST block PRD)',
                    mismatch,
                    f"baseline: {sol_bl.get('artifact_path')}, latest: {latest_sol}")

    # 其他 3 个阶段的基线一致性检查
    for stage in ('brd', 'uc', 'prototype'):
        bls = [b for b in (s.get('approved_baselines') or []) if b.get('stage') == stage]
        bl = bls[0] if bls else None
        arts = artifacts.get(stage, []) or []
        art = arts[-1] if arts else None
        if bl and art:
            ok = bl.get('artifact_path') == art
            assert_that('boundary-baseline-mismatch', f'{stage} baseline path consistent (no false positive)',
                        ok,
                        f"baseline: {bl.get('artifact_path')}, artifact: {art}")

    prd_confs = [c for c in (s.get('pm_confirmations') or []) if c.get('stage') == 'prd']
    assert_that('boundary-baseline-mismatch', 'pm_confirmations has NO prd entry (baseline mismatch blocks)',
                len(prd_confs) == 0,
                'prd should not proceed with broken baseline chain')


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print(f'{MAGENTA}PMFlow Boundary Gate Smoke Test{RESET}')
    print(f'{MAGENTA}Test root: {TEST_DIR}{RESET}')

    test_boundary_fail()
    test_boundary_warn()
    test_boundary_stale_review()
    test_boundary_baseline_mismatch()

    print(f'\n{MAGENTA}========================================{RESET}')
    print(f'{MAGENTA}  Summary{RESET}')
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
        print(f'{GREEN}All tests passed.{RESET}')
        sys.exit(0)
