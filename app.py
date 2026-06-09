import streamlit as st
import ollama
from pydantic import BaseModel, Field
from typing import List, Literal
import re

# 1. DEFINICIÓN DEL ESQUEMA (Pydantic)
class Entity(BaseModel):
    tipo: Literal['NOMBRE', 'EMAIL', 'TELEFONO', 'DNI', 'DIRECCION', 'IBAN', 'TARJETA','PEDIDO']
    texto: str = Field(description="El fragmento exacto de texto detectado")

class DetectionResult(BaseModel):
    entities: List[Entity]

# 2. LÓGICA DE DETECCIÓN (Ollama + Structured Output)
def detectar_entidades(texto_original: str) -> DetectionResult:
    prompt_system = (
        "Eres un experto en extracción de datos. Tu tarea es identificar los siguientes elementos:"
        "- Nombres de personas."
        "- Direcciones de email."
        "- Números de identificación (DNI)."
        "- **Números de pedido o referencias de compra (ejemplo: #12345, ORD-99).**"
        '- numeros de cuenta bancaria (IBAN)(ejemplo: ES9121000418450200051332).'
        "Devuelve un JSON con una lista de entidades, cada una con su tipo y el texto exacto detectado."
    )
    
    try:
        response = ollama.chat(
            model='llama3',  # Puedes cambiarlo por el modelo que tengas
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': f"Extrae los datos de este texto: {texto_original}"}
            ],
            format=DetectionResult.model_json_schema() # Uso de schema para salida estructurada
        )
        
        # Parseamos la respuesta directamente al modelo Pydantic
        return DetectionResult.model_validate_json(response['message']['content'])
    except Exception as e:
        st.error(f"Error en la detección: {e}")
        return DetectionResult(entities=[])

# 3. LÓGICA DE ANONIMIZACIÓN (Python puro)
def anonimizar_texto(texto_original: str, deteccion: DetectionResult) -> str:
    texto_modificado = texto_total = texto_original
    
    # IMPORTANTE: Ordenar las entidades por longitud (de mayor a menor)
    # Esto evita que si detecta "Juan" y "Juan Pérez", primero borre "Juan" 
    # y deje el texto corrupto como "[NOMBRE] Pérez".
    entidades_ordenadas = sorted(deteccion.entities, key=lambda x: len(x.texto), reverse=True)
    
    for ent in entidades_ordenadas:
        # Usamos escape para evitar errores con caracteres especiales en el texto detectado
        patron = re.escape(ent.texto)
        texto_modificado = re.sub(patron, f"[{ent.tipo}]", texto_modificado)
        
    return texto_modificado

# 4. INTERFAZ WEB (Streamlit)

def main():
    st.set_page_config(page_title="Anonymizer AI", page_icon="🛡️")
    st.title("🛡️ Local PII Anonymizer")

    # --- BARRA LATERAL: CONFIGURACIÓN ---
    st.sidebar.header("Configuración de Ollama")
    
    # Aquí el usuario puede escribir el nombre del modelo que tenga instalado
    # Por defecto pongo 'llama3', pero puedes cambiarlo por el tuyo
    modelo_seleccionado = st.sidebar.text_input("Nombre del modelo en Ollama:", value="llama3")
    
    st.sidebar.info(
        "💡 Tip: Usa `ollama list` en tu terminal para ver qué modelos tienes instalados "
        "y escribe el nombre exacto aquí."
    )

    st.markdown("Detecta y anonimiza datos personales sin que el texto salga de tu máquina.")

    # Input
    texto_input = st.text_area("Pega aquí el texto a procesar:", height=200, 
                                placeholder="Ej: Hola, soy Juan Pérez, mi email es juan@example.com...")

    if st.button("Procesar y Anonimizar"):
        if not texto_input.strip():
            st.warning("Por favor, introduce algún texto.")
            return

        with st.spinner(f"Analizando texto con {modelo_seleccionado}..."):
            # PASO 1: Llamamos a la detección pasando el modelo seleccionado
            # (Tendrás que modificar la función detectar_entidades para aceptar el modelo)
            try:
                resultado_deteccion = detectar_entidades_dinamico(texto_input, modelo_seleccionado)
                
                if resultado_deteccion.entities:
                    texto_anonimizado = anonimizar_texto(texto_input, resultado_deteccion)
                    
                    st.subheader("✅ Resultado de la anonimización")
                    st.text_area("Texto procesado:", value=texto_anonimizado, height=150, disabled=True)

                    st.subheader("📊 Datos detectados")
                    datos_tabla = [ent.model_dump() for ent in resultado_deteccion.entities]
                    st.table(datos_tabla)

                    st.download_button(
                        label="Descargar texto anonimizado",
                        data=texto_anonimizado,
                        file_name="texto_anonimizado.txt",
                        mime="text/plain"
                    )
                    st.success(f"Se han detectado y sustituido {len(resultado_deteccion.entities)} elementos.")
                else:
                    st.info("No se detectaron datos personales en el texto.")
            except Exception as e:
                st.error(f"Error al procesar: {e}")

# --- MODIFICACIÓN NECESARIA EN LA FUNCIÓN DE DETECCIÓN ---
def detectar_entidades_dinamico(texto_original: str, nombre_modelo: str) -> DetectionResult:
    prompt_system = (
        "Eres un experto en privacidad y detección de PII (Información de Identificación Personal). "
        "Tu tarea es analizar el texto y extraer únicamente los datos personales presentes. "
        "No inventes datos, solo extrae los que existan exactamente en el texto. "
        "Debes devolver un JSON con una lista de entidades bajo el esquema solicitado."
    )
    
    response = ollama.chat(
        model=nombre_modelo,  # <--- USAMOS EL MODELO DEL SIDEBAR
        messages=[
            {'role': 'system', 'content': prompt_system},
            {'role': 'user', 'content': f"Extrae los datos de este texto: {texto_original}"}
        ],
        format=DetectionResult.model_json_schema()
    )
    return DetectionResult.model_validate_json(response['message']['content'])
if __name__ == "__main__":
    main()