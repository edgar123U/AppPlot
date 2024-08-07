import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    fig, ax = pitch.draw()
    
    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color='blue', width=2)
            elif event_type == 'shot':
                pitch.scatter(event['x'], event['y'], ax=ax, color='red', s=100)
            elif event_type == 'recovery':
                pitch.scatter(event['x'], event['y'], ax=ax, color='green', s=100)

    return fig

# Inicializar o estado da sessão
if 'events' not in st.session_state:
    st.session_state.events = {'pass': [], 'shot': [], 'recovery': []}

# Configurar a página com um ícone de bola de futebol
st.set_page_config(
    page_title="Anotar Eventos no Campo de Futebol",
    page_icon="soccer_ball.png"  # Substitua pelo nome do arquivo do ícone que você baixou
)

st.title("Anotar Eventos no Campo de Futebol")

# Separar os inputs e gráficos para cada tipo de evento
tab1, tab2, tab3 = st.tabs(["Passes", "Remates", "Recuperações"])

with tab1:
    st.header("Adicionar Passe")
    x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="pass_x")
    y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="pass_y")
    end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="pass_end_x")
    end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="pass_end_y")

    if st.button("Adicionar Passe"):
        if end_x is not None and end_y is not None:
            event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y}
            st.session_state.events['pass'].append(event)
            st.success("Passe adicionado com sucesso!")

    # Desenhar o campo com eventos de passes
    fig = draw_pitch(st.session_state.events['pass'], 'pass')
    st.pyplot(fig)

with tab2:
    st.header("Adicionar Remate")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")

    if st.button("Adicionar Remate"):
        event = {'type': 'shot', 'x': x, 'y': y}
        st.session_state.events['shot'].append(event)
        st.success("Remate adicionado com sucesso!")

    # Desenhar o campo com eventos de remates
    fig = draw_pitch(st.session_state.events['shot'], 'shot')
    st.pyplot(fig)

with tab3:
    st.header("Adicionar Recuperação")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")

    if st.button("Adicionar Recuperação"):
        event = {'type': 'recovery', 'x': x, 'y': y}
        st.session_state.events['recovery'].append(event)
        st.success("Recuperação adicionada com sucesso!")

    # Desenhar o campo com eventos de recuperações
    fig = draw_pitch(st.session_state.events['recovery'], 'recovery')
    st.pyplot(fig)

# Mostrar todos os eventos adicionados
st.write("Todos os eventos adicionados:")
st.write(st.session_state.events)
