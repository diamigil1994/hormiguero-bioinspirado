import random
import networkx as nx

# Coordenadas (x, y) para visualizar el mapa en el frontend y calcular distancias reales
COORDENADAS = {
    "Nido": (60, 220),
    "A": (180, 90),
    "B": (180, 220),
    "C": (180, 350),
    "D": (320, 60),
    "E": (320, 175),
    "F": (320, 275),
    "G": (320, 380),
    "H": (460, 110),
    "I": (460, 215),
    "J": (460, 325),
    "K": (590, 155),
    "L": (590, 285),
    "Comida": (730, 220),
}

# 21 tramos base + 1 tramo de atajo (I - Comida)
# Distancias calibradas según los resultados del documento (759.1 base, 759.3 bloqueo, 722.4 atajo)
CONEXIONES_BASE = [
    ("Nido", "A", 180.0),
    ("Nido", "B", 120.0),
    ("Nido", "C", 185.0),
    ("A", "D", 145.0),
    ("A", "E", 170.0),
    ("B", "E", 150.0),
    ("B", "F", 155.0),
    ("C", "F", 160.0),
    ("C", "G", 145.0),
    ("D", "H", 150.0),
    ("E", "H", 161.0),   # Tramo que se cierra en el escenario de bloqueo
    ("E", "I", 161.0),
    ("F", "I", 165.0),
    ("F", "J", 150.0),
    ("G", "J", 155.0),
    ("H", "K", 160.0),
    ("I", "K", 155.0),
    ("I", "L", 165.0),
    ("J", "L", 145.0),
    ("K", "Comida", 168.1),  # Nido-B-E-H-K-Comida = 120 + 150 + 161 + 160 + 168.1 = 759.1
    ("L", "Comida", 189.3),  # Nido-B-F-J-L-Comida = 120 + 155 + 150 + 145 + 189.3 = 759.3
]

ATAJO = ("I", "Comida", 291.4)  # Nido-B-E-I-Comida = 120 + 150 + 161 + 291.4 = 722.4


def crear_grafo(bloquear_eh=False, abrir_atajo=False):
    grafo = nx.Graph()
    for nodo, (x, y) in COORDENADAS.items():
        grafo.add_node(nodo, x=x, y=y)

    for u, v, dist in CONEXIONES_BASE:
        cerrado = bloquear_eh and ({u, v} == {"E", "H"})
        grafo.add_edge(u, v, distancia=dist, feromona=1.0, cerrado=cerrado, es_atajo=False)

    u_a, v_a, dist_a = ATAJO
    grafo.add_edge(u_a, v_a, distancia=dist_a, feromona=1.0, cerrado=not abrir_atajo, es_atajo=True)
    return grafo


def obtener_camino_dijkstra(grafo):
    """Calcula el camino mínimo exacto considerando solo tramos abiertos."""
    grafo_abierto = nx.Graph()
    for u, v, datos in grafo.edges(data=True):
        if not datos["cerrado"]:
            grafo_abierto.add_edge(u, v, distancia=datos["distancia"])

    try:
        camino = nx.shortest_path(grafo_abierto, source="Nido", target="Comida", weight="distancia")
        distancia = nx.shortest_path_length(grafo_abierto, source="Nido", target="Comida", weight="distancia")
        return camino, round(distancia, 1)
    except nx.NetworkXNoPath:
        return [], None


def elegir_siguiente_nodo(grafo, actual, visitados, alpha, beta, es_exploradora):
    vecinos_validos = []
    for vecino in grafo.neighbors(actual):
        datos = grafo[actual][vecino]
        if not datos["cerrado"] and vecino not in visitados:
            vecinos_validos.append((vecino, datos))

    if not vecinos_validos:
        return None

    # Las hormigas exploradoras ignoran feromona y distancia (elección uniforme al azar)
    if es_exploradora:
        return random.choice(vecinos_validos)[0]

    pesos = []
    for vecino, datos in vecinos_validos:
        tau = datos["feromona"] ** alpha
        eta = (1.0 / datos["distancia"]) ** beta
        pesos.append(tau * eta)

    suma_pesos = sum(pesos)
    if suma_pesos == 0:
        return random.choice(vecinos_validos)[0]

    probabilidades = [p / suma_pesos for p in pesos]
    return random.choices([v[0] for v in vecinos_validos], weights=probabilidades, k=1)[0]


def simular_generacion(grafo, num_hormigas=20, num_exploradoras=2, alpha=1.0, beta=2.0, evaporacion=0.10):
    rutas_exitosas = []
    perdidas = 0

    for i in range(num_hormigas):
        es_exploradora = i < num_exploradoras
        actual = "Nido"
        camino = [actual]
        visitados = {actual}
        distancia_total = 0.0

        while actual != "Comida":
            siguiente = elegir_siguiente_nodo(grafo, actual, visitados, alpha, beta, es_exploradora)
            if siguiente is None:
                perdidas += 1
                break
            distancia_total += grafo[actual][siguiente]["distancia"]
            camino.append(siguiente)
            visitados.add(siguiente)
            actual = siguiente

        if actual == "Comida":
            rutas_exitosas.append({
                "camino": camino,
                "distancia": round(distancia_total, 1),
                "exploradora": es_exploradora
            })

    # 1. Evaporación en todos los tramos
    for _, _, datos in grafo.edges(data=True):
        datos["feromona"] = max(0.05, datos["feromona"] * (1.0 - evaporacion))

    # 2. Refuerzo únicamente de las 5 mejores rutas
    mejores = sorted(rutas_exitosas, key=lambda r: r["distancia"])[:5]
    for ruta in mejores:
        refuerzo = 100.0 / ruta["distancia"]
        for idx in range(len(ruta["camino"]) - 1):
            a = ruta["camino"][idx]
            b = ruta["camino"][idx + 1]
            grafo[a][b]["feromona"] = min(20.0, grafo[a][b]["feromona"] + refuerzo)

    return rutas_exitosas, perdidas


def ejecutar_simulacion(
    generaciones=260,
    num_hormigas=20,
    num_exploradoras=2,
    alpha=1.0,
    beta=2.0,
    evaporacion=0.10,
    gen_bloqueo=None,
    gen_atajo=None,
    semilla=None
):
    if semilla is not None:
        random.seed(semilla)

    grafo = crear_grafo(bloquear_eh=False, abrir_atajo=False)
    camino_optimo, dist_optima = obtener_camino_dijkstra(grafo)
    historial = []

    for gen in range(1, generaciones + 1):
        # Eventos dinámicos en la generación indicada (ej. generación 120)
        if gen_bloqueo and gen == gen_bloqueo:
            grafo["E"]["H"]["cerrado"] = True
            camino_optimo, dist_optima = obtener_camino_dijkstra(grafo)

        if gen_atajo and gen == gen_atajo:
            grafo["I"]["Comida"]["cerrado"] = False
            camino_optimo, dist_optima = obtener_camino_dijkstra(grafo)

        rutas, perdidas = simular_generacion(
            grafo, num_hormigas, num_exploradoras, alpha, beta, evaporacion
        )

        en_optimo = sum(1 for r in rutas if r["camino"] == camino_optimo)
        pct_optimo = round((en_optimo / num_hormigas) * 100, 1)
        mejor = min(rutas, key=lambda r: r["distancia"], default=None)
        dist_media = round(sum(r["distancia"] for r in rutas) / len(rutas), 1) if rutas else None

        historial.append({
            "generacion": gen,
            "pct_optimo": pct_optimo,
            "mejor_distancia": mejor["distancia"] if mejor else None,
            "distancia_media": dist_media,
            "mejor_camino": mejor["camino"] if mejor else [],
            "optimo_referencia": camino_optimo,
            "distancia_optima": dist_optima,
            "perdidas": perdidas
        })

    return historial, grafo
