// static/js/share.js

$(function () {
  const togglePublic     = $('#togglePublic');
  const userSelect       = $('#shareUsers')[0];
  const checkAllMatches  = $('#checkAll');
  const shareBtn         = $('#btnShare');

  //—— OptionGroup auxiliary constructor——
  function OptionGroup(label) {
    this.el = document.createElement('optgroup');
    this.el.label = label;
    this.hasChildren = () => this.el.children.length > 0;
    this.append = o => this.el.appendChild(o);
  }

  //—— Switch private user area display & initialize list & update Public badge ——
  function toggleUserSection() {
    const isPub = togglePublic.is(':checked');
    $('#privateUsersSection').toggle(!isPub);
    populateUsers();
    updatePublicBadges();
  }
  togglePublic.on('change', toggleUserSection);

  //——Select All/Deselect Match——
  checkAllMatches.on('change', () => {
    $('.match-checkbox').prop('checked', checkAllMatches.is(':checked'));
    populateUsers();
    updatePublicBadges();
  });
  $('.match-checkbox').on('change', () => {
    populateUsers();
    updatePublicBadges();
  });

  //—— Click the share button——
  shareBtn.on('click', async () => {
    const matchIds = $('.match-checkbox:checked').map((_, el) => el.value).get();
    const isPublic = togglePublic.is(':checked');
    const usernames = isPublic
      ? []
      : [...userSelect.selectedOptions].map(o => o.value);

    if (!matchIds.length) {
      return alert('⚠️ Please select at least one match.');
    }
    if (!isPublic && !usernames.length) {
      return alert('⚠️ Please select at least one recipient.');
    }

    try {
      const res = await fetch('/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_ids: matchIds, usernames, public: isPublic })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || res.statusText);
      }
      alert('✅ Share success!');
      location.reload();
    } catch (err) {
      alert('❌ Share failed: ' + err.message);
    }
  });

  //—— Update private user drop-down content——
  function populateUsers() {
    const selectedIds = $('.match-checkbox:checked').map((_, el) => parseInt(el.value, 10)).get();
    const disabledSet = new Set();
    selectedIds.forEach(id => {
      (sharedMap[id] || []).forEach(uid => disabledSet.add(uid));
    });

    // Clear old options
    userSelect.innerHTML = '';

    const newGroup = new OptionGroup('Selectable users');
    const oldGroup = new OptionGroup('Shared (not optional)');

    allUsers.forEach(u => {
      const o = document.createElement('option');
      o.value = u.username;
      o.textContent = u.username;
      if (u.username === currentUser) {
        o.disabled = true;
        o.textContent += '(Own)';
        oldGroup.append(o);
      } else if (disabledSet.has(u.id)) {
        o.disabled = true;
        o.textContent += '(Shared privately)';
        oldGroup.append(o);
      } else {
        newGroup.append(o);
      }
    });

    if (newGroup.hasChildren()) userSelect.appendChild(newGroup.el);
    if (oldGroup.hasChildren()) userSelect.appendChild(oldGroup.el);
  }

  // -- Update the display of the Public badge --
  function updatePublicBadges() {
    const show = togglePublic.is(':checked');
    $('tr[data-id]').each((_, row) => {
      const $row  = $(row);
      const id    = parseInt($row.attr('data-id'), 10);
      const badge = $row.find('.public-badge');
      if (show && publicShared.includes(id)) {
        badge.show();
      } else {
        badge.hide();
      }
    });
  }

  //—— Initialized when the page first loads——
  toggleUserSection();
});
