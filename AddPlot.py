import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type, team_colors):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', goal_type="box", corner_arcs=True)
    
    # Configurar a figura com espaço para a legenda
    fig, ax = plt.subplots(figsize=(12, 7))
    pitch.draw(ax=ax)

    # Dicionários de cores para eventos e equipes
    pass_colors = {'quebra linhas': 'purple', 'variação do flanco de jogo': 'orange'}
    shot_colors = {'golo': 'red', 'defesa': 'blue', 'para fora': 'green', 'bloqueado': 'brown'}
    duel_colors = {'ganho': 'green', 'perdido': 'red'}

    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            color = team_colors.get(event.get('team'), 'gray')
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                pass_type_color = pass_colors.get(event.get('pass_type'), 'blue')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=pass_type_color, width=2)
            elif event_type == 'shot':
                shot_color = shot_colors.get(event.get('outcome'), 'red')
                pitch.scatter(event['x'], event['y'], ax=ax, color=shot_color, s=100)
            elif event_type == 'recovery':
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                assist_color = pass_colors.get(event.get('assist_type'), 'orange')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=assist_color, width=2)
            elif event_type == 'duel':
                duel_color = duel_colors.get(event.get('outcome'), 'gray')
                pitch.scatter(event['x'], event['y'], ax=ax, color=duel_color, s=150, marker='^')

    # Adicionar legendas fora do campo
    if event_type == 'pass':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=2, label=label) 
                           for label, color in pass_colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Passes')
    elif event_type == 'shot':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='o', lw=0, label=label) 
                           for label, color in shot_colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Remates')
    elif event_type == 'duel':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='^', lw=0, label=label) 
                           for label, color in duel_colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Duelos Aéreos')

    return fig

# Inicializar o estado da sessão
if 'games' not in st.session_state:
    st.session_state.games = []
if 'events' not in st.session_state:
    st.session_state.events = {'pass': [], 'shot': [], 'recovery': [], 'assist': [], 'duel': []}
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = {'pass': None, 'shot': None, 'recovery': None, 'assist': None, 'duel': None}
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None

# Função para exportar eventos para Excel
def export_to_excel(events, game_name):
    df_list = []
    for event_type, events_list in events.items():
        df = pd.DataFrame(events_list)
        df['type'] = event_type
        df['game'] = game_name
        df_list.append(df)
    
    all_events_df = pd.concat(df_list, ignore_index=True)
    return all_events_df

# Função para remover um jogo
def remove_game(game_name):
    if game_name in st.session_state.games:
        st.session_state.games.remove(game_name)
        if st.session_state.selected_game == game_name:
            st.session_state.selected_game = None
        st.session_state.events = {'pass': [], 'shot': [], 'recovery': [], 'assist': [], 'duel': []}
        st.success(f"Jogo '{game_name}' removido com sucesso!")
    else:
        st.error("Jogo não encontrado.")

# Configurar a página com um ícone de bola de futebol
st.set_page_config(
    page_title="Anotar Eventos no Campo de Futebol",
    page_icon="icons8-soccer-ball-50.png"
)

st.title("Anotar Eventos no Campo de Futebol")

# Seção para adicionar novos jogos
st.sidebar.header("Adicionar Novo Jogo")
game_name = st.text_input("Nome do Jogo")
if st.button("Adicionar Jogo"):
    if game_name:
        st.session_state.games.append(game_name)
        st.success(f"Jogo '{game_name}' adicionado com sucesso!")

# Seção para remover jogos
st.sidebar.header("Remover Jogo")
if st.session_state.games:
    game_to_remove = st.selectbox("Escolha um jogo para remover", st.session_state.games)
    if st.button("Remover Jogo"):
        if game_to_remove:
            remove_game(game_to_remove)
else:
    st.write("Nenhum jogo disponível para remover.")

# Selecionar o jogo para exibir eventos
st.sidebar.header("Selecionar Jogo")
selected_game = st.selectbox("Escolha um jogo", st.session_state.games)
st.session_state.selected_game = selected_game

if selected_game:
    st.title(f"Eventos para o jogo: {selected_game}")

    # Definir as cores das equipes
    team_colors = {
        'home': 'blue',
        'away': 'red'
    }

    # Separar os inputs e gráficos para cada tipo de evento
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Passes", "Remates", "Recuperações", "Assistências", "Duelos Aéreos"])

    with tab1:
        st.header("Adicionar Passe")
        player_name = st.text_input("Nome do Jogador", key="pass_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="pass_minute")
        x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="pass_x")
        y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="pass_y")
        end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="pass_end_x")
        end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="pass_end_y")
        pass_type = st.selectbox("Categoria do Passe", ["quebra linhas", "variação do flanco de jogo"], key="pass_type")
        team = st.selectbox("Equipe", ["home", "away"], key="pass_team")

        if st.button("Adicionar Passe"):
            if end_x is not None and end_y is not None and player_name:
                event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name, 'pass_type': pass_type, 'team': team}
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

    with tab2:
        st.header("Adicionar Remate")
        player_name = st.text_input("Nome do Jogador", key="shot_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="shot_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
        outcome = st.selectbox("Resultado do Remate", ["golo", "defesa", "para fora", "bloqueado"], key="shot_outcome")
        team = st.selectbox("Equipe", ["home", "away"], key="shot_team")

        if st.button("Adicionar Remate"):
            if player_name:
                event = {'type': 'shot', 'x': x, 'y': y, 'player': player_name, 'outcome': outcome, 'team': team}
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

    with tab3:
        st.header("Adicionar Recuperação")
        player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="recovery_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
        team = st.selectbox("Equipe", ["home", "away"], key="recovery_team")

        if st.button("Adicionar Recuperação"):
            if player_name:
                event = {'type': 'recovery', 'x': x, 'y': y, 'player': player_name, 'team': team}
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

    with tab4:
        st.header("Adicionar Assistência")
        player_name = st.text_input("Nome do Jogador", key="assist_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="assist_minute")
        x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="assist_x")
        y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="assist_y")
        end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="assist_end_x")
        end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="assist_end_y")
        assist_type = st.selectbox("Categoria da Assistência", ["quebra linhas", "variação do flanco de jogo"], key="assist_type")
        team = st.selectbox("Equipe", ["home", "away"], key="assist_team")

        if st.button("Adicionar Assistência"):
            if end_x is not None and end_y is not None and player_name:
                event = {'type': 'assist', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name, 'assist_type': assist_type, 'team': team}
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

    with tab5:
        st.header("Adicionar Duelo Aéreo")
        player_name = st.text_input("Nome do Jogador", key="duel_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="duel_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
        outcome = st.selectbox("Resultado do Duelo", ["ganho", "perdido"], key="duel_outcome")
        team = st.selectbox("Equipe", ["home", "away"], key="duel_team")

        if st.button("Adicionar Duelo Aéreo"):
            if player_name:
                event = {'type': 'duel', 'x': x, 'y': y, 'player': player_name, 'outcome': outcome, 'team': team}
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

    # Exibir o campo com eventos
    if selected_game:
        for event_type, events_list in st.session_state.events.items():
            fig = draw_pitch(events_list, event_type, team_colors)
            st.pyplot(fig)
            
    # Exportar para Excel
    if st.button("Exportar Eventos para Excel"):
        excel_data = export_to_excel(st.session_state.events, selected_game)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            excel_data.to_excel(writer, index=False, sheet_name='Eventos')
        output.seek(0)
        st.download_button(label="Download Excel", data=output, file_name=f"eventos_{selected_game}.xlsx")
