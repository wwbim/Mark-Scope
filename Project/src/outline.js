/**
 * Mark Scope - Advanced Floating Outline & Stats Widget
 * 1. Collapsed state: Vertical minimalist dash bars mapping top-2 levels of headings (Screenshot 2)
 *    - Highest level: Full-length dashes (.level-top)
 *    - Second level: Shorter, indented dashes (.level-sub)
 * 2. Single-point active dash highlighting in pure white; non-active in dark grey, syncing in real-time with scroll
 * 3. Expanded floating panel with rounded frosted dark surface (Screenshot 1)
 * 4. Dual Tabs: [T Outline] and [📊 Stats]
 * 5. Outline tab: Default depth set to H3; 6-level interactive slider track (H1~H6) & hierarchical indented tree
 * 6. Stats tab: Clean line-by-line metrics (Words, Sentences, Paragraphs, Characters, Last Saved)
 * 7. Pinned (📌) state & Hover auto-reveal/collapse
 */
class OutlineManager {
  constructor(app) {
    this.app = app;
    this.headings = [];
    this.dashHeadings = []; // Top 2 levels of headings
    this.isPinned = false;
    this.currentTab = 'outline'; // 'outline' | 'stats'
    this.maxHeadingLevel = 3; // Requirement 2: Default depth set to H3
    this.activeHeadingIndex = 0;
    this.activeDashIndex = 0;
    this.updateDebounceTimer = null;
    this.scrollThrottleTimer = null;
    this.isMouseInside = false;
  }

  init() {
    this.bindPanelEvents();
    this.bindTabs();
    this.bindLevelFilter();
    this.bindScrollListener();
  }

  // Bind hover and pin actions
  bindPanelEvents() {
    const container = document.getElementById('ms-float-outline-container');
    const pinBtn = document.getElementById('btn-pin-outline');

    if (!container) return;

    // Hover reveal and collapse
    container.addEventListener('mouseenter', () => {
      this.isMouseInside = true;
      if (!this.isPinned) {
        container.classList.add('is-open');
      }
    });

    container.addEventListener('mouseleave', () => {
      this.isMouseInside = false;
      if (!this.isPinned) {
        container.classList.remove('is-open');
      }
    });

    // Pin button toggle
    if (pinBtn) {
      pinBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.togglePin();
      });
    }
  }

  togglePin() {
    this.isPinned = !this.isPinned;
    const container = document.getElementById('ms-float-outline-container');
    const pinBtn = document.getElementById('btn-pin-outline');

    if (container) {
      container.classList.toggle('is-pinned', this.isPinned);
      if (!this.isPinned && !this.isMouseInside) {
        container.classList.remove('is-open');
      }
    }

    if (pinBtn) {
      pinBtn.classList.toggle('pinned', this.isPinned);
    }

    if (this.isPinned) {
      this.app.showToast('已固定右侧大纲面板', 'info');
    }
  }

  // Bind Outline & Stats Tabs
  bindTabs() {
    const outlineTabBtn = document.getElementById('tab-btn-outline');
    const statsTabBtn = document.getElementById('tab-btn-stats');
    const outlineView = document.getElementById('view-tab-outline');
    const statsView = document.getElementById('view-tab-stats');

    if (outlineTabBtn && statsTabBtn) {
      outlineTabBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.switchTab('outline');
      });

      statsTabBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.switchTab('stats');
      });
    }
  }

  switchTab(tabName) {
    this.currentTab = tabName;
    const outlineTabBtn = document.getElementById('tab-btn-outline');
    const statsTabBtn = document.getElementById('tab-btn-stats');
    const outlineView = document.getElementById('view-tab-outline');
    const statsView = document.getElementById('view-tab-stats');

    if (tabName === 'outline') {
      if (outlineTabBtn) outlineTabBtn.classList.add('active');
      if (statsTabBtn) statsTabBtn.classList.remove('active');
      if (outlineView) outlineView.classList.add('active');
      if (statsView) statsView.classList.remove('active');
    } else {
      if (statsTabBtn) statsTabBtn.classList.add('active');
      if (outlineTabBtn) outlineTabBtn.classList.remove('active');
      if (statsView) statsView.classList.add('active');
      if (outlineView) outlineView.classList.remove('active');
      if (this.app.statusbar) {
        this.app.statusbar.updateStatsTab(this.app.getContent());
      }
    }
  }

  // Bind 6-Level Slider Dots & Active Track Fill
  bindLevelFilter() {
    const dotsContainer = document.querySelector('.level-dots-container');
    if (!dotsContainer) return;

    const dots = dotsContainer.querySelectorAll('.level-dot');
    dots.forEach((dot) => {
      dot.addEventListener('click', (e) => {
        e.preventDefault();
        const level = parseInt(dot.getAttribute('data-level')) || 3;
        this.setLevelFilter(level);
      });
    });

    // Default to Level 3 (Requirement 2)
    this.updateLevelTrackUI(this.maxHeadingLevel);
  }

  setLevelFilter(level) {
    this.maxHeadingLevel = level;
    this.updateLevelTrackUI(level);
    this.applyLevelFilterToTree();
  }

  updateLevelTrackUI(level) {
    const dots = document.querySelectorAll('.level-dot');
    const fill = document.getElementById('level-track-fill');

    dots.forEach((dot) => {
      const dotLevel = parseInt(dot.getAttribute('data-level'));
      dot.classList.toggle('active', dotLevel <= level);
    });

    if (fill) {
      // Calculate percentage width: level 1 = 0%, level 6 = 100%
      const pct = ((level - 1) / 5) * 100;
      fill.style.width = `${pct}%`;
    }
  }

  applyLevelFilterToTree() {
    const items = document.querySelectorAll('.float-outline-item');
    items.forEach((item) => {
      const itemLevel = parseInt(item.getAttribute('data-level'));
      item.style.display = itemLevel <= this.maxHeadingLevel ? 'flex' : 'none';
    });
  }

  // Triggered on document content update
  onContentChange(content) {
    clearTimeout(this.updateDebounceTimer);
    this.updateDebounceTimer = setTimeout(() => {
      this.extractAndRenderHeadings(content);
      if (this.app.statusbar) {
        this.app.statusbar.updateStatsTab(content);
      }
    }, 250);
  }

  // Extract H1~H6 Markdown headings
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

    // Requirement 1: Extract top 2 levels of headings in doc
    const uniqueLevels = Array.from(new Set(headings.map(h => h.level))).sort((a, b) => a - b);
    const topLevel1 = uniqueLevels[0] || 1;
    const topLevel2 = uniqueLevels[1] !== undefined ? uniqueLevels[1] : null;

    this.dashHeadings = headings.filter(h => h.level === topLevel1 || (topLevel2 !== null && h.level === topLevel2)).map(h => ({
      ...h,
      isTop: h.level === topLevel1,
      dashClass: h.level === topLevel1 ? 'level-top' : 'level-sub'
    }));

    this.renderDashes();
    this.renderOutlineTree();
    this.updateActiveHeadingOnScroll();
  }

  // Render Collapsed Vertical Dashes (Top 2 levels)
  renderDashes() {
    const container = document.getElementById('ms-outline-dashes');
    if (!container) return;

    if (this.dashHeadings.length === 0) {
      container.innerHTML = '<div class="ms-dash level-top" title="暂无标题"></div>';
      return;
    }

    let html = '';
    this.dashHeadings.forEach((h, idx) => {
      const isActive = (idx === this.activeDashIndex);
      html += `<div class="ms-dash ${h.dashClass} ${isActive ? 'active' : ''}" data-dash-index="${idx}" title="H${h.level} ${h.text}"></div>`;
    });

    container.innerHTML = html;

    const dashes = container.querySelectorAll('.ms-dash');
    dashes.forEach((dash) => {
      dash.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const idx = parseInt(dash.getAttribute('data-dash-index'));
        if (this.dashHeadings[idx]) {
          this.scrollToHeading(this.dashHeadings[idx]);
        }
      });
    });
  }

  // Render Expanded Outline Tree
  renderOutlineTree() {
    const listContainer = document.getElementById('float-outline-list');
    if (!listContainer) return;

    if (this.headings.length === 0) {
      listContainer.innerHTML = '<div class="float-outline-empty">暂无文档标题<br><small style="color:#71717a">输入 # 标题 即可生成大纲</small></div>';
      return;
    }

    let html = '';
    this.headings.forEach((h, idx) => {
      const isVisible = h.level <= this.maxHeadingLevel;
      html += `
        <div class="float-outline-item level-${h.level} ${idx === this.activeHeadingIndex ? 'active' : ''}"
             data-index="${idx}"
             data-level="${h.level}"
             style="display: ${isVisible ? 'flex' : 'none'}"
             title="${h.text}">
          <span class="outline-title-text">${h.text}</span>
        </div>
      `;
    });

    listContainer.innerHTML = html;

    const items = listContainer.querySelectorAll('.float-outline-item');
    items.forEach((item) => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const idx = parseInt(item.getAttribute('data-index'));
        if (this.headings[idx]) {
          this.scrollToHeading(this.headings[idx]);
        }
      });
    });
  }

  // Requirement 4: Robust, Multi-container Scroll Listener
  bindScrollListener() {
    const onScroll = () => {
      this.updateActiveHeadingOnScroll();
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('scroll', onScroll, { passive: true });

    // Continuously monitor and attach to Vditor's inner scrollable containers
    const attachVditorScrollers = () => {
      const scrollers = document.querySelectorAll(
        '.vditor-content, .vditor-ir, .vditor-reset, .vditor-wysiwyg, .vditor-sv, .editor-viewport'
      );
      scrollers.forEach((el) => {
        if (!el.__ms_scroll_attached) {
          el.__ms_scroll_attached = true;
          el.addEventListener('scroll', onScroll, { passive: true });
        }
      });
    };

    [50, 150, 400, 1000].forEach((delay) => setTimeout(attachVditorScrollers, delay));
  }

  // Calculate active heading & single-dash highlight based on current viewport
  updateActiveHeadingOnScroll() {
    if (this.headings.length === 0) return;

    const editorEl = document.getElementById('vditor-container');
    if (!editorEl) return;

    const domHeadings = Array.from(editorEl.querySelectorAll('h1, h2, h3, h4, h5, h6'));
    if (domHeadings.length === 0) return;

    let activeHeadingItem = this.headings[0];
    let activeHeadingIdx = 0;
    const viewThreshold = 180; // Distance from top of viewport

    for (let i = 0; i < domHeadings.length; i++) {
      const rect = domHeadings[i].getBoundingClientRect();
      if (rect.top <= viewThreshold) {
        activeHeadingIdx = i;
        activeHeadingItem = this.headings[i] || activeHeadingItem;
      } else {
        break;
      }
    }

    this.activeHeadingIndex = activeHeadingIdx;

    // Highlight in outline list
    const items = document.querySelectorAll('.float-outline-item');
    items.forEach((item, idx) => {
      item.classList.toggle('active', idx === activeHeadingIdx);
    });

    // Requirement 1 & 4: Highlight single active dash in top 2 levels
    if (this.dashHeadings.length > 0 && activeHeadingItem) {
      let activeDashIdx = 0;
      for (let d = 0; d < this.dashHeadings.length; d++) {
        if (this.dashHeadings[d].line <= activeHeadingItem.line) {
          activeDashIdx = d;
        } else {
          break;
        }
      }

      this.activeDashIndex = activeDashIdx;

      // Update dashes highlight (only 1 active white dash!)
      const dashes = document.querySelectorAll('.ms-dash');
      dashes.forEach((dash, idx) => {
        dash.classList.toggle('active', idx === activeDashIdx);
      });
    }
  }

  // Smooth scroll to target heading
  scrollToHeading(heading) {
    const container = document.getElementById('vditor-container');
    if (!container) return;

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
      targetEl.classList.add('heading-jump-highlight');
      setTimeout(() => targetEl.classList.remove('heading-jump-highlight'), 1200);
    }
  }

  refreshOutline() {
    this.extractAndRenderHeadings(this.app.getContent());
  }
}
