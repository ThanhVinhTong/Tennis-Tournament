$(function () {
  // --- Defensive checks for backend data ---
  if (typeof sharedMap !== 'object' || !Array.isArray(allUsers) || typeof currentUser !== 'string') {
    console.error('Required backend data (sharedMap, allUsers, currentUser) is missing or invalid.');
    $('#shareUsers').append('<option disabled>Error: Unable to load users</option>');
    return;
  }

  // --- Select2 for user selection ---
  $('#shareUsers').select2({
    placeholder: 'Select users...',
    allowClear: true,
    width: '100%',
    dropdownAutoWidth: true
  });

  // --- Row highlight and user dropdown update ---
  $('#matchesTable').on('change', '.match-checkbox', function() {
    $(this).closest('tr').toggleClass('table-primary', this.checked);
    populateUsers();
  });

  // --- Check all ---
  $('#checkAll').on('change', function() {
    $('.match-checkbox').prop('checked', this.checked).trigger('change');
  });

  // --- History search ---
  $('#historySearch').on('keyup', function() {
    const val = $(this).val().toLowerCase();
    $('#historyTable tbody tr').each(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(val) > -1);
    });
  });

  // --- Matches table pagination and search ---
  const matchesTable = document.getElementById('matchesTable');
  if (matchesTable) {
    const matchesTbody = matchesTable.querySelector('tbody');
    const allRows = Array.from(matchesTbody.querySelectorAll('tr'));
    const pagination = document.getElementById('matchesPagination');
    const perPageSelect = document.getElementById('matchesPerPage');
    const searchInput = document.getElementById('matchesSearch');
    let currentPage = 1;
    let filteredRows = allRows;

    function renderTablePage(page, perPage) {
      const total = filteredRows.length;
      const totalPages = Math.ceil(total / perPage) || 1;
      if (page > totalPages) page = totalPages;
      if (page < 1) page = 1;
      allRows.forEach(row => row.style.display = 'none');
      const start = (page - 1) * perPage;
      const end = start + perPage;
      filteredRows.slice(start, end).forEach(row => row.style.display = '');
      let pagHtml = '';
      if (totalPages > 1) {
        pagHtml += `<li class="page-item${page===1?' disabled':''}"><a class="page-link" href="#" data-page="${page-1}">&lt;</a></li>`;
        pagHtml += `<li class="page-item${page===1?' active':''}"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (page > 3) pagHtml += `<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`;
        if (page !== 1 && page !== totalPages) {
          pagHtml += `<li class="page-item active"><span class="page-link">${page}</span></li>`;
        }
        if (page < totalPages - 2) pagHtml += `<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`;
        if (totalPages > 1) {
          pagHtml += `<li class="page-item${page===totalPages?' active':''}"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        pagHtml += `<li class="page-item${page===totalPages?' disabled':''}"><a class="page-link" href="#" data-page="${page+1}">&gt;</a></li>`;
        pagHtml += `<li class="page-item" style="margin-left:12px;"><input type="number" min="1" max="${totalPages}" value="${page}" class="form-control form-control-sm pagination-goto" style="width:60px;display:inline-block;" title="Go to page"></li>`;
        pagHtml += `<li class="page-item"><button class="btn btn-sm btn-outline-success pagination-goto-btn" style="margin-left:4px;">Go</button></li>`;
      }
      pagination.innerHTML = pagHtml;
      pagination.querySelectorAll('a.page-link').forEach(link => {
        link.onclick = function(e) {
          e.preventDefault();
          const p = parseInt(this.getAttribute('data-page'));
          if (!isNaN(p) && p >= 1 && p <= totalPages) {
            currentPage = p;
            renderTablePage(currentPage, parseInt(perPageSelect.value));
          }
        };
      });
      const gotoInput = pagination.querySelector('.pagination-goto');
      const gotoBtn = pagination.querySelector('.pagination-goto-btn');
      if (gotoInput && gotoBtn) {
        gotoInput.addEventListener('input', function() {
          this.value = this.value.replace(/[^0-9]/g, '');
          if (this.value && parseInt(this.value) > totalPages) this.value = totalPages;
        });
        gotoBtn.onclick = function() {
          const p = parseInt(gotoInput.value);
          if (!isNaN(p) && p >= 1 && p <= totalPages) {
            currentPage = p;
            renderTablePage(currentPage, parseInt(perPageSelect.value));
          } else {
            gotoInput.classList.add('is-invalid');
            setTimeout(() => gotoInput.classList.remove('is-invalid'), 1200);
          }
        };
        gotoInput.onkeydown = function(e) {
          if (e.key === 'Enter') gotoBtn.click();
        };
      }
    }

    if (perPageSelect) {
      perPageSelect.addEventListener('change', function() {
        currentPage = 1;
        renderTablePage(currentPage, parseInt(this.value));
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', debounce(function() {
        const val = this.value.toLowerCase();
        filteredRows = allRows.filter(row => row.innerText.toLowerCase().indexOf(val) > -1);
        currentPage = 1;
        renderTablePage(currentPage, parseInt(perPageSelect.value));
      }, 300));
    }

    renderTablePage(currentPage, parseInt(perPageSelect.value));
  }

  // --- History table pagination and search ---
  const historyTable = document.getElementById('historyTable');
  const historyPagination = document.getElementById('historyPagination');
  const historySearchInput = document.getElementById('historySearch');
  const historyPerPageSelect = document.getElementById('historyPerPage');
  if (historyTable && historyPagination) {
    const historyTbody = historyTable.querySelector('tbody');
    const allHistoryRows = Array.from(historyTbody.querySelectorAll('tr'));
    let historyCurrentPage = 1;
    let historyPerPage = parseInt(historyPerPageSelect ? historyPerPageSelect.value : 10);
    let filteredHistoryRows = allHistoryRows;

    function renderHistoryPage(page, perPage) {
      const total = filteredHistoryRows.length;
      const totalPages = Math.ceil(total / perPage) || 1;
      if (page > totalPages) page = totalPages;
      if (page < 1) page = 1;
      allHistoryRows.forEach(row => row.style.display = 'none');
      const start = (page - 1) * perPage;
      const end = start + perPage;
      filteredHistoryRows.slice(start, end).forEach(row => row.style.display = '');
      let pagHtml = '';
      if (totalPages > 1) {
        pagHtml += `<li class="page-item${page===1?' disabled':''}"><a class="page-link" href="#" data-page="${page-1}">&lt;</a></li>`;
        pagHtml += `<li class="page-item${page===1?' active':''}"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (page > 3) pagHtml += `<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`;
        if (page !== 1 && page !== totalPages) {
          pagHtml += `<li class="page-item active"><span class="page-link">${page}</span></li>`;
        }
        if (page < totalPages - 2) pagHtml += `<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`;
        if (totalPages > 1) {
          pagHtml += `<li class="page-item${page===totalPages?' active':''}"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        pagHtml += `<li class="page-item${page===totalPages?' disabled':''}"><a class="page-link" href="#" data-page="${page+1}">&gt;</a></li>`;
        pagHtml += `<li class="page-item" style="margin-left:12px;"><input type="number" min="1" max="${totalPages}" value="${page}" class="form-control form-control-sm pagination-goto-history" style="width:60px;display:inline-block;" title="Go to page"></li>`;
        pagHtml += `<li class="page-item"><button class="btn btn-sm btn-outline-success pagination-goto-btn-history" style="margin-left:4px;">Go</button></li>`;
      }
      historyPagination.innerHTML = pagHtml;
      historyPagination.querySelectorAll('a.page-link').forEach(link => {
        link.onclick = function(e) {
          e.preventDefault();
          const p = parseInt(this.getAttribute('data-page'));
          if (!isNaN(p) && p >= 1 && p <= totalPages) {
            historyCurrentPage = p;
            renderHistoryPage(historyCurrentPage, historyPerPage);
          }
        };
      });
      const gotoInput = historyPagination.querySelector('.pagination-goto-history');
      const gotoBtn = historyPagination.querySelector('.pagination-goto-btn-history');
      if (gotoInput && gotoBtn) {
        gotoInput.addEventListener('input', function() {
          this.value = this.value.replace(/[^0-9]/g, '');
          if (this.value && parseInt(this.value) > totalPages) this.value = totalPages;
        });
        gotoBtn.onclick = function() {
          const p = parseInt(gotoInput.value);
          if (!isNaN(p) && p >= 1 && p <= totalPages) {
            historyCurrentPage = p;
            renderHistoryPage(historyCurrentPage, historyPerPage);
          } else {
            gotoInput.classList.add('is-invalid');
            setTimeout(() => gotoInput.classList.remove('is-invalid'), 1200);
          }
        };
        gotoInput.onkeydown = function(e) {
          if (e.key === 'Enter') gotoBtn.click();
        };
      }
    }

    if (historyPerPageSelect) {
      historyPerPageSelect.addEventListener('change', function() {
        historyPerPage = parseInt(this.value);
        historyCurrentPage = 1;
        renderHistoryPage(historyCurrentPage, historyPerPage);
      });
    }

    if (historySearchInput) {
      historySearchInput.addEventListener('input', debounce(function() {
        const val = this.value.toLowerCase();
        filteredHistoryRows = allHistoryRows.filter(row => row.innerText.toLowerCase().indexOf(val) > -1);
        historyCurrentPage = 1;
        renderHistoryPage(historyCurrentPage, historyPerPage);
      }, 300));
    }

    renderHistoryPage(historyCurrentPage, historyPerPage);
  }

  // --- Existing user selection and sharing logic ---
  const userSelect = $('#shareUsers')[0];
  const checkAllMatches = $('#checkAll');
  const shareBtn = $('#btnShare');

  // --- OptionGroup helper ---
  function OptionGroup(label) {
    this.el = document.createElement('optgroup');
    this.el.label = label;
    this.hasChildren = () => this.el.children.length > 0;
    this.append = o => this.el.appendChild(o);
  }

  // --- Select all/clear users ---
  $('#selectAllUsers').on('click', () => {
    $('#shareUsers option:not(:disabled)').prop('selected', true);
    $('#shareUsers').trigger('change.select2');
  });

  $('#clearUsers').on('click', () => {
    $('#shareUsers option:selected').prop('selected', false);
    $('#shareUsers').trigger('change.select2');
  });

  // --- Share button click ---
  shareBtn.on('click', async () => {
    const matchIds = $('.match-checkbox:checked').map((_, el) => el.value).get();
    const usernames = [...userSelect.selectedOptions].map(o => o.value);

    if (!matchIds.length) {
      return alert('⚠️ Please select at least one match.');
    }
    if (!usernames.length) {
      return alert('⚠️ Please select at least one recipient.');
    }

    try {
      const res = await fetch('/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_ids: matchIds, usernames })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || res.statusText);

      alert('✅ Share success!');
      location.reload();
    } catch (err) {
      alert('❌ Share failed: ' + err.message);
    }
  });

  // --- Update user dropdown ---
  function populateUsers() {
    const prevSelected = new Set($('#shareUsers').val() || []);
    const selectedIds = $('.match-checkbox:checked').map((_, el) => parseInt(el.value, 10)).get();
    const disabledSet = new Set();
    selectedIds.forEach(id => (sharedMap[id] || []).forEach(uid => disabledSet.add(uid)));

    const options = allUsers.map(u => ({
      id: u.username,
      text: u.display_name || u.username,
      selected: prevSelected.has(u.username),
      disabled: u.username === currentUser || disabledSet.has(u.id)
    }));

    $('#shareUsers').empty().select2({
      data: options,
      placeholder: 'Select users...',
      allowClear: true,
      width: '100%',
      dropdownAutoWidth: true
    });
  }

  // --- Initial population of users ---
  populateUsers();

  // --- Unshare (remove shared match) from history ---
  $('#historyTable').on('click', '.btn-unshare', function() {
    const btn = $(this);
    const shareId = btn.data('share-id');
    if (!shareId) return;
    if (!confirm('Remove this share?')) return;
    btn.prop('disabled', true);
    $.post(`/unshare/${shareId}`, function() {
      alert('✅ Share removed.');
      location.reload();
    }).fail(function(xhr) {
      alert('❌ Failed to remove share: ' + (xhr.responseJSON?.message || xhr.statusText));
      btn.prop('disabled', false);
    });
  });

  // --- Bulk unshare for Private Share History ---
  $('#historyTable').on('change', '.history-checkbox, #historyCheckAll', function() {
    const $table = $('#historyTable');
    const $visibleCheckboxes = $table.find('tbody tr:visible .history-checkbox');
    const $checkedVisible = $visibleCheckboxes.filter(':checked');
    const $checkAll = $('#historyCheckAll');
    const $deleteButton = $('#btnDeleteHistory');

    if (this.id === 'historyCheckAll') {
      $visibleCheckboxes.prop('checked', this.checked);
    }

    const allChecked = $visibleCheckboxes.length > 0 && $checkedVisible.length === $visibleCheckboxes.length;
    $checkAll.prop('checked', allChecked).attr('aria-checked', allChecked);
    $deleteButton.prop('disabled', $table.find('.history-checkbox:checked').length === 0).attr('aria-disabled', $deleteButton.prop('disabled'));
  });

  $('#btnDeleteHistory').on('click', function() {
    const btn = $(this);
    const ids = $('.history-checkbox:checked').map((_, el) => $(el).val()).get();
    if (!ids.length) return;
    if (!confirm(`Remove ${ids.length} selected shares?`)) return;
    btn.prop('disabled', true);
    $('.history-checkbox, #historyCheckAll').prop('disabled', true);
    Promise.allSettled(ids.map(id =>
      $.post(`/unshare/${id}`).promise()
    )).then(results => {
      const failed = results.filter(r => r.status === 'rejected').length;
      if (failed > 0) {
        alert(`✅ ${ids.length - failed} shares removed, ${failed} failed.`);
      } else {
        alert('✅ Selected shares removed.');
      }
      location.reload();
    });
  });

  // --- Bulk delete for Your Matches ---
  $('#matchesTable').on('change', '.match-checkbox, #matchesCheckAll', function() {
    const $table = $('#matchesTable');
    const $visibleCheckboxes = $table.find('tbody tr:visible .match-checkbox');
    const $checkedVisible = $visibleCheckboxes.filter(':checked');
    const $checkAll = $('#matchesCheckAll');
    const $deleteButton = $('#btnDeleteMatches');

    if (this.id === 'matchesCheckAll') {
      $visibleCheckboxes.prop('checked', this.checked).trigger('change');
    }

    const allChecked = $visibleCheckboxes.length > 0 && $checkedVisible.length === $visibleCheckboxes.length;
    $checkAll.prop('checked', allChecked).attr('aria-checked', allChecked);
    $deleteButton.prop('disabled', $table.find('.match-checkbox:checked').length === 0).attr('aria-disabled', $deleteButton.prop('disabled'));

    populateUsers();
  });

  $('#btnDeleteMatches').on('click', function() {
    const btn = $(this);
    const ids = $('.match-checkbox:checked').map((_, el) => $(el).val()).get();
    if (!ids.length) return;
    if (!confirm(`Delete ${ids.length} selected matches? This cannot be undone.`)) return;
    btn.prop('disabled', true);
    $('.match-checkbox, #matchesCheckAll').prop('disabled', true);
    Promise.allSettled(ids.map(id =>
      $.post(`/delete_match/${id}`).promise()
    )).then(results => {
      const failed = results.filter(r => r.status === 'rejected').length;
      if (failed > 0) {
        alert(`✅ ${ids.length - failed} matches deleted, ${failed} failed.`);
      } else {
        alert('✅ Selected matches deleted.');
      }
      location.reload();
    });
  });

  // --- Debounce utility ---
  function debounce(fn, delay) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), delay);
    };
  }
});