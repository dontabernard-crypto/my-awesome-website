// Wade Compliance Solutions — page behavior
(function () {
  'use strict';
  document.documentElement.classList.remove('no-js');

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Footer year
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  // Header gets denser once the page scrolls
  var header = document.querySelector('.site-header');
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 24);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Scroll reveal
  var reveals = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    reveals.forEach(function (el, i) {
      // Stagger siblings in the same grid
      el.style.transitionDelay = (Array.prototype.indexOf.call(el.parentElement.children, el) % 4) * 80 + 'ms';
      io.observe(el);
    });
  }

  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // Hero scene follows the pointer
  var scene = document.querySelector('[data-parallax]');
  if (scene && finePointer && !reduceMotion) {
    window.addEventListener('pointermove', function (e) {
      var x = e.clientX / window.innerWidth - 0.5;
      var y = e.clientY / window.innerHeight - 0.5;
      scene.style.setProperty('--ry', (x * 14).toFixed(2) + 'deg');
      scene.style.setProperty('--rx', (-y * 10).toFixed(2) + 'deg');
    }, { passive: true });
  }

  // Cards tilt toward the pointer
  if (finePointer && !reduceMotion) {
    document.querySelectorAll('.tilt').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'perspective(1000px) rotateX(' + (-y * 6).toFixed(2) + 'deg) rotateY(' + (x * 8).toFixed(2) + 'deg) translateY(-6px)';
      });
      card.addEventListener('pointerleave', function () { card.style.transform = ''; });
    });
  }

  // Contact form: validate, then open the visitor's email client addressed to Wade Compliance
  var form = document.getElementById('contact-form');
  if (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fields = form.querySelectorAll('input[required], textarea[required]');
      var firstBad = null;
      fields.forEach(function (f) {
        var ok = f.value.trim() !== '' && (f.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim()));
        f.setAttribute('aria-invalid', ok ? 'false' : 'true');
        if (!ok && !firstBad) firstBad = f;
      });
      if (firstBad) {
        status.textContent = 'Please fill in your name, a valid work email and a short message.';
        firstBad.focus();
        return;
      }
      var data = new FormData(form);
      var subject = 'Readiness scan request — ' + data.get('name') + (data.get('org') ? ' (' + data.get('org') + ')' : '');
      var body = data.get('message') + '\n\n—\n' + data.get('name') + (data.get('org') ? '\n' + data.get('org') : '') + '\n' + data.get('email');
      window.location.href = 'mailto:donta@wadecompliance.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      status.textContent = 'Opening your email app… If nothing happens, write to donta@wadecompliance.com.';
    });
  }
})();
