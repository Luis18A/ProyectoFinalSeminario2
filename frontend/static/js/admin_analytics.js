document.addEventListener('DOMContentLoaded', () => {
    // 1. Filtro de búsqueda en la tabla de Logs de Auditoría
    const searchInput = document.getElementById('audit-search-input');
    const tableBody = document.getElementById('audit-table-body');
    
    if (searchInput && tableBody) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase().trim();
            const rows = tableBody.querySelectorAll('tr');
            
            rows.forEach(row => {
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

    // 2. Dibujado Dinámico de la Curva de Pareto
    const svg = document.getElementById('pareto-curve-svg');
    const path = document.getElementById('pareto-curve-path');
    const pointsGroup = document.getElementById('pareto-curve-points');
    const bars = document.querySelectorAll('.pareto-bar-wrapper');

    function renderParetoLine() {
        if (!svg || !path || !bars.length) return;

        const svgRect = svg.getBoundingClientRect();
        const W = svgRect.width;
        const H = svgRect.height;

        if (W === 0 || H === 0) {
            // Reintentar brevemente si el contenedor aún no tiene dimensiones en el DOM
            setTimeout(renderParetoLine, 100);
            return;
        }

        // Limpiar puntos y etiquetas anteriores
        pointsGroup.innerHTML = '';

        const points = [];

        bars.forEach((barWrapper, idx) => {
            const barRect = barWrapper.getBoundingClientRect();
            
            // Posición X del centro de la barra respecto al SVG
            const x = barRect.left - svgRect.left + barRect.width / 2;

            // Porcentaje acumulado leído del atributo data
            const acumulado = parseFloat(barWrapper.getAttribute('data-acumulado')) || 0;
            
            // Posición Y de la curva (100% es Y=0, 0% es Y=H)
            const y = H - (acumulado / 100) * H;

            points.push({ x, y, acumulado, dia: barWrapper.getAttribute('data-dia') });

            // Círculo marcador
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', '5');
            circle.setAttribute('fill', '#ffffff');
            circle.setAttribute('stroke', '#2563eb');
            circle.setAttribute('stroke-width', '2');
            circle.setAttribute('class', 'transition-all duration-200 cursor-pointer');
            
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `Acumulado ${barWrapper.getAttribute('data-dia')}: ${acumulado}%`;
            circle.appendChild(title);

            // Etiqueta de texto para mostrar el valor del porcentaje acumulado encima del punto
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            // Si el punto está muy al tope, colocar la etiqueta abajo en lugar de arriba para evitar que se corte
            const textY = y < 15 ? y + 15 : y - 10;
            text.setAttribute('y', textY);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#1d4ed8'); // azul oscuro
            text.setAttribute('font-size', '9px');
            text.setAttribute('font-family', 'monospace');
            text.setAttribute('font-weight', 'bold');
            text.textContent = `${acumulado}%`;

            pointsGroup.appendChild(circle);
            pointsGroup.appendChild(text);

            // Eventos para resaltado cruzado (Barra <-> Punto SVG)
            barWrapper.addEventListener('mouseenter', () => {
                circle.setAttribute('r', '8');
                circle.setAttribute('fill', '#2563eb');
                circle.setAttribute('stroke', '#ffffff');
                text.setAttribute('font-size', '11px');
                text.setAttribute('fill', '#1e40af'); // azul más oscuro en hover
            });
            
            barWrapper.addEventListener('mouseleave', () => {
                circle.setAttribute('r', '5');
                circle.setAttribute('fill', '#ffffff');
                circle.setAttribute('stroke', '#2563eb');
                text.setAttribute('font-size', '9px');
                text.setAttribute('fill', '#1d4ed8');
            });
        });

        // Construir la línea del trazado
        let pathD = '';
        points.forEach((pt, idx) => {
            if (idx === 0) {
                pathD = `M ${pt.x} ${pt.y}`;
            } else {
                pathD += ` L ${pt.x} ${pt.y}`;
            }
        });

        path.setAttribute('d', pathD);
    }

    // Retardo inicial para dar tiempo a que termine el reflow del layout y renderizar
    setTimeout(renderParetoLine, 250);

    // Redibujar en cada redimensión para mantener la alineación responsiva
    window.addEventListener('resize', renderParetoLine);
});
