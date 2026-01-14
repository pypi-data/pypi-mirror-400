# Changelog Directory

This directory contains detailed changelog files for different features and versions.

## Current Version: 0.3.1

### Latest Changes

#### [CHANGELOG_CLI_v2.md](./CHANGELOG_CLI_v2.md)
**CLI 脚手架工具 v2 - 架构统一更新**
- 项目结构调整为与 infoman/service 完全一致
- 新增 core, services, middleware, infrastructure 模块
- 优化配置文件和示例代码
- 完善文档和开发指南

#### [CHANGELOG_CLI.md](./CHANGELOG_CLI.md)
**CLI 脚手架工具 v1 - 初始版本**
- 首次发布 `infomancli init` 命令
- 实现项目结构自动生成
- 提供基础配置文件模板

### Previous Versions

#### [CHANGELOG_v0.3.0.md](./CHANGELOG_v0.3.0.md)
**双 ORM 支持**
- 同时支持 Tortoise ORM 和 SQLAlchemy 2.0
- 100% 向前兼容
- 性能提升 20-40%
- 渐进式迁移支持

## Quick Links

- 主 Changelog: [../../CHANGELOG.md](../../CHANGELOG.md)
- 迁移指南: [../MIGRATION_TO_SQLALCHEMY.md](../MIGRATION_TO_SQLALCHEMY.md)
- CLI 使用文档: [../../infoman/cli/README.md](../../infoman/cli/README.md)

## File Naming Convention

- `CHANGELOG_<feature>.md` - Feature-specific changelogs
- `CHANGELOG_v<version>.md` - Version-specific changelogs

## Navigation

```
doc/
├── changelog/           👈 You are here
│   ├── README.md
│   ├── CHANGELOG_CLI_v2.md      # CLI v2 (latest)
│   ├── CHANGELOG_CLI.md         # CLI v1
│   └── CHANGELOG_v0.3.0.md      # ORM support
├── MIGRATION_TO_SQLALCHEMY.md   # Migration guide
└── ...                          # Other documentation
```
