document.addEventListener('DOMContentLoaded', function() {
    // Matches data organized by year and month
    const matches = {
        2025: {
            3: { // April (0-based index: 3)
                3: {'title': 'Quarter Final', 'players': 'Emma vs Naomi', 'time': '14:00', 'court': 'Court 1'},
                7: {'title': 'Semi Final', 'players': 'Serena vs Venus', 'time': '15:30', 'court': 'Center Court'},
                15: {'title': 'Mixed Doubles', 'players': 'Alex & Sam vs Tina & Mike', 'time': '13:00', 'court': 'Court 2'},
                21: {'title': 'Final', 'players': 'Rafael vs Novak', 'time': '16:00', 'court': 'Center Court'}
            },
            4: { // May
                5: {'title': 'Finals', 'players': 'TBD vs TBD', 'time': '16:00', 'court': 'Center Court'}
            }
        },
        2026: {
            3: { // April
                10: {'title': 'Opening Round', 'players': 'Carlos vs Andy', 'time': '12:00', 'court': 'Court 1'}
            }
        }
    };

    // Get DOM elements
    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');

    // Function to calculate days in a month and first day
    function getMonthInfo(year, month) {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const firstDay = new Date(year, month, 1).getDay();
        return { days: daysInMonth, firstDay: firstDay };
    }

    // Function to show calendar
    function showCalendar(year, month) {
        const monthInfo = getMonthInfo(year, month);
        const monthMatches = matches[year] && matches[year][month] ? matches[year][month] : {};
        const calendarBody = document.getElementById('calendar-body');
        
        let html = '';
        let day = 1;

        while (day <= monthInfo.days) {
            html += '<tr>';
            for (let i = 0; i < 7; i++) {
                if ((day === 1 && i < monthInfo.firstDay) || day > monthInfo.days) {
                    html += '<td></td>';
                } else {
                    html += `
                        <td>
                            <div class="calendar-day">
                                ${day}
                                ${monthMatches[day] ? `<div class="match-indicator" data-match='${JSON.stringify(monthMatches[day])}'>🎾</div>` : ''}
                            </div>
                        </td>
                    `;
                    day++;
                }
            }
            html += '</tr>';
        }
        calendarBody.innerHTML = html;
        
        // Add event listeners to match indicators
        const matchIndicators = document.querySelectorAll('.match-indicator');
        let activeMessageBox = null;

        matchIndicators.forEach(indicator => {
            indicator.addEventListener('mouseover', function() {
                const matchData = JSON.parse(this.dataset.match);
                activeMessageBox = showMatchDetails(matchData);
            });

            indicator.addEventListener('mouseout', function() {
                if (activeMessageBox) {
                    activeMessageBox.remove();
                    activeMessageBox = null;
                }
            });
        });
    }

    // Function to show match details
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
            messageBox.style.left = (e.pageX + 10) + 'px';
            messageBox.style.top = (e.pageY + 10) + 'px';
        });

        document.body.appendChild(messageBox);
        return messageBox;
    }

    // Event listener for dropdown changes
    function updateCalendar() {
        const selectedMonth = parseInt(monthSelect.value);
        const selectedYear = parseInt(yearSelect.value);
        showCalendar(selectedYear, selectedMonth);
    }

    monthSelect.addEventListener('change', updateCalendar);
    yearSelect.addEventListener('change', updateCalendar);

    // Show default calendar (April 2025)
    showCalendar(2025, 3);
});

// Generate calendar for a month
function showCalendar(matches, months, monthName) {
    const month = months[monthName];
    const monthMatches = matches[monthName];
    const calendarBody = document.getElementById('calendar-body');
    
    let html = '';
    let day = 1;

    while (day <= month.days) {
        html += '<tr>';
        for (let i = 0; i < 7; i++) {
            if ((day === 1 && i < month.firstDay) || day > month.days) {
                html += '<td></td>';
            } else {
                html += `
                    <td>
                        <div class="calendar-day">
                            ${day}
                            ${monthMatches[day] ? `<div class="match-indicator" data-match='${JSON.stringify(monthMatches[day])}'>🎾</div>` : ''}
                        </div>
                    </td>
                `;
                day++;
            }
        }
        html += '</tr>';
    }
    calendarBody.innerHTML = html;
        
    // Add event listeners to match indicators
    const matchIndicators = document.querySelectorAll('.match-indicator');
    let activeMessageBox = null;

    matchIndicators.forEach(indicator => {
        indicator.addEventListener('mouseover', function() {
            const matchData = JSON.parse(this.dataset.match);
            activeMessageBox = showMatchDetails(matchData);
        });

        indicator.addEventListener('mouseout', function() {
            if (activeMessageBox) {
                activeMessageBox.remove();
            }
        });
    });
}

function showMatchDetails(match) {
    // Create message box
    const messageBox = document.createElement('div');
    messageBox.className = 'match-message-box';
    messageBox.innerHTML = `
        <h3>Match Details</h3>
        <p>Title: ${match.title}</p>
        <p>Players: ${match.players}</p>
        <p>Time: ${match.time}</p>
        <p>Court: ${match.court}</p>
    `;

    // Position the message box near the cursor
    document.addEventListener('mousemove', function updatePosition(e) {
        messageBox.style.left = (e.pageX + 10) + 'px';
        messageBox.style.top = (e.pageY + 10) + 'px';
    });

    // Append message box to body
    document.body.appendChild(messageBox);

    // Return the message box to remove event listener later
    return messageBox;
}