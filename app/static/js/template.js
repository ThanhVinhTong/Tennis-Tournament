// template.js —— Control sidebar folding & responsiveness
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.getElementById('sidebarToggle');

    // Default: expand on large screen, collapse on small screen
    function initState() {
        if (window.innerWidth < 768) {
            sidebar.classList.remove('collapsed');
            body.classList.toggle('sidebar-collapsed', false);
        } else {
            sidebar.classList.toggle('collapsed', body.classList.contains('sidebar-collapsed'));
        }
    }
    initState();

    // Click to switch
    toggle.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        body.classList.toggle('sidebar-collapsed', isCollapsed);
        // Force redraw
        void sidebar.offsetWidth; 
    });

    
    window.addEventListener('resize', initState);
});