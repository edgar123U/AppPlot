import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type, team1_name, team2_name):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', goal_type="box", corner_arcs=True)
    
    # Configurar a figura com espaço para a legenda
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    # Dicionários de cores
    assist_colors = {'cruzamento': 'orange', 'passe atrasado': 'blue'}
    shot_colors = {'golo': 'red', 'defesa': 'blue', 'para fora': 'green', 'bloqueado': 'brown'}
    duel_colors = {'ganho': 'green', 'perdido': 'red'}

    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                color = 'blue' if event.get('team') == team1_name else 'cyan'
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'shot':
                color = shot_colors.get(event.get('outcome'), 'red') if event.get('team') == team1_name else 'cyan'
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'recovery':
                color = 'green' if event.get('team') == team1_name else 'orange'
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                color = assist_colors.get(event.get('assist_type'), 'orange') if event.get('team') == team1_name else 'cyan'
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'duel':
                color = duel_colors.get(event.get('outcome'), 'gray') if event.get('team') == team1_name else 'cyan'
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=150, marker='^')

    # Adicionar legendas fora do campo
    if event_type == 'assist':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=2, label=label) 
                           for label, color in assist_colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Assistências')
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
if 'team1_name' not in st.session_state:
    st.session_state.team1_name = "Team 1"
if 'team2_name' not in st.session_state:
    st.session_state.team2_name = "Team 2"

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
    page_icon="⚽️"
)

st.title("Anotar Eventos no Campo de Futebol")

# Seção para adicionar novos jogos
st.sidebar.header("Adicionar Novo Jogo")
game_name = st.text_input("Nome do Jogo")
team1_name = st.text_input("Nome da Equipe 1", value=st.session_state.team1_name)
team2_name = st.text_input("Nome da Equipe 2", value=st.session_state.team2_name)

if st.button("Adicionar Jogo"):
    if game_name:
        st.session_state.games.append(game_name)
        st.session_state.team1_name = team1_name
        st.session_state.team2_name = team2_name
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
        team = st.selectbox("Equipe", [team1_name, team2_name], key="pass_team")

        if st.button("Adicionar Passe"):
            if end_x is not None and end_y is not None and player_name:
                event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name, 'team': team}
                st.session_state.events['pass'].append(event)
                st.success("Passe adicionado com sucesso!")

        st.header("Remover Passe")
        if st.session_state.events['pass']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['pass']))]
            selected_option = st.selectbox("Selecione um evento para apagar", options)
            if selected_option:
                index = options.index(selected_option)
                st.session_state.selected_event['pass'] = index

            if st.button("Apagar Passe"):
                if st.session_state.selected_event['pass'] is not None:
                    st.session_state.events['pass'].pop(st.session_state.selected_event['pass'])
                    st.success("Passe apagado com sucesso!")

        if st.session_state.events['pass']:
            st.header("Visualização de Passes")
            fig = draw_pitch(st.session_state.events['pass'], 'pass', team1_name, team2_name)
            st.pyplot(fig)

    with tab2:
        st.header("Adicionar Remate")
        player_name = st.text_input("Nome do Jogador", key="shot_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="shot_minute")
        x = st.number_input("Coordenada X do Remate", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
        y = st.number_input("Coordenada Y do Remate", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
        outcome = st.selectbox("Resultado", ["golo", "defesa", "para fora", "bloqueado"], key="shot_outcome")
        team = st.selectbox("Equipe", [team1_name, team2_name], key="shot_team")

        if st.button("Adicionar Remate"):
            if player_name:
                event = {'type': 'shot', 'x': x, 'y': y, 'outcome': outcome, 'player': player_name, 'team': team}
                st.session_state.events['shot'].append(event)
                st.success("Remate adicionado com sucesso!")

        st.header("Remover Remate")
        if st.session_state.events['shot']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['shot']))]
            selected_option = st.selectbox("Selecione um evento para apagar", options)
            if selected_option:
                index = options.index(selected_option)
                st.session_state.selected_event['shot'] = index

            if st.button("Apagar Remate"):
                if st.session_state.selected_event['shot'] is not None:
                    st.session_state.events['shot'].pop(st.session_state.selected_event['shot'])
                    st.success("Remate apagado com sucesso!")

        if st.session_state.events['shot']:
            st.header("Visualização de Remates")
            fig = draw_pitch(st.session_state.events['shot'], 'shot', team1_name, team2_name)
            st.pyplot(fig)

    with tab3:
        st.header("Adicionar Recuperação de Bola")
        player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="recovery_minute")
        x = st.number_input("Coordenada X da Recuperação", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
        y = st.number_input("Coordenada Y da Recuperação", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
        team = st.selectbox("Equipe", [team1_name, team2_name], key="recovery_team")

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

            if st.button("Apagar Recuperação"):
                if st.session_state.selected_event['recovery'] is not None:
                    st.session_state.events['recovery'].pop(st.session_state.selected_event['recovery'])
                    st.success("Recuperação apagada com sucesso!")

        if st.session_state.events['recovery']:
            st.header("Visualização de Recuperações")
            fig = draw_pitch(st.session_state.events['recovery'], 'recovery', team1_name, team2_name)
            st.pyplot(fig)

    with tab4:
        st.header("Adicionar Assistência")
        player_name = st.text_input("Nome do Jogador", key="assist_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="assist_minute")
        x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="assist_x")
        y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="assist_y")
        end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="assist_end_x")
        end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="assist_end_y")
        assist_type = st.selectbox("Tipo de Assistência", ["cruzamento", "passe atrasado"], key="assist_type")
        team = st.selectbox("Equipe", [team1_name, team2_name], key="assist_team")

        if st.button("Adicionar Assistência"):
            if player_name and end_x is not None and end_y is not None:
                event = {'type': 'assist', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'assist_type': assist_type, 'player': player_name, 'team': team}
                st.session_state.events['assist'].append(event)
                st.success("Assistência adicionada com sucesso!")

        st.header("Remover Assistência")
        if st.session_state.events['assist']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['assist']))]
            selected_option = st.selectbox("Selecione um evento para apagar", options)
            if selected_option:
                index = options.index(selected_option)
                st.session_state.selected_event['assist'] = index

            if st.button("Apagar Assistência"):
                if st.session_state.selected_event['assist'] is not None:
                    st.session_state.events['assist'].pop(st.session_state.selected_event['assist'])
                    st.success("Assistência apagada com sucesso!")

        if st.session_state.events['assist']:
            st.header("Visualização de Assistências")
            fig = draw_pitch(st.session_state.events['assist'], 'assist', team1_name, team2_name)
            st.pyplot(fig)

    with tab5:
        st.header("Adicionar Duelo Aéreo")
        player_name = st.text_input("Nome do Jogador", key="duel_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="duel_minute")
        x = st.number_input("Coordenada X do Duelo", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
        y = st.number_input("Coordenada Y do Duelo", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
        outcome = st.selectbox("Resultado", ["ganho", "perdido"], key="duel_outcome")
        team = st.selectbox("Equipe", [team1_name, team2_name], key="duel_team")

        if st.button("Adicionar Duelo"):
            if player_name:
                event = {'type': 'duel', 'x': x, 'y': y, 'outcome': outcome, 'player': player_name, 'team': team}
                st.session_state.events['duel'].append(event)
                st.success("Duelo adicionado com sucesso!")

        st.header("Remover Duelo")
        if st.session_state.events['duel']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['duel']))]
            selected_option = st.selectbox("Selecione um evento para apagar", options)
            if selected_option:
                index = options.index(selected_option)
                st.session_state.selected_event['duel'] = index

            if st.button("Apagar Duelo"):
                if st.session_state.selected_event['duel'] is not None:
                    st.session_state.events['duel'].pop(st.session_state.selected_event['duel'])
                    st.success("Duelo apagado com sucesso!")

        if st.session_state.events['duel']:
            st.header("Visualização de Duelos Aéreos")
            fig = draw_pitch(st.session_state.events['duel'], 'duel', team1_name, team2_name)
            st.pyplot(fig)

# Exportar dados para Excel
if st.button("Exportar Eventos para Excel"):
    if selected_game:
        df = export_to_excel(st.session_state.events)
        filename = f"eventos_partida_{selected_game}.xlsx"
        df.to_excel(filename, index=False)
        with open(filename, "rb") as file:
            st.download_button("Baixar Excel", data=file, file_name=filename)
