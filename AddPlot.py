import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    fig, ax = pitch.draw()
    
    # Dicionários de cores
    assist_colors = {'cruzamento': 'orange', 'passe atrasado': 'purple'}
    shot_colors = {'goal': 'darkred', 'save': 'blue', 'miss': 'gray'}
    duel_colors = {'ganho': 'green', 'perdido': 'red'}
    
    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color='blue', width=2)
            elif event_type == 'shot':
                color = shot_colors.get(event.get('outcome'), 'red')  # Redefine a cor com base no resultado
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'recovery':
                pitch.scatter(event['x'], event['y'], ax=ax, color='green', s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                color = assist_colors.get(event.get('assist_type'), 'orange')  # Redefine a cor com base no tipo de assistência
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'duel':
                color = duel_colors.get(event.get('outcome'), 'gray')  # Redefine a cor com base no resultado do duelo
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=150, marker='^')

    # Adicionar legendas
    if event_type == 'pass':
        ax.legend(handles=[plt.Line2D([0], [0], color='blue', lw=2, label='Passes')],
                  loc='upper right', title='Legendas')
    elif event_type == 'assist':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=2, label=label) 
                           for label, color in assist_colors.items()],
                  loc='upper right', title='Assistências')
    elif event_type == 'shot':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='o', lw=0, label=label) 
                           for label, color in shot_colors.items()],
                  loc='upper right', title='Remates')
    elif event_type == 'duel':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='^', lw=0, label=label) 
                           for label, color in duel_colors.items()],
                  loc='upper right', title='Duelos Aéreos')

    return fig

# Inicializar o estado da sessão
if 'events' not in st.session_state:
    st.session_state.events = {'pass': [], 'shot': [], 'recovery': [], 'assist': [], 'duel': []}

if 'selected_event' not in st.session_state:
    st.session_state.selected_event = {'pass': None, 'shot': None, 'recovery': None, 'assist': None, 'duel': None}

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
    page_icon="icons8-soccer-ball-50.png"
)

st.title("Anotar Eventos no Campo de Futebol")

# Separar os inputs e gráficos para cada tipo de evento
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Passes", "Remates", "Recuperações", "Assistências", "Duelos Aéreos"])

with tab1:
    st.header("Adicionar Passe")
    player_name = st.text_input("Nome do Jogador", key="pass_player_name")
    x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="pass_x")
    y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="pass_y")
    end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="pass_end_x")
    end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="pass_end_y")

    if st.button("Adicionar Passe"):
        if end_x is not None and end_y is not None and player_name:
            event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name}
            st.session_state.events['pass'].append(event)
            st.success("Passe adicionado com sucesso!")

    st.header("Remover Passe")
    if st.session_state.events['pass']:
        options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['pass']))]
        selected_option = st.selectbox("Selecione um evento para apagar", options)
        if selected_option:
            index = options.index(selected_option)
            st.session_state.selected_event['pass'] = index
    if st.button("Remover Passe"):
        index = st.session_state.selected_event['pass']
        if index is not None:
            st.session_state.events['pass'].pop(index)
            st.success("Passe removido com sucesso!")

    # Desenhar o campo com eventos de passes
    fig = draw_pitch(st.session_state.events['pass'], 'pass')
    st.pyplot(fig)

with tab2:
    st.header("Adicionar Remate")
    player_name = st.text_input("Nome do Jogador", key="shot_player_name")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
    xg = st.number_input("xG (Expected Goals)", min_value=0.0, max_value=10.0, step=0.01, key="shot_xg")
    outcome = st.selectbox("Resultado", ["goal", "save", "miss"], key="shot_outcome")

    if st.button("Adicionar Remate"):
        if player_name:
            event = {'type': 'shot', 'x': x, 'y': y, 'player': player_name, 'xg': xg, 'outcome': outcome}
            st.session_state.events['shot'].append(event)
            st.success("Remate adicionado com sucesso!")

    st.header("Remover Remate")
    if st.session_state.events['shot']:
        options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['shot']))]
        selected_option = st.selectbox("Selecione um evento para apagar", options)
        if selected_option:
            index = options.index(selected_option)
            st.session_state.selected_event['shot'] = index
    if st.button("Remover Remate"):
        index = st.session_state.selected_event['shot']
        if index is not None:
            st.session_state.events['shot'].pop(index)
            st.success("Remate removido com sucesso!")

    # Desenhar o campo com eventos de remates
    fig = draw_pitch(st.session_state.events['shot'], 'shot')
    st.pyplot(fig)

with tab3:
    st.header("Adicionar Recuperação")
    player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")

    if st.button("Adicionar Recuperação"):
        if player_name:
            event = {'type': 'recovery', 'x': x, 'y': y, 'player': player_name}
            st.session_state.events['recovery'].append(event)
            st.success("Recuperação adicionada com sucesso!")

    st.header("Remover Recuperação")
    if st.session_state.events['recovery']:
        options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['recovery']))]
        selected_option = st.selectbox("Selecione um evento para apagar", options)
        if selected_option:
            index = options.index(selected_option)
            st.session_state.selected_event['recovery'] = index
    if st.button("Remover Recuperação"):
        index = st.session_state.selected_event['recovery']
        if index is not None:
            st.session_state.events['recovery'].pop(index)
            st.success("Recuperação removida com sucesso!")

    # Desenhar o campo com eventos de recuperações
    fig = draw_pitch(st.session_state.events['recovery'], 'recovery')
    st.pyplot(fig)

with tab4:
    st.header("Adicionar Assistência")
    player_name = st.text_input("Nome do Jogador", key="assist_player_name")
    x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="assist_x")
    y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="assist_y")
    end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="assist_end_x")
    end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="assist_end_y")
    assist_type = st.selectbox("Tipo de Assistência", ["cruzamento", "passe atrasado"], key="assist_type")

    if st.button("Adicionar Assistência"):
        if end_x is not None and end_y is not None and player_name:
            event = {'type': 'assist', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name, 'assist_type': assist_type}
            st.session_state.events['assist'].append(event)
            st.success("Assistência adicionada com sucesso!")

    st.header("Remover Assistência")
    if st.session_state.events['assist']:
        options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['assist']))]
        selected_option = st.selectbox("Selecione um evento para apagar", options)
        if selected_option:
            index = options.index(selected_option)
            st.session_state.selected_event['assist'] = index
    if st.button("Remover Assistência"):
        index = st.session_state.selected_event['assist']
        if index is not None:
            st.session_state.events['assist'].pop(index)
            st.success("Assistência removida com sucesso!")

    # Desenhar o campo com eventos de assistências
    fig = draw_pitch(st.session_state.events['assist'], 'assist')
    st.pyplot(fig)

with tab5:
    st.header("Adicionar Duelo Aéreo")
    player_name = st.text_input("Nome do Jogador", key="duel_player_name")
    x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
    y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
    outcome = st.selectbox("Resultado", ["ganho", "perdido"], key="duel_outcome")

    if st.button("Adicionar Duelo Aéreo"):
        if player_name:
            event = {'type': 'duel', 'x': x, 'y': y, 'player': player_name, 'outcome': outcome}
            st.session_state.events['duel'].append(event)
            st.success("Duelo Aéreo adicionado com sucesso!")

    st.header("Remover Duelo Aéreo")
    if st.session_state.events['duel']:
        options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['duel']))]
        selected_option = st.selectbox("Selecione um evento para apagar", options)
        if selected_option:
            index = options.index(selected_option)
            st.session_state.selected_event['duel'] = index
    if st.button("Remover Duelo Aéreo"):
        index = st.session_state.selected_event['duel']
        if index is not None:
            st.session_state.events['duel'].pop(index)
            st.success("Duelo Aéreo removido com sucesso!")

    # Desenhar o campo com eventos de duelos aéreos
    fig = draw_pitch(st.session_state.events['duel'], 'duel')
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
