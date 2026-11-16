# Hormiguero Bioinspirado — Optimización por Colonias de Hormigas (ACO)

Prototipo web interactivo de un agente inteligente basado en **Optimización por Colonias de Hormigas (ACO — Ant System)** para la toma de decisiones y adaptación dinámica en la búsqueda de rutas óptimas.

Proyecto desarrollado para el curso **Computación Bioinspirada** del programa de **Ingeniería de Software — Corporación Universitaria Minuto de Dios (UNIMINUTO)**.

---

## Descripción del problema y enfoque

Las hormigas reales carecen de visión global y control central, pero logran encontrar los caminos más cortos entre el nido y una fuente de alimento mediante comunicación indirecta (**estigmergia**) depositando rastros de feromona.

Este proyecto modela ese fenómeno colectivo en un territorio representado como un grafo de **14 nodos** (`Nido`, puntos intermedios `A`–`L` y `Comida`) y **21 tramos base**, más **1 tramo adicional de atajo (`I–Comida`)**. Cada hormiga construye su camino paso a paso evaluando de forma probabilística la feromona acumulada ($\tau$) y la cercanía heurística ($\eta = 1/L$):

$$p_j = \frac{\tau_j^{\alpha}\,\eta_j^{\beta}}{\sum_{k}\tau_k^{\alpha}\,\eta_k^{\beta}}$$

### Parámetros del modelo base
* **Peso de la feromona ($\alpha$):** `1.0`
* **Peso de la cercanía ($\beta$):** `2.0`
* **Tasa de evaporación ($\rho$):** `0.10` por generación
* **Población:** `20` hormigas por generación (`18` seguidoras + `2` exploradoras que ignoran el rastro)
* **Refuerzo elitista:** Solo las **5 mejores rutas** de cada generación depositan feromona, acotada en el rango $[0.05, 20.0]$

---

## Funcionalidades principales

* **Motor ACO en Python (`hormigas.py`):** Simulación paso a paso con evaporación, refuerzo elitista, hormigas exploradoras y cálculo del camino mínimo exacto de referencia mediante el **algoritmo de Dijkstra** (`NetworkX`).
* **Interfaz web interactiva (`Flask` + `HTML5 Canvas` + `Chart.js`):**
  * **Mapa en tiempo real:** El grosor y color de cada tramo reflejan la concentración de feromona; las hormigas animadas recorren las rutas de la última generación.
  * **Eventos dinámicos en vivo:** Botones para **Bloquear tramo (`E–H`)** (simula un obstáculo en la ruta óptima) y **Abrir atajo (`I–Comida`)** (habilita una ruta 4,8 % más corta).
  * **Controles deslizables:** Ajuste en vivo de $\alpha$, $\beta$, $\rho$, número de hormigas, exploradoras y velocidad de simulación.
  * **Indicadores y gráfica:** Generación actual, porcentaje de hormigas en el camino óptimo, mejor longitud, longitud media, hormigas perdidas y curva de convergencia con marcadores de eventos.
* **Suite de validación estadística (`validar.py`):** Ejecución automatizada de **30 semillas por escenario** (Base, Bloqueo en generación 120, Atajo en generación 120) y **pruebas de ablación** (sin exploradoras, sin cercanía $\beta=0$, sin feromona $\alpha=0$).

---

## Estructura del proyecto

```text
hormiguero-bioinspirado/
│
├── app.py                  # Servidor web Flask y API REST (/estado, /paso, /bloquear, /atajo)
├── hormigas.py             # Núcleo del algoritmo ACO, grafo de 14 nodos y referencia Dijkstra
├── validar.py              # Script de validación estadística (30 corridas y ablación)
├── requirements.txt        # Dependencias del proyecto
├── .gitignore              # Exclusión de entorno virtual y archivos temporales
├── README.md               # Documentación del proyecto
│
├── templates/
│   └── index.html          # Estructura de la interfaz web
│
└── static/
    ├── css/
    │   └── estilos.css     # Estilos responsivos del panel y visualización
    └── js/
        └── simulacion.js   # Renderizado en Canvas, animación de hormigas y gráfica Chart.js


## Tecnologías utilizadas
Backend y Algoritmo: Python 3, Flask, NetworkX, NumPy

Frontend y Visualización: HTML5, CSS3, JavaScript (ES6+), Canvas API, Chart.js

Control de versiones: Git & GitHub

## Instalación y ejecución local
1. Clonar el repositorio:

git clone [https://github.com/diamigil1994/hormiguero-bioinspirado.git](https://github.com/diamigil1994/hormiguero-bioinspirado.git)
cd hormiguero-bioinspirado

2. Crear y activar el entorno virtual:
python -m venv venv
source venv/Scripts/activate      # En Windows (Git Bash)
# source venv/bin/activate        # En Linux / macOS

3. Instalar las dependencias:
pip install -r requirements.txt

4. Iniciar la aplicación web:
python app.py
Abre tu navegador en http://127.0.0.1:5000 y pulsa Iniciar.

5. Ejecutar la validación estadística (opcional):
python validar.py

## Configuración,Éxito en escenario base,Eficiencia media,Recuperación / Adaptación
"Agente completo (α=1,β=2, 2 exploradoras)",100 % (30/30),"95,4 % – 96,4 %",Alta adaptación ante bloqueos y apertura de rutas
Sin exploradoras,97 % – 100 %,"98,7 % – 99,6 %",Baja capacidad de escape ante cambios dinámicos
Sin cercanía (β=0),97 % – 100 %,"94,9 % – 96,2 %",Convergencia inicial más lenta
Sin feromona (α=0),0 % (0/30),"63,0 % – 65,8 %",No converge (búsqueda aleatoria)


Autora
Diana Milena Gil Giraldo

Estudiante de Ingeniería de Software — Corporación Universitaria Minuto de Dios (UNIMINUTO)

GitHub: @diamigil1994