# daily-skills

个人 Codex skills 的统一源码仓库。每个 skill 独立放在 `skills/<skill-name>/`，仓库根目录负责版本、校验、安装和发布。

## 当前 skills

| Skill | Version | Description |
| --- | --- | --- |
| `image-compress` | `1.0.0` | 批量压缩 PNG 图片，默认无损，可选轻度有损，并跳过未修改的历史文件。 |
| `ios-swiftui-ui-quality` | `1.0.0` | SwiftUI 专属 UI 工作流；适用于页面、导航、动效、Preview 和 UI Test 的实现与视觉验收。 |
| `ui-quality-workflow` | `1.0.0` | 为非轻微 UI 改动建立设计契约、可访问性检查与真实画面验收；适用于新页面、重要布局或共享组件改动。 |
| `refine-code` | `1.0.0` | 基于证据改进代码的可靠性、可扩展性和可维护性，同时保护预期行为与公开契约。 |
| `release-readiness-review` | `1.0.0` | 在生产、TestFlight、beta 或正式发布前执行风险导向的 go/no-go 审查。 |
| `product-team-facilitation` | `1.0.0` | 组织产品、技术、数据、增长和运营视角，收敛功能优先级、路线图与增长决策。 |
| `project-docs-manager` | `1.2.0` | 初始化、维护和增量升级项目文档体系，并管理可执行的活 Plan |

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

## 远程安装

不克隆仓库，直接安装最新发布版本到 Codex：

```bash
curl -fsSL https://raw.githubusercontent.com/wenhaiz/daily-skills/main/scripts/install-remote.sh \
  | bash -s -- project-docs-manager
```

安装到 Claude Code：

```bash
curl -fsSL https://raw.githubusercontent.com/wenhaiz/daily-skills/main/scripts/install-remote.sh \
  | bash -s -- project-docs-manager --platform claude
```

脚本默认根据 `skills.json` 安装对应的发布 tag。使用 `--version 1.2.0` 可以固定版本；目标已存在时，显式增加 `--replace`，旧版本会先移动到安装目录下的 `.daily-skills-backups/`。

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

它会创建 `project-docs-manager-v1.2.0` 形式的 annotated tag。增加 `--push` 才会推送 tag；远端收到 tag 后，GitHub Actions 会创建对应 Release。

## 从 GitHub 安装固定版本

```bash
install-skill-from-github.py \
  --repo <owner>/daily-skills \
  --path skills/project-docs-manager \
  --ref project-docs-manager-v1.2.0
```
