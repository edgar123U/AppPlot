import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type, home_team, away_team):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black',goal_type="box",corner_arcs=True)
    
    # Configurar a figura com espaço para a legenda
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    # Dicionários de cores para os eventos
    assist_colors = {home_team: {'cruzamento': 'orange', 'passe atrasado': 'blue'},
                     away_team: {'cruzamento': 'cyan', 'passe atrasado': 'magenta'}}
    
    shot_colors = {home_team: {'golo': 'red', 'defesa': 'blue', 'para fora': 'green', "bloqueado": 'brown'},
                   away_team: {'golo': 'green', 'defesa': 'blue', 'para fora': 'black', "bloqueado": 'orange'}}
    
    duel_colors = {home_team: {'ganho': 'green', 'perdido': 'red'},
                   away_team: {'ganho': 'cyan', 'perdido': 'orange'}}

    # Adicionar eventos ao campo
    for event in events:
        team = event.get('team')
        if event['type'] == event_type:
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                color = 'blue' if team == home_team else 'cyan'
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'shot':
                color = shot_colors[team].get(event.get('outcome'), 'red')
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'recovery':
                color = 'green' if team == home_team else 'orange'
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                color = assist_colors[team].get(event.get('assist_type'), 'orange')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'duel':
                color = duel_colors[team].get(event.get('outcome'), 'gray')
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=150, marker='^')

    # Adicionar legendas fora do campo
    if event_type == 'assist':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=2, label=f"{label} ({team})") 
                           for team, colors in assist_colors.items() 
                           for label, color in colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Assistências')
    elif event_type == 'shot':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='o', lw=0, label=f"{label} ({team})") 
                           for team, colors in shot_colors.items() 
                           for label, color in colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Remates')
    elif event_type == 'duel':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, marker='^', lw=0, label=f"{label} ({team})") 
                           for team, colors in duel_colors.items() 
                           for label, color in colors.items()],
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
if 'home_team' not in st.session_state:
    st.session_state.home_team = None
if 'away_team' not in st.session_state:
    st.session_state.away_team = None

# Configurar a página com um ícone de bola de futebol
st.set_page_config(
    page_title="Anotar Eventos no Campo de Futebol",
    page_icon="⚽"
)

st.title("Anotar Eventos no Campo de Futebol")

# Seção para adicionar nomes das equipes
st.sidebar.header("Configuração de Equipes")
home_team = st.text_input("Nome da Equipe da Casa", key="home_team")
away_team = st.text_input("Nome da Equipe Visitante", key="away_team")

if st.button("Salvar Nomes das Equipes"):
    st.session_state.home_team = home_team
    st.session_state.away_team = away_team
    st.success("Nomes das equipes salvos com sucesso!")

home_team = st.session_state.home_team
away_team = st.session_state.away_team

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
            st.session_state.games.remove(game_to_remove)
            st.success(f"Jogo '{game_to_remove}' removido com sucesso!")
else:
    st.write("Nenhum jogo disponível para remover.")

# Selecionar o jogo para exibir eventos
st.sidebar.header("Selecionar Jogo")
selected_game = st.selectbox("Escolha um jogo", st.session_state.games)
st.session_state.selected_game = selected_game

if selected_game and home_team and away_team:
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
        team = st.selectbox("Equipe", [home_team, away_team], key="pass_team")

        if st.button("Adicionar Passe"):
            if end_x is not None and end_y is not None and player_name:
                event = {'type': 'pass', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'player': player_name, 'team': team}
                st.session_state.events['pass'].append(event)
                st.success("Passe adicionado com sucesso!")

        st.header("Remover Passe")
        if st.session_state.events['pass']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['pass']))]
            selected_option = st.selectbox("Escolha um passe para remover", options)
            if st.button("Remover Passe"):
                idx = options.index(selected_option)
                st.session_state.events['pass'].pop(idx)
                st.success("Passe removido com sucesso!")

        if st.session_state.events['pass']:
            fig = draw_pitch(st.session_state.events['pass'], 'pass', home_team, away_team)
            st.pyplot(fig)

    with tab2:
        st.header("Adicionar Remate")
        player_name = st.text_input("Nome do Jogador", key="shot_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="shot_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
        outcome = st.selectbox("Resultado do Remate", ["golo", "defesa", "para fora", "bloqueado"], key="shot_outcome")
        team = st.selectbox("Equipe", [home_team, away_team], key="shot_team")

        if st.button("Adicionar Remate"):
            if player_name:
                event = {'type': 'shot', 'x': x, 'y': y, 'outcome': outcome, 'player': player_name, 'team': team}
                st.session_state.events['shot'].append(event)
                st.success("Remate adicionado com sucesso!")

        st.header("Remover Remate")
        if st.session_state.events['shot']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['shot']))]
            selected_option = st.selectbox("Escolha um remate para remover", options)
            if st.button("Remover Remate"):
                idx = options.index(selected_option)
                st.session_state.events['shot'].pop(idx)
                st.success("Remate removido com sucesso!")

        if st.session_state.events['shot']:
            fig = draw_pitch(st.session_state.events['shot'], 'shot', home_team, away_team)
            st.pyplot(fig)

    with tab3:
        st.header("Adicionar Recuperação")
        player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="recovery_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
        team = st.selectbox("Equipe", [home_team, away_team], key="recovery_team")

        if st.button("Adicionar Recuperação"):
            if player_name:
                event = {'type': 'recovery', 'x': x, 'y': y, 'player': player_name, 'team': team}
                st.session_state.events['recovery'].append(event)
                st.success("Recuperação adicionada com sucesso!")

        st.header("Remover Recuperação")
        if st.session_state.events['recovery']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['recovery']))]
            selected_option = st.selectbox("Escolha uma recuperação para remover", options)
            if st.button("Remover Recuperação"):
                idx = options.index(selected_option)
                st.session_state.events['recovery'].pop(idx)
                st.success("Recuperação removida com sucesso!")

        if st.session_state.events['recovery']:
            fig = draw_pitch(st.session_state.events['recovery'], 'recovery', home_team, away_team)
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
        team = st.selectbox("Equipe", [home_team, away_team], key="assist_team")

        if st.button("Adicionar Assistência"):
            if player_name and end_x is not None and end_y is not None:
                event = {'type': 'assist', 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'assist_type': assist_type, 'player': player_name, 'team': team}
                st.session_state.events['assist'].append(event)
                st.success("Assistência adicionada com sucesso!")

        st.header("Remover Assistência")
        if st.session_state.events['assist']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['assist']))]
            selected_option = st.selectbox("Escolha uma assistência para remover", options)
            if st.button("Remover Assistência"):
                idx = options.index(selected_option)
                st.session_state.events['assist'].pop(idx)
                st.success("Assistência removida com sucesso!")

        if st.session_state.events['assist']:
            fig = draw_pitch(st.session_state.events['assist'], 'assist', home_team, away_team)
            st.pyplot(fig)

    with tab5:
        st.header("Adicionar Duelo Aéreo")
        player_name = st.text_input("Nome do Jogador", key="duel_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="duel_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
        outcome = st.selectbox("Resultado do Duelo", ["ganho", "perdido"], key="duel_outcome")
        team = st.selectbox("Equipe", [home_team, away_team], key="duel_team")

        if st.button("Adicionar Duelo Aéreo"):
            if player_name:
                event = {'type': 'duel', 'x': x, 'y': y, 'outcome': outcome, 'player': player_name, 'team': team}
                st.session_state.events['duel'].append(event)
                st.success("Duelo Aéreo adicionado com sucesso!")

        st.header("Remover Duelo Aéreo")
        if st.session_state.events['duel']:
            options = [f"Evento {i + 1}" for i in range(len(st.session_state.events['duel']))]
            selected_option = st.selectbox("Escolha um duelo para remover", options)
            if st.button("Remover Duelo Aéreo"):
                idx = options.index(selected_option)
                st.session_state.events['duel'].pop(idx)
                st.success("Duelo Aéreo removido com sucesso!")

        if st.session_state.events['duel']:
            fig = draw_pitch(st.session_state.events['duel'], 'duel', home_team, away_team)
            st.pyplot(fig)


    # Mostrar todos os eventos adicionados
    st.write("Todos os eventos adicionados:")
    st.write(st.session_state.events)

    # Exportar para Excel
    if st.button("Exportar para Excel"):
        all_events_df = export_to_excel(st.session_state.events, selected_game)
        # Salvar em um buffer para download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            all_events_df.to_excel(writer, index=False, sheet_name='Eventos')
        buffer.seek(0)
        
        st.download_button(
            label="Download Eventos em Excel",
            data=buffer,
            file_name=f'eventos_{selected_game}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.write("Por favor, selecione um jogo para exibir e adicionar eventos.")
