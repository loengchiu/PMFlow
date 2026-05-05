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
    'agents/pmflow-reviewer.md',
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
    'agents',
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
        ok('pmflow-reviewer' in text,
           f'{name}/SKILL.md 未引用 pmflow-reviewer')
        ok('Claude Code' in text,
           f'{name}/SKILL.md 未提及 Claude Code')
        ok('PMFLOW-REVIEW-RESULT' in text,
           f'{name}/SKILL.md 未提及 PMFLOW-REVIEW-RESULT')
        ok('人读产物与 metadata 不一致' in text,
           f'{name}/SKILL.md 缺少人读产物与 metadata 一致性 fail 规则')


def check_agent_definition() -> None:
    agent_path = ROOT / 'agents' / 'pmflow-reviewer.md'
    ok(agent_path.is_file(), '缺少文件: agents/pmflow-reviewer.md')
    if agent_path.is_file():
        text = read(agent_path)
        ok('name: pmflow-reviewer' in text,
           'agents/pmflow-reviewer.md 缺少 name: pmflow-reviewer')
        ok('PMFLOW-REVIEW-RESULT' in text,
           'agents/pmflow-reviewer.md 缺少 PMFLOW-REVIEW-RESULT')
        ok('next_stage_notes' in text,
           'agents/pmflow-reviewer.md 缺少 next_stage_notes')
        ok('warnings 只放业务风险' in text,
           'agents/pmflow-reviewer.md 缺少 warnings 业务风险规则')


def check_multi_round_sync() -> None:
    human_sync = read(ROOT / 'contracts' / 'human-sync.md')
    ok('阶段 writer 多轮同步职责' in human_sync,
       'contracts/human-sync.md 缺少阶段 writer 多轮同步职责')
    ok('同类关联点' in human_sync,
       'contracts/human-sync.md 缺少同类关联点')
    new_main = read(ROOT / 'contracts' / 'new-main-chain.md')
    ok('当前阶段命令负责多轮更新' in new_main,
       'contracts/new-main-chain.md 缺少当前阶段命令负责多轮更新')
    review_debt = read(ROOT / 'contracts' / 'review-debt.md')
    ok('同类关联点' in review_debt,
       'contracts/review-debt.md 缺少同类关联点')
    writer_skills = [
        'pm-align',
        'pm-design',
        'pm-wireframe',
        'pm-prd',
        'pm-prototype',
    ]
    for name in writer_skills:
        path = ROOT / 'skills' / name / 'SKILL.md'
        if not path.is_file():
            continue
        text = read(path)
        ok('多轮更新' in text,
           f'{name}/SKILL.md 缺少多轮更新描述')
        ok('不得只更新' in text,
           f'{name}/SKILL.md 缺少不得只更新单侧的规则')
        ok('同类关联点' in text,
           f'{name}/SKILL.md 缺少同类关联点')
    fix_text = read(ROOT / 'skills' / 'pm-fix' / 'SKILL.md')
    ok('同类关联点检查结果' in fix_text,
       'skills/pm-fix/SKILL.md 缺少同类关联点检查结果')
    fix_review_text = read(ROOT / 'skills' / 'pm-fix-reviewer' / 'SKILL.md')
    ok('同类关联点' in fix_review_text,
       'skills/pm-fix-reviewer/SKILL.md 缺少同类关联点')
    # P0-1: revision 校验
    for name in writer_skills:
        path = ROOT / 'skills' / name / 'SKILL.md'
        if not path.is_file():
            continue
        text = read(path)
        ok('artifact_revision' in text,
           f'{name}/SKILL.md 缺少 artifact_revision')
        ok('metadata_revision' in text,
           f'{name}/SKILL.md 缺少 metadata_revision')
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
        ok('reviewed_artifact_revision' in text,
           f'{name}/SKILL.md 缺少 reviewed_artifact_revision')
        ok('reviewed_metadata_revision' in text,
           f'{name}/SKILL.md 缺少 reviewed_metadata_revision')
    # P0-2: baseline 校验
    input_profile = read(ROOT / 'profiles' / 'input.profile.yaml')
    ok('不是需求事实基线' in input_profile,
       'profiles/input.profile.yaml 缺少不是需求事实基线')
    align_profile = read(ROOT / 'profiles' / 'align.profile.yaml')
    ok('第一个需求事实基线' in align_profile,
       'profiles/align.profile.yaml 缺少第一个需求事实基线')
    align_reviewer = read(ROOT / 'skills' / 'pm-align-reviewer' / 'SKILL.md')
    ok('input 只作来源索引' in align_reviewer,
       'skills/pm-align-reviewer/SKILL.md 缺少 input 只作来源索引')
    ok('不得作为 warning' in align_reviewer,
       'skills/pm-align-reviewer/SKILL.md 缺少不得作为 warning')
    agent_text = read(ROOT / 'agents' / 'pmflow-reviewer.md')
    ok('input 只作来源索引' in agent_text,
       'agents/pmflow-reviewer.md 缺少 input 只作来源索引')
    ok('阶段递进基线' in agent_text,
       'agents/pmflow-reviewer.md 缺少阶段递进基线')
    new_main_text = read(ROOT / 'contracts' / 'new-main-chain.md')
    ok('阶段递进基线' in new_main_text,
       'contracts/new-main-chain.md 缺少阶段递进基线')
    guide_text = read(ROOT / 'skills' / 'pm-guide' / 'SKILL.md')
    ok('revision' in guide_text,
       'skills/pm-guide/SKILL.md 缺少 revision 判断')
    # 检查 profiles baseline_rule
    design_profile = read(ROOT / 'profiles' / 'design.profile.yaml')
    ok('详细设计事实基线' in design_profile,
       'profiles/design.profile.yaml 缺少详细设计事实基线')
    wireframe_profile = read(ROOT / 'profiles' / 'wireframe.profile.yaml')
    ok('页面组织和交互表达基线' in wireframe_profile,
       'profiles/wireframe.profile.yaml 缺少页面组织和交互表达基线')
    prd_profile = read(ROOT / 'profiles' / 'prd-new-main.profile.yaml')
    ok('研发评审与归档基线' in prd_profile,
       'profiles/prd-new-main.profile.yaml 缺少研发评审与归档基线')
    prototype_profile = read(ROOT / 'profiles' / 'prototype-new-main.profile.yaml')
    ok('高保真交互表达基线' in prototype_profile,
       'profiles/prototype-new-main.profile.yaml 缺少高保真交互表达基线')
    # 轻量 metadata 校验
    lightweight_metadata = read(ROOT / 'contracts' / 'lightweight-metadata.md')
    ok('metadata 是外部轻量索引' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少 metadata 是外部轻量索引')
    ok('人读物是事实主体' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少人读物是事实主体')
    ok('anchors' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少 anchors')
    ok('source_refs' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少 source_refs')
    ok('relations' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少 relations')
    ok('禁止字段' in lightweight_metadata,
       'contracts/lightweight-metadata.md 缺少禁止字段')
    # 检查 writer skill 引用 lightweight-metadata.md
    writer_skills = [
        'pm-input',
        'pm-align',
        'pm-design',
        'pm-wireframe',
        'pm-prd',
        'pm-prototype',
    ]
    for name in writer_skills:
        path = ROOT / 'skills' / name / 'SKILL.md'
        if not path.is_file():
            continue
        text = read(path)
        ok('lightweight-metadata.md' in text,
           f'{name}/SKILL.md 未引用 lightweight-metadata.md')
    # 检查 reviewer skill 引用 lightweight-metadata.md
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
        ok('lightweight-metadata.md' in text,
           f'{name}/SKILL.md 未引用 lightweight-metadata.md')
    # 检查 agent 引用 lightweight-metadata.md
    ok('lightweight-metadata.md' in agent_text,
       'agents/pmflow-reviewer.md 未引用 lightweight-metadata.md')
    # 检查 profiles 轻量 metadata 描述
    ok('只索引页面/字段/规则/流程' in design_profile,
       'profiles/design.profile.yaml 缺少只索引页面/字段/规则/流程')
    ok('只记录字段落点、动作落点、规则引用' in prd_profile,
       'profiles/prd-new-main.profile.yaml 缺少只记录字段落点、动作落点、规则引用')
    ok('不保存 HTML' in prototype_profile,
       'profiles/prototype-new-main.profile.yaml 缺少不保存 HTML')
    # 检查 pm-fix 不复制正文到 metadata
    fix_text = read(ROOT / 'skills' / 'pm-fix' / 'SKILL.md')
    ok('不复制正文到 metadata' in fix_text,
       'skills/pm-fix/SKILL.md 缺少不复制正文到 metadata')
    # 检查禁止字段不出现在 profile/skill 输出结构中
    forbidden_fields = [
        'full_content',
        'paragraph',
        'page_body',
        'section_body',
        'html_body',
        'detail_text',
        'long_description',
        'raw_markdown',
        'raw_html',
        'copied_text',
        'full_acceptance_text',
    ]
    check_paths = [
        ROOT / 'profiles' / 'input.profile.yaml',
        ROOT / 'profiles' / 'align.profile.yaml',
        ROOT / 'profiles' / 'design.profile.yaml',
        ROOT / 'profiles' / 'wireframe.profile.yaml',
        ROOT / 'profiles' / 'prd-new-main.profile.yaml',
        ROOT / 'profiles' / 'prototype-new-main.profile.yaml',
        ROOT / 'skills' / 'pm-input' / 'SKILL.md',
        ROOT / 'skills' / 'pm-align' / 'SKILL.md',
        ROOT / 'skills' / 'pm-design' / 'SKILL.md',
        ROOT / 'skills' / 'pm-wireframe' / 'SKILL.md',
        ROOT / 'skills' / 'pm-prd' / 'SKILL.md',
        ROOT / 'skills' / 'pm-prototype' / 'SKILL.md',
    ]
    for path in check_paths:
        if not path.is_file():
            continue
        text = read(path)
        for field in forbidden_fields:
            ok(field not in text, f'{path.relative_to(ROOT)} 包含禁止字段: {field}')
    # 检查 align/input 不得出现容易生成长正文的 metadata 字段口径
    long_text_fields = [
        'description',
        'business_direction',
        'content_summary',
        'context',
        'task',
    ]
    align_input_paths = [
        ROOT / 'profiles' / 'input.profile.yaml',
        ROOT / 'profiles' / 'align.profile.yaml',
    ]
    for path in align_input_paths:
        if not path.is_file():
            continue
        text = read(path)
        # 只检查 machine_output_requirements 部分的字段名
        in_machine_section = False
        for line in text.splitlines():
            if 'machine_output_requirements' in line:
                in_machine_section = True
            if in_machine_section:
                for field_name in long_text_fields:
                    # 检查是否作为 YAML 字段名出现
                    # 匹配形式：description: / # description: / #   description: 等
                    import re
                    # 去掉行首空白，然后检查是否是注释或非注释的字段名
                    stripped = line.strip()
                    # 匹配模式：可选的 # 号 + 可选的空白 + 字段名 + 冒号
                    pattern = r'^#?\s*' + re.escape(field_name) + r'\s*:'
                    if re.match(pattern, stripped):
                        ok(False, f'{path.relative_to(ROOT)} machine_output_requirements 包含长文本字段: {field_name}')


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
    ok("'pmflow-reviewer'" in host_script, '安装脚本未映射 agent: pmflow-reviewer')
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
    check_agent_definition()
    check_multi_round_sync()
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
