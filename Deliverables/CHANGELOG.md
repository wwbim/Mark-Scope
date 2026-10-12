# 变更记录 / Changelog

本文档记录 Mark Scope 从项目创建至今的所有正式版本演进与主要改动记录。  
This document records all formal version iterations and major changes of Mark Scope since project initiation.

> **版本号命名规则 / Versioning Convention**:  
> - 主版本号固定为 `v1`（日常对外显示简写为 `v1`）；
> - 完整细版本号格式为 `v1.<YYMMDDHHMM>`，小数点后 10 位数字精确对应具体发布的年月日时分。  
> - Major version is fixed at `v1` (displayed as `v1` in everyday usage);  
> - Full sub-version follows `v1.<YYMMDDHHMM>`, where the 10-digit timestamp represents Year, Month, Day, Hour, Minute.

---

## 项目开发耗时统计 / Development Time Metrics

> ⏱️ **项目累计总工时 / Total Active Development Time**: **3 小时 10 分钟 (3.17 Hours)**  
> 📅 **自然时间跨度 / Total Calendar Span**: **2026-10-11 16:18 至 2026-10-11 18:55**  
> 🔢 **累计交互与执行步骤 / Total Engineering Steps**: **138 Steps** (初始立项至首发交付与排版精修 Sprint)  
> 🔄 **更新机制 / Update Policy**: 每次版本构建打包发布时基于真实日志更新记录。

### 阶段与每日工时分解 / Daily Breakdown
| 日期 / Date | 活跃开发时段 / Active Sprints | 有效工时 / Active Hours | 核心迭代内容 / Milestones |
| :--- | :--- | :---: | :--- |
| **2026-10-11** | 16:18~18:15 | 2h 45m (2.75h) | 项目立项、离线静态资源提取、离线单文件构建管线搭建、大纲导航、状态栏、防崩溃草稿系统与首发交付 / Project kickoff, offline asset bundling, build pipeline, ToC outline, HUD statusbar, crash draft recovery & initial release |
| **2026-10-11** | 18:15~18:55 | 0h 40m (0.67h) | 全宽正文模式、智能表格各行列高自适应平衡算法、表头分割线手动拖拽调宽与单表突破全宽排版引擎 / Full-width mode, intelligent table row-balancing, interactive column resizer & table breakout engine |

---

## [v1.2610111855] - 2026-10-11 18:55

### 📏 全宽正文模式与智能表格平衡排版重构 / Full-Width Viewport & Intelligent Table Engineering Suite

- **表格渲染引擎与智能平衡修复 (Table Rendering & Adaptive Auto-Balance)**
  - **中文**:
    1. **消除横向滚动条与强制折行**: 修复了样式继承中的 `white-space: nowrap` 冲突，强制表格采用 `table-layout: fixed` 与 `white-space: normal`，彻底消除了表格向右伸出上千像素产生横向滚动条的问题。
    2. **文本体量加权自动平衡**: 自动分析各列文字长度分布，为短文本列分配紧凑宽度、为长文本列分配主导宽度（如 CHANGELOG 历史记录表的 4 列自动平衡为 13%、12%、14%、61%），使各行高度均匀齐平。
    3. **表头分割线交互拖拽 (Interactive Resizer)**: 修复拖拽手柄高度解析，光标移至表头右边框即可出现高亮拖拽线，按住鼠标左右拖拽即时调节相邻列宽，双击分割线随时恢复智能平衡宽度。
    4. **单表独立突破全宽 (Table Breakout Pill)**: 悬停表格右上角浮现微型操作胶囊，点击【表格全宽】可在正文居中排版下单独将复杂表格扩展至 100% 视口全宽。

- **全局正文全宽模式 (Full-Width Mode)**
  - **中文**:
    1. **顶部一键全宽切换**: 顶部工具栏【📏 全宽 / 适应版心】按钮，一键消除正文 880px 居中版心限制，使正文与代码块占满可用视口宽度（排除左侧大纲），最大化利用宽屏显示器的工作空间。
    2. **响应式自适应保留**: 切换模式时自动保留舒适的内边距，大纲展开/折叠时编辑工作区平滑响应适配。

- **MD 表格智能自适应与各行列高平衡算法 (Balanced Column Layout Engine)**
  - **中文**:
    1. **文本体量加权平衡**: 表格不再生硬撑向右侧无尽远处，而是依据各列单元格的字数体量（均值与峰值联合加权公式 $W_i = \text{avg}^{0.65} \times 2.2 + \text{max}^{0.35} + 8$）自动计算最佳百分比列宽。
    2. **行高均衡消灭极端折行**: 彻底消除“短文本列过宽、长文本列被挤压折成六七行”的传统 HTML/Markdown 表格痛点，实现各列行数尽可能平齐对称；对字符数极少的小微表格智能保留紧凑自适应。

- **交互式手动调节表格栏宽 (Interactive Column Resizer)**
  - **中文**:
    1. **表头分割线实时拖拽**: 光标移动至表头分割线自动变更为 `↔` 调整指示，按住鼠标左右拖动可实时自由调节相邻列宽。
    2. **双击一键重置**: 双击分割线或点击工具栏按钮，可随时重置回算法计算的最佳平衡列宽。
    3. **保持 Markdown 源码纯粹**: 手动列宽仅在前端渲染层生效，不向 `.md` 源码中插入任何 `<th style="...">` 等破坏性 HTML 脏代码。

- **单表独立突破版心全宽 (Table-Only Breakout)**
  - **中文**:
    1. **悬停微型操作胶囊**: 鼠标悬停在任意表格上方时，右上角浮现微型操作工具栏，提供【⛶ 表格全宽 / ⊡ 适应正文】与【⚖️ 智能平衡】快捷胶囊。
    2. **局部版心突破**: 支持在正文保持舒适居中阅读宽度时，允许复杂多列大表格单独“突破版心”向两侧撑满整个视口，极大提升复杂工程数据表格的查阅体验。

---

## [v1.2610111815] - 2026-10-11 18:15

### 📝 Mark Scope 首发立项与 100% 离线单文件生产交付 / Mark Scope Initial Release & 100% Standalone Offline Pipeline

- **纯客户端单文件架构与 Vditor 离线深度内联 / Zero-Server Standalone Architecture & Offline Bundling**
  - **中文**:
    1. **零服务端依赖与单文件交付**: 秉承与 BIM Scope 一脉相承的工程哲学，整个 Markdown 编辑器与阅读器完全自包含于单个 `MarkScope.html` 文件中（约 9.0MB），无需 Node.js、无需 Python 本地服务，支持离线或 `file:///` 本地协议直接双击启动，不发起任何外网 CDN 网络请求。
    2. **核心解析与扩展引擎全内联**: 提取并内联 Vditor 核心、Lute AST Markdown 解析引擎、Mermaid 矢量流程图引擎、KaTeX 现代数学排版引擎（内嵌 20 组 WOFF2 字体 Base64 数据，彻底解决离线数学公式字体缺失）、Highlight.js 代码高亮库以及 Ant 矢量图标集。
    3. **HTML 脚本安全防截断机制**: 攻克了 `lute.min.js` 中包含字面量 `</script>` 导致浏览器解析器过早闭合标签的经典 Bug，设计了自动化安全转义转置处理（`safe_script`），保障超大 JS 代码在单 HTML 内联环境下的语法完整性。

- **三模编辑与沉浸式阅读模式 / Tri-Mode Editing & Immersive Reader Mode**
  - **中文**:
    1. **三模编辑一键无损切换**: 支持【即时渲染 (IR / Typora 式行内实时排版，默认启动模式)】、【所见即所得 (WYSIWYG / 完全富文本排版)】与【分屏对照 (SV / 经典源码与预览双栏)】。
    2. **沉浸式纯净阅读模式 (Reader Mode)**: 点击顶部【阅读模式】或按下快捷键，自动隐藏所有编辑工具栏、侧边栏及状态栏，排版自适应居中优化，文章只读保护，右下角提供半透明悬浮退出胶囊，支持按下 `Esc` 键一键退出。

- **本地文件读写、防丢快照与崩溃恢复 / Local File I/O, Snapshots & Crash Recovery**
  - **中文**:
    1. **现代双轨文件保存机制**: 优先调用浏览器原生 File System Access API 实现 `Ctrl+S` 原地存盘覆写本地 `.md` 文件；在不支持该 API 的环境或旧版浏览器中自动平滑降级为标准 Blob 安全下载；支持【另存为...】。
    2. **无缝拖拽打开**: 支持全局拖拽本地 `.md` / `.txt` 文档进入窗口，即时解析加载。
    3. **独立 HTML 与 PDF 导出**: 工具栏支持一键【导出为独立 HTML】（内嵌自适应样式，可直接用于离线分享传阅）以及【导出为 PDF】（内嵌 `@media print` 打印排版优化）。
    4. **双重防丢与崩溃智能恢复**: 每 300ms 自动向本地存储同步草稿快照；绑定 `beforeunload` 误触关闭拦截；启动时若检测到意外退出或崩溃遗留的未存盘草稿，顶部展示友好恢复横幅，支持一键无损恢复。
    5. **全局拖拽事件捕获与防吞没修复**: 将拖放事件侦听器升级为 DOM Capture 捕获阶段优先处理，并将拖拽悬浮层统一设为单块响应表面，彻底解决 Vditor 编辑容器内部原生 drop 事件拦截冒泡导致文件被卡在“释放鼠标即可...”遮罩层的缺陷。

- **专业工程视觉与交互辅助 / Professional Engineering UI & HUD**
  - **中文**:
    1. **BIM Scope 质感工程主题**: 默认采用高级暗黑工程主题（Dark Engineering），提供明亮主题（Light Paper）一键切换；顶部操作按钮采用稳健经典的 6px 圆角（Tab-matched 6px rounded geometry），主操作按钮具备发光边框提示。
    2. **侧边文档大纲树 (ToC)**: 左侧独立侧边栏实时解析 Markdown H1~H6 标题层级，支持树状缩进、一键原地折叠收缩、点击平滑滚动跳转与瞬时高光反馈。
    3. **底部状态栏 (HUD)**: 实时精确统计文档字符数、词数（支持中西文混合智能分词）、行数、预计阅读耗时、当前编辑模式及文件存盘状态指示器。
