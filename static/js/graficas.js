function iniciarGraficaAprobados(porcentaje) {
    const ctx = document.getElementById('graficaAprobados');
    if (!ctx) return;

    const pct = parseFloat(porcentaje);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Aprobados', 'Suspensos'],
            datasets: [{
                data: [pct, 100 - pct],
                backgroundColor: ['#4ecb71', '#e05f5f'],
                borderColor: ['#3aad5a', '#c04040'],
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '72%',
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cfcfe8', font: { size: 12 }, padding: 16 } },
                tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.toFixed(2)}%` } }
            }
        }
    });
}