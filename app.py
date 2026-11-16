
from flask import Flask, render_template, jsonify
from hormigas import ejecutar_simulacion

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/simular")
def simular():
    resultados, grafo = ejecutar_simulacion(100)

    return jsonify({
        "resultados": resultados,
        "nodos": list(grafo.nodes()),
        "conexiones": [
            {
                "origen": origen,
                "destino": destino,
                "distancia": datos["distancia"],
                "feromona": round(datos["feromona"], 4)
            }
            for origen, destino, datos in grafo.edges(data=True)
        ]
    })


if __name__ == "__main__":
    app.run(debug=True)
