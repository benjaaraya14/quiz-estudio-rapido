import streamlit as st
import json
import random
import os
import time

ARCHIVO = "preguntas.json"

def cargar_preguntas():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_preguntas(nuevas):
    preguntas = cargar_preguntas()
    preguntas.extend(nuevas)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=4, ensure_ascii=False)

def modo_estudio():
    st.header("📚 Modo Estudio - Ingresar Preguntas")
    cantidad = st.number_input("¿Cuántas preguntas quieres ingresar?", min_value=1, step=1)

    with st.form("form_preguntas"):
        nuevas = []
        for i in range(cantidad):
            st.subheader(f"Pregunta {i+1}")
            texto = st.text_input(f"Texto pregunta {i+1}", key=f"p{i}")
            a = st.text_input("Opción A", key=f"a{i}")
            b = st.text_input("Opción B", key=f"b{i}")
            c = st.text_input("Opción C", key=f"c{i}")
            correcta = st.selectbox("¿Cuál es la correcta?", ["A", "B", "C"], key=f"r{i}")
            nuevas.append({
                "texto": texto,
                "opciones": {"A": a, "B": b, "C": c},
                "respuesta_correcta": correcta
            })
        enviado = st.form_submit_button("Guardar preguntas")

        if enviado:
            preguntas_validas = [q for q in nuevas if q["texto"] and all(q["opciones"].values())]
            if preguntas_validas:
                guardar_preguntas(preguntas_validas)
                st.success("✅ Preguntas guardadas con éxito")
            else:
                st.error("⚠️ Debes completar todas las preguntas y opciones antes de guardar.")

def modo_quiz():
    st.header("🧠 Modo Repaso - Quiz")
    preguntas = cargar_preguntas()
    
    if not preguntas:
        st.warning("⚠️ No hay preguntas guardadas aún.")
        return
    
    if "indice" not in st.session_state:
        st.session_state.indice = 0
        st.session_state.puntaje = 0
        st.session_state.resultados = []
        random.shuffle(preguntas)
        st.session_state.preguntas = preguntas
        st.session_state.start_time = time.time()

    idx = st.session_state.indice
    if idx >= len(st.session_state.preguntas):
        st.header("📊 Resultados finales")
        st.subheader(f"Puntaje: {st.session_state.puntaje} / {len(st.session_state.preguntas)}")
        for r in st.session_state.resultados:
            correcto = r["usuario"] == r["correcta"]
            color = "✅" if correcto else "❌"
            st.markdown(f"""{color} **{r['pregunta']}**
• Tu respuesta: `{r['usuario']}`
• Correcta: `{r['correcta']}`""")
        return
    
    p = st.session_state.preguntas[idx]

    usar_tiempo = st.radio("¿Quieres activar tiempo por pregunta?", ["No", "Sí"])
    tiempo_limite = 0
    if usar_tiempo == "Sí":
        tiempo_limite = st.slider("Tiempo por pregunta (segundos)", 5, 60, 15)

    st.subheader(f"Pregunta {idx+1} de {len(st.session_state.preguntas)}")
    st.write(p["texto"])

    opciones = p["opciones"]
    opcion_mostrar = [f"{key}: {valor}" for key, valor in opciones.items()]
    respuesta = st.radio("Opciones:", opcion_mostrar, key="respuesta_actual")

    respuesta_letra = respuesta.split(":")[0]

    tiempo_pasado = time.time() - st.session_state.start_time

    if usar_tiempo == "Sí":
        st.write(f"Tiempo: {int(tiempo_pasado)}s / {tiempo_limite}s")
        if tiempo_pasado > tiempo_limite:
            st.warning("⏰ Tiempo agotado para esta pregunta.")
            st.session_state.resultados.append({
                "pregunta": p["texto"],
                "correcta": p["respuesta_correcta"],
                "usuario": "Sin respuesta (tiempo agotado)"
            })
            st.session_state.indice += 1
            st.session_state.start_time = time.time()
            return

    if st.button("Responder"):
        if usar_tiempo == "Sí" and tiempo_pasado > tiempo_limite:
            st.error("⏰ Tiempo agotado, respuesta no válida.")
        else:
            correcto = respuesta_letra == p["respuesta_correcta"]
            if correcto:
                st.session_state.puntaje += 1
                st.success("✅ ¡Correcto!")
            else:
                st.error(f"❌ Incorrecto. La respuesta correcta era: {p['respuesta_correcta']}")

            st.session_state.resultados.append({
                "pregunta": p["texto"],
                "correcta": p["respuesta_correcta"],
                "usuario": respuesta_letra
            })

            st.session_state.indice += 1
            st.session_state.start_time = time.time()

st.title("📝 Quiz Estudio Rápido")
opcion = st.selectbox("Selecciona modo", ["Elegir...", "Ingresar preguntas", "Hacer el quiz"])

if opcion == "Ingresar preguntas":
    modo_estudio()
elif opcion == "Hacer el quiz":
    modo_quiz()
