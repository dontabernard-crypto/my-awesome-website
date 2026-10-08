// Wade Compliance Solutions — page behavior
(function () {
  'use strict';
  document.documentElement.classList.remove('no-js');

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  var year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());

  // ---------- Scroll: header state + progress bar ----------
  var header = $('.site-header');
  var progress = $('.scroll-progress span');
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      if (progress) progress.style.setProperty('--p', (max > 0 ? window.scrollY / max : 0).toFixed(4));
      if (header) header.classList.toggle('scrolled', window.scrollY > 24);
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- Section rail + nav highlight + mobile CTA ----------
  var sections = $$('[data-section]');
  var railLinks = $$('[data-rail]');
  var navLinks = $$('[data-nav]');
  var mobileCta = $('[data-mobile-cta]');
  if ('IntersectionObserver' in window) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var id = entry.target.id;
        var idx = sections.indexOf(entry.target);
        railLinks.forEach(function (a, i) {
          a.classList.toggle('active', a.getAttribute('href') === '#' + id);
          a.classList.toggle('done', i < idx);
        });
        navLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + id); });
        if (mobileCta) mobileCta.classList.toggle('hide', id === 'demo' || id === 'top');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { sectionObserver.observe(s); });
  } else if (mobileCta) {
    mobileCta.classList.remove('hide');
  }

  // ---------- Reveal on scroll ----------
  var reveals = $$('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.1 });
    reveals.forEach(function (el) {
      el.style.transitionDelay = (Array.prototype.indexOf.call(el.parentElement.children, el) % 4) * 50 + 'ms';
      revealObserver.observe(el);
    });
  }

  // ---------- Pointer effects ----------
  if (finePointer && !reduceMotion) {
    var glow = $('.cursor-glow');
    var scene = $('[data-parallax]');
    var px = 0, py = 0, pending = false;
    window.addEventListener('pointermove', function (e) {
      px = e.clientX; py = e.clientY;
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () {
        if (glow) { glow.style.setProperty('--mx', px + 'px'); glow.style.setProperty('--my', py + 'px'); }
        if (scene) {
          scene.style.setProperty('--ry', ((px / window.innerWidth - 0.5) * 12).toFixed(2) + 'deg');
          scene.style.setProperty('--rx', ((0.5 - py / window.innerHeight) * 8).toFixed(2) + 'deg');
        }
        pending = false;
      });
    }, { passive: true });

    $$('.tilt').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'perspective(1000px) rotateX(' + (-y * 6).toFixed(2) + 'deg) rotateY(' + (x * 8).toFixed(2) + 'deg) translateY(-4px)';
      });
      card.addEventListener('pointerleave', function () { card.style.transform = ''; });
    });
  }

  // ---------- Hero path chooser ----------
  var PATHS = {
    teaming: { chipTitle: 'Bid-ready', chipSub: 'Partner package complete', link: '#teaming', linkText: 'How teaming works' },
    soc2: { chipTitle: 'Audit-ready', chipSub: 'Evidence package complete', link: '#soc2', linkText: 'Check your SOC 2 readiness' }
  };
  var pathLink = $('[data-path-link]');
  function setPath(path) {
    if (!PATHS[path]) return;
    $$('[data-view]').forEach(function (v) { v.hidden = v.getAttribute('data-view') !== path; });
    $('[data-chip-title]').textContent = PATHS[path].chipTitle;
    $('[data-chip-sub]').textContent = PATHS[path].chipSub;
    if (pathLink) { pathLink.setAttribute('href', PATHS[path].link); pathLink.textContent = PATHS[path].linkText; }
    store('wcs-path', path);
  }
  $$('input[name="path"]').forEach(function (r) {
    r.addEventListener('change', function () { if (r.checked) setPath(r.value); });
  });
  var savedPath = store('wcs-path');
  if (savedPath && PATHS[savedPath]) {
    var radio = $('input[name="path"][value="' + savedPath + '"]');
    if (radio) radio.checked = true;
    setPath(savedPath);
  }

  // ---------- SOC 2 readiness check ----------
  var TIERS = [
    { max: 2, title: 'Early stage', text: "Start with a gap assessment. We'll map every control you need and the fastest order to build them." },
    { max: 4, title: 'Getting close', text: 'Targeted fixes close the remaining gaps — then we assemble evidence for your auditor.' },
    { max: 6, title: 'Nearly audit-ready', text: 'An evidence review and auditor prep can get you to your Type I or Type II report sooner.' }
  ];
  var checks = $$('input[name="soc2"]');
  var ring = $('[data-ring]');
  var CIRC = 2 * Math.PI * 52;
  function updateSoc2() {
    var on = checks.filter(function (c) { return c.checked; });
    var n = on.length;
    $('[data-count]').textContent = String(n);
    if (ring) ring.style.strokeDashoffset = String(CIRC * (1 - n / checks.length));
    var tier = TIERS.filter(function (t) { return n <= t.max; })[0];
    $('[data-tier-title]').textContent = tier.title;
    $('[data-tier-text]').textContent = tier.text;
    store('wcs-soc2', on.map(function (c) { return c.value; }).join('|'));
  }
  var savedSoc2 = (store('wcs-soc2') || '').split('|');
  checks.forEach(function (c) {
    c.checked = savedSoc2.indexOf(c.value) !== -1;
    c.addEventListener('change', updateSoc2);
  });
  updateSoc2();

  // ---------- Services tabs (arrow keys, Home/End) ----------
  var tabs = $$('[role="tab"]');
  function selectTab(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectTab(t); });
    t.addEventListener('keydown', function (e) {
      var next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
      if (e.key === 'Home') next = tabs[0];
      if (e.key === 'End') next = tabs[tabs.length - 1];
      if (next) { e.preventDefault(); selectTab(next, true); }
    });
  });

  // ---------- Book a demo: Google Calendar appointment schedule ----------
  // Full schedule links (calendar.google.com/calendar/appointments/schedules/…) are embedded on the page.
  // Short share links (calendar.app.google/…) can't be embedded, so they open in a new tab.
  var demo = $('#demo');
  var booking = $('[data-booking]');
  var bookingUrl = (demo.getAttribute('data-booking-url') || '').trim();
  var openLink = $('[data-booking-open]');
  var ctaLink = $('[data-booking-link]');
  var embeddable = /^https:\/\/calendar\.google\.com\/calendar\/(u\/\d+\/)?appointments\//.test(bookingUrl);

  if (bookingUrl && /^https:\/\//.test(bookingUrl)) {
    ctaLink.href = bookingUrl;
    openLink.href = bookingUrl;
    openLink.hidden = false;
  }

  if (embeddable) {
    var src = bookingUrl + (bookingUrl.indexOf('?') === -1 ? '?' : '&') + 'gv=true';
    var mount = function () {
      if (booking.querySelector('iframe')) return;
      var frame = document.createElement('iframe');
      frame.src = src;
      frame.title = 'Book a demo with Wade Compliance — Google Calendar';
      frame.loading = 'lazy';
      frame.addEventListener('load', function () { booking.classList.add('loaded'); });
      booking.appendChild(frame);
    };
    if ('IntersectionObserver' in window) {
      var bookingObserver = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { mount(); bookingObserver.disconnect(); }
      }, { rootMargin: '800px 0px' });
      bookingObserver.observe(booking);
    } else {
      mount();
    }
    // Any "Book a demo" click starts loading right away
    $$('a[href="#demo"]').forEach(function (a) { a.addEventListener('click', mount); });
  } else {
    booking.classList.add('is-link');
  }
})();
