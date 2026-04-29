document.addEventListener('DOMContentLoaded', () => {
    console.log('App JS Loaded');
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    console.log('Sidebar element:', sidebar);
    console.log('Toggle button:', toggleBtn);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            console.log('Sidebar toggle clicked');
            document.body.classList.toggle('sidebar-collapsed');
            
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }
});
