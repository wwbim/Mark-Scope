/**
 * Mark Scope - Main Application Coordinator
 * Manages Vditor lifecycle, toolbar actions, theme/mode switching,
 * toast notifications, and keyboard shortcuts.
 */
class MarkScopeApp {
  constructor() {
    this.vditor = null;
    this.currentFileName = '欢迎体验_MarkScope.md';
    this.currentMode = 'ir'; // Default: Instant Rendering (Typora style)
    this.currentTheme = 'dark'; // Default: Dark Engineering theme
    this.isReaderMode = false;
    this.isFullWidth = false;

    // Submodules
    this.draftManager = new DraftManager(this);
    this.fileIO = new FileIO(this);
    this.outline = new OutlineManager(this);
    this.statusbar = new StatusbarManager(this);
    this.tableManager = new TableManager(this);
  }

  async init() {
    console.log('[MarkScope] Initializing application...');
    this.initTheme();
    this.initVditor();
    this.bindHeaderActions();
    this.bindShortcuts();
    this.fileIO.init();
    this.outline.init();
    this.statusbar.init();
    this.draftManager.init();
    this.tableManager.init();
  }

  // Initialize Vditor in offline self-contained configuration
  initVditor() {
    const defaultMarkdown = `# 📝 欢迎使用 Mark Scope

> **100% 离线单文件 Markdown 所见即所得编辑器与阅读器**  
> *Pure Client-Side, 100% Offline Standalone Single-File Markdown WYSIWYG Editor & Reader*

---

## ⚡ 核心离线工程特性

### 1. 🧮 现代数学公式排版 (KaTeX)
行内公式如爱因斯坦质能方程 $E = mc^2$ 以及高斯积分 $\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$。

块级公式：
$$
f(x) = \\frac{1}{\\sigma \\sqrt{2\\pi}} \\exp\\left( -\\frac{(x - \\mu)^2}{2\\sigma^2} \\right)
$$

### 2. 📊 矢量图表与流程拓扑 (Mermaid)
\`\`\`mermaid
graph LR
    A[本地 .md 文件] --> B(Mark Scope 离线引擎)
    B --> C{多模态排版与阅读}
    C -->|即时渲染| D[Typora 风格沉浸式编辑]
    C -->|所见即所得| E[富文本式流畅排版]
    C -->|纯净阅读| F[一键极简优雅阅读]
    C --> G[Ctrl+S 原地覆写 / 导出 HTML / PDF]
\`\`\`

### 3. 💻 语法高亮代码块 (Highlight.js)
\`\`\`python
# Mark Scope 离线引擎状态守护
def mark_scope_guard():
    status = "100% Standalone Offline"
    print(f"[{status}] - Zero-Server, 零外部网络依赖，极致保护文档隐私。")
    return True

mark_scope_guard()
\`\`\`

### 4. 📋 任务清单与工程表格
- [x] 100% 离线自包含单文件启动
- [x] Lute 核心离线 AST 解析引擎
- [x] 原地直接覆写保存 (File System Access API) 与安全下载
- [x] 实时防丢失本地快照与崩溃一键恢复
- [x] 树状大纲目录 ToC 实时导航与平滑跳转

| 特性模块 | 运行环境 | 网络外链请求 | 响应表现 |
| :--- | :---: | :---: | :---: |
| **Lute 解析引擎** | 纯客户端 | 0 | 毫秒级即时响应 |
| **KaTeX 数学排版** | 内置 WOFF2 字体 | 0 | 矢量锐利高精呈现 |
| **Mermaid 拓扑图** | 纯客户端 | 0 | 动态渲染拓扑图 |
| **文件安全写盘** | 浏览器沙箱 | 0 | 原地存盘 / 安全导出 |

---
*提示：按 **Ctrl+S** 可直接保存修改；按 **Ctrl+O** 可打开本地 Markdown 文件；点击顶部右上角可一键切换【阅读模式】与【深浅主题】。*
`;

    this.vditor = new Vditor('vditor-container', {
      value: defaultMarkdown,
      mode: this.currentMode,
      theme: this.currentTheme,
      preview: {
        theme: {
          current: this.currentTheme
        },
        hljs: {
          style: 'atom-one-dark',
          lineNumber: true
        },
        math: {
          engine: 'KaTeX'
        }
      },
      toolbar: [
        'emoji', 'headings', 'bold', 'italic', 'strike', 'link', '|',
        'list', 'ordered-list', 'check', 'outdent', 'indent', '|',
        'quote', 'line', 'code', 'inline-code', 'insert-before', 'insert-after', '|',
        'table', 'undo', 'redo', '|',
        'edit-mode', 'fullscreen'
      ],
      toolbarConfig: {
        pin: true
      },
      cache: {
        enable: false
      },
      input: (value) => {
        this.draftManager.onContentChange(value);
        this.outline.onContentChange(value);
        this.statusbar.onContentChange(value);
      },
      after: () => {
        console.log('[MarkScope] Vditor ready!');
        this.updateFileName(this.currentFileName);
        this.draftManager.markClean(defaultMarkdown);
        this.outline.refreshOutline();
        this.statusbar.onContentChange(defaultMarkdown, true);
        this.statusbar.updateMode(this.currentMode);
        setTimeout(() => this.tableManager.enhanceAllTables(), 100);
      }
    });
  }

  // Get current markdown plain text
  getContent() {
    return this.vditor ? this.vditor.getValue() : '';
  }

  // Load new document from file or recovery
  loadDocument(text, fileName) {
    if (this.vditor) {
      this.vditor.setValue(text);
    }
    this.updateFileName(fileName);
    this.draftManager.markClean(text);
    this.outline.refreshOutline();
    this.statusbar.onContentChange(text);
    [50, 200, 500, 1000].forEach(delay => {
      setTimeout(() => this.tableManager.enhanceAllTables(), delay);
    });
  }

  // Restore content from crash draft
  restoreContent(text, fileName) {
    if (this.vditor) {
      this.vditor.setValue(text);
    }
    this.updateFileName(fileName);
    this.outline.refreshOutline();
    this.statusbar.onContentChange(text);
    [50, 200, 500, 1000].forEach(delay => {
      setTimeout(() => this.tableManager.enhanceAllTables(), delay);
    });
  }

  updateFileName(name) {
    this.currentFileName = name;
    const titleEl = document.getElementById('current-doc-title');
    if (titleEl) titleEl.textContent = name;
    document.title = `${name} - Mark Scope`;
  }

  // Bind top navbar buttons and dropdowns
  bindHeaderActions() {
    // Open & Save
    document.getElementById('btn-open-file')?.addEventListener('click', () => this.fileIO.openFile());
    document.getElementById('btn-save-file')?.addEventListener('click', () => this.fileIO.saveFile());
    document.getElementById('btn-save-as')?.addEventListener('click', () => this.fileIO.saveFileAs());

    // Export Dropdown
    const exportBtn = document.getElementById('btn-export-dropdown');
    const exportMenu = document.getElementById('export-menu');
    if (exportBtn && exportMenu) {
      exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportMenu.classList.toggle('show');
      });
      document.addEventListener('click', () => exportMenu.classList.remove('show'));
    }

    document.getElementById('action-export-html')?.addEventListener('click', () => {
      exportMenu.classList.remove('show');
      this.fileIO.exportHTML();
    });

    document.getElementById('action-export-pdf')?.addEventListener('click', () => {
      exportMenu.classList.remove('show');
      this.fileIO.exportPDF();
    });

    // Theme Toggle
    document.getElementById('btn-toggle-theme')?.addEventListener('click', () => this.toggleTheme());

    // Full Width Toggle
    document.getElementById('btn-toggle-full-width')?.addEventListener('click', () => this.toggleFullWidth());

    // Mode switches
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetMode = btn.getAttribute('data-mode');
        this.switchEditorMode(targetMode);
      });
    });

    // Reader Mode
    document.getElementById('btn-reader-mode')?.addEventListener('click', () => this.enterReaderMode());
    document.getElementById('btn-exit-reader-mode')?.addEventListener('click', () => this.exitReaderMode());
  }

  // Toggle Full Width Mode (100% available viewport width)
  toggleFullWidth() {
    this.isFullWidth = !this.isFullWidth;
    document.body.classList.toggle('mode-full-width', this.isFullWidth);

    const fullWidthBtn = document.getElementById('btn-toggle-full-width');
    if (fullWidthBtn) {
      fullWidthBtn.classList.toggle('active-mode', this.isFullWidth);
      fullWidthBtn.innerHTML = this.isFullWidth ? '<span>📏 适应版心</span>' : '<span>📏 全宽</span>';
    }

    if (this.tableManager) {
      this.tableManager.enhanceAllTables();
    }
    this.showToast(this.isFullWidth ? '已开启正文全宽模式' : '已恢复标准舒适阅读宽度', 'info');
  }

  // Switch between IR, WYSIWYG, and Split View
  switchEditorMode(mode) {
    if (this.currentMode === mode) return;
    this.currentMode = mode;

    document.querySelectorAll('.mode-btn').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-mode') === mode);
    });

    if (this.vditor) {
      // Re-initialize or update mode
      const currentVal = this.getContent();
      this.vditor.destroy();
      this.initVditorWithMode(mode, currentVal);
    }
  }

  initVditorWithMode(mode, value) {
    this.vditor = new Vditor('vditor-container', {
      value: value,
      mode: mode,
      theme: this.currentTheme,
      preview: {
        theme: {
          current: this.currentTheme
        },
        hljs: {
          style: this.currentTheme === 'dark' ? 'atom-one-dark' : 'github',
          lineNumber: true
        },
        math: {
          engine: 'KaTeX'
        }
      },
      toolbar: [
        'emoji', 'headings', 'bold', 'italic', 'strike', 'link', '|',
        'list', 'ordered-list', 'check', 'outdent', 'indent', '|',
        'quote', 'line', 'code', 'inline-code', 'insert-before', 'insert-after', '|',
        'table', 'undo', 'redo', '|',
        'edit-mode', 'fullscreen'
      ],
      toolbarConfig: {
        pin: true
      },
      cache: {
        enable: false
      },
      input: (val) => {
        this.draftManager.onContentChange(val);
        this.outline.onContentChange(val);
        this.statusbar.onContentChange(val);
      },
      after: () => {
        this.statusbar.updateMode(mode);
        this.outline.refreshOutline();
        setTimeout(() => this.tableManager.enhanceAllTables(), 100);
      }
    });
  }

  // Toggle Dark / Light Theme
  toggleTheme() {
    this.currentTheme = this.currentTheme === 'dark' ? 'classic' : 'dark';
    const isDark = this.currentTheme === 'dark';
    document.body.classList.toggle('theme-dark', isDark);
    document.body.classList.toggle('theme-light', !isDark);

    const themeBtn = document.getElementById('btn-toggle-theme');
    if (themeBtn) {
      themeBtn.innerHTML = isDark ? '🌙 深色' : '☀️ 明亮';
    }

    if (this.vditor) {
      this.vditor.setTheme(this.currentTheme, this.currentTheme, isDark ? 'atom-one-dark' : 'github');
    }
  }

  initTheme() {
    const isDark = this.currentTheme === 'dark';
    document.body.classList.toggle('theme-dark', isDark);
    document.body.classList.toggle('theme-light', !isDark);
    const themeBtn = document.getElementById('btn-toggle-theme');
    if (themeBtn) {
      themeBtn.innerHTML = isDark ? '🌙 深色' : '☀️ 明亮';
    }
  }

  // Reader Mode
  enterReaderMode() {
    this.isReaderMode = true;
    document.body.classList.add('reader-mode');
    this.vditor.disabled();
    this.showToast('已进入沉浸阅读模式（按 Esc 或右下角退出）', 'info');
  }

  exitReaderMode() {
    this.isReaderMode = false;
    document.body.classList.remove('reader-mode');
    this.vditor.enable();
    this.showToast('已返回编辑模式', 'info');
  }

  // Keyboard Shortcuts
  bindShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ctrl+S / Cmd+S: Save
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        if (e.shiftKey) {
          this.fileIO.saveFileAs();
        } else {
          this.fileIO.saveFile();
        }
      }

      // Ctrl+O / Cmd+O: Open
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        this.fileIO.openFile();
      }

      // Esc: Exit Reader Mode
      if (e.key === 'Escape' && this.isReaderMode) {
        this.exitReaderMode();
      }
    });
  }

  // Toast Notification System
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => container.removeChild(toast), 300);
    }, 3000);
  }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.markScopeApp = new MarkScopeApp();
  window.markScopeApp.init();
});
