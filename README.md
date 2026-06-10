# Ticket Insight Analyzer

App de escritorio local para analizar archivos CSV con tickets de soporte y generar una lectura rápida del estado del backlog.

## Índice

- [Descripción](#descripción)
- [Demo rápida](#demo-rápida)
- [Herramientas usadas](#herramientas-usadas)
- [Características](#características)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Reporte generado](#reporte-generado)
- [Dataset de ejemplo](#dataset-de-ejemplo)
- [Mejoras futuras](#mejoras-futuras)

## Descripción

**Ticket Insight Analyzer** permite cargar un CSV de tickets de soporte, detectar columnas comunes, calcular métricas clave y exportar un reporte ejecutivo en Markdown.

El objetivo del proyecto es ofrecer un MVP simple, local y útil para personas de soporte, operaciones, producto o data que necesitan entender rápidamente el estado de un backlog sin usar una plataforma de BI.

## Demo rápida

Flujo principal:

1. Cargar un archivo `.csv`.
2. Revisar la preview inicial.
3. Ejecutar el análisis.
4. Visualizar KPIs y gráficos.
5. Exportar un reporte Markdown.
6. Abrir la carpeta de reportes desde la app.

## Herramientas usadas

<p>
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-Desktop%20UI-green" alt="PySide6">
  <img src="https://img.shields.io/badge/pandas-Data%20Analysis-purple?logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/matplotlib-Charts-orange" alt="matplotlib">
  <img src="https://img.shields.io/badge/Markdown-Reports-black?logo=markdown&logoColor=white" alt="Markdown">
</p>

## Características

- Carga local de archivos CSV.
- Preview de las primeras filas.
- Detección automática de columnas comunes.
- Mapeo avanzado opcional de columnas.
- KPIs principales del backlog.
- Gráficos simples de estados, prioridades, categorías, agentes y clientes.
- Detección de tickets abiertos antiguos.
- Análisis de palabras frecuentes en títulos o descripciones.
- Cálculo de un **Backlog Health Score** de 0 a 100.
- Recomendaciones simples basadas en reglas.
- Exportación de reporte Markdown en la carpeta `reports/`.
- Botón para abrir directamente la carpeta de reportes.

## Estructura del proyecto

```text
ticket-insight-analyzer/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── reports/
├── sample_data/
│   └── sample_support_tickets.csv
│
└── src/
    ├── __init__.py
    ├── csv_loader.py
    ├── column_mapper.py
    ├── analyzer.py
    ├── text_analyzer.py
    ├── report.py
    └── ui.py
```

## Instalación

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Actualizar `pip`:

```powershell
python -m pip install --upgrade pip
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Uso

Ejecutar la aplicación:

```powershell
python main.py
```

Luego, desde la interfaz:

1. Click en **Load CSV**.
2. Seleccionar un archivo de tickets.
3. Click en **Analyze Tickets**.
4. Revisar KPIs, gráficos y recomendaciones.
5. Click en **Export Markdown Report** para generar el reporte.
6. Click en **Open Reports Folder** para abrir la carpeta de salida.

## Reporte generado

El reporte Markdown incluye:

- Resumen ejecutivo.
- Total de tickets.
- Porcentaje de tickets abiertos.
- Tickets high o critical.
- Tickets abiertos antiguos.
- Top estados.
- Top prioridades.
- Top categorías.
- Top agentes.
- Top clientes.
- Palabras frecuentes.
- Backlog Health Score.
- Recomendaciones.

Los archivos se guardan automáticamente en:

```text
reports/
```

## Dataset de ejemplo

El proyecto incluye un dataset de prueba en:

```text
sample_data/sample_support_tickets.csv
```

Este archivo permite probar el flujo completo sin necesitar un export real de tickets.

## Mejoras futuras

- Exportar también en PDF.
- Agregar filtros por fecha, estado o prioridad.
- Permitir configurar reglas del Backlog Health Score.
- Guardar gráficos como imágenes dentro del reporte.
- Empaquetar la app como `.exe` usando PyInstaller.
- Mejorar soporte para distintos formatos de fecha.
- Agregar modo claro/oscuro desde la interfaz.

## Empaquetado futuro

Comando base para generar un ejecutable en Windows:

```powershell
pyinstaller --onefile --windowed --name ticket-insight-analyzer main.py
```

> Esta etapa queda fuera del MVP inicial, pero el proyecto está pensado para poder empaquetarse más adelante.
