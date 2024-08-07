import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# Função para desenhar o campo e eventos
def draw_pitch(events):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    fig, ax = pitch.draw()
    
    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == 'pass':
            pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color='blue', width=2)
        elif event['type'] == 'shot':
            pitch.scatter(event['x'], event['y'], ax=ax, color='red', s=100)
        elif event['type'] == 'recovery':
            pitch.scatter(event['x'], event['y'], ax=ax, color='green', s=100)

    return fig, ax

# Inicializar o estado da sessão
if 'events' not in st.session_state:
    st.session_state.events = []
if 'current_event' not in st.session_state:
    st.session_state.current_event = {}

st.title("Anotar Eventos no Campo de Futebol")

event_type = st.selectbox("Tipo de Evento", ["pass", "shot", "recovery"])

# Configurar a tela desenhável
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",  # Transparente
    stroke_width=2,
    background_color="#aabb97",
    height=500,
    width=700,
    drawing_mode="line" if event_type == "pass" else "point",
    key="canvas"
)

# Capturar eventos do canvas
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data["objects"]:
        if event_type == "pass":
            if 'start' not in st.session_state.current_event:
                st.session_state.current_event['start'] = (obj['left'], obj['top'])
            else:
                st.session_state.current_event['end'] = (obj['left'], obj['top'])
                st.session_state.events.append({
                    'type': 'pass',
                    'x': st.session_state.current_event['start'][0],
                    'y': st.session_state.current_event['start'][1],
                    'end_x': st.session_state.current_event['end'][0],
                    'end_y': st.session_state.current_event['end'][1]
                })
                st.session_state.current_event = {}
                st.experimental_rerun()
        else:
            st.session_state.events.append({
                'type': event_type,
                'x': obj['left'],
                'y': obj['top']
            })
            st.experimental_rerun()

# Desenhar o campo com eventos
fig, ax = draw_pitch(st.session_state.events)
st.pyplot(fig)

st.write(st.session_state.events)

