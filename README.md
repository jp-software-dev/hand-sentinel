# Hand Sentinel: Computer Vision Engine

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange.svg?style=for-the-badge&logo=google&logoColor=white)](https://google.github.io/mediapipe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Hand Sentinel** es un motor de reconocimiento gestual de alto rendimiento desarrollado en Python. Utiliza modelos de Deep Learning para el mapeo de 21 nodos articulares, traduciendo movimientos físicos en flujos de datos binarios para control de interfaces y automatización táctica.

---

## Quick Start (Windows)

Sigue estos pasos para desplegar el centinela en tu entorno local:

```bash
# 1. Clonar el repositorio
git clone [https://github.com/jp-software-dev/hand-sentinel.git](https://github.com/jp-software-dev/hand-sentinel.git)
cd hand-sentinel

# 2. Configurar entorno virtual e instalar dependencias
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Ejecutar el orquestador
python main.py