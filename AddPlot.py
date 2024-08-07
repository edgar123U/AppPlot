import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

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

# Função de callback para cliques
def onclick(event, event_type):
    if event.xdata is not None and event.ydata is not None:
        if event_type == "pass":
            if 'start' not in st.session_state.current_event:
                st.session_state.current_event['start'] = (event.xdata, event.ydata)
            else:
                st.session_state.current_event['end'] = (event.xdata, event.ydata)
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
                'x': event.xdata,
                'y': event.ydata
            })
            st.experimental_rerun()

st.title("Anotar Eventos no Campo de Futebol")

event_type = st.selectbox("Tipo de Evento", ["pass", "shot", "recovery"])

# Desenhar o campo com eventos
fig, ax = draw_pitch(st.session_state.events)
cid = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, event_type))
st.pyplot(fig)

st.write(st.session_state.events)
