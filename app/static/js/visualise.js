
const ctx = document.getElementById('performanceChart2').getCotnext('2d');

const performanceChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Matches Won',
        data: [2, 3, 1, 4, 2, 3, 5, 2, 1, 3, 2, 4],
        borderColor: '#1b842c',
        backgroundColor: 'rgba(27, 132, 44, 0.1)',
        tension: 0.3,
        fill: true
      },
      {
        label: 'Matches Lost',
        data :[1, 0, 2, 1, 1, 2, 0, 1, 2, 0, 1, 1],
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        tension: 0.3,
        fill: true
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
