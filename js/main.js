/**
 * iViTech - Modern Interactions & Simulator Scripts
 * Phiên bản hoàn thiện theo kế hoạch cải thiện UI/UX & Luồng chuyển đổi (P0, P1, P2)
 */

document.addEventListener('DOMContentLoaded', () => {
  initStickyHeader();
  initMobileMenu();
  initMegaDropdown();
  initCurrentPageIndicator();
  initPreselectedSolution();
  initHeroSimulator();
  initHeroRolePicker();
  initChallengeSolutionToggle();
  initRoadmapTabs();
  initUnifiedEcosystem();
  initContactForm();
  initBackToTop();
  initScrollSpy();
  initMobileStickyBar();
  initVideoShowcase();
  initVideoLightboxModal();
  initTracking();
});

// 1. Sticky Header
function initStickyHeader() {
  const header = document.querySelector('.main-header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, { passive: true });
}

// 2. Mobile Menu
function initMobileMenu() {
  const btn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('.nav-links');
  if (!btn || !nav) return;

  btn.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('mobile-open');
    btn.setAttribute('aria-expanded', isOpen);
    btn.innerHTML = isOpen 
      ? '<i class="fas fa-times"></i>' 
      : '<i class="fas fa-bars"></i>';
  });

  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('mobile-open');
      btn.setAttribute('aria-expanded', 'false');
      btn.innerHTML = '<i class="fas fa-bars"></i>';
    });
  });

  // ESC to close mobile menu
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('mobile-open')) {
      nav.classList.remove('mobile-open');
      btn.setAttribute('aria-expanded', 'false');
      btn.innerHTML = '<i class="fas fa-bars"></i>';
    }
  });
}

// 2b. Mega Dropdown Interactions (P0-2)
function initMegaDropdown() {
  const megaItem = document.querySelector('.nav-item.has-mega');
  const toggleBtn = document.getElementById('megaMenuBtn');
  const dropdown = megaItem ? megaItem.querySelector('.mega-dropdown') : null;
  if (!megaItem || !toggleBtn || !dropdown) return;

  let closeTimer = null;

  // Hover with 150ms close buffer
  megaItem.addEventListener('mouseenter', () => {
    if (closeTimer) clearTimeout(closeTimer);
    megaItem.classList.add('is-open');
    toggleBtn.setAttribute('aria-expanded', 'true');
  });

  megaItem.addEventListener('mouseleave', () => {
    closeTimer = setTimeout(() => {
      megaItem.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }, 150);
  });

  // Touch / Click toggle
  toggleBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const isOpen = megaItem.classList.toggle('is-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Keyboard navigation: Escape to close, click outside
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && megaItem.classList.contains('is-open')) {
      megaItem.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      toggleBtn.focus();
    }
  });

  document.addEventListener('click', (e) => {
    if (!megaItem.contains(e.target)) {
      megaItem.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });
}

// 2c. Current Page Indicator (P0-1)
function initCurrentPageIndicator() {
  let path = window.location.pathname.split('/').pop() || 'index.html';
  if (!path || path === '/') path = 'index.html';

  const megaLinks = document.querySelectorAll('.mega-sub-item a');
  megaLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.includes(path) && path !== 'index.html') {
      link.setAttribute('aria-current', 'page');
      const parentBtn = document.getElementById('megaMenuBtn');
      if (parentBtn) {
        parentBtn.setAttribute('aria-current', 'page');
      }
    }
  });
}

// 2d. Pre-select Solution in Contact Form via query param ?solution= (P0-5)
function initPreselectedSolution() {
  const params = new URLSearchParams(window.location.search);
  const solution = params.get('solution');
  if (!solution) return;

  const leadSolution = document.getElementById('leadSolution');
  if (leadSolution) {
    const map = {
      'digitization': 'Số hóa',
      'smart-ivier': 'Smart iVier',
      'ivihrm': 'iViHRM',
      'smart-study-2': 'Smart Study',
      'interactive-displays': 'Màn hình tương tác',
      'nexta': 'Nexta',
      'ivivi': 'iViVi'
    };
    const needle = map[solution];
    if (needle) {
      for (let i = 0; i < leadSolution.options.length; i++) {
        if (leadSolution.options[i].text.toLowerCase().includes(needle.toLowerCase())) {
          leadSolution.selectedIndex = i;
          break;
        }
      }
    }
  }

  if (window.location.hash === '#contact') {
    const contactEl = document.getElementById('contact');
    if (contactEl) {
      setTimeout(() => {
        contactEl.scrollIntoView({ behavior: 'smooth' });
      }, 250);
    }
  }
}

// 3. Hero Live Simulator (Smart iVier, iViHRM, iViVi)
function initHeroSimulator() {
  if (typeof SIMULATOR_DATA === 'undefined') return;

  const tabs = document.querySelectorAll('.sim-tab-trigger');
  const scenarioBtnsContainer = document.getElementById('simScenarioBtns');
  const queryDisplay = document.getElementById('smartIvierQuery');
  const responseDisplay = document.getElementById('smartIvierResponse');
  const citationsContainer = document.getElementById('simCitationsContainer');
  const verifiedDisplay = document.getElementById('simVerifiedDate');
  const disclaimerDisplay = document.getElementById('simDisclaimer');

  if (disclaimerDisplay && SIMULATOR_DATA.disclaimer) {
    disclaimerDisplay.textContent = SIMULATOR_DATA.disclaimer;
  }

  let currentTabKey = 'smart-ivier';
  let isTyping = false;

  function renderScenariosForTab(tabKey) {
    const tabData = SIMULATOR_DATA[tabKey];
    if (!tabData || !scenarioBtnsContainer) return;

    currentTabKey = tabKey;
    scenarioBtnsContainer.innerHTML = '';

    tabData.scenarios.forEach((sc, idx) => {
      const btn = document.createElement('button');
      btn.className = `btn btn-sm btn-secondary sim-sample-query ${idx === 0 ? 'active' : ''}`;
      btn.dataset.scenarioId = sc.id;
      btn.setAttribute('type', 'button');
      btn.innerHTML = `<i class="fas fa-chevron-right" style="font-size:0.7rem;margin-right:4px;"></i> ${sc.label}`;
      btn.addEventListener('click', () => {
        if (isTyping) return;
        scenarioBtnsContainer.querySelectorAll('.sim-sample-query').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        playScenario(sc);
      });
      scenarioBtnsContainer.appendChild(btn);
    });

    if (tabData.scenarios.length > 0) {
      playScenario(tabData.scenarios[0], false);
    }

    // Sync Video Preview Trigger in hero simulator
    const simVideoLink = document.getElementById('simVideoLink');
    const simVideoLabel = document.getElementById('simVideoLabel');
    if (simVideoLink) {
      if (tabKey === 'smart-ivier') {
        simVideoLink.style.display = 'inline-flex';
        simVideoLink.setAttribute('data-video-open', 'smart-ivier-short');
        if (simVideoLabel) simVideoLabel.textContent = 'Xem video Smart iVier thực tế (4:05)';
      } else if (tabKey === 'ivivi') {
        simVideoLink.style.display = 'inline-flex';
        simVideoLink.setAttribute('data-video-open', 'ivivi-ai');
        if (simVideoLabel) simVideoLabel.textContent = 'Xem video lớp học iViVi Robotics (2:35)';
      } else {
        // iViHRM has no video currently
        simVideoLink.style.display = 'none';
      }
    }
  }

  function playScenario(sc, animate = true) {
    if (!queryDisplay || !responseDisplay) return;

    queryDisplay.textContent = sc.question;
    if (verifiedDisplay) {
      verifiedDisplay.textContent = `Căn cứ cập nhật đến: ${sc.verifiedAt || '15/01/2026'}`;
    }

    // Render citations
    if (citationsContainer) {
      citationsContainer.innerHTML = '<span style="font-size:0.75rem;font-weight:700;color:#64748b;margin-right:6px;"><i class="fas fa-shield-halved text-green"></i> Căn cứ:</span>';
      if (sc.citations && sc.citations.length > 0) {
        sc.citations.forEach(c => {
          const chip = document.createElement('span');
          chip.className = 'cite-chip';
          chip.title = c.tooltip || '';
          chip.innerHTML = `${c.text} <i class="fas fa-info-circle" style="font-size:0.65rem;"></i>`;
          citationsContainer.appendChild(chip);
        });
      }
    }

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!animate || prefersReducedMotion) {
      responseDisplay.innerHTML = sc.response.map(line => `<p style="margin-bottom:6px;">${line}</p>`).join('');
      return;
    }

    // Typing simulation (600-900ms)
    isTyping = true;
    responseDisplay.innerHTML = `
      <div class="sim-typing-dots">
        <span class="sim-typing-dot"></span>
        <span class="sim-typing-dot"></span>
        <span class="sim-typing-dot"></span>
        <span style="font-size:0.78rem;color:#64748b;margin-left:6px;">AI đang truy xuất căn cứ pháp lý & dữ liệu...</span>
      </div>
    `;

    setTimeout(() => {
      let lineIndex = 0;
      responseDisplay.innerHTML = '';
      const lines = sc.response;

      const interval = setInterval(() => {
        if (lineIndex < lines.length) {
          const p = document.createElement('p');
          p.style.marginBottom = '6px';
          p.textContent = lines[lineIndex];
          responseDisplay.appendChild(p);
          lineIndex++;
        } else {
          clearInterval(interval);
          isTyping = false;
        }
      }, 120);
    }, 650);
  }

  // Handle Tab Switch
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const targetKey = tab.dataset.targetKey;
      renderScenariosForTab(targetKey);
    });

    // Keyboard arrow keys navigation for tablist
    tab.addEventListener('keydown', (e) => {
      const tabList = Array.from(tabs);
      const index = tabList.indexOf(tab);
      let nextTab = null;

      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        nextTab = tabList[(index + 1) % tabList.length];
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        nextTab = tabList[(index - 1 + tabList.length) % tabList.length];
      }

      if (nextTab) {
        nextTab.focus();
        nextTab.click();
      }
    });
  });

  // simVideoLink click: scroll to embedded video in roadmap
  const simVideoBtn = document.getElementById('simVideoLink');
  if (simVideoBtn) {
    simVideoBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const currentTab = document.querySelector('.sim-tab.active')?.dataset.tab;
      if (currentTab === 'ivivi') {
        const schoolBtn = document.querySelector('.org-pill-btn[data-org="school"]');
        if (schoolBtn) schoolBtn.click();
        const iviviChip = document.querySelector('[data-roadmap-school-vid="1-Vt5HCICZY"]');
        if (iviviChip) iviviChip.click();
      } else {
        const govBtn = document.querySelector('.org-pill-btn[data-org="gov"]');
        if (govBtn) govBtn.click();
      }
      const targetWrap = document.getElementById('roadmapRoleMediaWrap');
      if (targetWrap) {
        targetWrap.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetWrap.classList.add('video-highlight-pulse');
        setTimeout(() => targetWrap.classList.remove('video-highlight-pulse'), 3000);
      }
    });
  }

  // Initial load
  renderScenariosForTab('smart-ivier');
}

// 4. Hero Role Picker (Scrolls to roadmap, selects tab & pre-fills form)
function initHeroRolePicker() {
  const roleButtons = document.querySelectorAll('.role-chip-btn');
  const orgTypeSelect = document.getElementById('leadOrgType');
  const orgRadioInputs = document.querySelectorAll('input[name="org_type_choice"]');

  roleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      roleButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const role = btn.dataset.role; // 'gov', 'business', 'school'

      // Save to sessionStorage
      try {
        sessionStorage.setItem('ivitech_user_role', role);
      } catch (err) {
        // safe ignore
      }

      // Sync with Roadmap section tab
      const roadmapBtn = document.querySelector(`.org-pill-btn[data-org="${role}"]`);
      if (roadmapBtn) {
        roadmapBtn.click();
      }

      // Pre-select form radio
      if (orgRadioInputs) {
        orgRadioInputs.forEach(r => {
          if (r.value === role) {
            r.checked = true;
            r.closest('.role-radio-label')?.classList.add('active');
          } else {
            r.closest('.role-radio-label')?.classList.remove('active');
          }
        });
      }

      // Smooth scroll to roadmap
      const roadmapSection = document.getElementById('roadmap');
      if (roadmapSection) {
        roadmapSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// 5. Problem vs Solution Toggle (Concise, without H02/H03 labels)
function initChallengeSolutionToggle() {
  const btns = document.querySelectorAll('.toggle-view-btn');
  const viewProblem = document.getElementById('viewChallenges');
  const viewApproach = document.getElementById('viewApproach');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const target = btn.dataset.view;
      if (target === 'challenges') {
        if (viewProblem) viewProblem.style.display = 'grid';
        if (viewApproach) viewApproach.style.display = 'none';
      } else {
        if (viewProblem) viewProblem.style.display = 'none';
        if (viewApproach) viewApproach.style.display = 'block';
      }
    });
  });
}

// 6. Organization Roadmap Tabs
function initRoadmapTabs() {
  const buttons = document.querySelectorAll('.org-pill-btn');
  const title = document.getElementById('orgRoadmapTitle');
  const desc = document.getElementById('orgRoadmapDesc');
  const rec1 = document.getElementById('orgRec1');
  const rec2 = document.getElementById('orgRec2');
  const benefit = document.getElementById('orgBenefit');

  const roadmapData = {
    gov: {
      title: 'Dành cho cơ quan nhà nước, UBND xã/phường và đơn vị hành chính công',
      desc: 'Giải tỏa áp lực xử lý hồ sơ một cửa, chuẩn hóa kho lưu trữ lịch sử và trang bị trợ lý công vụ chuẩn pháp lý cho cán bộ chuyên môn.',
      rec1: 'Smart iVier (Bộ 3 trợ lý AI: Công vụ, Pháp luật, Soạn thảo văn bản)',
      rec2: 'Chỉnh lý và số hóa hồ sơ lưu trữ theo chuẩn quy định văn thư',
      benefit: 'Giúp rút ngắn đáng kể thời gian xử lý thủ tục, văn bản soạn thảo chuẩn theo thể thức Nghị định 30/2020/NĐ-CP, bảo vệ trách nhiệm cán bộ.'
    },
    business: {
      title: 'Dành cho doanh nghiệp, tập đoàn và bộ phận quản trị nhân sự (HR)',
      desc: 'Hợp nhất toàn bộ dữ liệu nhân sự, tự động bóc tách hồ sơ ứng viên bằng AI OCR và chuẩn hóa quy trình chấm công, tính lương minh bạch.',
      rec1: 'iViHRM (Nền tảng quản trị nhân sự tập trung ứng dụng AI OCR)',
      rec2: 'Số hóa và chuẩn hóa hồ sơ tài liệu doanh nghiệp',
      benefit: 'Tự động hóa hơn 60% thao tác giấy tờ thủ công của phòng nhân sự, loại bỏ sai sót tính lương, quản trị dữ liệu tập trung.'
    },
    school: {
      title: 'Dành cho nhà trường, giáo viên, phụ huynh và học sinh K-12',
      desc: 'Kết nối thiết bị, học liệu số và phương pháp 20/80 giúp học sinh phát triển năng lực số, ngoại ngữ và tư duy sáng tạo cùng AI/Robotics.',
      rec1: 'Môi trường học tập số (Máy tính bảng Smart Study 2 + Màn hình tương tác + App Nexta)',
      rec2: 'Chương trình giáo dục công nghệ iViVi (Robotics, AI, Năng lực số 20/80)',
      benefit: 'Học sinh được thực hành sáng tạo 80% thời lượng, chuyển hóa từ người dùng công nghệ thụ động sang người tự tin làm chủ công nghệ.'
    }
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const type = btn.dataset.org;
      const data = roadmapData[type];
      if (data && title) {
        title.textContent = data.title;
        desc.textContent = data.desc;
        rec1.textContent = data.rec1;
        rec2.textContent = data.rec2;
        benefit.textContent = data.benefit;
      }

      // Switch role embed container with 200ms fade
      const roleEmbeds = document.querySelectorAll('.roadmap-role-embed');
      roleEmbeds.forEach(re => {
        if (re.dataset.roleEmbed === type) {
          re.style.display = 'block';
          re.style.opacity = '0';
          setTimeout(() => {
            re.style.transition = 'opacity 200ms ease';
            re.style.opacity = '1';
          }, 10);
        } else {
          re.style.display = 'none';
        }
      });
    });

    // Arrow keys support
    btn.addEventListener('keydown', (e) => {
      const btnList = Array.from(buttons);
      const index = btnList.indexOf(btn);
      let nextBtn = null;
      if (e.key === 'ArrowRight') nextBtn = btnList[(index + 1) % btnList.length];
      if (e.key === 'ArrowLeft') nextBtn = btnList[(index - 1 + btnList.length) % btnList.length];
      if (nextBtn) {
        nextBtn.focus();
        nextBtn.click();
      }
    });
  });

  // School role video switcher chips (Lớp học số <-> Robotics)
  const schoolChips = document.querySelectorAll('[data-roadmap-school-vid]');
  const schoolIframe = document.getElementById('roadmapSchoolIframe');
  const schoolDur = document.getElementById('roadmapSchoolDur');
  schoolChips.forEach(chip => {
    chip.addEventListener('click', () => {
      schoolChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const vidId = chip.dataset.roadmapSchoolVid;
      const dur = chip.dataset.vidDur;
      const title = chip.dataset.vidTitle;
      if (schoolIframe && vidId) {
        schoolIframe.src = `https://www.youtube-nocookie.com/embed/${vidId}?rel=0`;
        if (title) schoolIframe.title = title;
      }
      if (schoolDur && dur) {
        schoolDur.textContent = `Thời lượng: ${dur}`;
      }
    });
  });
}

// 7. Unified 4-Layer Ecosystem (Architecture + Detail unified with deep linking)
function initUnifiedEcosystem() {
  const tabs = document.querySelectorAll('.eco-stack-tab');
  const panes = document.querySelectorAll('.eco-pane');

  function activateLayer(layerId) {
    tabs.forEach(t => {
      const isActive = t.dataset.layer === layerId;
      t.classList.toggle('active', isActive);
      t.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    panes.forEach(p => {
      const isActive = p.id === `ecoPane-${layerId}`;
      p.classList.toggle('active', isActive);
    });
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const layerId = tab.dataset.layer;
      activateLayer(layerId);
      // update hash without abrupt jump
      if (history.replaceState) {
        history.replaceState(null, '', `#ecosystem/${layerId}`);
      }
    });

    tab.addEventListener('keydown', (e) => {
      const tabList = Array.from(tabs);
      const index = tabList.indexOf(tab);
      let next = null;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = tabList[(index + 1) % tabList.length];
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = tabList[(index - 1 + tabList.length) % tabList.length];
      if (next) {
        next.focus();
        next.click();
      }
    });
  });

  // Handle URL deep link e.g. #ecosystem/layer-2 or #ecosystem?layer=2
  function checkUrlHash() {
    const hash = window.location.hash;
    if (hash.includes('layer-1')) activateLayer('layer-1');
    else if (hash.includes('layer-2')) activateLayer('layer-2');
    else if (hash.includes('layer-3')) activateLayer('layer-3');
    else if (hash.includes('layer-4')) activateLayer('layer-4');
  }

  checkUrlHash();
  window.addEventListener('hashchange', checkUrlHash);
}

// 8. Contact Form Submission, Validation & Privacy Consent
function initContactForm() {
  const form = document.getElementById('ivitechLeadForm');
  const toast = document.getElementById('ivitechToast');
  const optionalToggle = document.getElementById('toggleOptionalFields');
  const optionalWrap = document.getElementById('optionalFieldsWrap');

  if (!form) return;

  // Toggle optional fields
  if (optionalToggle && optionalWrap) {
    optionalToggle.addEventListener('click', () => {
      const isOpen = optionalWrap.classList.toggle('open');
      optionalToggle.innerHTML = isOpen 
        ? '<i class="fas fa-minus-circle"></i> Thu gọn thông tin chi tiết' 
        : '<i class="fas fa-plus-circle"></i> Thêm thông tin để tư vấn chính xác hơn';
    });
  }

  // Radio selection styling
  const radioLabels = form.querySelectorAll('.role-radio-label');
  radioLabels.forEach(label => {
    label.addEventListener('click', () => {
      radioLabels.forEach(l => l.classList.remove('active'));
      label.classList.add('active');
    });
  });

  // Load saved role from sessionStorage
  try {
    const savedRole = sessionStorage.getItem('ivitech_user_role');
    if (savedRole) {
      const targetRadio = form.querySelector(`input[name="org_type_choice"][value="${savedRole}"]`);
      if (targetRadio) {
        targetRadio.checked = true;
        radioLabels.forEach(l => l.classList.remove('active'));
        targetRadio.closest('.role-radio-label')?.classList.add('active');
      }
    }
  } catch (e) {}

  // Form submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nameInput = document.getElementById('leadName');
    const phoneInput = document.getElementById('leadPhone');
    const consentInput = document.getElementById('leadConsent');
    const phoneError = document.getElementById('phoneError');
    const consentError = document.getElementById('consentError');

    let isValid = true;

    // Reset errors
    phoneError.classList.remove('show');
    phoneInput.classList.remove('input-invalid');
    if (consentError) consentError.classList.remove('show');

    // Phone validation regex for Vietnam: (0|+84) followed by 9-10 digits
    const vnPhoneRegex = /^(0|\+84)\d{9,10}$/;
    const phoneValue = phoneInput.value.trim().replace(/\s+/g, '');

    if (!vnPhoneRegex.test(phoneValue)) {
      phoneInput.classList.add('input-invalid');
      phoneError.classList.add('show');
      phoneInput.setAttribute('aria-invalid', 'true');
      phoneInput.focus();
      isValid = false;
    } else {
      phoneInput.setAttribute('aria-invalid', 'false');
    }

    // Consent checkbox check
    if (consentInput && !consentInput.checked) {
      if (consentError) consentError.classList.add('show');
      if (isValid) consentInput.focus();
      isValid = false;
    }

    if (!isValid) return;

    // Loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang gửi yêu cầu...';

    const formData = {
      name: nameInput.value.trim(),
      phone: phoneValue,
      email: document.getElementById('leadEmail')?.value.trim() || '',
      organization: document.getElementById('leadOrg')?.value.trim() || '',
      org_type: form.querySelector('input[name="org_type_choice"]:checked')?.value || 'Chưa chọn',
      solution_interest: document.getElementById('leadSolution')?.value || 'Tư vấn chung',
      message: document.getElementById('leadMessage')?.value.trim() || '',
      submitted_at: new Date().toISOString()
    };

    // Tracking event
    trackEvent('ContactForm', 'SubmitAttempt', formData.org_type);

    try {
      // Mock API call / FORM_ENDPOINT
      const FORM_ENDPOINT = 'https://api.ivitech.vn/v1/contact';
      
      // Simulate fast network dispatch
      await new Promise(resolve => setTimeout(resolve, 800));

      // Reset and display success toast
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
      form.reset();

      // Clear radio styling
      radioLabels.forEach(l => l.classList.remove('active'));

      if (toast) {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 5000);
      }

      trackEvent('ContactForm', 'SubmitSuccess', formData.org_type);

    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
      alert('Có lỗi xảy ra khi kết nối máy chủ. Vui lòng liên hệ trực tiếp hotline 0989 318 789 hoặc Zalo để được hỗ trợ ngay.');
      trackEvent('ContactForm', 'SubmitError', err.message);
    }
  });
}

// 9. Scroll Spy (Highlights active navigation menu item)
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links .nav-link');

  if (sections.length === 0 || navLinks.length === 0) return;

  window.addEventListener('scroll', () => {
    let current = '';
    const scrollPos = window.scrollY + 120;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      const href = link.getAttribute('href');
      if (href === `#${current}` || (current === 'ecosystem' && href.includes('ecosystem'))) {
        link.classList.add('active');
      }
    });
  }, { passive: true });
}

// 10. Mobile Sticky Bottom Bar (Hides when Contact Section is visible)
function initMobileStickyBar() {
  const bar = document.querySelector('.mobile-sticky-bar');
  const contactSection = document.getElementById('contact');

  if (!bar || !contactSection) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        bar.classList.add('hide-bar');
      } else {
        bar.classList.remove('hide-bar');
      }
    });
  }, { threshold: 0.15 });

  observer.observe(contactSection);
}

// 11. Back to Top Button
function initBackToTop() {
  const btn = document.getElementById('ivitechBackToTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      btn.classList.add('show');
    } else {
      btn.classList.remove('show');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// 12. Event Tracking Helper
function initTracking() {
  document.querySelectorAll('[data-cta]').forEach(el => {
    el.addEventListener('click', () => {
      const ctaName = el.getAttribute('data-cta');
      trackEvent('CTA', 'Click', ctaName);
    });
  });
}

function trackEvent(category, action, label) {
  // Console logging for audit & integration with Google Analytics (gtag/dataLayer)
  if (typeof window.dataLayer !== 'undefined') {
    window.dataLayer.push({
      event: 'custom_event',
      eventCategory: category,
      eventAction: action,
      eventLabel: label
    });
  }
}

// 13. Video Showcase Cards (Dynamic Thumbnails & Metadata)
function initVideoShowcase() {
  const videoCards = document.querySelectorAll('.video-card[data-video]');
  if (!videoCards.length) return;

  const videos = window.IVITECH_VIDEOS || {};

  videoCards.forEach(card => {
    const videoKey = card.getAttribute('data-video');
    const data = videos[videoKey];
    if (!data) return;

    const thumbUrl = `https://i.ytimg.com/vi/${data.id}/hqdefault.jpg`;

    card.innerHTML = `
      <div class="video-card-thumb" style="background-image: url('${thumbUrl}'); background-size: cover; background-position: center; width: 100%; height: 100%;">
        <div class="video-card-overlay">
          <div class="video-card-top">
            ${data.badge ? `<span class="video-card-badge"><i class="fas fa-play" style="font-size:0.6rem;"></i> ${data.badge}</span>` : '<span></span>'}
            <span class="video-card-duration"><i class="far fa-clock" aria-hidden="true"></i> ${data.duration}</span>
          </div>
          <button type="button" class="video-play-center" aria-label="Phát video: ${data.title}" data-video-open="${videoKey}">
            <i class="fas fa-play" aria-hidden="true"></i>
          </button>
          <div class="video-card-bottom">
            <h5 class="video-card-title">${data.title}</h5>
          </div>
        </div>
      </div>
    `;

    // Click whole thumb to trigger modal
    const thumbWrap = card.querySelector('.video-card-thumb');
    if (thumbWrap) {
      thumbWrap.style.cursor = 'pointer';
      thumbWrap.addEventListener('click', (e) => {
        // Prevent if clicking on already attached button event
        if (e.target.closest('.video-play-center')) return;
        openVideoModal(videoKey);
      });
    }
  });
}

// 14. Video Lightbox Modal
let lastActiveVideoTrigger = null;

function initVideoLightboxModal() {
  const modal = document.getElementById('ivitechVideoModal');
  const closeBtn = document.getElementById('videoModalCloseBtn');
  const iframeWrap = document.getElementById('videoModalIframeWrap');
  if (!modal || !iframeWrap) return;

  // Delegate clicks on any button or element with [data-video-open]
  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-video-open]');
    if (trigger) {
      e.preventDefault();
      lastActiveVideoTrigger = trigger;
      const videoKey = trigger.getAttribute('data-video-open');
      openVideoModal(videoKey);
    }
  });

  // Close via button
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      closeVideoModal();
    });
  }

  // Close via backdrop click outside dialog
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeVideoModal();
    }
  });

  // Close via Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) {
      closeVideoModal();
    }
  });
}

function openVideoModal(videoKey) {
  const modal = document.getElementById('ivitechVideoModal');
  const iframeWrap = document.getElementById('videoModalIframeWrap');
  const modalTitle = document.getElementById('videoModalTitle');
  const modalDuration = document.getElementById('videoModalDuration');
  const closeBtn = document.getElementById('videoModalCloseBtn');

  if (!modal || !iframeWrap) return;

  const videos = window.IVITECH_VIDEOS || {};
  const data = videos[videoKey];
  if (!data) return;

  if (modalTitle) modalTitle.textContent = data.title;
  if (modalDuration) {
    modalDuration.innerHTML = `<i class="far fa-clock" aria-hidden="true"></i> <span>Thời lượng: ${data.duration}</span>`;
  }

  // Inject privacy-enhanced YouTube embed (youtube-nocookie)
  iframeWrap.innerHTML = `
    <iframe
      src="https://www.youtube-nocookie.com/embed/${data.id}?autoplay=1&rel=0&modestbranding=1&playsinline=1"
      title="${data.title}"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen
      loading="lazy"
      class="video-modal-iframe">
    </iframe>
  `;

  modal.hidden = false;
  setTimeout(() => {
    modal.classList.add('is-open');
  }, 10);
  document.body.style.overflow = 'hidden';

  trackEvent('Video', 'OpenModal', data.title);

  // Focus trap: set focus on close button
  setTimeout(() => {
    if (closeBtn) closeBtn.focus();
  }, 50);
}

function closeVideoModal() {
  const modal = document.getElementById('ivitechVideoModal');
  const iframeWrap = document.getElementById('videoModalIframeWrap');

  if (!modal) return;

  modal.classList.remove('is-open');

  // Crucial: Clear iframe DOM immediately to terminate YouTube audio/video playback
  if (iframeWrap) {
    iframeWrap.innerHTML = '';
  }

  setTimeout(() => {
    modal.hidden = true;
  }, 200);
  document.body.style.overflow = '';

  // Restore keyboard focus to the triggering element
  if (lastActiveVideoTrigger) {
    try {
      lastActiveVideoTrigger.focus();
    } catch (e) {
      // safe ignore
    }
  }
}

