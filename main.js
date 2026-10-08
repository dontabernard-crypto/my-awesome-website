// Wade Compliance Solutions — page behavior
(function () {
  'use strict';
  document.documentElement.classList.remove('no-js');

  var EMAIL = 'donta@wadecompliance.com';
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

  // Footer year
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
      var p = max > 0 ? window.scrollY / max : 0;
      if (progress) progress.style.setProperty('--p', p.toFixed(4));
      if (header) header.classList.toggle('scrolled', window.scrollY > 24);
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- Section rail + nav highlight ----------
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
      var i = Array.prototype.indexOf.call(el.parentElement.children, el) % 4;
      el.style.transitionDelay = i * 50 + 'ms';
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
          scene.style.setProperty('--ry', ((px / window.innerWidth - 0.5) * 14).toFixed(2) + 'deg');
          scene.style.setProperty('--rx', ((0.5 - py / window.innerHeight) * 10).toFixed(2) + 'deg');
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
    prime: { chipTitle: 'Partner letters ready', chipSub: 'For your proposal package', link: '#primes', linkText: 'See how teaming works' },
    soc2: { chipTitle: 'Evidence package ready', chipSub: 'Audit-ready documentation', link: '#soc2', linkText: 'Check your SOC 2 readiness' }
  };
  var currentPath = 'prime';
  var pathLink = $('[data-path-link]');
  function setPath(path) {
    if (!PATHS[path]) return;
    currentPath = path;
    $$('[data-view]').forEach(function (v) { v.hidden = v.getAttribute('data-view') !== path; });
    $('[data-chip-title]').textContent = PATHS[path].chipTitle;
    $('[data-chip-sub]').textContent = PATHS[path].chipSub;
    if (pathLink) { pathLink.setAttribute('href', PATHS[path].link); pathLink.textContent = PATHS[path].linkText; }
    setNeed(path);
    store('wcs-path', path);
  }
  $$('input[name="path"]').forEach(function (r) {
    r.addEventListener('change', function () { if (r.checked) setPath(r.value); });
  });

  // ---------- Prime: flip badges ----------
  $$('.badge').forEach(function (b) {
    b.addEventListener('click', function () {
      b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
    });
  });

  // ---------- SOC 2 readiness check ----------
  var TIERS = [
    { max: 2, title: 'Early stage', text: "Start with a gap assessment — we'll map every control you need and the fastest order to build them." },
    { max: 4, title: 'Getting close', text: 'Targeted remediation closes your remaining gaps, then we assemble evidence for the auditor.' },
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
    return { count: n, tier: tier.title, have: on.map(function (c) { return c.value; }) };
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

  // ---------- Book a demo wizard ----------
  var form = $('#demo-form');
  var step = 1;
  var notes = form.elements.notes;

  function setNeed(need) {
    var r = form.querySelector('input[name="need"][value="' + need + '"]');
    if (r) r.checked = true;
  }

  // Every "Book a demo" carries context into the form
  $$('[data-book]').forEach(function (a) {
    a.addEventListener('click', function () {
      setNeed(a.getAttribute('data-need') || currentPath);
      if (a.hasAttribute('data-carry-soc2')) {
        var s = updateSoc2();
        var line = 'SOC 2 self-check: ' + s.count + '/6 in place (' + s.tier + ')' + (s.have.length ? ' — have: ' + s.have.join(', ') : '');
        var existing = notes.value.replace(/^SOC 2 self-check:.*$/m, '').trim();
        notes.value = line + (existing ? '\n' + existing : '');
      }
      if (step === 4) goTo(1);
    });
  });

  // Sensible default day: the next five business days, first one preselected
  var daysBox = $('[data-days]');
  var dayFmt = { weekday: 'short' };
  var d = new Date();
  var made = 0;
  while (made < 5) {
    d.setDate(d.getDate() + 1);
    if (d.getDay() === 0 || d.getDay() === 6) continue;
    var label = document.createElement('label');
    label.className = 'day';
    var input = document.createElement('input');
    input.type = 'radio';
    input.name = 'day';
    input.value = d.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
    if (made === 0) input.checked = true;
    var face = document.createElement('span');
    var wk = document.createElement('small');
    wk.textContent = d.toLocaleDateString(undefined, dayFmt);
    var num = document.createElement('strong');
    num.textContent = String(d.getDate());
    face.appendChild(wk); face.appendChild(num);
    label.appendChild(input); label.appendChild(face);
    label.setAttribute('aria-label', input.value);
    daysBox.appendChild(label);
    made++;
  }
  var tz = '';
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { tz = ''; }
  if (tz) $('[data-tz]').textContent = 'Times in your time zone · ' + tz.replace(/_/g, ' ');

  var stepEls = $$('[data-step]', form);
  var stepperItems = $$('[data-stepper]', form);
  var stepperFill = $('[data-stepper-fill]', form);

  function goTo(n, focus) {
    step = n;
    stepEls.forEach(function (el) { el.hidden = Number(el.getAttribute('data-step')) !== n; });
    stepperItems.forEach(function (li) {
      var i = Number(li.getAttribute('data-stepper'));
      li.classList.toggle('is-current', i === n);
      li.classList.toggle('is-done', i < n);
      if (i === n) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
    });
    stepperFill.style.transform = 'scaleX(' + Math.min(n / 3, 1) + ')';
    if (focus) {
      var target = n === 4 ? stepEls[3] : $('input:checked, input, textarea', stepEls[n - 1]);
      if (target) target.focus({ preventScroll: true });
    }
  }

  $$('[data-next]', form).forEach(function (b) { b.addEventListener('click', function () { goTo(step + 1, true); }); });
  $$('[data-back]', form).forEach(function (b) { b.addEventListener('click', function () { goTo(step - 1, true); }); });

  // Enter on steps 1–2 advances instead of submitting
  form.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && step < 3 && e.target.tagName === 'INPUT') { e.preventDefault(); goTo(step + 1, true); }
  });

  // Inline validation: quiet until a field is touched, then live
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var required = ['name', 'org', 'email'];
  var submitBtn = $('[data-submit]', form);
  function valid(name) {
    var v = form.elements[name].value.trim();
    return name === 'email' ? EMAIL_RE.test(v) : v.length > 1;
  }
  function mark(name) { form.elements[name].setAttribute('aria-invalid', valid(name) ? 'false' : 'true'); }
  function refreshSubmit() {
    var ok = required.every(valid);
    submitBtn.setAttribute('aria-disabled', ok ? 'false' : 'true');
    return ok;
  }
  required.forEach(function (name) {
    var el = form.elements[name];
    var touched = false;
    el.addEventListener('blur', function () { if (el.value.trim()) { touched = true; mark(name); } });
    el.addEventListener('input', function () { if (touched) mark(name); refreshSubmit(); });
  });
  form.elements.email.addEventListener('blur', function () {
    form.elements.email.value = form.elements.email.value.trim().toLowerCase();
  });

  // Remember details for returning visitors
  ['name', 'org', 'email'].forEach(function (name) {
    var saved = store('wcs-' + name);
    if (saved) form.elements[name].value = saved;
  });
  refreshSubmit();

  var NEED_LABEL = { prime: 'Teaming as a certified partner (MBE / SB Micro / HUBZone)', soc2: 'SOC 2 readiness', other: 'Another compliance need' };

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!refreshSubmit()) {
      var first = null;
      required.forEach(function (n) { mark(n); if (!valid(n) && !first) first = form.elements[n]; });
      if (first) first.focus();
      return;
    }
    var f = form.elements;
    var need = NEED_LABEL[(form.querySelector('input[name="need"]:checked') || {}).value] || NEED_LABEL.other;
    var day = (form.querySelector('input[name="day"]:checked') || {}).value || 'Flexible';
    var time = (form.querySelector('input[name="time"]:checked') || {}).value || 'Flexible';
    ['name', 'org', 'email'].forEach(function (n) { store('wcs-' + n, f[n].value.trim()); });

    var subject = 'Demo request — ' + f.org.value.trim() + ' (' + need.split(' (')[0] + ')';
    var body = [
      'Topic: ' + need,
      'Preferred time: ' + day + ', ' + time + (tz ? ' (' + tz + ')' : ''),
      '',
      f.notes.value.trim() || '',
      '',
      '—',
      f.name.value.trim(),
      f.org.value.trim(),
      f.email.value.trim()
    ].join('\n').replace(/\n{3,}/g, '\n\n');

    $('[data-summary]', form).textContent = need + ' · ' + day + ', ' + time + '.';
    goTo(4, true);
    window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });

  // ---------- Restore last path ----------
  var savedPath = store('wcs-path');
  if (savedPath && PATHS[savedPath]) {
    var radio = $('input[name="path"][value="' + savedPath + '"]');
    if (radio) radio.checked = true;
    setPath(savedPath);
  } else {
    setPath('prime');
  }
  goTo(1);
})();
