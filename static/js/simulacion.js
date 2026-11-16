
let grafica = null;

async function iniciarSimulacion() {

    const respuesta = await fetch("/simular");
    const datos = await respuesta.json();

    const resultados = datos.resultados;

    const ultima = resultados[resultados.length - 1];

    document.getElementById("resultados").innerHTML = `
        <p><strong>Generaciones:</strong> ${resultados.length}</p>
        <p><strong>Mejor distancia:</strong>
        ${ultima.mejor_distancia ?? "Sin ruta"}</p>
        <p><strong>Mejor camino:</strong>
        ${ultima.mejor_camino.join(" → ")}</p>
        <p><strong>Hormigas perdidas:</strong>
        ${ultima.perdidas}</p>
    `;

    const contexto = document
        .getElementById("grafica")
        .getContext("2d");

    if (grafica) {
        grafica.destroy();
    }

    grafica = new Chart(contexto, {
        type: "line",

        data: {
            labels: resultados.map(r => r.generacion),

            datasets: [{
                label: "Mejor distancia por generación",
                data: resultados.map(r => r.mejor_distancia),
                borderWidth: 2,
                tension: 0.2
            }]
        },

        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
