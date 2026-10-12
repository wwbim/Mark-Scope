/**
 * Mark Scope - Draft & Crash Recovery Manager
 * Manages real-time localStorage snapshots, dirty-state tracking,
 * beforeunload protection, and crash-recovery banner notifications.
 */
class DraftManager {
  constructor(app) {
    this.app = app;
    this.storageKey = 'mark_scope_crash_draft_v1';
    this.isDirty = false;
    this.saveDebounceTimer = null;
    this.lastSavedHash = '';
  }

  init() {
    this.bindBeforeUnload();
    this.checkForRecoverableDraft();
  }

  // Calculate simple fast hash for dirty checking
  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return hash.toString();
  }

  // Triggered on every user input in the editor
  onContentChange(content) {
    const currentHash = this.hashString(content);
    const isNowDirty = (currentHash !== this.lastSavedHash);
    
    if (this.isDirty !== isNowDirty) {
      this.isDirty = isNowDirty;
      this.updateDirtyUI();
    }

    // Debounced draft snapshot to localStorage (300ms)
    clearTimeout(this.saveDebounceTimer);
    this.saveDebounceTimer = setTimeout(() => {
      this.saveDraftSnapshot(content);
    }, 300);
  }

  // Commit draft to localStorage
  saveDraftSnapshot(content) {
    try {
      const data = {
        fileName: this.app.currentFileName || '未命名文档.md',
        content: content,
        timestamp: Date.now(),
        isDirty: this.isDirty
      };
      localStorage.setItem(this.storageKey, JSON.stringify(data));
      if (this.app.statusbar) {
        this.app.statusbar.updateDraftStatus(this.isDirty ? '草稿已缓存' : '已存盘');
      }
    } catch (e) {
      console.warn('[MarkScope] Draft storage quota exceeded or unavailable:', e);
    }
  }

  // Mark content as committed to disk/file
  markClean(content) {
    this.lastSavedHash = this.hashString(content);
    this.isDirty = false;
    this.updateDirtyUI();
    this.saveDraftSnapshot(content);
  }

  updateDirtyUI() {
    const dirtyBadge = document.getElementById('file-dirty-indicator');
    if (dirtyBadge) {
      dirtyBadge.style.display = this.isDirty ? 'inline-block' : 'none';
    }
    const saveBtn = document.getElementById('btn-save-file');
    if (saveBtn) {
      if (this.isDirty) {
        saveBtn.classList.add('btn-highlight-save');
      } else {
        saveBtn.classList.remove('btn-highlight-save');
      }
    }
    if (this.app.statusbar) {
      this.app.statusbar.updateDirtyState(this.isDirty);
    }
  }

  // Check if a crash draft exists on startup
  checkForRecoverableDraft() {
    try {
      const raw = localStorage.getItem(this.storageKey);
      if (!raw) return;
      const data = JSON.parse(raw);
      
      // If the draft has content and was dirty before termination
      if (data && data.content && data.content.trim().length > 0 && data.isDirty) {
        const timeAgo = this.formatTimeAgo(data.timestamp);
        this.showRecoveryBanner(data.fileName, timeAgo, data.content);
      }
    } catch (e) {
      console.warn('[MarkScope] Failed to inspect crash draft:', e);
    }
  }

  showRecoveryBanner(fileName, timeAgo, content) {
    const banner = document.getElementById('crash-recovery-banner');
    if (!banner) return;

    const descEl = document.getElementById('recovery-banner-desc');
    if (descEl) {
      descEl.textContent = `检测到崩溃/意外退出前未保存的草稿（文件：${fileName}，缓存于 ${timeAgo}）。是否立即恢复？`;
    }

    const restoreBtn = document.getElementById('btn-restore-draft');
    const discardBtn = document.getElementById('btn-discard-draft');

    if (restoreBtn) {
      restoreBtn.onclick = () => {
        this.app.restoreContent(content, fileName);
        this.isDirty = true;
        this.updateDirtyUI();
        banner.style.display = 'none';
        this.app.showToast('✅ 草稿已恢复，请按 Ctrl+S 存盘！', 'success');
      };
    }

    if (discardBtn) {
      discardBtn.onclick = () => {
        this.clearDraftSnapshot();
        banner.style.display = 'none';
        this.app.showToast('已放弃历史草稿', 'info');
      };
    }

    banner.style.display = 'flex';
  }

  clearDraftSnapshot() {
    try {
      localStorage.removeItem(this.storageKey);
    } catch (e) {}
  }

  formatTimeAgo(timestamp) {
    if (!timestamp) return '不久前';
    const diff = Math.floor((Date.now() - timestamp) / 1000);
    if (diff < 60) return `${diff}秒前`;
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    return new Date(timestamp).toLocaleDateString();
  }

  bindBeforeUnload() {
    window.addEventListener('beforeunload', (e) => {
      if (this.isDirty) {
        e.preventDefault();
        e.returnValue = '您有未保存的文档修改，确定要退出吗？';
        return e.returnValue;
      }
    });
  }
}
