# Obsidian Pilot - 代码隔离方案

## 目录结构

```
obsidian-pilot/                  # 开源核心（GitHub 公开）
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   ├── __init__.py              # 版本号、作者信息
│   ├── __main__.py
│   ├── main.py                  # CLI 入口
│   ├── init.py                  # LLM-Wiki 建库
│   ├── note_import.py           # 笔记导入与分类
│   ├── link.py                  # 链接自动化
│   ├── route.py                 # AI 路由
│   ├── maintain.py              # 日常维护
│   └── wizard.py                # 交互式向导
├── tests/
├── .github/
└── docs/                        # 开源文档

obsidian-pilot-pro/              # 付费增值（闭源）
├── LICENSE_PRO
├── README.md
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                  # CLI 入口（引用开源核心）
│   ├── templater.py             # Templater 模板批量生成
│   ├── sync.py                  # 定时后台自动同步
│   ├── repair.py                # 断链修复、图谱完整性校验
│   ├── conflict.py              # 冲突检测模块
│   ├── skill_pack.py            # Hermes 专用 Skill 配套包
│   └── export.py                # 批量导出知识库归档
└── tests/

obsidian-pilot-enterprise/       # 企业版（闭源）
├── LICENSE_ENTERPRISE
├── src/
│   ├── team.py                  # 团队协作
│   ├── sso.py                   # SSO 集成
│   ├── audit.py                 # 审计日志
│   ├── api.py                   # REST API
│   └── branding.py              # 品牌定制
└── tests/
```

## 代码隔离原则

### 1. 依赖关系（单向）
```
开源核心 ← 付费增值 ← 企业版
```
- 开源核心不引用任何付费模块
- 付费增值通过 `import` 引用开源核心
- 企业版引用开源核心和付费增值

### 2. 许可证声明
每个仓库根目录必须包含 LICENSE 文件，开头保留版权声明：

```
MIT License

Copyright (c) 2026 NingXiaoBan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

### 3. 版本号管理
```python
# src/__init__.py (开源核心)
__version__ = "0.1.0"
__author__ = "NingXiaoBan"
__email__ = "18607570527tong@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026 NingXiaoBan"
```

### 4. 导入示例

**开源核心（不被修改）：**
```python
# src/main.py
"""Obsidian Pilot - LLM-Wiki ↔ Obsidian Bridge"""
__version__ = "0.1.0"
# ... MIT License header preserved
```

**付费增值（引用开源核心）：**
```python
# obsidian-pilot-pro/src/main.py
"""Obsidian Pilot Pro - Enhanced Features"""
import obsidian_pilot  # 从开源核心导入
from obsidian_pilot.init import create_folder_structure
from obsidian_pilot.note_import import scan_notes

# 付费功能在此实现
def batch_templater(vault_path):
    """批量生成 Templater 模板"""
    pass
```

## 分发策略

### 开源核心分发
- 仓库：`github.com/yourusername/obsidian-pilot`
- 协议：MIT
- 安装：`pip install obsidian-pilot`
- 内容：基础建库、导入、链接、路由、维护

### 付费增值分发
- 仓库：私有仓库（不公开）
- 协议：商业许可
- 安装：`pip install obsidian-pilot-pro`（需许可证密钥）
- 内容：Templater、同步、修复、冲突检测、Skill 包

### 企业版分发
- 仓库：私有仓库
- 协议：企业商业授权
- 安装：定制化部署
- 内容：团队、SSO、审计、API、品牌定制

## 许可证密钥机制

```python
# src/license_check.py (仅在付费模块)
import hashlib
import hmac

def verify_license(key, product_id="pro"):
    """验证许可证密钥"""
    # 从服务器验证或本地签名验证
    pass
```

## 注意事项

1. **不要混用代码：** 开源核心和付费模块必须在不同仓库/文件夹
2. **不要修改开源代码添加付费逻辑：** 只能通过 import 扩展
3. **README 清晰说明：** 区分开源核心和付费增值
4. **避免 MIT 协议纠纷：** 付费部分是独立项目，不是修改开源代码
5. **文档分离：** 开源文档和付费文档分开维护
