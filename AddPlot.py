import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt

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

    return fig

# Inicializar o estado da sessão
if 'events' not in st.session_state:
    st.session_state.events = []

st.title("Anotar Eventos no Campo de Futebol")

tab1, tab2, tab3 = st.tabs(["Passes", "Remates", "Recuperações"])

with tab1:
    st.header("Adicionar Passe")
    x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="pass_x")
    y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="pass_y")
    end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="pass_end_x")
    end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="pass_end_y")

    if st.button("Adicionar Passe"):
        event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y}
        st.session_state.events.append(event)
        st.success("Passe adicionado com sucesso!")

with tab2:
    st.header("Adicionar Remate")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")

    if st.button("Adicionar Remate"):
        event = {'type': 'shot', 'x': x, 'y': y}
        st.session_state.events.append(event)
        st.success("Remate adicionado com sucesso!")

with tab3:
    st.header("Adicionar Recuperação")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")

    if st.button("Adicionar Recuperação"):
        event = {'type': 'recovery', 'x': x, 'y': y}
        st.session_state.events.append(event)
        st.success("Recuperação adicionada com sucesso!")

# Desenhar o campo com eventos
fig = draw_pitch(st.session_state.events)
st.pyplot(fig)

# Mostrar os eventos adicionados
st.write("Eventos adicionados:")
st.write(st.session_state.events)
