import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

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

# Função para capturar cliques no gráfico
def onclick(event, event_type):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        if event_type == 'pass':
            if 'start' not in st.session_state:
                st.session_state.start = (x, y)
                st.session_state.pass_start = (x, y)
                st.session_state.event_type = 'pass'
                st.write("Clique no ponto final do passe.")
            else:
                end_x, end_y = x, y
                st.session_state.events['pass'].append({'type': 'pass', 'x': st.session_state.start[0], 'y': st.session_state.start[1], 'end_x': end_x, 'end_y': end_y})
                del st.session_state.start
                st.success("Passe adicionado com sucesso!")
                st.session_state.event_type = None
                st.experimental_rerun()
        elif event_type == 'shot':
            st.session_state.events['shot'].append({'type': 'shot', 'x': x, 'y': y})
            st.success("Remate adicionado com sucesso!")
            st.session_state.event_type = None
            st.experimental_rerun()
        elif event_type == 'recovery':
            st.session_state.events['recovery'].append({'type': 'recovery', 'x': x, 'y': y})
            st.success("Recuperação adicionada com sucesso!")
            st.session_state.event_type = None
            st.experimental_rerun()

# Inicializar o estado da sessão
if 'events' not in st.session_state:
    st.session_state.events = {'pass': [], 'shot': [], 'recovery': []}
if 'event_type' not in st.session_state:
    st.session_state.event_type = None
if 'start' not in st.session_state:
    st.session_state.start = None

# Função para exportar eventos para Excel
def export_to_excel(events):
    df_list = []
    for event_type, events_list in events.items():
        df = pd.DataFrame(events_list)
        df['type'] = event_type
        df_list.append(df)
    
    all_events_df = pd.concat(df_list, ignore_index=True)
    return all_events_df

# Configurar a página com um ícone de bola de futebol
st.set_page_config(
    page_title="Anotar Eventos no Campo de Futebol",
    page_icon="soccer_ball.png"  # Substitua pelo nome do arquivo do ícone que você baixou
)

st.title("Anotar Eventos no Campo de Futebol")

# Seleção do tipo de evento
event_type = st.selectbox("Tipo de Evento", ["Selecione", "pass", "shot", "recovery"])

# Adicionar instruções dependendo do tipo de evento selecionado
if event_type != "Selecione":
    st.write(f"Você selecionou {event_type}. Clique no campo para adicionar o evento.")

# Mostrar o campo e capturar cliques
fig = draw_pitch(st.session_state.events, 'pass')  # Inicialmente desenha todos os eventos
if event_type == "pass":
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, 'pass'))
elif event_type == "shot":
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, 'shot'))
elif event_type == "recovery":
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, 'recovery'))

st.pyplot(fig)

# Mostrar todos os eventos adicionados
st.write("Todos os eventos adicionados:")
st.write(st.session_state.events)

# Exportar para Excel
if st.button("Exportar para Excel"):
    all_events_df = export_to_excel(st.session_state.events)
    # Salvar em um buffer para download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        all_events_df.to_excel(writer, index=False, sheet_name='Eventos')
    buffer.seek(0)
    
    st.download_button(
        label="Download Eventos em Excel",
        data=buffer,
        file_name='eventos_futebol.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
