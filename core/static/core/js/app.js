// QueueStorm front-end helpers — minimal vanilla JS.
(function () {
  'use strict';

  // -------- Dynamic transaction-history rows on the submit form ---------
  function bindTransactionTable() {
    var table = document.getElementById('tx-table');
    var addBtn = document.getElementById('tx-add');
    if (!table || !addBtn) return;

    var idx = table.querySelectorAll('tbody tr').length;

    function reindex() {
      var rows = table.querySelectorAll('tbody tr');
      rows.forEach(function (row, i) {
        row.querySelectorAll('input, select').forEach(function (el) {
          if (el.name) el.name = el.name.replace(/transactions-\d+-/, 'transactions-' + i + '-');
        });
      });
    }

    function bindRemove(row) {
      var rm = row.querySelector('.tx-remove');
      if (!rm) return;
      rm.addEventListener('click', function () {
        if (table.querySelectorAll('tbody tr').length <= 1) {
          row.querySelectorAll('input').forEach(function (i) { i.value = ''; });
          row.querySelectorAll('select').forEach(function (s) { s.selectedIndex = 0; });
          return;
        }
        row.remove();
        reindex();
      });
    }

    table.querySelectorAll('tbody tr').forEach(bindRemove);

    addBtn.addEventListener('click', function () {
      var tbody = table.querySelector('tbody');
      var proto = tbody.querySelector('tr');
      var clone = proto.cloneNode(true);
      clone.querySelectorAll('input').forEach(function (i) { i.value = ''; });
      clone.querySelectorAll('select').forEach(function (s) { s.selectedIndex = 0; });
      // Assign new index names
      clone.querySelectorAll('input, select').forEach(function (el) {
        if (el.name) el.name = el.name.replace(/transactions-\d+-/, 'transactions-' + idx + '-');
      });
      tbody.appendChild(clone);
      idx += 1;
      bindRemove(clone);
    });
  }

  // -------- AJAX submission of the ticket form ---------
  function bindSubmitForm() {
    var form = document.getElementById('ticket-form');
    var result = document.getElementById('result');
    if (!form || !result) return;

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      btn.textContent = 'Analyzing…';

      var payload = formToJson(form);
      fetch('/analyze-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
        .then(function (resp) {
          btn.disabled = false;
          btn.textContent = 'Analyze ticket';
          if (!resp.ok) {
            renderError(result, resp.body);
            return;
          }
          renderResult(result, resp.body, payload);
        })
        .catch(function (err) {
          btn.disabled = false;
          btn.textContent = 'Analyze ticket';
          renderError(result, { error: err && err.message ? err.message : 'Network error' });
        });
    });
  }

  function formToJson(form) {
    var fd = new FormData(form);
    var ticket = {
      ticket_id: (fd.get('ticket_id') || '').toString().trim(),
      complaint: (fd.get('complaint') || '').toString(),
      language:  (fd.get('language')  || 'en').toString(),
      channel:   (fd.get('channel')   || null),
      user_type: (fd.get('user_type') || 'unknown').toString(),
      campaign_context: (fd.get('campaign_context') || '').toString(),
      metadata: {},
      transaction_history: [],
    };

    var idx = 0;
    while (fd.has('transactions-' + idx + '-transaction_id')) {
      var txnId = (fd.get('transactions-' + idx + '-transaction_id') || '').toString().trim();
      if (txnId) {
        ticket.transaction_history.push({
          transaction_id: txnId,
          timestamp:      toIso((fd.get('transactions-' + idx + '-timestamp') || '').toString()),
          type:           (fd.get('transactions-' + idx + '-type')       || 'transfer').toString(),
          amount:         parseFloat(fd.get('transactions-' + idx + '-amount') || '0') || 0,
          counterparty:   (fd.get('transactions-' + idx + '-counterparty') || '').toString(),
          status:         (fd.get('transactions-' + idx + '-status')     || 'completed').toString(),
        });
      }
      idx += 1;
    }

    // Strip empty optional strings / nulls per spec.
    if (!ticket.language) ticket.language = 'en';
    if (!ticket.channel)  ticket.channel  = null;
    if (!ticket.user_type) ticket.user_type = 'unknown';

    return ticket;
  }

  function toIso(value) {
    if (!value) return new Date().toISOString();
    var d = new Date(value);
    if (isNaN(d.getTime())) return new Date().toISOString();
    return d.toISOString();
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function verdictClass(v) { return v; }

  function renderResult(target, body, request) {
    target.innerHTML =
      '<div class="result-panel">' +
        '<h2>Result for ' + escapeHtml(body.ticket_id) + '</h2>' +
        '<div class="result-banner ' + verdictClass(body.evidence_verdict) + '">' +
          '<div class="row" style="gap:8px;flex-wrap:wrap;">' +
            '<span class="badge mono ' + severityBadge(body.severity) + '">' + escapeHtml(body.severity) + '</span>' +
            '<span class="badge mono">' + escapeHtml(body.case_type) + '</span>' +
            '<span class="badge mono department">' + escapeHtml(body.department) + '</span>' +
            (body.human_review_required ? '<span class="badge mono solid">HUMAN REVIEW</span>' : '<span class="badge mono">no review</span>') +
          '</div>' +
          '<div style="margin-top:12px">' +
            '<span class="verdict ' + verdictClass(body.evidence_verdict) + '">' +
              '<span class="dot"></span>' + escapeHtml(body.evidence_verdict) +
            '</span>' +
            ' &middot; ' +
            '<span class="mono small">tx: ' + escapeHtml(body.relevant_transaction_id || '—') + '</span>' +
            ' &middot; ' +
            '<span class="mono small">conf: ' + Number(body.confidence || 0).toFixed(2) + '</span>' +
          '</div>' +
        '</div>' +

        '<div class="card">' +
          '<h3>Agent summary</h3>' +
          '<div>' + escapeHtml(body.agent_summary) + '</div>' +
        '</div>' +

        '<div class="card surface">' +
          '<h3>Recommended next action</h3>' +
          '<div>' + escapeHtml(body.recommended_next_action) + '</div>' +
        '</div>' +

        '<div class="card">' +
          '<h3>Customer reply</h3>' +
          '<blockquote class="reply-block">' + escapeHtml(body.customer_reply) + '</blockquote>' +
        '</div>' +

        '<div class="card">' +
          '<h3>Reason codes</h3>' +
          '<div class="pills">' +
            (body.reason_codes || []).map(function (c) { return '<span class="pill">' + escapeHtml(c) + '</span>'; }).join('') +
          '</div>' +
        '</div>' +

        '<details style="margin-top:16px"><summary class="mono small">Raw JSON response</summary>' +
          '<pre class="mono">' + escapeHtml(JSON.stringify(body, null, 2)) + '</pre>' +
        '</details>' +
      '</div>';

    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function severityBadge(sev) {
    return 'severity-' + (sev || 'low');
  }

  function renderError(target, body) {
    var msg = (body && (body.error || body.details))
      ? (typeof body.details === 'string' ? body.error + ': ' + body.details
                                          : body.error + ': ' + JSON.stringify(body.details))
      : 'Unexpected response from the API.';
    target.innerHTML =
      '<div class="result-panel">' +
        '<div class="card" style="border-color:var(--accent)">' +
          '<h3>Error</h3>' +
          '<div>' + escapeHtml(msg) + '</div>' +
        '</div>' +
      '</div>';
  }

  // ------- Prefill ticket id -------
  function prefillTicketId() {
    var el = document.getElementById('id_ticket_id');
    if (el && !el.value) {
      el.value = 'TKT-' + Math.random().toString(36).slice(2, 8).toUpperCase();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindTransactionTable();
    bindSubmitForm();
    prefillTicketId();
  });
})();
