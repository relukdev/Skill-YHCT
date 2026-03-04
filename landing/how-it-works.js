/* How It Works — Interactivity */
(function () {
    'use strict';

    /* --- Scroll Reveal --- */
    const revealEls = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((e) => {
                if (e.isIntersecting) {
                    e.target.classList.add('visible');
                    revealObserver.unobserve(e.target);
                }
            });
        },
        { threshold: 0.12 }
    );
    revealEls.forEach((el) => revealObserver.observe(el));

    /* --- Nav scroll state --- */
    const nav = document.getElementById('nav');
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        if (y > 40) nav.classList.add('scrolled');
        else nav.classList.remove('scrolled');
        lastScroll = y;
    }, { passive: true });

    /* --- Tab Switching --- */
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            tabBtns.forEach((b) => b.classList.remove('active'));
            tabPanels.forEach((p) => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });

    /* --- Chat Replay Animation --- */
    const chatBody = document.getElementById('chatBody');
    if (chatBody) {
        const replayBtn = document.getElementById('replayChat');
        if (replayBtn) {
            replayBtn.addEventListener('click', () => {
                const msgs = chatBody.querySelectorAll('.chat-msg, .typing-indicator');
                msgs.forEach((m) => {
                    m.style.animation = 'none';
                    m.offsetHeight; // reflow
                    m.style.animation = '';
                });
            });
        }
    }

    /* --- Smooth scroll for anchor links --- */
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', (e) => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
})();
