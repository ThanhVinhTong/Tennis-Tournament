document.addEventListener('DOMContentLoaded', function () {
    const defaultMatches = {
        2025: {
            3: {
                3: { title: 'Quarter Final', players: 'Emma vs Naomi', time: '14:00', court: 'Court 1' },
                7: { title: 'Semi Final', players: 'Serena vs Venus', time: '15:30', court: 'Center Court' },
                15: { title: 'Mixed Doubles', players: 'Alex & Sam vs Tina & Mike', time: '13:00', court: 'Court 2' },
                21: { title: 'Final', players: 'Rafael vs Novak', time: '16:00', court: 'Center Court' }
            },
            4: {
                5: { title: 'Finals', players: 'TBD vs TBD', time: '16:00', court: 'Center Court' }
            }
        },
        2026: {
            3: {
                10: { title: 'Opening Round', players: 'Carlos vs Andy', time: '12:00', court: 'Court 1' }
            }
        }
    };

    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');

    function getMonthInfo(year, month) {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const firstDay = new Date(year, month, 1).getDay();
        return { days: daysInMonth, firstDay };
    }

    function mergeMatches(defaultMatches, userMatches) {
        const merged = { ...defaultMatches };
        for (const day in userMatches) {
            merged[day] = { ...merged[day], ...userMatches[day], isUserMatch: true };
        }
        return merged;
    }

    function renderCalendar(monthMatches, monthInfo) {
        const calendarBody = document.getElementById('calendar-body');
        let html = '';
        let day = 1;
        
        while (day <= monthInfo.days) {
            html += '<tr>';
            for (let i = 0; i < 7; i++) {
                if ((day === 1 && i < monthInfo.firstDay) || day > monthInfo.days) {
                    html += '<td></td>';
                } else {
                    const match = monthMatches[day];
                    const matchJson = match ? JSON.stringify(match).replace(/'/g, '&apos;') : '';
                    html += `
                        <td>
                            <div class="calendar-day">
                                ${day}
                                ${match ? `<div class="match-indicator${match.isUserMatch ? ' user-match' : ''}" 
                                    data-match='${matchJson}'>🎾</div>` : ''}
                            </div>
                        </td>
                    `;
                    day++;
                }
            }
            html += '</tr>';
        }
        calendarBody.innerHTML = html;

        document.querySelectorAll('.match-indicator').forEach(indicator => {
            indicator.addEventListener('mouseover', function () {
                try {
                    const matchData = JSON.parse(this.dataset.match.replace(/&apos;/g, "'"));
                    showMatchDetails(matchData);
                } catch (e) {
                    console.error('Error parsing match data:', e);
                }
            });
            
            indicator.addEventListener('mouseout', function () {
                const activeMessageBox = document.querySelector('.match-message-box');
                if (activeMessageBox) activeMessageBox.remove();
            });
        });
    }

    function showMatchDetails(match) {
        const messageBox = document.createElement('div');
        messageBox.className = 'match-message-box';
        messageBox.innerHTML = `
            <h3>Match Details</h3>
            <p>Title: ${match.title}</p>
            <p>Players: ${match.players}</p>
            <p>Time: ${match.time}</p>
            <p>Court: ${match.court}</p>
        `;

        document.addEventListener('mousemove', function updatePosition(e) {
            messageBox.style.left = `${e.pageX + 10}px`;
            messageBox.style.top = `${e.pageY + 10}px`;
        });

        document.body.appendChild(messageBox);
    }

    function showCalendar(year, month) {
        const monthInfo = getMonthInfo(year, month);
        let monthMatches = defaultMatches[year]?.[month] || {};

        if (window.isAuthenticated === 'true') {
            fetch(`/api/matches?year=${year}&month=${month + 1}`, {
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(userMatches => {
                    monthMatches = mergeMatches(monthMatches, userMatches);
                    renderCalendar(monthMatches, monthInfo);
                })
                .catch(() => renderCalendar(monthMatches, monthInfo));
        } else {
            renderCalendar(monthMatches, monthInfo);
        }
    }

    function updateCalendar() {
        const selectedMonth = parseInt(monthSelect.value);
        const selectedYear = parseInt(yearSelect.value);
        showCalendar(selectedYear, selectedMonth);
    }

    const importMatchForm = document.getElementById('importMatchForm');
    if (importMatchForm) {
        initializePlayerDropdowns();

        importMatchForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = {
                title: document.getElementById('title').value,
                players: `${document.getElementById('player1').value} vs ${document.getElementById('player2').value}`,
                time: document.getElementById('time').value,
                court: document.getElementById('court').value,
                match_date: document.getElementById('match_date').value,
                month: parseInt(document.getElementById('month').value) + 1
            };

            fetch('/api/matches', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw new Error(err.error); });
                    }
                    return response.json();
                })
                .then(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('importMatchModal'));
                    modal.hide();
                    updateCalendar();
                    alert('Match added successfully!');
                })
                .catch(error => alert('Failed to add match: ' + error.message));
        });
    }

    monthSelect.addEventListener('change', updateCalendar);
    yearSelect.addEventListener('change', updateCalendar);

    showCalendar(2025, 4);

    async function fetchPlayers() {
        try {
            const response = await fetch('/api/players');
            if (!response.ok) {
                throw new Error('Failed to fetch players');
            }
            const players = await response.json();
            return players;
        } catch (error) {
            console.error('Error fetching players:', error);
            return [];
        }
    }

    function createPlayerDropdown(players, elementId) {
        const select = document.getElementById(elementId);
        if (!select) return;
        
        select.innerHTML = '<option value="">Select Player</option>';
        players.forEach(player => {
            const option = document.createElement('option');
            option.value = player.name;
            option.textContent = player.name;
            select.appendChild(option);
        });
    }

    async function initializePlayerDropdowns() {
        const players = await fetchPlayers();
        const playerInputs = document.querySelectorAll('.player-input');
        
        playerInputs.forEach(input => {
            const select = document.createElement('select');
            select.className = input.className;
            select.id = input.id;
            select.required = input.required;
            input.parentNode.replaceChild(select, input);
            createPlayerDropdown(players, select.id);
        });
    }
});
