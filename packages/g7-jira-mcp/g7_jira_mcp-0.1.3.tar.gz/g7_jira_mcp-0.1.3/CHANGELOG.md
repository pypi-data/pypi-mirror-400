# Changelog

本文档记录了 g7-jira-mcp 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.3] - 2026-01-09

### 优化
- 扩展字段黑名单，排除更多无用的自定义字段
  - 新增排除: customfield_12816, customfield_12631, customfield_12647, customfield_12450

## [0.1.2] - 2025-01-11

### 修复
- 修复 Playwright 测试错误，提升测试稳定性

### 变更
- 将默认 JIRA 服务器 URL 更改为 `https://issues.chinawayltd.com`
- 优化环境变量加载机制

## [0.1.1] - 2025-01-10

### 新增
- 实现评论管理功能
  - `get_issue_comments`: 获取 JIRA 问题评论
  - `add_comment`: 添加 JIRA 问题评论
  - `format_comment`: 格式化评论数据
- 新增 DevLake 服务集成
  - 根据 JIRA ID 查询 GitLab Merge Request
  - 支持配置 DevLake 服务 URL
- 新增字段黑名单机制
  - 支持排除指定自定义字段（如线上问题分类）

### 优化
- 默认禁用 Playwright 追踪功能，减少不必要的文件生成
  - 可通过环境变量 `JIRA_ENABLE_TRACING=true` 启用调试追踪
- 调整脚本入口点配置
  - `g7-jira-mcp`: 主程序
  - `g7-jira-extract`: 单个附件提取
  - `g7-jira-attachments`: 批量附件下载

### 测试
- 新增评论功能单元测试（27 个测试用例）
- 新增 GitLab MR 查询功能测试
- 新增字段名称映射功能验证脚本

## [0.1.0] - 2025-01-08

### 新增
- 智能附件下载功能
  - 使用 Playwright 自动处理 JIRA 认证问题
  - 支持 REST API 下载失败时自动降级
  - 内容验证机制（HTML 检测、图片格式验证）
- 异步附件管理工具
  - `get_issue_attachments`: 获取并可选下载附件
  - `download_all_attachments`: 批量下载所有附件
  - `get_attachment_by_filename`: 根据文件名获取指定附件
- 自定义字段名称映射功能
  - 支持将自定义字段 ID 映射为可读名称

### 变更
- 项目重命名为 `g7-jira-mcp`
- 附件保存路径调整为项目根目录的 `.jira-mcp/{issue_key}/` 子目录
- Python 版本支持范围：3.10 - 3.12

### 测试
- 新增附件下载模块单元测试（37 个测试用例）
  - HTML 内容检测测试
  - 图片格式验证测试
  - Playwright 下载流程测试
- 测试覆盖率达到 89.47%（attachment_downloader 模块）

### 文档
- 新增 CLAUDE.md 项目指南
  - 项目架构说明
  - 开发命令参考
  - 配置示例
  - 单元测试规范

## [0.0.1] - 2025-01-05

### 新增
- 初始化项目，基于 FastMCP 框架
- 核心 JIRA 操作功能
  - `get_issue`: 获取问题详情
  - `search_issues`: 搜索问题
  - `create_issue`: 创建问题
  - `update_issue`: 更新问题
  - `get_projects`: 获取项目列表
  - `get_project`: 获取项目详情
  - `debug_issue_fields`: 调试问题字段
- 支持多种传输模式（stdio、sse、streamable-http）
- 配置管理模块（支持环境变量和 .env 文件）
- 基础附件管理功能

### 文档
- README.md 项目说明文档
- 配置示例和使用指南

---

## 链接说明

- [0.1.2]: https://github.com/YOUR_USERNAME/g7-jira-mcp/releases/tag/v0.1.2
- [0.1.1]: https://github.com/YOUR_USERNAME/g7-jira-mcp/releases/tag/v0.1.1
- [0.1.0]: https://github.com/YOUR_USERNAME/g7-jira-mcp/releases/tag/v0.1.0
- [0.0.1]: https://github.com/YOUR_USERNAME/g7-jira-mcp/releases/tag/v0.0.1
