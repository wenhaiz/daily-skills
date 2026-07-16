# daily-skills

个人 Codex skills 的统一源码仓库。每个 skill 独立放在 `skills/<skill-name>/`，仓库根目录负责版本、校验、安装和发布。

## 当前 skills

| Skill | Version | Description |
| --- | --- | --- |
| `project-docs-manager` | `1.0.0` | 初始化、维护和增量升级项目文档体系 |

版本真相以 `skills.json` 为准。

## 本地安装

开发时使用软链接，让仓库改动立即生效：

```bash
python3 scripts/install.py project-docs-manager --mode symlink
```

目标已存在时，显式增加 `--replace`。脚本会先把旧版本移动到 `~/.codex/skills/.daily-skills-backups/`。

需要稳定副本时使用：

```bash
python3 scripts/install.py project-docs-manager --mode copy
```

## 校验

```bash
python3 scripts/validate.py
```

校验覆盖目录、版本清单、`SKILL.md` 元数据、`agents/openai.yaml`、Python 语法和 Shell 语法。

## 发布

先更新 skill、`skills.json` 和 `CHANGELOG.md`，提交后运行：

```bash
python3 scripts/release.py project-docs-manager
```

它会创建 `project-docs-manager-v1.0.0` 形式的 annotated tag。增加 `--push` 才会推送 tag；远端收到 tag 后，GitHub Actions 会创建对应 Release。

## 从 GitHub 安装固定版本

```bash
install-skill-from-github.py \
  --repo <owner>/daily-skills \
  --path skills/project-docs-manager \
  --ref project-docs-manager-v1.0.0
```
