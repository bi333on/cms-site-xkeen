/**
 * Анимированный фон с частицами.
 * Тема определяется классом body: bg-particles, bg-summer, bg-winter,
 * bg-spring, bg-autumn, bg-newyear.
 * Каждый тип частицы — это span с классом .bg-particle и модификатором формы.
 */
(function () {
    'use strict';

    var THEMES = {
        particles: { count: 14, shapes: ['dot'], colors: ['#FF6B00', '#FFA34D'], rise: true },
        summer:    { count: 12, shapes: ['leaf'], colors: ['#4CAF50', '#81C784', '#AED581'], rise: true },
        winter:    { count: 22, shapes: ['snow'], colors: ['#FFFFFF', '#B3E5FC', '#81D4FA'], size: [8, 16] },
        spring:    { count: 14, shapes: ['petal'], colors: ['#F8BBD0', '#E1BEE7', '#FFE082'] },
        autumn:    { count: 14, shapes: ['leaf'], colors: ['#E65100', '#F57C00', '#FFB300', '#8D6E63'] },
        newyear:   { count: 14, shapes: ['dot', 'star', 'bauble'], colors: ['#FFD54F', '#FF6B00', '#4FC3F7', '#F06292'] }
    };

    var container = document.getElementById('bgParticles');
    if (!container) return;

    // Слой показываем только если тема определена и анимации разрешены.
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion) return;

    var theme = null;
    var bodyClass = document.body.className || '';
    var m = bodyClass.match(/bg-theme-([a-z]+)/);
    if (m && THEMES[m[1]]) theme = m[1];
    if (!theme) return;

    var cfg = THEMES[theme];

    function pick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    for (var i = 0; i < cfg.count; i++) {
        var el = document.createElement('span');
        el.className = 'bg-particle bgp-' + pick(cfg.shapes) + (cfg.rise ? ' bgp-rise' : '');
        el.style.left = (Math.random() * 100) + '%';
        el.style.animationDuration = (10 + Math.random() * 14) + 's';
        el.style.animationDelay = (-Math.random() * 20) + 's';
        el.style.background = pick(cfg.colors);
        var size = cfg.size ? (cfg.size[0] + Math.random() * (cfg.size[1] - cfg.size[0])) : (5 + Math.random() * 9);
        el.style.width = size + 'px';
        el.style.height = size + 'px';
        container.appendChild(el);
    }
})();
