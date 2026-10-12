/**
 * Mark Scope - File I/O & Export Controller
 * Supports:
 * - Native File System Access API (in-place disk overwrite via Ctrl+S)
 * - Safe fallback to standard Blob download
 * - Global file drag & drop into window
 * - Export to Standalone Styled Offline HTML
 * - Export to PDF (browser print with custom CSS)
 */
class FileIO {
  constructor(app) {
    this.app = app;
    this.fileHandle = null;
    this.hasFSAccess = typeof window.showOpenFilePicker === 'function';
  }

  init() {
    this.bindDropZone();
    this.bindFileInput();
  }

  // Open local file via modern picker or fallback input
  async openFile() {
    if (this.hasFSAccess) {
      try {
        const [handle] = await window.showOpenFilePicker({
          types: [{
            description: 'Markdown 文档 (*.md, *.markdown, *.txt)',
            accept: { 'text/markdown': ['.md', '.markdown', '.mdown', '.mkd', '.txt'] }
          }],
          multiple: false
        });
        const file = await handle.getFile();
        const text = await file.text();
        this.fileHandle = handle;
        this.app.loadDocument(text, file.name);
        this.app.showToast(`已成功打开文件：${file.name}`, 'success');
        return;
      } catch (err) {
        if (err.name === 'AbortError') return; // User cancelled
        console.warn('[MarkScope] File System Access API failed, falling back to input:', err);
      }
    }

    // Fallback: trigger hidden <input type="file">
    const input = document.getElementById('file-picker-input');
    if (input) {
      input.value = '';
      input.click();
    }
  }

  // Bind legacy file input
  bindFileInput() {
    const input = document.getElementById('file-picker-input');
    if (!input) return;
    input.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const text = await file.text();
      this.fileHandle = null; // Legacy input has no write handle
      this.app.loadDocument(text, file.name);
      this.app.showToast(`已成功打开文件：${file.name}`, 'success');
    });
  }

  // Global drag & drop handler with capture phase interception
  bindDropZone() {
    const overlay = document.getElementById('drag-drop-overlay');
    let dragCounter = 0;

    const hideOverlay = () => {
      dragCounter = 0;
      if (overlay) overlay.style.display = 'none';
    };

    window.addEventListener('dragenter', (e) => {
      e.preventDefault();
      dragCounter++;
      if (overlay) overlay.style.display = 'flex';
    }, true);

    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'copy';
      }
      if (overlay && overlay.style.display !== 'flex') {
        overlay.style.display = 'flex';
      }
    }, true);

    window.addEventListener('dragleave', (e) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter <= 0 || !e.relatedTarget) {
        hideOverlay();
      }
    }, true);

    window.addEventListener('drop', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      hideOverlay();

      const files = e.dataTransfer ? e.dataTransfer.files : null;
      if (files && files.length > 0) {
        const file = files[0];
        try {
          const text = await file.text();
          this.fileHandle = null;
          this.app.loadDocument(text, file.name);
          this.app.showToast(`已拖拽打开文件：${file.name}`, 'success');
        } catch (err) {
          console.error('[MarkScope] Error reading dropped file:', err);
          this.app.showToast(`读取拖入文件失败: ${err.message}`, 'error');
        }
      }
    }, true);

    // Escape or window blur as safety reset for drag overlay
    window.addEventListener('blur', hideOverlay);
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') hideOverlay();
    });
  }

  // Quick Save (Ctrl+S): In-place disk overwrite if handle exists, else Save As
  async saveFile() {
    const content = this.app.getContent();
    if (this.fileHandle && this.hasFSAccess) {
      try {
        const writable = await this.fileHandle.createWritable();
        await writable.write(content);
        await writable.close();
        this.app.draftManager.markClean(content);
        this.app.showToast(`已保存到磁盘：${this.app.currentFileName}`, 'success');
        return;
      } catch (err) {
        console.warn('[MarkScope] In-place write failed, switching to Save As:', err);
      }
    }
    // If no existing handle or write failed, trigger Save As
    await this.saveFileAs();
  }

  // Save As: Pick destination or trigger Blob download
  async saveFileAs() {
    const content = this.app.getContent();
    let fileName = this.app.currentFileName || '未命名文档.md';
    if (!fileName.endsWith('.md')) fileName += '.md';

    if (this.hasFSAccess) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: fileName,
          types: [{
            description: 'Markdown 文档 (*.md)',
            accept: { 'text/markdown': ['.md'] }
          }]
        });
        const writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();
        this.fileHandle = handle;
        const file = await handle.getFile();
        this.app.updateFileName(file.name);
        this.app.draftManager.markClean(content);
        this.app.showToast(`另存为成功：${file.name}`, 'success');
        return;
      } catch (err) {
        if (err.name === 'AbortError') return;
        console.warn('[MarkScope] showSaveFilePicker failed, falling back to download:', err);
      }
    }

    // Fallback: Safe Blob download
    this.downloadBlob(content, fileName, 'text/markdown;charset=utf-8');
    this.app.draftManager.markClean(content);
    this.app.showToast(`已下载文件：${fileName}`, 'success');
  }

  // Trigger standard browser download
  downloadBlob(content, fileName, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 150);
  }

  // Export to standalone styled offline HTML report
  async exportHTML() {
    this.app.showToast('正在生成独立 HTML 报告...', 'info');
    let htmlBody = '';
    try {
      htmlBody = await this.app.vditor.getHTML();
    } catch (e) {
      htmlBody = '<p>' + this.app.getContent() + '</p>';
    }

    const title = (this.app.currentFileName || 'Mark Scope 离线文档').replace(/\.md$/i, '');
    const isDark = document.body.classList.contains('theme-dark');
    const bgCol = isDark ? '#1a1e24' : '#ffffff';
    const textCol = isDark ? '#e2e8f0' : '#1e293b';
    const borderCol = isDark ? '#334155' : '#e2e8f0';

    const standaloneHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    body {
      background-color: ${bgCol};
      color: ${textCol};
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 40px 20px;
      line-height: 1.7;
    }
    .markdown-body {
      max-width: 900px;
      margin: 0 auto;
      padding: 30px;
      background: ${isDark ? '#16191f' : '#ffffff'};
      border: 1px solid ${borderCol};
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {
      border-bottom: 1px solid ${borderCol};
      padding-bottom: 0.3em;
    }
    .markdown-body table {
      border-collapse: collapse;
      width: 100%;
      margin: 16px 0;
    }
    .markdown-body table th, .markdown-body table td {
      border: 1px solid ${borderCol};
      padding: 8px 12px;
    }
    .markdown-body pre {
      background: ${isDark ? '#0f172a' : '#f1f5f9'};
      padding: 16px;
      border-radius: 6px;
      overflow-x: auto;
    }
    .markdown-body blockquote {
      border-left: 4px solid #3b82f6;
      margin: 16px 0;
      padding: 0 16px;
      color: ${isDark ? '#94a3b8' : '#64748b'};
    }
    .footer-watermark {
      text-align: center;
      margin-top: 30px;
      font-size: 12px;
      color: #64748b;
    }
  </style>
</head>
<body>
  <div class="markdown-body">
    ${htmlBody}
  </div>
  <div class="footer-watermark">
    Generated by Mark Scope &bull; 100% Offline Standalone Markdown Tool
  </div>
</body>
</html>`;

    this.downloadBlob(standaloneHtml, `${title}.html`, 'text/html;charset=utf-8');
    this.app.showToast(`HTML 导出完成：${title}.html`, 'success');
  }

  // Export to PDF via browser print
  exportPDF() {
    this.app.showToast('正在打开 PDF 打印窗口...', 'info');
    setTimeout(() => {
      window.print();
    }, 200);
  }
}
