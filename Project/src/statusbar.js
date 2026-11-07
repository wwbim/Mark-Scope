/**
 * Mark Scope - Statusbar & Stats Manager
 * Calculates real-time document metrics:
 * - Word count (CJK characters + Western words)
 * - Sentence count (句数)
 * - Paragraph count (段数)
 * - Character count (字符数)
 * - Last Saved Timestamp (最后保存，采用本地时间格式)
 * - Mode indicator & File save status
 */
class StatusbarManager {
  constructor(app) {
    this.app = app;
    this.updateDebounceTimer = null;
    this.lastSavedDate = new Date();
  }

  init() {
    this.updateMetrics('');
    this.updateLastSavedTime(new Date());
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
    const raw = text || '';
    const totalChars = raw.length;

    // Word count: English words + CJK characters
    const cjkMatches = raw.match(/[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]/g);
    const cjkCount = cjkMatches ? cjkMatches.length : 0;
    const westernMatches = raw.replace(/[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]/g, ' ').match(/[a-zA-Z0-9_\-]+/g);
    const westernWordCount = westernMatches ? westernMatches.length : 0;
    const totalWords = cjkCount + westernWordCount;

    // Sentence count (句数): Chinese full stops/exclamations/questions, Western periods/exclamations/questions
    const sentenceList = raw.trim() ? raw.split(/[。！？!?\n]+/).filter(s => s.trim().length > 0) : [];
    const sentenceCount = sentenceList.length;

    // Paragraph count (段数): Double newline or non-empty blocks
    const paragraphList = raw.trim() ? raw.split(/\n\s*\n/).filter(p => p.trim().length > 0) : [];
    const paragraphCount = paragraphList.length || (raw.trim() ? 1 : 0);

    // Update Floating Panel [Stats] tab
    this.updateStatsTabElements(totalWords, sentenceCount, paragraphCount, totalChars);
  }

  updateStatsTab(text) {
    this.updateMetrics(text);
  }

  updateStatsTabElements(words, sentences, paragraphs, chars) {
    const wordEl = document.getElementById('stat-val-words');
    const sentEl = document.getElementById('stat-val-sentences');
    const paraEl = document.getElementById('stat-val-paragraphs');
    const charEl = document.getElementById('stat-val-chars');

    if (wordEl) wordEl.textContent = words.toLocaleString();
    if (sentEl) sentEl.textContent = sentences.toLocaleString();
    if (paraEl) paraEl.textContent = paragraphs.toLocaleString();
    if (charEl) charEl.textContent = chars.toLocaleString();
  }

  updateLastSavedTime(date = new Date()) {
    this.lastSavedDate = date;
    const savedEl = document.getElementById('stat-val-last-saved');
    if (!savedEl) return;

    try {
      // Local computer/browser locale format: YYYY/MM/DD HH:mm:ss or locale specific
      const formatted = date.toLocaleString();
      savedEl.textContent = formatted;
    } catch (e) {
      savedEl.textContent = date.toISOString().replace('T', ' ').substring(0, 19);
    }
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
      this.updateLastSavedTime(new Date());
    }
  }

  updateDraftStatus(text) {
    const saveStatusEl = document.getElementById('stat-save-status');
    if (!saveStatusEl) return;
    saveStatusEl.textContent = text;
  }
}
