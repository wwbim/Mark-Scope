/**
 * Mark Scope - Statusbar HUD Manager
 * Calculates real-time document metrics:
 * - Character count (Total & non-space)
 * - Word count (CJK characters + Western words)
 * - Line count
 * - Estimated reading time
 * - Mode indicator & File save status
 */
class StatusbarManager {
  constructor(app) {
    this.app = app;
    this.updateDebounceTimer = null;
  }

  init() {
    this.updateMetrics('');
  }

  onContentChange(content, immediate = false) {
    if (immediate) {
      clearTimeout(this.updateDebounceTimer);
      this.updateMetrics(content);
      return;
    }
    clearTimeout(this.updateDebounceTimer);
    this.updateDebounceTimer = setTimeout(() => {
      this.updateMetrics(content);
    }, 250);
  }

  updateMetrics(text) {
    const totalChars = text.length;
    const nonSpaceChars = text.replace(/\s/g, '').length;
    
    // Words count: English words + CJK characters
    const cjkMatches = text.match(/[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]/g);
    const cjkCount = cjkMatches ? cjkMatches.length : 0;
    
    const westernMatches = text.replace(/[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]/g, ' ').match(/[a-zA-Z0-9_\-]+/g);
    const westernWordCount = westernMatches ? westernMatches.length : 0;
    
    const totalWords = cjkCount + westernWordCount;
    
    // Line count
    const lines = text ? text.split('\n').length : 1;
    
    // Reading time: standard ~300 words/minute
    const readMinutes = Math.max(1, Math.ceil(totalWords / 300));

    // Update DOM
    const charEl = document.getElementById('stat-chars');
    const wordEl = document.getElementById('stat-words');
    const lineEl = document.getElementById('stat-lines');
    const timeEl = document.getElementById('stat-time');

    if (charEl) charEl.textContent = `${totalChars.toLocaleString()} 字符`;
    if (wordEl) wordEl.textContent = `${totalWords.toLocaleString()} 词`;
    if (lineEl) lineEl.textContent = `${lines.toLocaleString()} 行`;
    if (timeEl) timeEl.textContent = `约 ${readMinutes} 分钟阅读`;
  }

  updateMode(mode) {
    const modeEl = document.getElementById('stat-mode');
    if (!modeEl) return;
    const modeNames = {
      'ir': '即时渲染 (IR)',
      'wysiwyg': '所见即所得 (WYSIWYG)',
      'sv': '分屏预览 (SV)'
    };
    modeEl.textContent = modeNames[mode] || mode.toUpperCase();
  }

  updateDirtyState(isDirty) {
    const saveStatusEl = document.getElementById('stat-save-status');
    if (!saveStatusEl) return;
    if (isDirty) {
      saveStatusEl.textContent = '● 未保存修改';
      saveStatusEl.className = 'status-item status-dirty';
    } else {
      saveStatusEl.textContent = '✓ 已存盘';
      saveStatusEl.className = 'status-item status-clean';
    }
  }

  updateDraftStatus(text) {
    const saveStatusEl = document.getElementById('stat-save-status');
    if (!saveStatusEl) return;
    saveStatusEl.textContent = text;
  }
}
