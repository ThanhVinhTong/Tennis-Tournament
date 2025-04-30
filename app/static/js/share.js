$(document).ready(function () {
    const mockMatches = {
      "2025-04-22": [
        { id: 1, title: "🏆 Alice vs Bob" },
        { id: 2, title: "🥇 Charlie vs Dan" }
      ],
      "2025-04-21": [
        { id: 3, title: "🏅 Eva vs Frank" }
      ]
    };
  
    const mockPlayers = [
      { name: "Jannik Sinner", country: "ITA", ranking: 1, matchType: "Singles", flag: "it" },
      { name: "Alexander Zverev", country: "GER", ranking: 2, matchType: "Singles", flag: "de" },
      { name: "Carlos Alcaraz", country: "ESP", ranking: 3, matchType: "Singles", flag: "es" },
      { name: "Taylor Fritz", country: "USA", ranking: 4, matchType: "Singles", flag: "us" },
      { name: "Novak Djokovic", country: "SRB", ranking: 5, matchType: "Singles", flag: "rs" },
    ];
  
    function renderPlayers(players) {
      const grid = $('#player-grid').empty();
      if (players.length === 0) {
        grid.append('<p class="text-muted">No players found</p>');
        return;
      }
  
      players.forEach((p, index) => {
        grid.append(`
          <div class="col-md-2 mb-4">
            <div class="player-card">
              <div class="fw-bold">${p.name}</div>
              <div>
                <img src="https://flagcdn.com/w40/${p.flag}.png" alt="${p.country} flag" class="flag-icon">
                <div>${p.country}</div>
              </div>
              <div class="text-muted small">Rank #${p.ranking}</div>
              <div class="form-check mt-2">
                <input class="form-check-input select-player" type="checkbox" data-name="${p.name}">
              </div>
            </div>
          </div>
        `);
      });
    }
  
    function filterPlayers() {
      const keyword = $('#search-player').val().toLowerCase();
      const type = $('#filter-type').val();
      const rank = $('#filter-ranking').val();
      const country = $('#filter-country').val();
  
      const filtered = mockPlayers.filter(p => {
        return (
          (!keyword || p.name.toLowerCase().includes(keyword)) &&
          (!type || p.matchType === type) &&
          (!country || p.country === country) &&
          (!rank || (rank === "Top 10" && p.ranking <= 10) ||
           (rank === "10-50" && p.ranking > 10 && p.ranking <= 50) ||
           (rank === "50+" && p.ranking > 50))
        );
      });
  
      renderPlayers(filtered);
    }
  
    // Tournament event handlers
    $('#tournament-date').on('change', function () {
      const date = $(this).val();
      const results = mockMatches[date] || [];
      const list = $('#tournament-list').empty();
  
      if (results.length === 0) {
        list.append('<p class="text-muted">No matches on this date</p>');
      } else {
        results.forEach(match => {
          list.append(`
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="match_${match.id}" value="${match.title}">
              <label class="form-check-label" for="match_${match.id}">${match.title}</label>
            </div>
          `);
        });
      }
    });
  
    $('#share-tournament').on('click', function () {
      const selectedMatches = $('#tournament-list input:checked').map(function () {
        return $(this).val();
      }).get();
      const users = $('#tournament-users').val();
  
      if (!selectedMatches.length || !users.length) {
        alert('Please select matches and users!');
        return;
      }
  
      alert('✅ Matches shared with: ' + users.join(', ') + '\nMatches: ' + selectedMatches.join('; '));
    });
  
    // Player event handlers
    $('#search-player, #filter-type, #filter-ranking, #filter-country').on('input change', filterPlayers);
  
    $('#reset-filters').on('click', function () {
      $('#search-player').val('');
      $('#filter-type').val('');
      $('#filter-ranking').val('');
      $('#filter-country').val('');
      renderPlayers(mockPlayers);
    });
  
    $('#share-player').on('click', function () {
      const selectedPlayers = $('.select-player:checked').map(function () {
        return $(this).data('name');
      }).get();
      const users = $('#player-users').val();
  
      if (!selectedPlayers.length || !users.length) {
        alert('Please select players and users!');
        return;
      }
  
      alert('✅ Player(s) shared with: ' + users.join(', ') + '\nPlayers: ' + selectedPlayers.join(', '));
    });
  
    // Initial render
    renderPlayers(mockPlayers);
  });
  