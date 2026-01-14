import sys
import click
from pathlib import Path

from . import SkillScheduler
from .utils.config import Config


@click.group()
@click.version_option(version="0.1.0")
@click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
@click.option('--skills-dir', '-s', type=click.Path(exists=True), help='Skills directory')
@click.pass_context
def cli(ctx, config, skills_dir):
    config_obj = Config(config) if config else Config()

    if skills_dir:
        config_obj.skills_dir = skills_dir

    ctx.ensure_object(dict)
    ctx.obj['scheduler'] = SkillScheduler(config=config_obj)


@cli.command()
@click.argument('skill_name')
@click.option('--param', '-p', multiple=True, help='Parameters in key=value format')
@click.pass_context
def run(ctx, skill_name, param):
    scheduler = ctx.obj['scheduler']

    params = {}
    for p in param:
        if '=' in p:
            key, value = p.split('=', 1)
            params[key] = value

    result = scheduler.run(skill_name, params)

    if result.get('success'):
        click.echo(result.get('output', ''))
    else:
        click.echo(f"Error: {result.get('message', 'Unknown error')}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.pass_context
def ask(ctx, query):
    scheduler = ctx.obj['scheduler']

    result = scheduler.ask(query)

    if result.get('success'):
        if 'final_output' in result:
            click.echo(result['final_output'])
        elif 'output' in result:
            click.echo(result['output'])
    else:
        click.echo(f"Error: {result.get('message', 'Unknown error')}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--tags', '-t', help='Filter by tags (comma-separated)')
@click.pass_context
def list(ctx, tags):
    scheduler = ctx.obj['scheduler']
    skills = scheduler.list_skills()

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        filtered = [s for s in skills if any(tag in s.get('tags', []) for tag in tag_list)]
        skills = filtered

    if not skills:
        click.echo("No skills found")
        return

    click.echo(f"Found {len(skills)} skill(s):\n")

    for skill in skills:
        click.echo(f"  {skill['name']}")
        click.echo(f"    {skill['description']}")
        if skill.get('tags'):
            click.echo(f"    Tags: {', '.join(skill['tags'])}")
        click.echo()


@cli.command()
@click.argument('skill_name')
@click.pass_context
def info(ctx, skill_name):
    scheduler = ctx.obj['scheduler']
    info = scheduler.get_skill_info(skill_name)

    if not info:
        click.echo(f"Skill '{skill_name}' not found", err=True)
        sys.exit(1)

    click.echo(f"Name: {info['name']}")
    click.echo(f"Description: {info['description']}")
    click.echo(f"Version: {info['version']}")
    click.echo(f"Tags: {', '.join(info['tags']) or 'None'}")
    click.echo(f"Timeout: {info['timeout']}s")

    if info['inputs']:
        click.echo("\nInputs:")
        for name, details in info['inputs'].items():
            required = "required" if details['required'] else "optional"
            click.echo(f"  --{name} ({details['type']}, {required})")
            if details.get('description'):
                click.echo(f"    {details['description']}")

    if info['dependencies']:
        click.echo(f"\nDependencies: {', '.join(info['dependencies'])}")


@cli.command()
@click.argument('skill_name')
@click.pass_context
def validate(ctx, skill_name):
    from .core.skill import Skill

    skills_dir = Path(ctx.obj['scheduler'].config.skills_dir)
    skill_path = skills_dir / skill_name

    if not skill_path.exists():
        click.echo(f"Skill '{skill_name}' not found", err=True)
        sys.exit(1)

    try:
        skill = Skill(skill_name, skill_path)
        click.echo(f"Skill '{skill_name}' is valid")
        click.echo(f"  Name: {skill.name}")
        click.echo(f"  Description: {skill.description}")
        click.echo(f"  Inputs: {len(skill.inputs)}")
        click.echo(f"  Dependencies: {len(skill.dependencies)}")
    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('skill_name')
@click.pass_context
def init(ctx, skill_name):
    from pathlib import Path

    skills_dir = Path(ctx.obj['scheduler'].config.skills_dir)
    skill_dir = skills_dir / skill_name

    if skill_dir.exists():
        click.echo(f"Skill '{skill_name}' already exists", err=True)
        sys.exit(1)

    skill_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    skill_md = f"""---
name: {skill_name}
description: Description of your skill
tags: []
dependencies: []
timeout: 30
script: "scripts/main.py"

# 输入参数定义
inputs:
  example_input:
    type: string
    required: true
    description: "An example input parameter"

# 权限配置
permissions:
  read_file: []
  write_file: []
  network: false
  execute_script: true
---

# {skill_name}

Description of your skill.

## When to Use This Skill

Trigger this skill when:
- User needs to perform specific task
- Certain conditions are met

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| example_input | string | Yes | An example input parameter |

## Output

- **Type**: string
- **Description**: Output description

## Usage Examples

### Example 1
\`\`\`python
scheduler.ask("{skill_name} example_input=World")
\`\`\`
"""

    (skill_dir / "skill.md").write_text(skill_md)
    (scripts_dir / "main.py").write_text(f"""#!/usr/bin/env python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--example_input", type=str, required=True)
    args = parser.parse_args()

    print(f"Hello from {skill_name}!")
    print(f"example_input: {{args.example_input}}")

if __name__ == "__main__":
    main()
""")

    click.echo(f"Created skill '{skill_name}' at {skill_dir}")
    click.echo(f"  - {skill_dir / 'skill.md'}")
    click.echo(f"  - {skill_dir / 'scripts/main.py'}")
    click.echo("\nEdit skill.md to configure your skill")
    click.echo("Run with: skillscheduler run --skill {skill_name} --param example_input=World".format(skill_name=skill_name))


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
