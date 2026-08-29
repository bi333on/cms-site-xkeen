/**
 * Editor blocks helper
 * Функции для работы с блоками редактора
 */
(function() {
    'use strict';

    // Словарь для вставки готовых HTML-блоков через Markdown
    window.EditorBlocks = {
        /**
         * Вставить кнопку в редактор
         * @param {object} editor - EasyMDE instance
         * @param {string} text - текст кнопки
         * @param {string} url - ссылка
         * @param {string} styleClass - CSS класс
         */
        insertButton: function(editor, text, url, styleClass) {
            var md = '[' + (text || 'Кнопка') + '](' + (url || '#') + '){: .btn .' + (styleClass || 'btn-orange') + '}\n\n';
            this._insertAtCursor(editor, md);
        },

        /**
         * Вставить инфо-блок
         */
        insertInfoBox: function(editor, title, text) {
            var md = '> **💡 ' + (title || 'Информация') + '**\n>\n> ' + (text || '') + '\n\n';
            this._insertAtCursor(editor, md);
        },

        /**
         * Вставить предупреждение
         */
        insertWarningBox: function(editor, title, text) {
            var md = '> **⚠️ ' + (title || 'Предупреждение') + '**\n>\n> ' + (text || '') + '\n\n';
            this._insertAtCursor(editor, md);
        },

        /**
         * Вставить CTA-блок
         */
        insertCTABox: function(editor, title, text, btnText, btnUrl) {
            var md = '<div class="cta-box">\n\n### ' + (title || 'Призыв к действию') + '\n\n' +
                     (text || '') + '\n\n[' + (btnText || 'Начать') + '](' + (btnUrl || '#') + '){: .btn .btn-orange .btn-lg}\n\n</div>\n\n';
            this._insertAtCursor(editor, md);
        },

        /**
         * Вставить блок кода
         */
        insertCodeBlock: function(editor, code, language) {
            var md = '```' + (language || 'bash') + '\n' + (code || 'echo "Hello"') + '\n```\n\n';
            this._insertAtCursor(editor, md);
        },

        /**
         * Вставка в позицию курсора
         */
        _insertAtCursor: function(editor, text) {
            var cm = editor.codemirror;
            var doc = cm.getDoc();
            var cursor = doc.getCursor();
            doc.replaceRange(text, cursor);
            cm.focus();
        }
    };

})();
