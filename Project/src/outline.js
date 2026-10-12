/**
 * Mark Scope - Outline / Table of Contents (ToC) Manager
 * Generates dynamic hierarchical navigation tree from Markdown headings,
 * supports smooth scrolling jumps, active heading highlighting, and collapsible sidebar.
 */
class OutlineManager {
  constructor(app) {
    this.app = app;
    this.isCollapsed = false;
    this.headings = [];
    this.updateDebounceTimer = null;
  }

  init() {
    this.bindSidebarToggle();
  }

  bindSidebarToggle() {
    const toggleBtn = document.getElementById('btn-toggle-outline');
    const collapseIconBtn = document.getElementById('btn-collapse-sidebar');
    const sidebar = document.getElementById('outline-sidebar');

    const doToggle = () => {
      this.isCollapsed = !this.isCollapsed;
      if (this.isCollapsed) {
        sidebar.classList.add('collapsed');
        if (toggleBtn) toggleBtn.classList.remove('active');
      } else {
        sidebar.classList.remove('collapsed');
        if (toggleBtn) toggleBtn.classList.add('active');
        this.refreshOutline();
      }
    };

    if (toggleBtn) toggleBtn.addEventListener('click', doToggle);
    if (collapseIconBtn) collapseIconBtn.addEventListener('click', doToggle);
  }

  // Triggered on content change to update heading tree
  onContentChange(content) {
    if (this.isCollapsed) return;
    clearTimeout(this.updateDebounceTimer);
    this.updateDebounceTimer = setTimeout(() => {
      this.extractAndRenderHeadings(content);
    }, 400);
  }

  // Extract Markdown headings H1-H6 from text
  extractAndRenderHeadings(content) {
    const lines = content.split('\n');
    const headings = [];
    let inCodeBlock = false;

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('```')) {
        inCodeBlock = !inCodeBlock;
        return;
      }
      if (inCodeBlock) return;

      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const text = match[2].trim().replace(/[#*`_~]/g, '');
        headings.push({
          level,
          text,
          line: index + 1
        });
      }
    });

    this.headings = headings;
    this.renderTree(headings);
  }

  renderTree(headings) {
    const treeContainer = document.getElementById('outline-tree');
    if (!treeContainer) return;

    if (headings.length === 0) {
      treeContainer.innerHTML = '<div class="outline-empty">暂无文档大纲标题<br><small style="color:var(--text-muted)">输入 # 标题 即可生成大纲</small></div>';
      return;
    }

    let html = '';
    headings.forEach((h, idx) => {
      const indentClass = `level-${h.level}`;
      html += `
        <div class="outline-item ${indentClass}" data-index="${idx}" data-line="${h.line}" title="${h.text}">
          <span class="outline-level-tag">H${h.level}</span>
          <span class="outline-title-text">${h.text}</span>
        </div>
      `;
    });

    treeContainer.innerHTML = html;

    // Attach click listeners to jump to headings
    const items = treeContainer.querySelectorAll('.outline-item');
    items.forEach(item => {
      item.addEventListener('click', () => {
        items.forEach(el => el.classList.remove('active'));
        item.classList.add('active');
        const idx = parseInt(item.getAttribute('data-index'));
        this.scrollToHeading(headings[idx]);
      });
    });
  }

  // Smooth scroll to target heading in Vditor editor area
  scrollToHeading(heading) {
    const container = document.getElementById('vditor-container');
    if (!container) return;

    // Look for heading element in Vditor DOM (IR / WYSIWYG / SV)
    const domHeadings = container.querySelectorAll(`h${heading.level}`);
    let targetEl = null;

    for (let el of domHeadings) {
      if (el.textContent.includes(heading.text) || heading.text.includes(el.textContent.trim())) {
        targetEl = el;
        break;
      }
    }

    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Brief highlight animation
      targetEl.classList.add('heading-jump-highlight');
      setTimeout(() => targetEl.classList.remove('heading-jump-highlight'), 1200);
    }
  }

  refreshOutline() {
    this.extractAndRenderHeadings(this.app.getContent());
  }
}
