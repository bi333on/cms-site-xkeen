/**
 * Копирование кода в буфер обмена
 * Добавляет кнопку "Копировать" ко всем блокам кода на странице.
 */
(function() {
    'use strict';

    function addCopyButtons() {
        var pres = document.querySelectorAll('pre');
        pres.forEach(function(pre) {
            // Пропускаем уже обработанные
            if (pre.dataset.copyReady) return;
            pre.dataset.copyReady = '1';

            var code = pre.querySelector('code');
            if (!code) return;

            // Позиционируем pre относительно кнопки
            var parent = pre.parentElement;
            var wrap = pre;

            // Если pre уже внутри .code-block — кнопку кинем в сам .code-block
            if (parent && parent.classList.contains('code-block')) {
                wrap = parent;
            }

            // Контейнер для кнопки
            var btn = document.createElement('button');
            btn.className = 'code-copy-btn';
            btn.type = 'button';
            btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
            btn.setAttribute('aria-label', 'Копировать код');

            btn.addEventListener('click', function() {
                var text = code.innerText || code.textContent || '';
                copyToClipboard(text).then(function() {
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    btn.classList.add('copied');
                    btn.setAttribute('aria-label', 'Скопировано');
                    setTimeout(function() {
                        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                        btn.classList.remove('copied');
                        btn.setAttribute('aria-label', 'Копировать код');
                    }, 2000);
                }).catch(function() {
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
                    setTimeout(function() {
                        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                    }, 2000);
                });
            });

            // Обеспечиваем корректное позиционирование кнопки
            wrap.style.position = 'relative';
            wrap.classList.add('has-copy-btn');

            // Принудительно позиционируем кнопку справа по центру
            btn.style.position = 'absolute';
            btn.style.top = '50%';
            btn.style.right = '1rem';
            btn.style.transform = 'translateY(-50%)';
            btn.style.zIndex = '10';

            wrap.appendChild(btn);
        });
    }

    function copyToClipboard(text) {
        // Современный API
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text);
        }
        // Fallback для старых браузеров
        return new Promise(function(resolve, reject) {
            var textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                resolve();
            } catch (e) {
                reject(e);
            }
            document.body.removeChild(textarea);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addCopyButtons);
    } else {
        addCopyButtons();
    }

    // Повторный запуск при загрузке динамического контента
    window.addCodeCopyButtons = addCopyButtons;
})();
