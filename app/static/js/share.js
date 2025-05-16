$(function () {
  // --- Select2 for user selection ---
  function getSelectableUsers() {
    // Exclude current user and already shared users
    const selectedIds = $('.match-checkbox:checked')
      .map((_, el) => parseInt(el.value, 10))
      .get();
    const disabledSet = new Set();
    selectedIds.forEach(id => {
      (sharedMap[id] || []).forEach(uid => disabledSet.add(uid));
    });
    return allUsers.filter(u => u.username !== currentUser && !disabledSet.has(u.id));
  }

  function refreshShareUsersDropdown() {
    const selectable = getSelectableUsers();
    $('#shareUsers').empty();
    if (selectable.length === 0) {
      $('#shareUsers').append('<option disabled>No users available to share with</option>');
    } else {
      selectable.forEach(u => {
        $('#shareUsers').append(new Option(u.display_name || u.username, u.username));
      });
    }
    $('#shareUsers').trigger('change.select2');
  }

  $('#shareUsers').select2({
    placeholder: 'Select users...',
    allowClear: true,
    width: '100%',
    dropdownAutoWidth: true
  });
  refreshShareUsersDropdown();
  // Refresh dropdown when matches are (de)selected
  $('.match-checkbox, #checkAll').on('change', refreshShareUsersDropdown);

  // --- Row highlight ---
  $('.match-checkbox').on('change', function() {
    $(this).closest('tr').toggleClass('table-primary', this.checked);
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
      // Hide all rows
      allRows.forEach(row => row.style.display = 'none');
      // Show only relevant filtered rows
      const start = (page - 1) * perPage;
      const end = start + perPage;
      filteredRows.slice(start, end).forEach(row => row.style.display = '');
      // Render advanced pagination: < 1 ... current ... max > ... goto
      let pagHtml = '';
      if (totalPages > 1) {
        // Previous arrow
        pagHtml += `<li class=\"page-item${page===1?' disabled':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${page-1}\">&lt;</a></li>`;
        // First page
        pagHtml += `<li class=\"page-item${page===1?' active':''}\"><a class=\"page-link\" href=\"#\" data-page=\"1\">1</a></li>`;
        // Ellipsis before current
        if (page > 3) pagHtml += `<li class=\"page-item disabled\"><span class=\"page-link\">&hellip;</span></li>`;
        // Current page (if not 1 or max)
        if (page !== 1 && page !== totalPages) {
          pagHtml += `<li class=\"page-item active\"><span class=\"page-link\">${page}</span></li>`;
        }
        // Ellipsis after current
        if (page < totalPages - 2) pagHtml += `<li class=\"page-item disabled\"><span class=\"page-link\">&hellip;</span></li>`;
        // Last page
        if (totalPages > 1) {
          pagHtml += `<li class=\"page-item${page===totalPages?' active':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${totalPages}\">${totalPages}</a></li>`;
        }
        // Next arrow
        pagHtml += `<li class=\"page-item${page===totalPages?' disabled':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${page+1}\">&gt;</a></li>`;
        // Goto input
        pagHtml += `<li class=\"page-item\" style=\"margin-left:12px;\"><input type=\"number\" min=\"1\" max=\"${totalPages}\" value=\"${page}\" class=\"form-control form-control-sm pagination-goto\" style=\"width:60px;display:inline-block;\" title=\"Go to page\"></li>`;
        pagHtml += `<li class=\"page-item\"><button class=\"btn btn-sm btn-outline-success pagination-goto-btn\" style=\"margin-left:4px;\">Go</button></li>`;
      }
      pagination.innerHTML = pagHtml;
      // Add event listeners
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
      // Goto input handler
      const gotoInput = pagination.querySelector('.pagination-goto');
      const gotoBtn = pagination.querySelector('.pagination-goto-btn');
      if (gotoInput && gotoBtn) {
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
      searchInput.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        filteredRows = allRows.filter(row => {
          return row.innerText.toLowerCase().indexOf(val) > -1;
        });
        currentPage = 1;
        renderTablePage(currentPage, parseInt(perPageSelect.value));
      });
    }
    // Initial render
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
      // Hide all rows
      allHistoryRows.forEach(row => row.style.display = 'none');
      // Show only relevant filtered rows
      const start = (page - 1) * perPage;
      const end = start + perPage;
      filteredHistoryRows.slice(start, end).forEach(row => row.style.display = '');
      // Render advanced pagination: < 1 ... current ... max > ... goto
      let pagHtml = '';
      if (totalPages > 1) {
        // Previous arrow
        pagHtml += `<li class=\"page-item${page===1?' disabled':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${page-1}\">&lt;</a></li>`;
        // First page
        pagHtml += `<li class=\"page-item${page===1?' active':''}\"><a class=\"page-link\" href=\"#\" data-page=\"1\">1</a></li>`;
        // Ellipsis before current
        if (page > 3) pagHtml += `<li class=\"page-item disabled\"><span class=\"page-link\">&hellip;</span></li>`;
        // Current page (if not 1 or max)
        if (page !== 1 && page !== totalPages) {
          pagHtml += `<li class=\"page-item active\"><span class=\"page-link\">${page}</span></li>`;
        }
        // Ellipsis after current
        if (page < totalPages - 2) pagHtml += `<li class=\"page-item disabled\"><span class=\"page-link\">&hellip;</span></li>`;
        // Last page
        if (totalPages > 1) {
          pagHtml += `<li class=\"page-item${page===totalPages?' active':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${totalPages}\">${totalPages}</a></li>`;
        }
        // Next arrow
        pagHtml += `<li class=\"page-item${page===totalPages?' disabled':''}\"><a class=\"page-link\" href=\"#\" data-page=\"${page+1}\">&gt;</a></li>`;
        // Goto input
        pagHtml += `<li class=\"page-item\" style=\"margin-left:12px;\"><input type=\"number\" min=\"1\" max=\"${totalPages}\" value=\"${page}\" class=\"form-control form-control-sm pagination-goto-history\" style=\"width:60px;display:inline-block;\" title=\"Go to page\"></li>`;
        pagHtml += `<li class=\"page-item\"><button class=\"btn btn-sm btn-outline-success pagination-goto-btn-history\" style=\"margin-left:4px;\">Go</button></li>`;
      }
      historyPagination.innerHTML = pagHtml;
      // Add event listeners
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
      // Goto input handler
      const gotoInput = historyPagination.querySelector('.pagination-goto-history');
      const gotoBtn = historyPagination.querySelector('.pagination-goto-btn-history');
      if (gotoInput && gotoBtn) {
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
      historySearchInput.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        filteredHistoryRows = allHistoryRows.filter(row => {
          return row.innerText.toLowerCase().indexOf(val) > -1;
        });
        historyCurrentPage = 1;
        renderHistoryPage(historyCurrentPage, historyPerPage);
      });
    }
    // Initial render
    renderHistoryPage(historyCurrentPage, historyPerPage);
  }

  // --- Existing user selection and sharing logic ---
  const userSelect      = $('#shareUsers')[0];
  const checkAllMatches = $('#checkAll');
  const shareBtn        = $('#btnShare');

  // —— OptionGroup 辅助构造 —— 
  function OptionGroup(label) {
    this.el = document.createElement('optgroup');
    this.el.label = label;
    this.hasChildren = () => this.el.children.length > 0;
    this.append = o => this.el.appendChild(o);
  }

  // —— 全选/反选比赛 —— 
  checkAllMatches.on('change', () => {
    const checked = checkAllMatches.is(':checked');
    $('.match-checkbox').prop('checked', checked);
    populateUsers();
  });
  $('.match-checkbox').on('change', () => {
    populateUsers();
  });

  // —— 全选/清空 用户列表 —— 
  $('#selectAllUsers').on('click', () => {
    $('#shareUsers option:not(:disabled)').prop('selected', true);
  });
  $('#clearUsers').on('click', () => {
    $('#shareUsers option:selected').prop('selected', false);
  });

  // —— 点击分享按钮 —— 
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

  // —— 更新用户下拉列表 —— 
  function populateUsers() {
    // 1. 记录之前已经选中的用户名
    const prevSelected = new Set(
      [...userSelect.selectedOptions].map(o => o.value)
    );

    // 2. 找出所有被选中比赛所对应的已分享用户 ID
    const selectedIds = $('.match-checkbox:checked')
      .map((_, el) => parseInt(el.value, 10))
      .get();
    const disabledSet = new Set();
    selectedIds.forEach(id => {
      (sharedMap[id] || []).forEach(uid => disabledSet.add(uid));
    });

    // 3. 清空当前选项
    userSelect.innerHTML = '';

    const selectableGroup = new OptionGroup('Selectable users');
    const disabledGroup   = new OptionGroup('Already shared');

    allUsers.forEach(u => {
      const o = document.createElement('option');
      o.value = u.username;
      o.textContent = u.username;

      // 自己或已分享的放到 disabledGroup
      if (u.username === currentUser || disabledSet.has(u.id)) {
        o.disabled = true;
        o.textContent += (u.username === currentUser) ? ' (Own)' : ' (Shared)';
        disabledGroup.append(o);
      } else {
        // 可选用户：如果之前选中过，保留选中状态
        if (prevSelected.has(u.username)) {
          o.selected = true;
        }
        selectableGroup.append(o);
      }
    });

    if (selectableGroup.hasChildren()) userSelect.appendChild(selectableGroup.el);
    if (disabledGroup.hasChildren())   userSelect.appendChild(disabledGroup.el);
  }

  // —— 页面初次加载时初始化 —— 
  populateUsers();

  // --- Unshare (remove shared match) from history ---
  $(document).on('click', '.btn-unshare', function() {
    const btn = $(this);
    const shareId = btn.data('share-id');
    if (!shareId) return;
    if (!confirm('Remove this share?')) return;
    btn.prop('disabled', true);
    $.post(`/unshare/${shareId}`, function() {
      // Optionally show a message, then reload
      alert('✅ Share removed.');
      location.reload();
    }).fail(function(xhr) {
      alert('❌ Failed to remove share: ' + (xhr.responseJSON?.message || xhr.statusText));
      btn.prop('disabled', false);
    });
  });

  // --- Bulk unshare for Private Share History ---
  $(document).on('change', '.history-checkbox, #historyCheckAll', function() {
    const visibleCheckboxes = $('#historyTable tbody tr:visible .history-checkbox');
    const checkedVisible = visibleCheckboxes.filter(':checked');
    // Select all logic
    if ($(this).attr('id') === 'historyCheckAll') {
      visibleCheckboxes.prop('checked', this.checked);
    }
    // Update select all state
    $('#historyCheckAll').prop('checked', visibleCheckboxes.length > 0 && checkedVisible.length === visibleCheckboxes.length);
    // Enable/disable delete button
    $('#btnDeleteHistory').prop('disabled', $('.history-checkbox:checked').length === 0);
  });

  $('#btnDeleteHistory').on('click', function() {
    const btn = $(this);
    const ids = $('.history-checkbox:checked').map((_, el) => $(el).val()).get();
    if (!ids.length) return;
    if (!confirm(`Remove ${ids.length} selected shares?`)) return;
    btn.prop('disabled', true);
    $('.history-checkbox, #historyCheckAll').prop('disabled', true);
    // Send all unshare requests in parallel
    Promise.all(ids.map(id =>
      $.post(`/unshare/${id}`).catch(() => null)
    )).then(() => {
      alert('✅ Selected shares removed.');
      location.reload();
    });
  });

  // --- Bulk delete for Your Matches ---
  $(document).on('change', '.matches-checkbox, #matchesCheckAll', function() {
    const visibleCheckboxes = $('#matchesTable tbody tr:visible .matches-checkbox');
    const checkedVisible = visibleCheckboxes.filter(':checked');
    // Select all logic
    if ($(this).attr('id') === 'matchesCheckAll') {
      visibleCheckboxes.prop('checked', this.checked);
    }
    // Update select all state
    $('#matchesCheckAll').prop('checked', visibleCheckboxes.length > 0 && checkedVisible.length === visibleCheckboxes.length);
    // Enable/disable delete button
    $('#btnDeleteMatches').prop('disabled', $('.matches-checkbox:checked').length === 0);
  });

  $('#btnDeleteMatches').on('click', function() {
    const btn = $(this);
    const ids = $('.matches-checkbox:checked').map((_, el) => $(el).val()).get();
    if (!ids.length) return;
    if (!confirm(`Delete ${ids.length} selected matches? This cannot be undone.`)) return;
    btn.prop('disabled', true);
    $('.matches-checkbox, #matchesCheckAll').prop('disabled', true);
    // Send all delete requests in parallel
    Promise.all(ids.map(id =>
      $.post(`/delete_match/${id}`).catch(() => null)
    )).then(() => {
      alert('✅ Selected matches deleted.');
      location.reload();
    });
  });
});
