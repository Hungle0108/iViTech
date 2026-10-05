/**
 * YouTube Embed Fallback for file:// protocol
 * YouTube blocks iframe playback with "Error 153" when opened directly via file://
 * because file:// does not provide a valid HTTP origin/referer.
 * This script detects file:// and gracefully replaces iframes with responsive 16:9
 * video cards featuring thumbnail and direct YouTube watch links.
 */
(function() {
  if (window.location.protocol !== 'file:') {
    return;
  }

  function extractYouTubeId(url) {
    if (!url) return null;
    const match = url.match(/(?:youtube\.com\/(?:embed\/|v\/|watch\?v=)|youtube-nocookie\.com\/embed\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  }

  function createFallbackCard(iframe) {
    const src = iframe.getAttribute('src') || iframe.src || '';
    const videoId = extractYouTubeId(src);
    if (!videoId) return;

    const title = iframe.getAttribute('title') || 'Xem video trên YouTube';
    const thumbUrl = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
    const watchUrl = `https://www.youtube.com/watch?v=${videoId}`;

    // Create fallback element
    const fallback = document.createElement('a');
    fallback.href = watchUrl;
    fallback.target = '_blank';
    fallback.rel = 'noopener noreferrer';
    fallback.className = 'yt-file-fallback';
    fallback.setAttribute('aria-label', `Xem video "${title}" trên YouTube`);
    fallback.style.cssText = `
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-decoration: none;
      background: #000c1e url('${thumbUrl}') center/cover no-repeat;
      border-radius: inherit;
      overflow: hidden;
      cursor: pointer;
      user-select: none;
      z-index: 2;
    `;

    fallback.innerHTML = `
      <div style="position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,18,46,0.92) 0%, rgba(0,18,46,0.3) 50%, rgba(0,18,46,0.6) 100%); pointer-events: none;"></div>
      <div style="position: relative; z-index: 2; padding: 12px 14px; display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
        <span style="background: rgba(220,38,38,0.9); color: #fff; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 5px; font-family: inherit;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
          Mở trên YouTube
        </span>
        <span style="background: rgba(0,0,0,0.7); color: #f8fafc; font-size: 0.7rem; padding: 3px 7px; border-radius: 4px; font-family: inherit;">
          Chế độ file:// cục bộ
        </span>
      </div>
      <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 2;">
        <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(220,38,38,0.95); color: #fff; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); transition: transform 0.2s ease, background 0.2s ease;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="margin-left: 3px;"><path d="M8 5v14l11-7z"/></svg>
        </div>
      </div>
      <div style="position: relative; z-index: 2; padding: 12px 14px; background: linear-gradient(to top, rgba(0,18,46,0.95), transparent);">
        <div style="color: #ffffff; font-size: 0.88rem; font-weight: 700; line-height: 1.35; margin: 0 0 4px 0; text-shadow: 0 1px 3px rgba(0,0,0,0.8); display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; font-family: inherit;">
          ${title}
        </div>
        <div style="color: rgba(255,255,255,0.75); font-size: 0.75rem; font-family: inherit;">
          Nhấn để phát video trực tiếp trên YouTube (Trang đang mở qua file://)
        </div>
      </div>
    `;

    // Ensure parent container is positioned relative
    const parent = iframe.parentElement;
    if (parent) {
      const pos = window.getComputedStyle(parent).position;
      if (pos === 'static') {
        parent.style.position = 'relative';
      }
      parent.replaceChild(fallback, iframe);
    }
  }

  function applyFallbacks() {
    const iframes = document.querySelectorAll('iframe[src*="youtube.com/embed"], iframe[src*="youtube-nocookie.com/embed"]');
    iframes.forEach(createFallbackCard);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyFallbacks);
  } else {
    applyFallbacks();
  }

  // Handle dynamically inserted iframes (e.g. tab switches or modals)
  const observer = new MutationObserver(function(mutations) {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.tagName === 'IFRAME' && (node.src.includes('youtube.com/embed') || node.src.includes('youtube-nocookie.com/embed'))) {
            createFallbackCard(node);
          } else {
            const nested = node.querySelectorAll?.('iframe[src*="youtube.com/embed"], iframe[src*="youtube-nocookie.com/embed"]');
            if (nested && nested.length) {
              nested.forEach(createFallbackCard);
            }
          }
        }
      }
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
