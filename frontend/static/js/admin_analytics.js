document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('audit-search-input');
    const tableBody = document.getElementById('audit-table-body');
    
    if (searchInput && tableBody) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase().trim();
            const rows = tableBody.querySelectorAll('tr');
            
            rows.forEach(row => {
                // Si es la fila de estado vacío, no hacer nada
                if (row.cells.length === 1 && row.cells[0].textContent.includes('Sin logs')) {
                    return;
                }
                
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
