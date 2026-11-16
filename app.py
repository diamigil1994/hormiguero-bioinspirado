from flask import Flask, render_template, jsonify, request
from hormigas import crear_grafo, simular_generacion, obtener_camino_dijkstra

app = Flask(__name__)

# Estado global de la sesión interactiva
estado = {
    "grafo": crear_grafo(bloquear_eh=False, abrir_atajo=False),
    "generacion": 0,
    "historial": [],
    "bloqueado": False,
    "atajo_abierto": False,
    "ultimas_rutas": []
}


def serializar_estado():
    grafo = estado["grafo"]
    camino_optimo, dist_optima = obtener_camino_dijkstra(grafo)

    nodos = [
        {"id": nodo, "x": datos["x"], "y": datos["y"]}
        for nodo, datos in grafo.nodes(data=True)
    ]

    conexiones = [
        {
            "origen": u,
            "destino": v,
            "distancia": datos["distancia"],
            "feromona": round(datos["feromona"], 4),
            "cerrado": datos["cerrado"],
            "es_atajo": datos["es_atajo"]
        }
        for u, v, datos in grafo.edges(data=True)
    ]

    ultimo = estado["historial"][-1] if estado["historial"] else {
        "generacion": 0,
        "pct_optimo": 0,
        "mejor_distancia": None,
        "distancia_media": None,
        "perdidas": 0,
        "evento": None
    }

    return {
        "generacion": estado["generacion"],
        "nodos": nodos,
        "conexiones": conexiones,
        "camino_optimo": camino_optimo,
        "distancia_optima": dist_optima,
        "bloqueado": estado["bloqueado"],
        "atajo_abierto": estado["atajo_abierto"],
        "ultimo": ultimo,
        "historial": estado["historial"],
        "rutas_actuales": [r["camino"] for r in estado["ultimas_rutas"]]
    }


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/estado")
def obtener_estado():
    return jsonify(serializar_estado())


@app.route("/paso", methods=["POST"])
def avanzar_paso():
    params = request.get_json() or {}
    alpha = float(params.get("alpha", 1.0))
    beta = float(params.get("beta", 2.0))
    evaporacion = float(params.get("evaporacion", 0.10))
    num_hormigas = int(params.get("num_hormigas", 20))
    num_exploradoras = int(params.get("num_exploradoras", 2))

    estado["generacion"] += 1
    grafo = estado["grafo"]

    rutas, perdidas = simular_generacion(
        grafo,
        num_hormigas=num_hormigas,
        num_exploradoras=num_exploradoras,
        alpha=alpha,
        beta=beta,
        evaporacion=evaporacion
    )
    estado["ultimas_rutas"] = rutas

    camino_optimo, dist_optima = obtener_camino_dijkstra(grafo)
    en_optimo = sum(1 for r in rutas if r["camino"] == camino_optimo)
    pct_optimo = round((en_optimo / num_hormigas) * 100) if num_hormigas > 0 else 0
    mejor = min(rutas, key=lambda r: r["distancia"], default=None)
    dist_media = round(sum(r["distancia"] for r in rutas) / len(rutas)) if rutas else None

    estado["historial"].append({
        "generacion": estado["generacion"],
        "pct_optimo": pct_optimo,
        "mejor_distancia": round(mejor["distancia"]) if mejor else None,
        "distancia_media": dist_media,
        "perdidas": perdidas,
        "evento": None
    })

    return jsonify(serializar_estado())


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    estado["grafo"] = crear_grafo(bloquear_eh=False, abrir_atajo=False)
    estado["generacion"] = 0
    estado["historial"] = []
    estado["bloqueado"] = False
    estado["atajo_abierto"] = False
    estado["ultimas_rutas"] = []
    return jsonify(serializar_estado())


@app.route("/bloquear", methods=["POST"])
def bloquear_tramo():
    if not estado["bloqueado"]:
        estado["grafo"]["E"]["H"]["cerrado"] = True
        estado["bloqueado"] = True
        if estado["historial"]:
            estado["historial"][-1]["evento"] = "Tramo cerrado"
    return jsonify(serializar_estado())


@app.route("/atajo", methods=["POST"])
def abrir_atajo():
    if not estado["atajo_abierto"]:
        estado["grafo"]["I"]["Comida"]["cerrado"] = False
        estado["atajo_abierto"] = True
        if estado["historial"]:
            estado["historial"][-1]["evento"] = "Atajo abierto"
    return jsonify(serializar_estado())


if __name__ == "__main__":
    app.run(debug=True)