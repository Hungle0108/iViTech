/*!
 * iViTech Motion Kit v1.0 — hiệu ứng chuyển động cho website iViTech
 * Không phụ thuộc thư viện. Chỉ dùng transform/opacity, IntersectionObserver, requestAnimationFrame.
 *
 * Cách gán hiệu ứng (ưu tiên từ trên xuống):
 *   1. Thuộc tính viết tay trong HTML:  data-reveal="fade-up" data-delay="120"
 *      data-stagger="80" (áp cho con trực tiếp), data-count="12000", data-parallax="0.2",
 *      data-tilt, data-spotlight, data-sequence=".child-selector"
 *   2. Bảng MAP bên dưới — gán tự động theo class đang có của site (không cần sửa HTML).
 *
 * Tắt toàn bộ: <html data-motion="off">  hoặc người dùng bật "Giảm chuyển động" trong hệ điều hành.
 */
(() => {
  'use strict';
  const html = document.documentElement;
  window.__ivMotion = true; // báo cho đoạn script an toàn trong <head> biết file đã tải

  const reduce =
    html.dataset.motion === 'off' ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    (navigator.connection && navigator.connection.saveData);

  if (reduce) {
    html.classList.remove('motion-ready');
    html.classList.add('motion-reduced');
    return;
  }
  html.classList.add('motion-ready');

  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ------------------------------------------------------------------
   * MAP: selector → hiệu ứng. Mục đứng trước được ưu tiên.
   * reveal: fade-up | fade-down | fade-left | fade-right | zoom | wipe | blur
   * stagger: ms giữa các phần tử cùng cha · delay: ms trễ ban đầu
   * ------------------------------------------------------------------ */
  const MAP = [
    // ===== Trang chủ — hero
    { sel: '.hero-copy-col > *', reveal: 'fade-up', stagger: 90, delay: 60 },
    { sel: '.hero-visual-col .hero-sim-card', reveal: 'fade-left', delay: 280, tilt: 3 },
    { sel: '.hero-glow-orb', parallax: 0.18 },

    // ===== Trang sản phẩm — hero
    { sel: '.product-hero-copy > *', reveal: 'fade-up', stagger: 90, delay: 60 },
    { sel: '.product-hero__visual > .media', reveal: 'wipe', delay: 200 },
    { sel: '.product-hero-card', reveal: 'fade-right', delay: 520 },
    { sel: '.hero-stat-list > .hero-stat-item', reveal: 'fade-up', stagger: 110, delay: 700 },

    // ===== Tiêu đề section (mọi trang)
    { sel: '.section-head > *', reveal: 'fade-up', stagger: 80 },
    { sel: 'section .eyebrow-pill, section .section-kicker', reveal: 'fade-up' },
    { sel: 'section .section-title, section .section-h2', reveal: 'fade-up', delay: 60 },
    { sel: 'section .section-desc, section .section-subtitle, section .section-lead', reveal: 'fade-up', delay: 120 },

    // ===== Lưới thẻ (stagger theo cha)
    { sel: '.trust-logos-grid > *', reveal: 'fade-up', stagger: 70 },
    { sel: '.grid-cards-4 > .observation-card', reveal: 'fade-up', stagger: 100 },
    { sel: '.capabilities-stepper > .cap-step-card', reveal: 'fade-up', stagger: 90 },
    { sel: '.case-grid > .case-card', reveal: 'fade-up', stagger: 120 },
    { sel: '.team-grid > .team-card', reveal: 'zoom', stagger: 90 },
    { sel: '.faq-accordion > .faq-item', reveal: 'fade-up', stagger: 60 },
    { sel: '.features-grid > .feature-card', reveal: 'fade-up', stagger: 100 },
    { sel: '.related-grid > .related-card', reveal: 'fade-up', stagger: 110 },
    { sel: '.audience-chips > .audience-chip', reveal: 'fade-left', stagger: 90 },
    { sel: '.video-grid-2 > *', reveal: 'fade-up', stagger: 120 },

    // ===== Quy trình: hiện lần lượt từng bước khi section vào màn hình
    { sel: '.process-stepper-5', sequence: '.process-step-box', interval: 220 },
    { sel: '.digitize-stepper', sequence: '.step-card-item', interval: 180 },

    // ===== Ảnh nội dung còn lại (không nằm trong thẻ đã có hiệu ứng)
    { sel: 'section figure.media:not(.related-card .media):not(.case-card .media):not(.observation-card .media)', reveal: 'wipe' },

    // ===== Khối CTA và liên hệ: ánh sáng theo con trỏ
    { sel: '.product-cta-section, .contact-section-v2', spotlight: true },
    { sel: '.product-cta-section .container > *, .contact-section-v2 .container > * > *', reveal: 'fade-up', stagger: 90 },
  ];

  const toNum = (v, d = 0) => (v == null || v === '' || isNaN(+v) ? d : +v);

  /* ---------------- 1. Áp MAP → data-attributes ---------------- */
  const counters = new Map(); // parent → số thứ tự để stagger
  for (const rule of MAP) {
    let nodes;
    try { nodes = document.querySelectorAll(rule.sel); } catch (e) { console.warn('[motion] selector lỗi:', rule.sel); continue; }
    nodes.forEach((el) => {
      if (rule.reveal && !el.hasAttribute('data-reveal') && !el.closest('[data-reveal-done]')) {
        // không lồng hiệu ứng: bỏ qua nếu tổ tiên đã có reveal
        if (el.parentElement && el.parentElement.closest('[data-reveal]')) return;
        const p = el.parentElement;
        const i = counters.get(p) || 0;
        counters.set(p, i + 1);
        el.setAttribute('data-reveal', rule.reveal);
        el.style.setProperty('--m-d', `${(rule.delay || 0) + i * (rule.stagger || 0)}ms`);
      }
      if (rule.parallax && !el.hasAttribute('data-parallax')) el.setAttribute('data-parallax', rule.parallax);
      if (rule.tilt && !el.hasAttribute('data-tilt')) el.setAttribute('data-tilt', rule.tilt);
      if (rule.spotlight) el.setAttribute('data-spotlight', '');
      if (rule.sequence && !el.hasAttribute('data-sequence')) {
        el.setAttribute('data-sequence', rule.sequence);
        if (rule.interval) el.setAttribute('data-interval', rule.interval);
      }
    });
  }

  // Thuộc tính viết tay: data-stagger trên cha → gán reveal cho con
  document.querySelectorAll('[data-stagger]').forEach((parent) => {
    const step = toNum(parent.dataset.stagger, 80);
    const effect = parent.dataset.revealChildren || 'fade-up';
    [...parent.children].forEach((c, i) => {
      if (!c.hasAttribute('data-reveal')) c.setAttribute('data-reveal', effect);
      c.style.setProperty('--m-d', `${toNum(parent.dataset.delay) + i * step}ms`);
    });
  });
  document.querySelectorAll('[data-reveal][data-delay]').forEach((el) => {
    el.style.setProperty('--m-d', `${toNum(el.dataset.delay)}ms`);
  });

  /* ---------------- 2. Reveal khi cuộn tới ---------------- */
  const DURATION = 900;
  const finish = (el) => {
    const d = parseFloat(getComputedStyle(el).getPropertyValue('--m-d')) || 0;
    setTimeout(() => {
      // Trả lại transition gốc của component (hover…) sau khi hiện xong
      el.removeAttribute('data-reveal');
      el.classList.remove('is-in');
      el.style.removeProperty('--m-d');
      el.setAttribute('data-reveal-done', '');
    }, d + DURATION + 50);
  };
  const revealIO = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        e.target.classList.add('is-in');
        revealIO.unobserve(e.target);
        finish(e.target);
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
  );
  const observeReveals = (root = document) =>
    root.querySelectorAll('[data-reveal]:not(.is-in)').forEach((el) => revealIO.observe(el));
  observeReveals();

  // An toàn: nếu vì lý do gì đó phần tử chưa hiện sau 4s mà đang trong màn hình → hiện luôn
  setTimeout(() => {
    document.querySelectorAll('[data-reveal]:not(.is-in)').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.top < innerHeight && r.bottom > 0 && r.width > 0) { el.classList.add('is-in'); finish(el); }
    });
  }, 4000);

  /* ---------------- 3. Chuỗi bước (process / stepper) ---------------- */
  const seqIO = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        seqIO.unobserve(e.target);
        const items = e.target.querySelectorAll(e.target.dataset.sequence);
        const gap = toNum(e.target.dataset.interval, 220);
        e.target.classList.add('seq-run');
        items.forEach((it, i) => setTimeout(() => {
          it.classList.add('is-step-on');
          e.target.style.setProperty('--m-progress', ((i + 1) / items.length).toFixed(3));
        }, 150 + i * gap));
      }
    },
    { threshold: 0.3 }
  );
  document.querySelectorAll('[data-sequence]').forEach((el) => {
    el.querySelectorAll(el.dataset.sequence).forEach((it) => it.classList.add('seq-item'));
    seqIO.observe(el);
  });

  /* ---------------- 4. Đếm số ---------------- */
  const fmt = (n, dec) => n.toLocaleString('vi-VN', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const countIO = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        countIO.unobserve(e.target);
        const el = e.target;
        const to = toNum(el.dataset.count);
        const from = toNum(el.dataset.from);
        const dec = toNum(el.dataset.decimals, String(to).includes('.') ? String(to).split('.')[1].length : 0);
        const dur = toNum(el.dataset.duration, 1400);
        const pre = el.dataset.prefix || '';
        const suf = el.dataset.suffix || '';
        const t0 = performance.now();
        const tick = (t) => {
          const p = Math.min(1, (t - t0) / dur);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = pre + fmt(from + (to - from) * eased, dec) + suf;
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }
    },
    { threshold: 0.6 }
  );
  document.querySelectorAll('[data-count]').forEach((el) => {
    el.style.minWidth = `${el.getBoundingClientRect().width}px`; // tránh nhảy layout
    countIO.observe(el);
  });

  /* ---------------- 5. Parallax nhẹ ---------------- */
  const pxEls = [...document.querySelectorAll('[data-parallax]')];
  if (pxEls.length) {
    const visible = new Set();
    const pxIO = new IntersectionObserver((es) => es.forEach((e) => (e.isIntersecting ? visible.add(e.target) : visible.delete(e.target))));
    pxEls.forEach((el) => pxIO.observe(el));
    let ticking = false;
    const update = () => {
      ticking = false;
      const vh = innerHeight;
      visible.forEach((el) => {
        const r = el.getBoundingClientRect();
        const offset = (r.top + r.height / 2 - vh / 2) * -toNum(el.dataset.parallax, 0.15);
        el.style.setProperty('--m-py', `${offset.toFixed(1)}px`);
      });
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  /* ---------------- 6. Nghiêng theo con trỏ (desktop) ---------------- */
  if (finePointer && innerWidth >= 1024) {
    document.querySelectorAll('[data-tilt]').forEach((el) => {
      const max = toNum(el.dataset.tilt, 4) || 4;
      let raf = 0;
      el.addEventListener('pointermove', (ev) => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          const r = el.getBoundingClientRect();
          const x = (ev.clientX - r.left) / r.width - 0.5;
          const y = (ev.clientY - r.top) / r.height - 0.5;
          el.style.setProperty('--m-rx', `${(-y * max).toFixed(2)}deg`);
          el.style.setProperty('--m-ry', `${(x * max).toFixed(2)}deg`);
          el.classList.add('is-tilting');
        });
      });
      el.addEventListener('pointerleave', () => {
        cancelAnimationFrame(raf);
        el.style.setProperty('--m-rx', '0deg');
        el.style.setProperty('--m-ry', '0deg');
        el.classList.remove('is-tilting');
      });
    });
  }

  /* ---------------- 7. Ánh sáng theo con trỏ ---------------- */
  if (finePointer) {
    document.querySelectorAll('[data-spotlight]').forEach((el) => {
      el.addEventListener('pointermove', (ev) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--m-mx', `${ev.clientX - r.left}px`);
        el.style.setProperty('--m-my', `${ev.clientY - r.top}px`);
      }, { passive: true });
    });
  }

  /* ---------------- 8. Thanh tiến độ cuộn trang ---------------- */
  const bar = document.createElement('div');
  bar.className = 'motion-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  let pTick = false;
  const setProgress = () => {
    pTick = false;
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
  };
  addEventListener('scroll', () => { if (!pTick) { pTick = true; requestAnimationFrame(setProgress); } }, { passive: true });
  setProgress();

  /* ---------------- 9. Tab / pane: chạy lại hiệu ứng khi đổi tab ---------------- */
  const PANE_SEL = '.eco-pane, [role="tabpanel"], .roadmap-pane, .roadmap-panel, .role-panel, .tab-pane';
  const isShown = (el) => el.offsetParent !== null || getComputedStyle(el).position === 'fixed';
  const state = new WeakMap();
  const panes = [...document.querySelectorAll(PANE_SEL)];
  panes.forEach((p) => state.set(p, isShown(p)));
  if (panes.length) {
    const mo = new MutationObserver(() => {
      panes.forEach((p) => {
        const now = isShown(p);
        if (now && !state.get(p)) {
          p.classList.remove('motion-pane-in');
          void p.offsetWidth; // khởi động lại animation
          p.classList.add('motion-pane-in');
          observeReveals(p);
        }
        state.set(p, now);
      });
    });
    panes.forEach((p) => mo.observe(p, { attributes: true, attributeFilter: ['class', 'hidden', 'style', 'aria-hidden'] }));
  }

  /* ---------------- 10. Ảnh: hiện mượt khi tải xong ---------------- */
  document.querySelectorAll('img.media__img').forEach((img) => {
    if (img.complete && img.naturalWidth) return img.classList.add('is-loaded');
    img.addEventListener('load', () => img.classList.add('is-loaded'), { once: true });
    img.addEventListener('error', () => img.classList.add('is-loaded'), { once: true });
  });
})();
