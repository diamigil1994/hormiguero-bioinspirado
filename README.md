# 🐜 Hormiguero Bioinspirado

Prototipo web interactivo de un agente inteligente basado en **Optimización por Colonias de Hormigas (ACO - Ant System)** para la toma de decisiones en la búsqueda de rutas dinámicas.

Proyecto desarrollado para el curso **Computación Bioinspirada** (Ingeniería de Software — UNIMINUTO).

## 📋 Descripción del proyecto

El sistema modela una colonia de hormigas artificiales que exploran un territorio representado como un grafo de **14 nodos** (`Nido`, puntos intermedios `A`–`L`, y `Comida`) y **21 tramos base** (más un tramo adicional de atajo `I–Comida`).

Cada hormiga decide su siguiente paso de forma probabilística combinando la **feromona acumulada** ($\tau$) y la **cercanía heurística** ($\eta = 1/L$):

$$p_j = \frac{\tau_j^{\alpha}\,\eta_j^{\beta}}{\sum_{k}\tau_k^{\alpha}\,\eta_k^{\beta}}$$

### Características principales
- **Motor ACO en Python (`hormigas.py`)**: 20 hormigas por generación (18 seguidoras + 2 exploradoras), evaporación ($\rho = 0.10$), refuerzo elitista de las 5 mejores rutas y límites de feromona $[0.05, 20]$.
- **Referencia exacta con Dijkstra (`NetworkX`)**: Cálculo en tiempo real del camino óptimo para medir eficacia y eficiencia.
- **Simulación dinámica e interactiva (`Flask` + `HTML5 Canvas` + `Chart.js`)**:
  - Visualización del grosor de feromona por tramo y desplazamiento de hormigas.
  - Controles deslizables en vivo para $\alpha$, $\beta$, $\rho$, población, exploradoras y velocidad.
  - Eventos dinámicos: **Bloquear tramo (`E–H`)** y **Abrir atajo (`I–Comida`)**.
- **Suite de validación estadística (`validar.py`)**: Ejecución automatizada de 30 semillas por escenario (Base, Bloqueo, Atajo) y pruebas de ablación (sin exploradoras, $\alpha=0$, $\beta=0$).

## 🛠️ Tecnologías utilizadas

- **Backend:** Python 3, Flask, NetworkX, NumPy
- **Frontend:** HTML5, CSS3, JavaScript (Canvas API), Chart.js
- **Control de versiones:** Git & GitHub

## 🚀 Instalación y ejecución local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/diamigil1994/hormiguero-bioinspirado.git](https://github.com/diamigil1994/hormiguero-bioinspirado.git)
   cd hormiguero-bioinspirado