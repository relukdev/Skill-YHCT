/* ============================================
   AI YHCT Landing Page — Scripts
   ============================================ */

(function () {
  'use strict';

  // === Navbar scroll effect & UI States ===
  const nav = document.getElementById('nav');
  let lastScrollY = window.scrollY;

  function updateNavState() {
    if (!nav) return;

    // Calculate and set nav height variable for main padding
    const navHeight = nav.offsetHeight;
    document.documentElement.style.setProperty('--nav-height', `${navHeight}px`);

    // Handle scroll direction and stuck state
    const currentScrollY = window.scrollY;

    if (currentScrollY > 40) {
      nav.classList.add('scrolled');

      // Hide nav when scrolling down, show when scrolling up
      if (currentScrollY > lastScrollY && currentScrollY > navHeight * 2) {
        nav.style.transform = `translateY(-${navHeight}px)`; // Hide
      } else {
        nav.style.transform = 'translateY(0)'; // Show
      }
    } else {
      nav.classList.remove('scrolled');
      nav.style.transform = 'translateY(0)';
    }

    lastScrollY = currentScrollY;
  }

  // Run on load, scroll, and resize
  window.addEventListener('load', updateNavState);
  window.addEventListener('scroll', updateNavState, { passive: true });
  window.addEventListener('resize', updateNavState, { passive: true });

  // === Scroll Reveal (IntersectionObserver) ===
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) { observer.observe(el); });
  } else {
    // Fallback: show all
    reveals.forEach(function (el) { el.classList.add('visible'); });
  }

  // === FAQ Accordion ===
  document.querySelectorAll('.faq-q').forEach(function (q) {
    q.addEventListener('click', function () {
      var item = q.parentElement;
      var answer = item.querySelector('.faq-a');
      var inner = item.querySelector('.faq-a-inner');
      var isOpen = item.classList.contains('open');

      // Close all others
      document.querySelectorAll('.faq-item.open').forEach(function (openItem) {
        openItem.classList.remove('open');
        openItem.querySelector('.faq-a').style.maxHeight = '0';
      });

      // Toggle current
      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = inner.scrollHeight + 'px';
      }
    });
  });

  // === Smooth Scroll for anchor links ===
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var targetId = link.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        var navHeight = nav ? nav.offsetHeight : 0;
        var top = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 8;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  // === Bottom Sheet Controller ===
  const sheetOverlay = document.getElementById('sheetOverlay');
  const registerSheet = document.getElementById('registerSheet');
  const closeSheetBtn = document.getElementById('closeSheetBtn');
  const ctaButtons = document.querySelectorAll('.nav-cta, #cta-main, .hero-actions .btn-primary, .final-cta .btn-primary');

  function openSheet() {
    if (!sheetOverlay || !registerSheet) return;
    sheetOverlay.classList.add('active');
    registerSheet.classList.add('active');
    document.body.style.overflow = 'hidden'; // Ngăn scroll nền
  }

  function closeSheet() {
    if (!sheetOverlay || !registerSheet) return;
    sheetOverlay.classList.remove('active');
    registerSheet.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Bind events
  ctaButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openSheet();
    });
  });

  if (closeSheetBtn) closeSheetBtn.addEventListener('click', closeSheet);
  if (sheetOverlay) sheetOverlay.addEventListener('click', closeSheet);

  // Handle swipe down to close (Native feel)
  let touchStartY = 0;
  if (registerSheet) {
    registerSheet.addEventListener('touchstart', e => {
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    registerSheet.addEventListener('touchend', e => {
      const touchEndY = e.changedTouches[0].screenY;
      if (touchEndY - touchStartY > 100) { // Swipe down distance threshold
        closeSheet();
      }
    }, { passive: true });
  }
})();
