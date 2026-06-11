// ================ Zona Contadores ================ //

function iniciarContadores() {
    document.querySelectorAll('.counter').forEach(el => {
        const target = parseFloat(el.getAttribute('data-target'));
        const isInt = Number.isInteger(target);
        let current = 0;
        const increment = target / 40;
        const timer = setInterval(() => {
            current = Math.min(current + increment, target);
            el.textContent = isInt ? Math.round(current) : current.toFixed(2);
            if (current >= target) clearInterval(timer);
        }, 30);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    iniciarContadores();
});

// ================ Zona Filtros ================ //

function toggleFiltros() {
    const panel = document.getElementById('filtrosPanel');
    const btn = document.getElementById('toggleFiltros');
    const abierto = panel.classList.toggle('abierto');
    btn.textContent = abierto ? '\u25BC Filtros' : '\u25BC Filtros';
}

// Si hay filtros activos, abrir panel al cargar
document.addEventListener('DOMContentLoaded', () => {
    iniciarContadores();
    const params = new URLSearchParams(window.location.search);
    if (params.toString()) {
        const panel = document.getElementById('filtrosPanel');
        const btn = document.getElementById('toggleFiltros');
        if (panel) { panel.classList.add('abierto'); btn.textContent = '\u25B2 Filtros'; }
    }
});

// ================ Zona Pestañas ================ //

function cambiarPestanaGrafica(evento, idPestanaTarget) {
    // Buscar solo dentro del contenedor padre de este botón
    const contenedor = evento.currentTarget.closest('.contenedor-pestanas-graficas');
    
    contenedor.querySelectorAll('.contenido-pestana')
        .forEach(bloque => bloque.classList.remove('activa'));
    contenedor.querySelectorAll('.pestana-btn')
        .forEach(boton => boton.classList.remove('activa'));

    document.getElementById(idPestanaTarget).classList.add('activa');
    evento.currentTarget.classList.add('activa');
}

function toggleFiltrosById(panelId, btnId) {
    const panel = document.getElementById(panelId);
    const btn = document.getElementById(btnId);
    const abierto = panel.classList.toggle('abierto');
    btn.textContent = abierto ? '\u25B2 Filtros' : '\u25BC Filtros';
}

// Al cargar, restaurar pestaña activa
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const pestanaActiva = params.get('pestana_activa');
    if (pestanaActiva) {
        const el = document.getElementById(pestanaActiva);
        if (el) {
            // Desactivar todas
            document.querySelectorAll('.contenido-pestana')
                .forEach(b => b.classList.remove('activa'));
            document.querySelectorAll('.pestana-btn')
                .forEach(b => b.classList.remove('activa'));
            // Activar la guardada
            el.classList.add('activa');
            // Activar el botón correspondiente
            document.querySelector(`[onclick*="${pestanaActiva}"]`)
                ?.classList.add('activa');
        }
    }
});