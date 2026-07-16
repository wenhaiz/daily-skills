# Repository Guidelines

- 使用中文沟通。
- 每个 skill 放在 `skills/<skill-name>/`，目录名必须和 `SKILL.md` 的 `name` 一致。
- Skill 目录只保存运行所需的 `SKILL.md`、`agents/`、`scripts/`、`references/` 和 `assets/`；仓库说明、版本和 Changelog 放在根目录。
- `skills.json` 是 skill 发布版本的事实源，版本使用 SemVer。
- Tag 使用 `<skill-name>-v<version>`，例如 `project-docs-manager-v1.0.0`。
- 发布前运行 `python3 scripts/validate.py`。
- 修改项目文档契约时，同步增加对应 skill 的迁移说明和 contract version；修正文案或内部脚本 bug 不需要增加 contract version。
- 不要自动迁移 `~/.codex/skills` 中未确认归属的其他 skill。
