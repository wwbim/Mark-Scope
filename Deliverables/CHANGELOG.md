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

> ⏱️ **项目累计总工时 / Total Active Development Time**: **4 小时 45 分钟 (4.75 Hours)**  
> 📅 **自然时间跨度 / Total Calendar Span**: **2026-10-11 16:18 至 2026-10-13 00:30**  
> 🔢 **累计交互与执行步骤 / Total Engineering Steps**: **198 Steps** (模式下沉浮动居中工具栏、全窗口物理居中文档名、880px对称沉浸阅读模式、大纲横条8px光晕微胶囊与严格右对齐)  
> 🔄 **更新机制 / Update Policy**: 每次版本构建打包发布时基于真实日志更新记录。

### 阶段与每日工时分解 / Daily Breakdown
| 日期 / Date | 活跃开发时段 / Active Sprints | 有效工时 / Active Hours | 核心迭代内容 / Milestones |
| :--- | :--- | :---: | :--- |
| **2026-10-11** | 16:18~18:15 | 2h 45m (2.75h) | 项目立项、离线静态资源提取、离线单文件构建管线搭建、大纲导航、状态栏、防崩溃草稿系统与首发交付 / Project kickoff, offline asset bundling, build pipeline, ToC outline, HUD statusbar, crash draft recovery & initial release |
| **2026-10-11** | 18:15~18:55 | 0h 40m (0.67h) | 全宽正文模式、智能表格各行列高自适应平衡算法、表头分割线手动拖拽调宽与单表突破全宽排版引擎 / Full-width mode, intelligent table row-balancing, interactive column resizer & table breakout engine |
| **2026-10-12** | 22:25~22:48 | 0h 23m (0.38h) | PWA 渐进式 Web 应用一键安装套件、Service Worker 极速离线守护、高分辨率矢量图标套件与系统级 `.md` 桌面文件关联协议 / PWA standalone installation suite, Service Worker offline caching, app icons & File Handling API |
| **2026-10-12** | 23:00~23:30 | 0h 30m (0.50h) | 右侧极简悬浮大纲与统计面板重构：最高级标题动态横线指示条、6级标题滑动过滤控杆、双标签页与 Pin 常驻模式 / Right-hand floating outline & stats suite: top-level heading dash minimap, 6-level slider filter, dual tabs & Pin mode |
| **2026-10-12~13** | 23:45~00:05 | 0h 22m (0.37h) | 双级大纲微缩横线、H3默认深度展开、去除顶部冗余按钮、页面滚动实时动态单点聚焦与编辑区深度聚焦暗黑背景 / 2-level minimap dashes, default H3 depth, top button cleanup, real-time scroll sync & deep focus darkening |
| **2026-10-13** | 00:10~00:30 | 0h 20m (0.33h) | 模式下沉浮动居中工具栏、全窗口物理居中文档名、880px对称沉浸阅读模式、大纲横条8px光晕微胶囊与严格右对齐 / Floating centered capsule toolbar, window-centered title, 880px symmetric reader mode, outline blur capsule & flush right alignment |

---

## [v1.2610130030] - 2026-10-13 00:30

### 🎨 浮动居中胶囊工具栏、物理窗口居中文件名、880px 对称阅读模式与大纲微质感光晕 / Floating Capsule Toolbar, Window Centered Title, 880px Reader Mode & Outline Glow Capsule

- **模式切换下沉与正文居中浮动工具栏 (Floating Centered Capsule Toolbar)**
  - **中文**:
    1. **模式切换集成至浮动工具栏**: 将原顶部导航栏中央的“即时渲染 / 所见即所得 / 分屏对照”模式按钮移至工具栏内部最左侧，后接一条精致的垂直细分割线，再排列常规 Markdown 格式工具。
    2. **居中文本版心的吸顶浮动岛**: 工具栏彻底告别窗口通栏拉伸，改为宽度随内容自适应且严格与正文版心居中对齐的浮动胶囊药丸（`max-width: 880px; margin: 10px auto;`），带有 10px 圆角、微立体投影与毛玻璃虚化（`backdrop-filter: blur(12px)`），吸顶固定。

- **文件名全窗口物理绝对居中 (Window-Centered File Title)**
  - **中文**:
    1. **彻底解耦左右按钮数量**: 使用绝对定位 `position: absolute; left: 50%; transform: translate(-50%, -50%)`，使文件名标签严格锁定在整个浏览器窗口正中央，不受左侧文件存盘按钮或右侧主题按钮增减变动的任何牵引。
    2. **自适应优雅省略**: 设定 `max-width: 40vw` 与文本溢出省略号，鼠标悬停即刻显示完整文件名原生 Tooltip，在小屏幕或长文件名下绝不与两侧按钮挤压重叠。

- **阅读模式彻底修复与 880px 严格对称居中 (880px Symmetric Reader Mode)**
  - **中文**:
    1. **黄金阅读版心重构**: 根除之前因 Vditor 内部不对称内边距引发的整体偏右与严重狭窄 Bug。阅读模式下重构为 **880px 舒适黄金阅读版心**，左右外边距严格对称自动均分，配备呼吸感内边距（`padding: 48px 32px 120px 32px`）。
    2. **双重导航保留**: 隐藏顶部操作栏、底部状态栏与编辑工具栏，但保留右侧极简大纲微缩横线组件，供纯净阅读过程中秒级感知章节与定位跳转。

- **大纲收起横条微胶囊背景与 8px 边缘模糊融合 (Outline Dashes Glow Capsule)**
  - **中文**:
    1. **自适应微胶囊毛玻璃背景**: 右侧横条收起容器 `.ms-outline-dashes` 赋予大纲面板同款背景色（深色模式 `rgba(24, 24, 27, 0.92)`），呈现随条目数量自适应高度的垂直微型圆角胶囊容器。
    2. **8px 柔和向外模糊融合**: 通过 `box-shadow: 0 0 16px 8px ...` 与 `backdrop-filter: blur(8px)`，使横条背景边缘平滑虚化过渡融入文本区深邃背景。

- **大纲横条全部严格靠右对齐 (Flush Right-Aligned Dashes)**
  - **中文**:
    1. **端点平齐对齐**: 所有横条（一级 22px / 二级 13px）右端边缘统一设为 `margin-right: 0` 严格向右看齐对齐，完全由横线自身长短差异呈现结构层级，视觉上整齐洗练。

---

## [v1.2610130005] - 2026-10-13 00:05

### 🎯 悬浮大纲双级微缩横线、H3默认深度展开与沉浸编辑背景 / 2-Level Minimap, H3 Depth & Deep Focus Immersion

- **收起状态双级大纲横线 (Two-Level Collapsed Dashes Minimap)**
  - **中文**:
    1. **文内前两级标题差异化微缩呈现**: 收起态由仅呈现最高级单级横线升级为动态提取文内最高 2 级标题。最高级标题展示为 22px 满长横线（右对齐），次级标题展示为 13px 较短横线并缩进 7px，形成视觉层次分明、紧凑优雅的微型文档地图（Minimap）。
    2. **单点聚焦实时滚动跟踪 (Real-time Scroll Tracking)**: 监听编辑器即时渲染容器、滚动视口以及窗口的实时滚动事件，取消延迟节流，确保当前视口所在标题对应的横线毫秒级保持单点纯白高亮（其余平滑淡化为暗灰），滚动至任意二级章节即可实时随动高亮切换。

- **大纲面板展开体验精进 (Refined Outline Panel Experience)**
  - **中文**:
    1. **默认层级深度设为 H3**: 展开面板后，6 级滑动控杆默认点亮前 3 颗指示点（H1~H3），大纲列表默认展示至三级标题，既过滤了过度琐碎的底层标记，又保障了充实的信息量。
    2. **顶部标题栏按钮精简**: 彻底移除顶部导航栏中的【大纲】按钮，面板展开与钉选操作完全归属于右侧悬浮组件交互与右上角 📌 Pin 按钮，导航栏更显精炼纯粹。

- **编辑区沉浸聚焦调深 (Deep Editor Focus Immersion)**
  - **中文**:
    1. **输入聚焦背景深度加深**: 当光标或焦点进入 Markdown 编辑区时，编辑区背景平滑过渡调深至 `#050811`（深色模式）/ `#e2e8f0`（浅色模式），将视觉焦点与思考重心牢牢锚定在创作内容本身；失焦时平滑恢复。

---

## [v1.2610122330] - 2026-10-12 23:30

### 🧭 右侧极简悬浮大纲与度量统计套件 / Right-hand Floating Outline & Stats Suite

- **平时极简收起横线指示器 (Collapsed Heading Dash Indicator)**
  - **中文**:
    1. **最高级标题动态映射**: 平时彻底移除左侧占用空间的侧边栏，改为在屏幕右侧居中竖排排列一组极简小横线，精准映射当前文档中最高级的标题列表。
    2. **滚动高亮实时同步**: 当前阅读视口所在的最高级标题以纯白色高亮横线呈现，其余为暗灰色横线，随页面滚动平滑联动切换高亮，点击任意横线即可秒级平滑定位跳转。

- **悬浮展开暗黑圆角面板 (Expanded Floating Panel & Dual Tabs)**
  - **中文**:
    1. **悬停智能展开与 Pin 钉选**: 鼠标移至右侧横线即平滑展开精致微质感暗黑浮动面板；右上角配备 📌 Pin 按钮，点击即可常驻锁定显现，Unpin 时移开鼠标自动淡出收起；顶部工具栏【大纲】按钮同步作为全局 Pin 快捷键。
    2. **大纲页 - 6 级层级滑动控杆 (6-Level Heading Slider)**: 大纲列表上方配备带 6 个圆点的调节横轨（H1~H6），点击任意圆点横轨从左至右发光高亮至该圆点，大纲列表即时动态筛选仅展示至该层级，兼顾宏观把握与微观检索。
    3. **统计页 - 仿大纲行式实时度量 (Stats Tab Metrics)**: 仿照大纲优雅行式排版，实时展示字数、句数、段数、字符数与采用本地系统格式的最后保存时间戳。
    4. **底部状态栏精简**: 移除底部冗余字数与阅读耗时，保留存盘状态与渲染模式指示，全面提升垂直阅读视野。

---

## [v1.2610122248] - 2026-10-12 22:48

### 📱 PWA 渐进式 Web 应用安装套件与桌面文件关联 / PWA Standalone Suite & Desktop File Association

- **标准 PWA 浏览器一键安装支持 (Standard PWA Installation)**
  - **中文**:
    1. **原生应用窗口运行**: 补充标准 `manifest.json` 与全套尺寸图标（192x192、512x512 PNG 以及无损 SVG 矢量图标），支持在 Chrome / Edge / 移动端浏览器一键点击地址栏【安装应用】图标，脱离浏览器标签页化身为原生独立桌面应用。
    2. **Service Worker 零丢包极速离线守护**: 针对单文件架构定制 `sw.js` 缓存策略，首次访问即自动缓存单文件核心壳体，即使网络彻底中断，也能以本地桌面级速度秒级启动。
    3. **双重兼容保障**: 在本地双击 `file:///` 启动时，代码自动静默绕过 Service Worker，保持 100% 纯本地离线单文件运行零报错。

- **系统级 `.md` 文件关联协议 (File Handling API)**
  - **中文**:
    1. **桌面双击直接唤起**: 声明 `file_handlers` 规范并集成 `window.launchQueue`；当安装为 PWA 后，可在 Windows / macOS 系统中将 Mark Scope 设为 Markdown 文件的默认打开方式。
    2. **文件句柄原生衔接**: 双击桌面 `.md` 文件直接唤起 Mark Scope 独立窗口并加载内容，且自动绑定底层文件句柄，编辑后按 `Ctrl+S` 直接静默覆盖写回本地文件。

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
