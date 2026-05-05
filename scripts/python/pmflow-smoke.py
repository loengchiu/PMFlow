from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SKILLS = [
    'pm-guide',
    'pm-input',
    'pm-align',
    'pm-align-reviewer',
    'pm-design',
    'pm-design-reviewer',
    'pm-wireframe',
    'pm-wireframe-reviewer',
    'pm-prd',
    'pm-prd-reviewer',
    'pm-prototype',
    'pm-prototype-reviewer',
    'pm-fix',
    'pm-fix-reviewer',
]

REQUIRED_FILES = [
    'AGENTS.md',
    'README.md',
    'install.py',
    'docs/usage/claude-install.md',
    'contracts/gates.md',
    'contracts/human-sync.md',
    'contracts/new-main-chain.md',
    'contracts/review-debt.md',
    'contracts/reviewer-independence.md',
    'contracts/snapshot-diff.md',
    'schemas/status.schema.yaml',
    'profiles/input.profile.yaml',
    'profiles/align.profile.yaml',
    'profiles/design.profile.yaml',
    'profiles/wireframe.profile.yaml',
    'profiles/prd-new-main.profile.yaml',
    'profiles/prd-review-new-main.profile.yaml',
    'profiles/prototype-new-main.profile.yaml',
    'profiles/prototype-review-new-main.profile.yaml',
    'templates/input.md',
    'templates/align.md',
    'templates/design.md',
    'templates/prd.md',
    'templates/wireframe.md',
    'references/prd-writing.md',
    'references/prd-action-examples.md',
    'references/prototype-ui-style.md',
    'references/wireframe-writing.md',
    'references/writing-principles.md',
    'scripts/python/pmflow-host.py',
]

FORBIDDEN_PATHS = [
    'commands',
    'test',
    'docs/plans',
    'docs/acceptance',
    'contracts/confirmation.md',
    'contracts/build-type.md',
    'contracts/input-classification.md',
    'skills/pm-confirm',
    'skills/brd-interviewer',
    'skills/uc-interviewer',
    'skills/solution-writer',
    'skills/solution-reviewer',
    'skills/prototype-designer',
    'skills/prototype-reviewer',
    'skills/prd-writer',
    'skills/prd-reviewer',
]

REMOVED_PROFILE_FILES = [
    'brd.profile.yaml',
    'uc.profile.yaml',
    'solution.profile.yaml',
    'solution-review.profile.yaml',
    'prototype.profile.yaml',
    'prototype-review.profile.yaml',
    'prd.profile.yaml',
    'prd-review.profile.yaml',
]

REMOVED_TEMPLATE_FILES = [
    'brd-note.md',
    'uc-note.md',
    'solution-note.md',
    'prototype-note.md',
]

RELEASE_DIRS = {
    '.git',
    'contracts',
    'docs',
    'profiles',
    'references',
    'schemas',
    'scripts',
    'skills',
    'templates',
}

ROOT_FILES = {
    '.gitignore',
    'AGENTS.md',
    'README.md',
    'install.py',
}


failures: list[str] = []


def ok(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig')


def check_required_files() -> None:
    for rel in REQUIRED_FILES:
        ok((ROOT / rel).is_file(), f'缺少文件: {rel}')


def check_skills() -> None:
    skill_dirs = sorted(p.name for p in (ROOT / 'skills').iterdir() if p.is_dir())
    ok(skill_dirs == sorted(REQUIRED_SKILLS), f'skills 目录不匹配: {skill_dirs}')
    for name in REQUIRED_SKILLS:
        path = ROOT / 'skills' / name / 'SKILL.md'
        ok(path.is_file(), f'缺少 SKILL.md: {name}')
        if path.is_file():
            lines = read(path).splitlines()
            ok(len(lines) < 300, f'{name}/SKILL.md 超过 300 行: {len(lines)}')
            ok('triggers:' in read(path), f'{name}/SKILL.md 缺少 triggers frontmatter')


def check_removed_paths() -> None:
    for rel in FORBIDDEN_PATHS:
        ok(not (ROOT / rel).exists(), f'不应存在旧路径: {rel}')
    for name in REMOVED_PROFILE_FILES:
        ok(not (ROOT / 'profiles' / name).exists(), f'不应存在旧 profile: {name}')
    for name in REMOVED_TEMPLATE_FILES:
        ok(not (ROOT / 'templates' / name).exists(), f'不应存在旧 template: {name}')


def check_release_shape() -> None:
    # 跳过所有以 . 开头的目录（编辑器/工具配置，均在 .gitignore 中）
    # .gitignore 本身在 ROOT_FILES 白名单中，由文件分支处理
    for item in ROOT.iterdir():
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            ok(item.name in RELEASE_DIRS, f'根目录不应存在目录: {item.name}')
        else:
            ok(item.name in ROOT_FILES, f'根目录不应存在文件: {item.name}')


def check_reviewer_independence() -> None:
    contract_path = ROOT / 'contracts' / 'reviewer-independence.md'
    ok(contract_path.is_file(), '缺少文件: contracts/reviewer-independence.md')
    reviewer_skills = [
        'pm-align-reviewer',
        'pm-design-reviewer',
        'pm-wireframe-reviewer',
        'pm-prd-reviewer',
        'pm-prototype-reviewer',
        'pm-fix-reviewer',
    ]
    for name in reviewer_skills:
        path = ROOT / 'skills' / name / 'SKILL.md'
        if not path.is_file():
            continue
        text = read(path)
        ok('reviewer-independence.md' in text,
           f'{name}/SKILL.md 未引用 reviewer-independence.md')
        ok('独立审查' in text,
           f'{name}/SKILL.md 缺少"独立审查"关键词')


def check_no_old_markers() -> None:
    targets = [
        ROOT / 'AGENTS.md',
        ROOT / 'skills' / 'pm-guide' / 'SKILL.md',
        ROOT / 'contracts' / 'new-main-chain.md',
        ROOT / 'contracts' / 'gates.md',
        ROOT / 'schemas' / 'status.schema.yaml',
        ROOT / 'profiles' / 'pm-guide.profile.yaml',
    ]
    forbidden = [
        '/pm-confirm',
        'pm_confirmations',
        'approved_baselines',
        'brd-interviewer',
        'uc-interviewer',
        'solution-writer',
        'prototype-designer',
        '旧主链',
    ]
    for path in targets:
        if not path.exists():
            continue
        text = read(path)
        for token in forbidden:
            ok(token not in text, f'{path.relative_to(ROOT)} 包含旧标记: {token}')


def check_installer() -> None:
    host_script = read(ROOT / 'scripts' / 'python' / 'pmflow-host.py')
    for skill in REQUIRED_SKILLS:
        ok(f"'{skill}'" in host_script, f'安装脚本未映射 skill: {skill}')
    ok("'claude-code'" in host_script, '安装脚本缺少 claude-code host')
    ok("'trae-cn'" in host_script, '安装脚本缺少 trae-cn host')
    ok('rules' in host_script and 'pmflow-global.md' in host_script,
       '安装脚本缺少 Trae-CN 全局规则写入')


def main() -> int:
    check_required_files()
    check_skills()
    check_removed_paths()
    check_release_shape()
    check_reviewer_independence()
    check_no_old_markers()
    check_installer()

    if failures:
        print('pmflow-smoke:fail')
        for failure in failures:
            print(f'- {failure}')
        return 1

    print('pmflow-smoke:ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
