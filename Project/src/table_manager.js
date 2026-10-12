/**
 * Mark Scope - Advanced Table Engine
 * 1. Overrides Vditor's block/keep-all table layout with true responsive table layout
 * 2. Adaptive Column Balancing Algorithm (eliminates excessive line wrapping and horizontal scrollbars)
 * 3. Interactive Column Resizer via drag-and-drop handles on column borders
 * 4. External floating action pill for Table-Only Full Width Breakout without polluting Markdown AST
 */
class TableManager {
  constructor(app) {
    this.app = app;
    this.resizingData = null;
    this.floatingPill = null;
    this.currentHoveredTable = null;
    this.debounceTimer = null;
    this.hidePillTimer = null;
  }

  init() {
    this.createFloatingPill();
    this.bindGlobalEvents();
    this.observeEditorTables();
  }

  // Create single shared floating action pill
  createFloatingPill() {
    if (document.getElementById('ms-table-floating-pill')) return;

    const pill = document.createElement('div');
    pill.id = 'ms-table-floating-pill';
    pill.className = 'ms-table-floating-pill';
    pill.innerHTML = `
      <button class="ms-pill-btn btn-pill-breakout" title="让此表格向两侧展开至视口全宽 / 恢复正文宽">
        <span class="icon">⛶</span> <span class="label">表格全宽</span>
      </button>
      <button class="ms-pill-btn btn-pill-balance" title="重新智能平衡列宽与行高（亦可双击列分割线重置）">
        <span class="icon">⚖️</span> <span class="label">智能平衡</span>
      </button>
    `;

    document.body.appendChild(pill);
    this.floatingPill = pill;

    // Button actions
    const breakoutBtn = pill.querySelector('.btn-pill-breakout');
    const balanceBtn = pill.querySelector('.btn-pill-balance');

    breakoutBtn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!this.currentHoveredTable) return;
      this.toggleTableBreakout(this.currentHoveredTable, breakoutBtn);
    };

    balanceBtn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!this.currentHoveredTable) return;
      delete this.currentHoveredTable.dataset.customColWidths;
      this.balanceColumnWidths(this.currentHoveredTable, true);
      this.app.showToast('已重新计算并应用最佳平衡列宽', 'info');
    };

    // Keep pill visible when hovering over pill itself
    pill.addEventListener('mouseenter', () => {
      clearTimeout(this.hidePillTimer);
    });

    pill.addEventListener('mouseleave', () => {
      this.hidePillTimer = setTimeout(() => {
        this.floatingPill.style.display = 'none';
      }, 200);
    });
  }

  // Observe editor for table DOM updates
  observeEditorTables() {
    const container = document.getElementById('vditor-container');
    if (!container) return;

    this.enhanceAllTables();

    const observer = new MutationObserver(() => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.enhanceAllTables();
      }, 150);
    });

    observer.observe(container, {
      childList: true,
      subtree: true
    });
  }

  // Enhance all tables in the editor
  enhanceAllTables() {
    const container = document.getElementById('vditor-container');
    if (!container) return;

    const tables = container.querySelectorAll('table');
    tables.forEach(table => {
      this.enhanceSingleTable(table);
    });
  }

  enhanceSingleTable(table) {
    if (!table || table.rows.length === 0) return;

    // Force table layout rules
    table.classList.add('ms-balanced-table');
    table.style.display = 'table';
    table.style.width = '100%';
    table.style.tableLayout = 'fixed';
    table.style.borderCollapse = 'collapse';

    // Auto-balance columns
    this.balanceColumnWidths(table);

    // Attach interactive column resizer handles
    this.attachColumnResizers(table);

    // Attach hover listener for floating pill
    if (!table.dataset.pillAttached) {
      table.dataset.pillAttached = 'true';
      table.addEventListener('mouseenter', () => this.showFloatingPillForTable(table));
      table.addEventListener('mouseleave', () => {
        this.hidePillTimer = setTimeout(() => {
          if (this.floatingPill) this.floatingPill.style.display = 'none';
        }, 300);
      });
    }
  }

  showFloatingPillForTable(table) {
    clearTimeout(this.hidePillTimer);
    this.currentHoveredTable = table;

    const rect = table.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    const pill = this.floatingPill;
    pill.style.display = 'flex';
    pill.style.top = `${Math.max(10, rect.top - 32)}px`;
    pill.style.left = `${Math.max(10, rect.right - pill.offsetWidth - 8)}px`;

    // Sync breakout button state
    const breakoutBtn = pill.querySelector('.btn-pill-breakout');
    const isFull = table.classList.contains('table-breakout-full');
    breakoutBtn.querySelector('.label').textContent = isFull ? '适应正文' : '表格全宽';
    breakoutBtn.classList.toggle('active', isFull);
  }

  toggleTableBreakout(table, breakoutBtn) {
    const isFull = table.classList.toggle('table-breakout-full');
    breakoutBtn.querySelector('.label').textContent = isFull ? '适应正文' : '表格全宽';
    breakoutBtn.classList.toggle('active', isFull);

    // Calculate dynamic negative margin based on parent reset padding
    const reset = table.closest('.vditor-reset');
    if (reset) {
      const pad = parseInt(window.getComputedStyle(reset).paddingLeft) || 90;
      if (isFull && pad > 20) {
        table.style.marginLeft = `-${pad - 16}px`;
        table.style.marginRight = `-${pad - 16}px`;
        table.style.width = `calc(100% + ${(pad - 16) * 2}px)`;
        table.style.maxWidth = `calc(100% + ${(pad - 16) * 2}px)`;
      } else {
        table.style.marginLeft = '';
        table.style.marginRight = '';
        table.style.width = '100%';
        table.style.maxWidth = '100%';
      }
    }

    this.balanceColumnWidths(table);
    this.showFloatingPillForTable(table);
  }

  // Requirement 3: Smart Column Width Balancing Algorithm
  balanceColumnWidths(table, force = false) {
    if (table.dataset.customColWidths && !force) {
      return;
    }

    const rows = Array.from(table.rows);
    if (rows.length === 0) return;

    const headerCells = Array.from(rows[0].cells);
    const colCount = headerCells.length;
    if (colCount <= 1) return;

    // Collect stats for each column
    const colStats = [];
    let grandTotalChars = 0;

    for (let c = 0; c < colCount; c++) {
      const headerText = headerCells[c] ? headerCells[c].textContent.trim() : '';
      let totalCellChars = 0;
      let maxCellChars = 0;
      let count = 0;

      for (let r = 1; r < rows.length; r++) {
        if (rows[r].cells[c]) {
          const txt = rows[r].cells[c].textContent.trim();
          totalCellChars += txt.length;
          if (txt.length > maxCellChars) maxCellChars = txt.length;
          count++;
        }
      }

      const avgChars = count > 0 ? (totalCellChars / count) : 0;
      grandTotalChars += totalCellChars + headerText.length;
      colStats.push({
        hLen: headerText.length,
        avgLen: avgChars,
        maxLen: maxCellChars
      });
    }

    // Calculate intelligent weights
    // Columns with only dates/codes get compact proportions, rich columns get larger proportions
    const rawWeights = colStats.map(s => {
      const headerBase = Math.min(26, Math.max(12, s.hLen * 0.9));
      const contentFactor = Math.pow(Math.max(0, s.avgLen - 6), 0.6) * 7.0 + Math.pow(Math.max(0, s.maxLen - 12), 0.4) * 5.0;
      return headerBase + contentFactor;
    });

    const sumWeights = rawWeights.reduce((a, b) => a + b, 0);
    const minColPct = Math.max(10, Math.floor(100 / (colCount * 2.6)));

    let colPcts = rawWeights.map(w => Math.max(minColPct, Math.round((w / sumWeights) * 100)));
    let sumPcts = colPcts.reduce((a, b) => a + b, 0);

    // Normalize exact sum to 100%
    if (sumPcts !== 100) {
      const diff = 100 - sumPcts;
      colPcts[colPcts.length - 1] += diff;
    }

    // Apply via <colgroup> for 100% strict W3C table column width compliance
    let colgroup = table.querySelector('colgroup');
    if (!colgroup) {
      colgroup = document.createElement('colgroup');
      table.insertBefore(colgroup, table.firstChild);
    }

    colgroup.innerHTML = '';
    colPcts.forEach((pct, idx) => {
      const col = document.createElement('col');
      col.style.width = `${pct}%`;
      col.setAttribute('data-col-index', idx);
      colgroup.appendChild(col);
    });

    headerCells.forEach((th, idx) => {
      th.style.width = `${colPcts[idx]}%`;
    });
  }

  // Requirement 2: Attach interactive draggable column border resizers
  attachColumnResizers(table) {
    const rows = table.rows;
    if (rows.length === 0) return;

    const headerCells = Array.from(rows[0].cells);
    const colCount = headerCells.length;

    headerCells.forEach((th, idx) => {
      th.style.position = 'relative';
      th.style.overflow = 'visible';

      if (idx === colCount - 1) return; // Last column doesn't need right-edge handle

      let handle = th.querySelector('.ms-col-resizer');
      if (!handle) {
        handle = document.createElement('div');
        handle.className = 'ms-col-resizer';
        handle.title = '拖拽调节列宽（双击重置为最佳平衡列宽）';
        th.appendChild(handle);

        handle.addEventListener('mousedown', (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.startColumnResize(e, table, idx);
        });

        handle.addEventListener('dblclick', (e) => {
          e.preventDefault();
          e.stopPropagation();
          delete table.dataset.customColWidths;
          this.balanceColumnWidths(table, true);
          this.app.showToast('已重置此表格为最佳平衡列宽', 'info');
        });
      }
    });
  }

  startColumnResize(e, table, colIndex) {
    const colgroup = table.querySelector('colgroup');
    const cols = colgroup ? Array.from(colgroup.querySelectorAll('col')) : [];
    const tableWidth = table.offsetWidth;
    const ths = Array.from(table.rows[0].cells);

    const w1 = ths[colIndex].offsetWidth;
    const w2 = ths[colIndex + 1] ? ths[colIndex + 1].offsetWidth : 0;

    this.resizingData = {
      table,
      cols,
      ths,
      colIndex,
      startX: e.clientX,
      startW1: w1,
      startW2: w2,
      tableWidth
    };

    document.body.classList.add('ms-resizing-col');
  }

  bindGlobalEvents() {
    window.addEventListener('mousemove', (e) => {
      if (!this.resizingData) return;
      e.preventDefault();

      const { table, cols, ths, colIndex, startX, startW1, startW2, tableWidth } = this.resizingData;
      const deltaX = e.clientX - startX;

      const minPx = 45;
      let newW1 = Math.max(minPx, startW1 + deltaX);
      let newW2 = Math.max(minPx, startW2 - deltaX);

      if (newW1 === minPx) newW2 = (startW1 + startW2) - minPx;
      if (newW2 === minPx) newW1 = (startW1 + startW2) - minPx;

      const pct1 = ((newW1 / tableWidth) * 100).toFixed(1);
      const pct2 = ((newW2 / tableWidth) * 100).toFixed(1);

      if (cols.length > colIndex + 1) {
        cols[colIndex].style.width = `${pct1}%`;
        cols[colIndex + 1].style.width = `${pct2}%`;
      }
      ths[colIndex].style.width = `${pct1}%`;
      if (ths[colIndex + 1]) ths[colIndex + 1].style.width = `${pct2}%`;

      table.dataset.customColWidths = 'true';
    });

    window.addEventListener('mouseup', () => {
      if (this.resizingData) {
        document.body.classList.remove('ms-resizing-col');
        this.resizingData = null;
      }
    });
  }
}
