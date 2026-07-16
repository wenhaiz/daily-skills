# {{PROJECT_NAME}} 文档导航

项目知识分为 Ideas、Plans、ProductFact 和 Changelog 四类。

## 入口

- [Ideas](2-Ideas/README.md)：尚未进入开发的想法。
- [Plans](1-Plans/README.md)：开发计划、进度、验证和收口记录。
- [ProductFact](0-ProductFact/README.md)：稳定意图、当前行为和代码证据。
- [Changelog](3-Changelog/README.md)：精简的交付历史。

## 流转

1. 想法确定开发后，建立 Plan。
2. 开发期间持续更新同一份 Plan。
3. 完成后根据最终代码更新 ProductFact 和证据。
4. 有意义的交付写入 Changelog。
5. ProductFact 完成核验后，Plan 才能标记为 completed。
6. 将 completed Plan 移到 `1-Plans/archived/`，并更新仓库内引用。
