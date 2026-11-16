let grafica = null;
let ejecutando = false;
let temporizador = null;
let estadoActual = null;
let progresoAnimacion = 0;

// Plugin de Chart.js para dibujar línea punteada vertical en cambios (Bloqueo / Atajo)
const pluginEventos = {
    id: "lineasEventos",
    afterDatasetsDraw(chart) {
        if (!estadoActual || !estadoActual.historial) return;
        const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;

        estadoActual.historial.forEach((punto, idx) => {
            if (punto.evento) {
                const posX = x.getPixelForValue(idx);
                ctx.save();
                ctx.beginPath();
                ctx.setLineDash([4, 4]);
                ctx.strokeStyle = "#c85a32";
                ctx.lineWidth = 1.5;
                ctx.moveTo(posX, top);
                ctx.lineTo(posX, bottom);
                ctx.stroke();

                ctx.fillStyle = "#c85a32";
                ctx.font = "11px sans-serif";
                ctx.fillText(punto.evento, posX + 5, top + 12);
                ctx.restore();
            }
        });
    }
};

function inicializarGrafica() {
    const ctx = document.getElementById("grafica").getContext("2d");
    grafica = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "% en camino óptimo",
                data: [],
                borderColor: "#0d6e52",
                borderWidth: 1.8,
                pointRadius: 0,
                tension: 0.15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    display: true,
                    ticks: { maxTicksLimit: 8, font: { size: 10 } },
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 50,
                        callback: val => val + "%",
                        font: { size: 10 }
                    }
                }
            }
        },
        plugins: [pluginEventos]
    });
}

function dibujarMapa() {
    if (!estadoActual) return;
    const canvas = document.getElementById("mapaCanvas");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const mapaNodos = {};
    estadoActual.nodos.forEach(n => { mapaNodos[n.id] = n; });

    // Conjunto de aristas del camino óptimo de referencia
    const aristasOptimas = new Set();
    const opt = estadoActual.camino_optimo || [];
    for (let i = 0; i < opt.length - 1; i++) {
        aristasOptimas.add(`${opt[i]}-${opt[i + 1]}`);
        aristasOptimas.add(`${opt[i + 1]}-${opt[i]}`);
    }

    // 1. Dibujar conexiones (grosor según feromona)
    estadoActual.conexiones.forEach(c => {
        // Si es el atajo y aún está cerrado, no se muestra todavía
        if (c.es_atajo && c.cerrado) return;

        const p1 = mapaNodos[c.origen];
        const p2 = mapaNodos[c.destino];
        const esOptima = aristasOptimas.has(`${c.origen}-${c.destino}`);

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);

        if (c.cerrado) {
            ctx.setLineDash([6, 5]);
            ctx.strokeStyle = "#c85a32";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Dibujar X en el centro del tramo cerrado
            const mx = (p1.x + p2.x) / 2;
            const my = (p1.y + p2.y) / 2;
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.moveTo(mx - 6, my - 6);
            ctx.lineTo(mx + 6, my + 6);
            ctx.moveTo(mx + 6, my - 6);
            ctx.lineTo(mx - 6, my + 6);
            ctx.stroke();
        } else {
            // Grosor proporcional a la feromona (0.05 a 20 -> 0.8px a 7.5px)
            const grosor = Math.max(0.8, Math.min(7.5, c.feromona * 0.45));
            ctx.strokeStyle = c.feromona > 2.5 ? "#0d6e52" : (esOptima ? "#7ab3a1" : "#c6d4ce");
            ctx.lineWidth = grosor;
            ctx.stroke();
        }
        ctx.restore();
    });

    // 2. Dibujar hormigas animadas de la última generación
    if (estadoActual.rutas_actuales && estadoActual.rutas_actuales.length > 0) {
        ctx.fillStyle = "#1a1a1a";
        estadoActual.rutas_actuales.forEach((camino, idx) => {
            if (camino.length < 2) return;
            const fase = (progresoAnimacion + (idx * 0.05)) % 1;
            const posExacta = fase * (camino.length - 1);
            const tramo = Math.floor(posExacta);
            const t = posExacta - tramo;

            const nA = mapaNodos[camino[tramo]];
            const nB = mapaNodos[camino[Math.min(tramo + 1, camino.length - 1)]];
            const hx = nA.x + (nB.x - nA.x) * t;
            const hy = nA.y + (nB.y - nA.y) * t;

            ctx.beginPath();
            ctx.arc(hx, hy, 2.5, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // 3. Dibujar nodos
    estadoActual.nodos.forEach(n => {
        ctx.save();
        ctx.beginPath();
        const esExtremo = n.id === "Nido" || n.id === "Comida";
        const radio = esExtremo ? 12 : 6;
        ctx.arc(n.x, n.y, radio, 0, Math.PI * 2);

        if (n.id === "Comida") {
            ctx.fillStyle = "#c4882b";
            ctx.fill();
        } else {
            ctx.fillStyle = "#ffffff";
            ctx.fill();
            ctx.lineWidth = esExtremo ? 2.5 : 1.5;
            ctx.strokeStyle = "#1f2d27";
            ctx.stroke();
        }

        ctx.fillStyle = "#2b3b34";
        ctx.font = esExtremo ? "bold 12px sans-serif" : "11px sans-serif";
        ctx.textAlign = "center";
        const offsetY = esExtremo ? 26 : -12;
        ctx.fillText(n.id, n.x, n.y + offsetY);
        ctx.restore();
    });
}

function bucleAnimacion() {
    if (ejecutando) {
        progresoAnimacion = (progresoAnimacion + 0.04) % 1;
        dibujarMapa();
    }
    requestAnimationFrame(bucleAnimacion);
}

function actualizarInterfaz(datos) {
    estadoActual = datos;
    const u = datos.ultimo;

    document.getElementById("ind-gen").textContent = datos.generacion;
    document.getElementById("ind-pct").textContent = `${u.pct_optimo}%`;
    document.getElementById("ind-mejor").textContent = u.mejor_distancia ?? "-";
    document.getElementById("ind-media").textContent = u.distancia_media ?? "-";
    document.getElementById("ind-perdidas").textContent = u.perdidas;

    const rutaTxt = (datos.camino_optimo || []).join(" → ");
    let extra = "";
    if (datos.bloqueado) extra += " Se cerró el tramo E–H.";
    if (datos.atajo_abierto) extra += " Se abrió el atajo I–Comida.";
    document.getElementById("texto-optimo").innerHTML =
        `Camino óptimo de referencia: <strong>${rutaTxt}</strong> (${Math.round(datos.distancia_optima)} unidades).${extra}`;

    document.getElementById("btn-bloquear").disabled = datos.bloqueado;
    document.getElementById("btn-atajo").disabled = datos.atajo_abierto;

    // Actualizar gráfica
    grafica.data.labels = datos.historial.map(h => h.generacion);
    grafica.data.datasets[0].data = datos.historial.map(h => h.pct_optimo);
    grafica.update();

    dibujarMapa();
}

async function ejecutarPaso() {
    if (!ejecutando) return;
    const payload = {
        alpha: document.getElementById("alpha").value,
        beta: document.getElementById("beta").value,
        evaporacion: document.getElementById("evaporacion").value,
        num_hormigas: document.getElementById("num_hormigas").value,
        num_exploradoras: document.getElementById("num_exploradoras").value
    };

    const res = await fetch("/paso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const datos = await res.json();
    actualizarInterfaz(datos);
}

function alternarPausa() {
    ejecutando = !ejecutando;
    const btn = document.getElementById("btn-pausar");
    if (ejecutando) {
        btn.textContent = "Pausar";
        iniciarTemporizador();
    } else {
        btn.textContent = "Reanudar";
        clearInterval(temporizador);
    }
}

function iniciarTemporizador() {
    clearInterval(temporizador);
    const vel = parseInt(document.getElementById("velocidad").value, 10);
    temporizador = setInterval(ejecutarPaso, Math.round(1000 / vel));
}

function actualizarVelocidad() {
    actualizarEtiqueta("velocidad");
    if (ejecutando) iniciarTemporizador();
}

function actualizarEtiqueta(id) {
    document.getElementById(`val-${id}`).textContent = document.getElementById(id).value;
}

async function reiniciarSimulacion() {
    const res = await fetch("/reiniciar", { method: "POST" });
    const datos = await res.json();
    actualizarInterfaz(datos);
}

async function bloquearTramo() {
    const res = await fetch("/bloquear", { method: "POST" });
    const datos = await res.json();
    actualizarInterfaz(datos);
}

async function abrirAtajo() {
    const res = await fetch("/atajo", { method: "POST" });
    const datos = await res.json();
    actualizarInterfaz(datos);
}

window.onload = async () => {
    inicializarGrafica();
    const res = await fetch("/estado");
    const datos = await res.json();
    actualizarInterfaz(datos);
    requestAnimationFrame(bucleAnimacion);
};