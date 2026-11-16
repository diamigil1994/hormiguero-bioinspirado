import statistics
from hormigas import ejecutar_simulacion

def evaluar_escenario(nombre, **kwargs):
    exitos = 0
    gens_exito = []
    eficiencias = []
    perdidas_totales = []

    gen_cambio = kwargs.get("gen_bloqueo") or kwargs.get("gen_atajo") or 1

    for semilla in range(1, 31):
        historial, _ = ejecutar_simulacion(generaciones=260, semilla=semilla, **kwargs)
        perdidas_totales.append(sum(h["perdidas"] for h in historial) / 260)

        # Eficiencia en las últimas 20 generaciones
        ultimas_20 = historial[-20:]
        efics = [
            (h["distancia_optima"] / h["distancia_media"]) * 100
            for h in ultimas_20 if h["distancia_media"]
        ]
        if efics:
            eficiencias.append(statistics.mean(efics))

        # Éxito: >= 80% en camino óptimo durante 5 generaciones seguidas tras el cambio
        racha = 0
        for h in historial:
            if h["generacion"] >= gen_cambio:
                if h["pct_optimo"] >= 80.0:
                    racha += 1
                    if racha == 5:
                        exitos += 1
                        gens_exito.append(h["generacion"] - gen_cambio - 4)
                        break
                else:
                    racha = 0

    mediana_gen = statistics.median(gens_exito) if gens_exito else "No converge"
    ef_media = round(statistics.mean(eficiencias), 1) if eficiencias else 0
    perd_media = round(statistics.mean(perdidas_totales), 1)
    print(f"{nombre:<25} | Éxito: {exitos}/30 ({round(exitos/30*100)}%) | Mediana gen: {mediana_gen} | Eficiencia: {ef_media}% | Perdidas: {perd_media}")

if __name__ == "__main__":
    print("=== VALIDACIÓN DE ESCENARIOS (30 SEMILLAS) ===")
    evaluar_escenario("Base (Completo)")
    evaluar_escenario("Bloqueo E-H (gen 120)", gen_bloqueo=120)
    evaluar_escenario("Atajo I-Comida (gen 120)", gen_atajo=120)
    print("\n=== PRUEBAS DE ABLACIÓN ===")
    evaluar_escenario("Sin exploradoras", num_exploradoras=0)
    evaluar_escenario("Sin cercanía (beta=0)", beta=0.0)
    evaluar_escenario("Sin feromona (alpha=0)", alpha=0.0)