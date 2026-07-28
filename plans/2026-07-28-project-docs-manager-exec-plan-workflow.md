# 优化 project-docs-manager 的可执行 Plan 流程

状态：`completed`

本文档是一份活文档。实施期间必须持续更新「进度（Progress）」「意外与发现（Surprises & Discoveries）」「决策记录（Decision Log）」和「结果与回顾（Outcomes & Retrospective）」，保证新的执行者只阅读当前仓库和本文档也能继续工作。

## 目的

参考 OpenAI ExecPlan 指南，增强 `project-docs-manager` 生成和维护 Plan 的能力。完成后，普通 Plan 也必须自包含、持续更新并提供可验证结果；复杂功能、重要重构、跨模块或长时间任务使用完整 ExecPlan，使不了解仓库的新执行者可以只依赖当前工作树和一份 Plan 继续开发。

## 上下文

`skills/project-docs-manager/` 管理 Ideas、Plans、ProductFact 和 Changelog 的文档生命周期。当前 contract 是 v2，已经规定 completed Plan 的归档位置，但现有规则没有完整说明如何生成可执行 Plan，也没有把开发过程中的进度、发现、决策和结果回顾设为稳定合同。

本次修改会更新 skill 说明、文档模型、初始化资源、迁移合同和检查脚本，并把 `skills.json` 中的发布版本从 `1.1.0` 更新为 `1.2.0`。本次不提交、不打 tag、不发布，也不自动迁移其他项目。

## 范围

包含：

- 普通 Plan 与完整 ExecPlan 的分层规则。
- Plan 创建、执行、验证、收口和归档流程。
- 项目侧 `PLANS.md` 合同和 Plan 模板。
- contract v3、manifest 新路径和 `inspect` 路径检查。
- skill 版本、README 和 Changelog 更新。

不包含：

- 批量改写已有 archived Plan。
- 自动迁移其他仓库。
- 自动提交、打 tag 或发布。

## 实施步骤

1. 补充 skill 和文档模型中的 Plan 分层、生成、执行和收口规则。
2. 增加项目侧 Plan 合同和模板资源，并把它们接入初始化 scaffold。
3. 将 contract 升级到 v3，增加 manifest 路径、检查结果和迁移说明。
4. 将 skill 版本升级到 `1.2.0`，同步仓库说明和 Changelog。
5. 执行初始化、兼容性、内容和仓库校验，将结果写回本文档。

## 进度（Progress）

- [x] 2026-07-28 16:40 +0800：完成仓库、现有 skill、v2 contract 和 OpenAI ExecPlan 指南调研。
- [x] 2026-07-28 16:40 +0800：创建本计划文档并标记为 `active`。
- [x] 2026-07-28 16:44 +0800：更新 Plan 分层、生成、实施、验证和收口流程。
- [x] 2026-07-28 16:44 +0800：增加项目侧 `PLANS.md` 合同、Plan 模板和初始化 scaffold。
- [x] 2026-07-28 16:44 +0800：将 contract 升级到 v3，增加 manifest 路径和迁移说明。
- [x] 2026-07-28 16:44 +0800：将 `project-docs-manager` 升级到 `1.2.0` 并更新发布文档。
- [x] 2026-07-28 16:48 +0800：完成新项目初始化、重复初始化、v2 自定义目录、显式 manifest 路径、内容和仓库校验。

## 意外与发现（Surprises & Discoveries）

- 观察：现有初始化脚本只提供 Plans 导航，没有可直接复制的 Plan 模板或项目侧执行合同。
  证据：`SCAFFOLD` 仅包含 `plans-root.md` 和 `plans-archive-root.md`。
- 观察：现有 `inspect` 已经按 manifest 派生 Plans 和 archive 路径，可沿用同一方式支持 Plan 合同和模板的自定义路径。
  证据：`scripts/project_docs.py` 从 `manifest.paths` 读取 `plans` 和 `plans_archive`。
- 观察：OpenAI 的完整 ExecPlan 结构适合复杂工作，但直接要求所有轻量 Plan 填写全部章节会增加不必要成本。
  证据：本次用普通必需章节承载活文档要求，将里程碑、接口、恢复和产物证据保留为完整 ExecPlan 附加章节。
- 观察：v2 manifest 没有新增字段时，也可以从已有 `product_fact` 和 `plans` 自定义目录安全派生合同与模板位置。
  证据：临时 v2 fixture 在 `knowledge/plans/PLANS.md` 和 `knowledge/facts/90-templates/plan-template.md` 存在时，`inspect` 将两项都报告为 `true`。

## 决策记录（Decision Log）

- 决策：采用分层 Plan，而不是要求所有任务使用完整 ExecPlan。
  理由：所有 Plan 保持可恢复和可验证，复杂任务再承担完整合同的文档成本。
  日期：2026-07-28。
- 决策：不采用官方示例中的强制频繁提交规则。
  理由：提交行为必须继续服从用户授权、仓库规则和审批边界。
  日期：2026-07-28。
- 决策：v3 迁移不批量改写历史 Plan。
  理由：升级应保护项目已有内容；活动 Plan 在恢复开发时再补齐新合同。
  日期：2026-07-28。

## 验证与验收

- 在仓库根目录运行 `python3 scripts/validate.py`：通过，输出 `OK project-docs-manager 1.2.0`，其他 skill 也全部通过。
- 在临时目录运行 `project_docs.py init --apply`：生成 `Docs/1-Plans/PLANS.md`、`Docs/0-ProductFact/90-templates/plan-template.md` 和包含两个新路径的 manifest；`inspect` 报告目标 contract 为 v3，两项路径都存在。
- 对同一临时目录重复运行 `init --apply`：所有文件输出 `KEEP`，没有覆盖已有内容。
- 对 contract v2、自定义 Plans 和 ProductFact 目录的 fixture 运行 `inspect`：从已有目录派生 Plan 合同和模板位置，活动及归档 Plan 校验和保持不变。
- 对带显式 `paths.plan_contract` 和 `paths.plan_template` 的 fixture 运行 `inspect`：两个非默认路径都报告为 `true`。
- 检查生成模板：包含 `Progress`、`Surprises & Discoveries`、`Decision Log`、`Outcomes & Retrospective`，并包含完整 ExecPlan 的接口、恢复和证据章节。
- 在仓库根目录运行 `git diff --check`：通过。

## ProductFact 收口

本仓库没有启用 project-docs-manager 管理的 ProductFact。稳定规则写入 skill 自身的 `SKILL.md`、references 和 assets；交付说明写入根目录 Changelog。

## 结果与回顾（Outcomes & Retrospective）

已完成 Plan 分层、活文档合同、生成模板、依据 Plan 开发的持续维护规则、contract v3、manifest 路径检查和 `1.2.0` 版本文档。新项目可以直接得到完整的 Plan 执行入口；旧项目可以按 v3 迁移说明增量补齐，不会批量改写历史 Plan。

本次没有提交、打 tag、发布或迁移外部仓库。后续发布时仍需按仓库流程提交，并在发布前再次运行 `python3 scripts/validate.py`。
