document.addEventListener('DOMContentLoaded', function() {
    // Simple month configuration
    const months = {
        april: { days: 30, firstDay: 2 },
        may: { days: 31, firstDay: 4 }
    };

    // Get matches data
    const matches = {
        april: {
            3: {'title': 'Quarter Final', 'players': 'Emma vs Naomi', 'time': '14:00', 'court': 'Court 1'},
            7: {'title': 'Semi Final', 'players': 'Serena vs Venus', 'time': '15:30', 'court': 'Center Court'},
            15: {'title': 'Mixed Doubles', 'players': 'Alex & Sam vs Tina & Mike', 'time': '13:00', 'court': 'Court 2'},
            21: {'title': 'Final', 'players': 'Rafael vs Novak', 'time': '16:00', 'court': 'Center Court'}
        },
        may: {
            5: { title: "Finals", players: "TBD vs TBD", time: "16:00", court: "Center Court" }
        }
    };

    // Get DOM elements
    const btnApril = document.getElementById('btn-april');
    const btnMay = document.getElementById('btn-may');

    // Add button listeners
    btnApril.addEventListener('click', () => {
        btnMay.classList.remove('active');
        btnApril.classList.add('active');
        showCalendar(matches, months, 'april');
    });

    btnMay.addEventListener('click', () => {
        btnApril.classList.remove('active');
        btnMay.classList.add('active');
        showCalendar(matches, months, 'may');
    });

    // Show April calendar by default
    showCalendar(matches, months, 'april');
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