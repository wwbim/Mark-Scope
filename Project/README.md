# 📝 Mark Scope

> **100% 离线单文件 Markdown 所见即所得编辑器与阅读器**  
> **Pure Client-Side, 100% Offline Standalone Single-File Markdown WYSIWYG Editor & Reader**

---

## 📖 项目简介 / Introduction

**Mark Scope** 是与 **BIM Scope** 秉承相同技术哲学的姊妹工程——专注于打造一个**零服务端依赖 (Zero-Server)、100% 纯客户端、单文件自包含 (Standalone Single HTML)** 的现代化 Markdown 编辑与阅读环境。

双击单个 `MarkScope.html` 文件，即可在任意现代浏览器中离线启动运行，不发起任何外部网络请求，保障极致的工程文档隐私与便携性。

- **技术底座**：基于开源强大的 **[Vditor](https://github.com/vanessa219/vditor)**（MIT License）。
- **核心定位**：所见即所得 (WYSIWYG) 完全版编辑器 + 沉浸式即时渲染 (Typora 风格) + 纯净阅读视图。
- **目标产物**：`Deliverables/MarkScope.html`（独立单文件，无需任何外置文件夹）。

---

## 🌟 核心特性规划 / Key Features

1. **三模编辑 + 沉浸阅读**：
   - **所见即所得 (WYSIWYG)**：富文本般平滑直观。
   - **即时渲染 (Instant Rendering)**：Typora 式行内实时排版，输入 `#` 即变标题。
   - **分屏预览 (Split View)**：传统双栏对照编辑。
   - **纯净阅读模式 (Reader Mode)**：一键隐去全部编辑工具栏，极简优雅阅读文档。
2. **离线文件交互 (File I/O)**：
   - 拖拽本地 `.md` 文件直接打开解析。
   - 顶部工具栏支持【打开本地文件】与【保存 / 另存为 .md】（支持 `Ctrl+S` 快捷键保存）。
   - 【导出为独立 HTML】与【导出为 PDF】（打印排版优化）。
   - 本地 `localStorage` 编辑草稿自动防丢失保存。
3. **专业级视觉与工程交互**：
   - 现代暗黑工程主题 (Dark Theme) 与 明亮阅读主题 (Light Theme) 一键切换。
   - 可折叠侧边文档大纲树 (Outline ToC)。
   - 底部状态栏实时呈现字符数、单词数、行数与阅读耗时预估。

---

## 🤖 AI 开发助手接力指引 / For AI Assistant Relay

如果您是正在接手此项目开发的 AI 助手，请直接查阅：
👉 **[`Project/AI_INSTRUCTIONS.md`](./Project/AI_INSTRUCTIONS.md)**

该文档记录了完整的技术方案、Vditor 动态依赖离线单文件化的攻坚策略、构建管线设计与起步任务清单。

---

## 📂 目录结构 / Directory Structure

```
Mark Scope/
├── Project/                 # 源码与单文件打包编译工程
│   ├── src/                 # 外壳 UI、文件交互与控制器
│   ├── libs/                # Vditor 核心离线依赖包
│   ├── build_mark_scope.py  # 单文件生成管线
│   ├── README.md            # 工程说明
│   └── AI_INSTRUCTIONS.md   # AI 开发接力详尽指示档案
└── Deliverables/            # 最终发布目录
    ├── MarkScope.html       # 100% 离线自包含单文件（用户直接使用）
    └── index.html           # 镜像入口
```
