# Changelog

## project-docs-manager 1.1.0 - 2026-07-16

- 新增 Plan 归档契约：明确完成的 Plan 移到 `<plans>/archived/`。
- 初始化时创建归档目录入口，并在 manifest 中单独记录归档路径。
- 增加 v2 迁移说明，要求归档后同步更新仓库内引用。

## project-docs-manager 1.0.0 - 2026-07-16

- 建立 Ideas、Plans、ProductFact、Changelog 文档生命周期。
- 支持现有文档审计、安全初始化和契约版本迁移。
- 提供通用文档模板和 ProductFact freshness 检查。
