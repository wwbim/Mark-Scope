# 🚀 Mark Scope - AI 开发助手立项与技术接力指南 / AI Engineering Blueprint

> 📌 **致后续接力的 AI 助手 (Dear Incoming AI Assistant)**：  
> 当用户在新的对话中启动 **Mark Scope** 的开发时，**请首先通读本文档**。本文档记录了与用户深度对齐（通过 `/grill-me` 讨论确定）的核心技术决策、业务定位、架构选型与离线单文件实现路径。

---

## 🎯 一、 项目核心定位与设计哲学 / Core Vision & Philosophy

- **项目名称**：**Mark Scope**（产物：`MarkScope.html`）
- **核心定位**：**纯客户端、100% 离线、单文件自包含（Zero-Server, 100% Offline Standalone Single HTML）的所见即所得 Markdown 编辑与阅读器**。
- **与 BIM Scope 的血统传承**：
  1. **零服务端依赖 (Zero-Server)**：双击本地单个 `MarkScope.html` 文件即可在任意现代浏览器运行，无需 Node.js、无需 Python 本地服务、无需后端。
  2. **100% 本地隐私安全**：所有文档读写与编辑 100% 在客户端内存中完成，无任何网络上传，保障文档隐私。
  3. **单文件即全功能**：无需解压文件夹，无需携带外部静态资源包，一个 HTML 随身携带。

---

## 🧩 二、 核心技术选型与业务需求 / Technology & Requirements

### 1. 技术底座
- **选型**：开源项目 **[Vditor](https://github.com/vanessa219/vditor)**（MIT License）。
- **用户明确要求**：**WYSIWYG 完全版编辑器**。
- **核心模式**：
  * **所见即所得 (WYSIWYG)**：富文本式流畅排版。
  * **即时渲染 (IR / Instant Rendering)**：Typora 风格，输入 Markdown 标记后即刻就地排版。
  * **分屏预览 (SV / Split View)**：左侧编辑、右侧实时渲染。
  * **纯净阅读模式 (Reader Mode)**：一键隐藏工具栏与编辑框，仅呈现精美排版的文章阅读视图。

### 2. 本地单文件文件交互 (File I/O)
- **打开文件**：
  * 支持拖拽本地 `.md` 文件直接进入窗口打开解析。
  * 工具栏提供【打开模型/文档】按钮（通过 `<input type="file" accept=".md,.markdown,.txt">` 或 File System Access API）。
- **保存与导出**：
  * 支持快捷键 `Ctrl+S` / `Cmd+S` 快速保存/下载 `.md` 文件（通过 Blob URL 触发安全下载并保持原文件名）。
  * 支持【另存为 .md】。
  * 支持【导出为独立 HTML】（包含样式的离线网页报告）。
  * 支持【导出为 PDF】（调用浏览器原生打印窗口，内嵌 `@media print` 排版优化）。
- **防丢失机制**：
  * 基于 `localStorage` 或 `IndexedDB` 实时保存编辑草稿，意外刷新或关闭浏览器后可一键恢复。

### 3. UI 界面风格与工程质感
- **主题风格**：
  * 现代暗黑工程主题 (Dark Engineering Theme) 与 经典纯白阅读主题 (Light Theme) 一键切换。
  * 工具栏按钮风格对齐 BIM Scope：圆润稳健的 `6px` 圆角，半透明磨砂毛玻璃底色。
- **侧边栏与辅助视窗**：
  * **文档大纲 (Outline / ToC)**：实时解析标题层级，支持侧边树状折叠与点击平滑定位跳转。
  * **底部状态栏 (Footer Status HUD)**：实时统计字符数、词数、行数、阅读耗时预估、当前模式标识。

---

## ⚡ 三、 核心技术难点与攻坚方案：Vditor 离线单文件化 / Offline Bundling

这是本项目的**技术核心与关键挑战**，接力 AI 必须重点攻克：

### 1. 痛点：Vditor 的网络动态加载机制
Vditor 的核心库虽然打包为 `dist/index.min.js`，但其内部架构是**动态按需加载**的。在运行时，它会通过 `options.cdn`（默认指向 `https://unpkg.com/vditor@...`）向外拉取大量外部资源：
1. `dist/js/lute/lute.min.js`：这是 Vditor 运行所必须的 **Markdown 解析核心引擎**（由 Go 语言编译为 JS/Wasm，体积约 1.8MB）。若无法加载 `lute.min.js`，Vditor 会直接抛出异常白屏。
2. `dist/js/highlight.js/`：代码块语法高亮引擎及语言包。
3. `dist/js/katex/`：数学公式渲染引擎与字体。
4. `dist/js/icons/ant.js`：SVG 图标集。
5. `dist/index.css`：核心样式表及代码高亮主题。

在**断网离线**或**本地 `file://` 双击打开**时，由于无互联网或被浏览器 `file://` 同源安全策略阻止，这些外部请求会导致 Vditor 初始化失败。

### 2. 攻坚方案：单文件内联与资源虚拟化管线
我们必须设计一个自动化打包构建管线（类似 BIM Scope 的 `build_viewer.py`）：

1. **资源下载与本地归档**：
   - 提取 Vditor release 的离线资产（`index.min.js`、`lute.min.js`、`index.css`、`icons/ant.js` 等）。
2. **提前全局挂载核心依赖**：
   - 在主 HTML 中，**先于 Vditor 加载并执行 `lute.min.js`**，使其全局对象 `window.Lute` 提前初始化就绪。
   - 拦截或预先注入 Vditor 的依赖检查逻辑，检测到 `window.Lute` 已存在时跳过网络请求。
3. **CDN 虚拟化拦截**：
   - 将 Vditor 初始化参数中的 `cdn` 配置指向内联数据，或者重写/Mock 内部的资源加载器（例如利用 `Blob(..., {type: 'application/javascript'})` 创建内存 `URL.createObjectURL(blob)` 虚拟 URL 提供给 Vditor）。
4. **CSS 与图标内联**：
   - 将 `index.css`、主题样式、SVG 图标以 `<style>` 和内联 JavaScript 方式嵌入单个 HTML 中。
5. **Python 构建管线 (`build_mark_scope.py`)**：
   - 自动化读取源码、依赖库、预设模板，一键生成 `Deliverables/MarkScope.html`。

---

## 📂 四、 推荐工程架构目录规划 / Directory Layout

```
H:\我的云端硬盘\Software Develop\Mark Scope\
├── Project/                        # 源码工程与构建管线
│   ├── src/                        # 业务逻辑与外壳控制器
│   │   ├── app.js                  # 入口调度、Vditor 实例化与事件总线
│   │   ├── file_io.js              # 文件拖拽、打开、另存为、导出 HTML/PDF
│   │   ├── outline.js              # 侧边栏文档大纲 ToC 导航与跳转
│   │   ├── statusbar.js            # 底栏字数/行数统计与模式指示器
│   │   ├── theme.js                # 深浅色主题与阅读模式切换
│   │   └── styles.css              # 外壳容器、工具栏与自定义样式
│   ├── libs/                       # 本地第三方库资源
│   │   ├── vditor/                 # Vditor 完整提取的离线包
│   │   │   ├── index.min.js
│   │   │   ├── index.css
│   │   │   ├── lute.min.js
│   │   │   └── icons/
│   ├── build_mark_scope.py         # 单文件编译器（注入资源生成单 HTML）
│   ├── README.md                   # 本地项目开发指南
│   └── AI_INSTRUCTIONS.md          # 本交接指南
└── Deliverables/                   # 最终交付产物
    ├── MarkScope.html              # 100% 离线自包含单文件应用（用户直接双击使用）
    └── index.html                  # 镜像入口（便于 Web/Pages 部署）
```

---

## 🛠️ 五、 接力开发者的起步行动清单 / Action Checklist for Incoming AI

当用户在新对话中说“开始创建 Mark Scope”时，请按以下步骤执行：

1. **环境准备与依赖获取**：
   - 检查 `Project/libs/vditor`，通过脚本从官方 release 下载或提取完整的 Vditor 离线资产（包括 `index.min.js`、`lute.min.js`、`index.css`、`ant.js` 图标等）。
2. **离线单文件可行性最小原型验证 (PoC)**：
   - 先构建一个最小的单文件 HTML，验证在无网络连接且 `file://` 协议下，预加载 `window.Lute` 能否让 Vditor 成功渲染所见即所得编辑器。
3. **编写外壳框架与文件 I/O 模块**：
   - 开发顶部工具栏（打开、保存、另存为、导出、阅读模式、深浅色）。
   - 实现全局拖拽 `.md` 打开文件、`Ctrl+S` 保存。
   - 实现侧栏大纲与底栏统计。
4. **编写自动化打包脚本 `build_mark_scope.py`**：
   - 将 HTML、CSS、JS、Vditor 资源合并内联，输出到 `Deliverables/MarkScope.html`。
5. **全面测试与交付**：
   - 测试断网离线双击打开、大文件编辑流畅度、公式/图表/表格渲染、导出与保存功能。

---

*档案创建时间：2026-10-09 | 关联工程：BIM Scope / SWBIM Scope 姊妹篇*
