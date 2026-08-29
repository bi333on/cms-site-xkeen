/**
 * Falling Stars Animation
 * Creates subtle falling stars on light background
 */
(function() {
    var canvas = document.getElementById('stars-canvas');
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var stars = [];
    var STAR_COUNT = 80;
    var w, h;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function randomStar() {
        return {
            x: Math.random() * w,
            y: Math.random() * h * -1,
            size: Math.random() * 1.8 + 0.4,
            speed: Math.random() * 0.4 + 0.15,
            opacity: Math.random() * 0.22 + 0.04,
            twinkleSpeed: Math.random() * 0.01 + 0.003,
            twinkleOffset: Math.random() * Math.PI * 2,
            angle: (Math.random() - 0.5) * 0.35
        };
    }

    function init() {
        stars = [];
        for (var i = 0; i < STAR_COUNT; i++) {
            var s = randomStar();
            s.y = Math.random() * h;
            stars.push(s);
        }
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);

        for (var i = 0; i < stars.length; i++) {
            var s = stars[i];
            var flicker = Math.sin(Date.now() * s.twinkleSpeed + s.twinkleOffset) * 0.5 + 0.5;
            var alpha = s.opacity * (0.6 + flicker * 0.4);

            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = '#D4A574';

            var cx = s.x;
            var cy = s.y;
            var r = s.size;

            ctx.beginPath();
            ctx.moveTo(cx, cy - r);
            ctx.lineTo(cx + r * 0.3, cy - r * 0.3);
            ctx.lineTo(cx + r, cy);
            ctx.lineTo(cx + r * 0.3, cy + r * 0.3);
            ctx.lineTo(cx, cy + r);
            ctx.lineTo(cx - r * 0.3, cy + r * 0.3);
            ctx.lineTo(cx - r, cy);
            ctx.lineTo(cx - r * 0.3, cy - r * 0.3);
            ctx.closePath();
            ctx.fill();

            // Draw a tiny tail
            ctx.beginPath();
            ctx.globalAlpha = alpha * 0.4;
            ctx.strokeStyle = '#D4A574';
            ctx.lineWidth = 0.5;
            ctx.moveTo(cx, cy + r);
            ctx.lineTo(cx - r * 1.5, cy + r * 2.5);
            ctx.stroke();

            ctx.restore();

            // Move star
            s.y += s.speed;
            s.x += Math.sin(s.angle) * 0.2;

            if (s.y > h + 20) {
                s.y = -10;
                s.x = Math.random() * w;
            }
            if (s.x > w + 20) s.x = -10;
            if (s.x < -20) s.x = w + 10;
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', function() {
        resize();
        init();
    });

    resize();
    init();
    draw();
})();
