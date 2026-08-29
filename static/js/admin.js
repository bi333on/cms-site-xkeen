/**
 * CMS Admin JavaScript
 * Общие функции для админ-панели
 */
(function() {
    'use strict';

    // Подтверждение удаления
    window.confirmDelete = function(message, callback) {
        if (confirm(message || 'Вы уверены?')) {
            callback();
        }
    };

    // AJAX-запросы с обработкой ошибок
    window.apiCall = function(url, options) {
        options = options || {};
        return fetch(url, {
            method: options.method || 'GET',
            headers: Object.assign({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }, options.headers || {}),
            body: options.body ? JSON.stringify(options.body) : undefined
        })
        .then(function(r) {
            if (r.status === 401) {
                return r.json().then(function(d) {
                    if (d.redirect) window.location.href = d.redirect;
                    throw new Error('Unauthorized');
                });
            }
            var ct = r.headers.get('content-type') || '';
            if (ct.includes('application/json')) return r.json();
            return r.text();
        });
    };

    // Поиск по таблице
    window.filterTable = function(inputId, tableId, columnIndex) {
        var input = document.getElementById(inputId);
        var table = document.getElementById(tableId);
        if (!input || !table) return;

        input.addEventListener('input', function() {
            var query = this.value.toLowerCase();
            var rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                var cell = row.cells[columnIndex];
                if (cell) {
                    var text = cell.textContent.toLowerCase();
                    row.style.display = text.includes(query) ? '' : 'none';
                }
            });
        });
    };

    // Форматирование даты
    window.formatDate = function(dateStr) {
        if (!dateStr) return '—';
        var d = new Date(dateStr);
        return d.toLocaleDateString('ru-RU') + ' ' + d.toLocaleTimeString('ru-RU', {hour:'2-digit',minute:'2-digit'});
    };

})();
