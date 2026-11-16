
import networkx as nx
import random

# Crear el territorio como un grafo
def crear_grafo():
    grafo = nx.Graph()

    conexiones = [
        ("Nido", "A", 100),
        ("Nido", "B", 150),
        ("A", "C", 120),
        ("B", "C", 90),
        ("B", "D", 110),
        ("C", "Comida", 180),
        ("D", "Comida", 130),
    ]

    for origen, destino, distancia in conexiones:
        grafo.add_edge(
            origen,
            destino,
            distancia=distancia,
            feromona=1.0,
            abierta=True
        )

    return grafo


# Calcular la decisión de cada hormiga
def elegir_camino(grafo, actual, visitados, alfa, beta, exploradora):

    opciones = []

    for vecino in grafo.neighbors(actual):
        datos = grafo[actual][vecino]

        if not datos["abierta"] or vecino in visitados:
            continue

        distancia = datos["distancia"]
        feromona = datos["feromona"]

        if exploradora:
            peso = 1 / distancia
        else:
            peso = (feromona ** alfa) * ((1 / distancia) ** beta)

        opciones.append((vecino, peso))

    if not opciones:
        return None

    # Selección probabilística
    total = sum(peso for _, peso in opciones)
    valor = random.random() * total

    acumulado = 0

    for vecino, peso in opciones:
        acumulado += peso
        if acumulado >= valor:
            return vecino

    return opciones[-1][0]


# Simulación de una generación
def simular_generacion(
    grafo,
    hormigas=20,
    exploradoras=2,
    alfa=1,
    beta=2,
    evaporacion=0.10
):

    rutas = []
    perdidas = 0

    for numero in range(hormigas):

        exploradora = numero < exploradoras
        actual = "Nido"
        visitados = [actual]
        distancia_total = 0

        while actual != "Comida":

            siguiente = elegir_camino(
                grafo,
                actual,
                visitados,
                alfa,
                beta,
                exploradora
            )

            if siguiente is None:
                perdidas += 1
                break

            distancia_total += grafo[actual][siguiente]["distancia"]
            visitados.append(siguiente)
            actual = siguiente

        if actual == "Comida":
            rutas.append({
                "camino": visitados,
                "distancia": distancia_total
            })

    # Evaporación de feromonas
    for origen, destino in grafo.edges():

        datos = grafo[origen][destino]

        if datos["abierta"]:
            datos["feromona"] *= (1 - evaporacion)
            datos["feromona"] = max(0.05, datos["feromona"])

    # Reforzar las cinco mejores rutas
    mejores = sorted(rutas, key=lambda ruta: ruta["distancia"])[:5]

    for ruta in mejores:
        refuerzo = 100 / ruta["distancia"]

        for i in range(len(ruta["camino"]) - 1):
            a = ruta["camino"][i]
            b = ruta["camino"][i + 1]

            datos = grafo[a][b]
            datos["feromona"] += refuerzo
            datos["feromona"] = min(20, datos["feromona"])

    return rutas, perdidas


# Ejecutar varias generaciones
def ejecutar_simulacion(generaciones=100):

    grafo = crear_grafo()
    resultados = []

    for generacion in range(generaciones):

        rutas, perdidas = simular_generacion(grafo)

        mejor = min(
            rutas,
            key=lambda ruta: ruta["distancia"],
            default=None
        )

        resultados.append({
            "generacion": generacion + 1,
            "mejor_distancia": (
                mejor["distancia"] if mejor else None
            ),
            "mejor_camino": (
                mejor["camino"] if mejor else []
            ),
            "perdidas": perdidas,
            "rutas_encontradas": len(rutas)
        })

    return resultados, grafo
