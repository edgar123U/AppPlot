import streamlit as st
from mplsoccer import Pitch, VerticalPitch
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

# Lista de eventos
events = []

st.title("Anotar Eventos no Campo de Futebol")

event_type = st.selectbox("Tipo de Evento", ["pass", "shot", "recovery"])
x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1)
y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1)
end_x = None
end_y = None

if event_type == "pass":
    end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1)
    end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1)

if st.button("Adicionar Evento"):
    event = {'type': event_type, 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y}
    events.append(event)
    st.success("Evento adicionado com sucesso!")

# Desenhar o campo com eventos
fig = draw_pitch(events)
st.pyplot(fig)
