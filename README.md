# Local PII Anonymizer

Anonimizador de datos personales (PII) que corre **100% en local** usando Ollama y Streamlit. Detecta información sensible mediante IA y la sustituye por etiquetas, sin que los datos salgan de tu máquina.

## Motivación

Enviar datos personales a APIs externas viola el RGPD. La solución: un modelo local (Ollama) que analiza el texto en tu propio hardware y lo anonimiza antes de cualquier procesamiento externo.

## Cómo funciona

Dos pasos separados:

1. **El modelo DETECTA** — Ollama devuelve una lista estructurada de entidades encontradas (tipo + fragmento exacto), usando `format=` con un esquema Pydantic.
2. **Tu código TACHA** — Python reemplaza cada fragmento por una etiqueta del tipo `[NOMBRE]`, `[EMAIL]`, etc.

Esta separación garantiza que los datos desaparecen (no dependes de que el modelo los omita al reescribir) y permite auditar exactamente qué se eliminó.

## Entidades detectadas

| Tipo | Ejemplo |
|------|--------|
| NOMBRE | Juan Pérez |
| EMAIL | juan@example.com |
| TELEFONO | +34 612 345 678 |
| DNI | 12345678A |
| DIRECCION | Calle Mayor 1, Madrid |
| IBAN | ES9121000418450200051332 |
| TARJETA | 4111 1111 1111 1111 |
| PEDIDO | #12345, ORD-99 |

## Requisitos

- Python 3.10+
- [Ollama](https://ollama.ai/) instalado y corriendo con al menos un modelo descargado (ej. `llama3`, `qwen3:4b`)

## Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd anonimizador

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install streamlit ollama pydantic
```

## Uso

```bash
# Asegúrate de que Ollama esté corriendo
ollama serve

# Arranca la web
streamlit run app.py
```

1. Pega un texto en el área de texto.
2. Haz clic en "Procesar y Anonimizar".
3. Revisa el texto anonimizado y la tabla de entidades detectadas.
4. Descarga el resultado si lo necesitas.

Puedes cambiar el modelo de Ollama desde la barra lateral.

## Estructura del proyecto

```
anonimizador/
├── app.py                    # Aplicación Streamlit (detección + anonimización + UI)
├── enunciado_anonimizador.md # Enunciado original del proyecto
├── requirements.txt          # Dependencias de Python
├── LICENSE                   # Licencia MIT
└── README.md                 # Este archivo
```

## Licencia

MIT
