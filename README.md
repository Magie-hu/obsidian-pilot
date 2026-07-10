# Obsidian Pilot Plugin

> Your First Obsidian Assistant - 一个简洁易用的 Obsidian 插件，配合后端 API 使用。

## 安装

### 前提条件

1. 安装 [Obsidian](https://obsidian.md)
2. 启动 API 后端服务：
   ```bash
   cd obsidian-pilot-api
   ./venv/bin/python -m uvicorn obsidian_pilot_api.main:app
   ```

### 安装插件

1. 从 [GitHub Releases](https://github.com/Magie-hu/obsidian-pilot/releases) 下载最新版本的 zip 文件
2. 在 Obsidian 中：设置 → 第三方插件 → 加载离线插件 → 选择解压后的文件夹
3. 启用插件

### 手动编译安装

如果你有 TypeScript 环境：
```bash
cd obsidian-llm-wiki-plugin
npm install
node build.js
# 将 dist/ 文件夹复制到 Obsidian 的 .obsidian/plugins/obsidian-pilot/
```

## 功能

| 功能 | 说明 |
|------|------|
| 📁 初始化知识库 | 一键创建 LLM-Wiki 标准目录结构 |
| 📥 导入分类 | 扫描所有笔记并按内容分类 |
| 🔗 自动链接 | 分析笔记间的链接关系，发现孤立笔记 |
| 🤖 AI 路由 | 根据问题推荐合适的 AI 模型 |
| 🧹 日常维护 | 检查过期笔记、重复标题、孤立链接 |
| 📊 链接报告 | 详细的链接分析报告 |

## 使用流程

1. 打开 Obsidian，选择一个 vault
2. 点击侧边栏的书本图标 📖
3. 弹出面板显示所有功能按钮
4. 点击按钮执行操作，结果在面板底部显示

## 开发

```bash
npm install        # 安装依赖
node build.js      # 编译
node build.js --watch  # 开发模式（监听变化）
```

## 许可证

MIT License - Copyright (c) 2026 NingXiaoBan
