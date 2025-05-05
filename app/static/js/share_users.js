document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('userSearch');
  
    // Search function: filter the user list based on input
    if (searchInput) {
      searchInput.addEventListener('input', function () {
        const filter = this.value.toLowerCase();
        document.querySelectorAll('#userList .form-check').forEach(item => {
          const labelText = item.querySelector('label').textContent.toLowerCase();
          item.style.display = labelText.includes(filter) ? '' : 'none';
        });
      });
    }
  
    // Select all optional users
    document.getElementById('btnSelectAll')?.addEventListener('click', () => {
      document.querySelectorAll('.user-checkbox:not(:disabled)').forEach(cb => {
        // Only select users that are not already shared (not disabled)
        cb.checked = true;
      });
    });
  
    // Clear all user selections
    document.getElementById('btnClearAll')?.addEventListener('click', () => {
      document.querySelectorAll('.user-checkbox').forEach(cb => {
        cb.checked = false;
      });
    });
  });
  