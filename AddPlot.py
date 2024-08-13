import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type, team_colors, team1_name, team2_name):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', goal_type="box", corner_arcs=True)
    
    # Configurar a figura com espaço para a legenda
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    # Dicionários de cores
    assist_colors = {'cruzamento': 'orange', 'passe atrasado': 'blue'}
    shot_colors = {'golo': 'red', 'defesa': 'blue', 'para fora': 'green', 'bloqueado': 'brown'}
    duel_colors = {'ganho': 'green', 'perdido': 'red'}
    pass_colors = {'passe': 'blue', 'passe quebra linhas': 'purple', 'variação de CJ': 'brown'}

    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                color = pass_colors.get(event.get('pass_type'), 'blue') if event.get('team') == team1_name else team_colors[team2_name]
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'shot':
                color = shot_colors.get(event.get('outcome'), 'red') if event.get('team') == team1_name else team_colors[team2_name]
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
                # Adicionar valor de xG ao lado do remate
                ax.text(event['x']+1, event['y']+1, f"xG: {event['xG']:.2f}", fontsize=10, color=color)
            elif event_type == 'recovery':
                color = 'green' if event.get('team') == team1_name else 'orange'
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                color = assist_colors.get(event.get('assist_type'), 'orange') if event.get('team') == team1_name else team_colors[team2_name]
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'duel':
                color = duel_colors.get(event.get('outcome'), 'gray') if event.get('team') == team1_name else team_colors[team2_name]
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
    elif event_type == 'pass':
        ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=2, label=label) 
                           for label, color in pass_colors.items()],
                  loc='center left', bbox_to_anchor=(1, 0.5), title='Passes')

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
if 'team_colors' not in st.session_state:
    st.session_state.team_colors = {}

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
team1_name = st.text_input("Nome da Equipe 1")
team2_name = st.text_input("Nome da Equipe 2")
team1_color = st.color_picker("Cor da Equipe 1", "#0000FF")
team2_color = st.color_picker("Cor da Equipe 2", "#FF0000")

if st.button("Adicionar Jogo"):
    if game_name and team1_name and team2_name:
        st.session_state.games.append(game_name)
        st.session_state.team_colors[team1_name] = team1_color
        st.session_state.team_colors[team2_name] = team2_color
        st.success(f"Jogo '{game_name}' com as equipes '{team1_name}' e '{team2_name}' adicionado com sucesso!")

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
    
    # Verificar se as equipes foram definidas corretamente
    if len(st.session_state.team_colors) < 2:
        st.error("As equipes ainda não foram definidas. Adicione um jogo com as equipes primeiro.")
    else:
        # Obter nomes e cores das equipes
        team1_name, team2_name = list(st.session_state.team_colors.keys())[:2]
        team_colors = st.session_state.team_colors

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
            pass_type = st.selectbox("Tipo de Passe", ["passe", "passe quebra linhas", "variação de CJ"], key="pass_type")
            team = st.selectbox("Equipe", [team1_name, team2_name], key="pass_team")

            if st.button("Adicionar Passe"):
                st.session_state.events['pass'].append({
                    'player_name': player_name,
                    'minute': minute,
                    'x': x,
                    'y': y,
                    'end_x': end_x,
                    'end_y': end_y,
                    'pass_type': pass_type,
                    'team': team,
                    'type': 'pass'
                })
                st.success("Passe adicionado com sucesso!")

            # Mostrar os passes no campo
            st.subheader("Visualizar Passes")
            fig = draw_pitch(st.session_state.events['pass'], 'pass', team_colors, team1_name, team2_name)
            st.pyplot(fig)

        with tab2:
            st.header("Adicionar Remate")
            player_name = st.text_input("Nome do Jogador", key="shot_player_name")
            minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="shot_minute")
            x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
            y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
            outcome = st.selectbox("Resultado", ["golo", "defesa", "para fora", "bloqueado"], key="shot_outcome")
            xG = st.number_input("xG (expected goals)", min_value=0.0, max_value=1.0, step=0.01, key="shot_xG")
            team = st.selectbox("Equipe", [team1_name, team2_name], key="shot_team")

            if st.button("Adicionar Remate"):
                st.session_state.events['shot'].append({
                    'player_name': player_name,
                    'minute': minute,
                    'x': x,
                    'y': y,
                    'outcome': outcome,
                    'xG': xG,
                    'team': team,
                    'type': 'shot'
                })
                st.success("Remate adicionado com sucesso!")

            # Mostrar os remates no campo
            st.subheader("Visualizar Remates")
            fig = draw_pitch(st.session_state.events['shot'], 'shot', team_colors, team1_name, team2_name)
            st.pyplot(fig)

        with tab3:
            st.header("Adicionar Recuperação")
            player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
            minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="recovery_minute")
            x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
            y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
            team = st.selectbox("Equipe", [team1_name, team2_name], key="recovery_team")

            if st.button("Adicionar Recuperação"):
                st.session_state.events['recovery'].append({
                    'player_name': player_name,
                    'minute': minute,
                    'x': x,
                    'y': y,
                    'team': team,
                    'type': 'recovery'
                })
                st.success("Recuperação adicionada com sucesso!")

            # Mostrar as recuperações no campo
            st.subheader("Visualizar Recuperações")
            fig = draw_pitch(st.session_state.events['recovery'], 'recovery', team_colors, team1_name, team2_name)
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
                st.session_state.events['assist'].append({
                    'player_name': player_name,
                    'minute': minute,
                    'x': x,
                    'y': y,
                    'end_x': end_x,
                    'end_y': end_y,
                    'assist_type': assist_type,
                    'team': team,
                    'type': 'assist'
                })
                st.success("Assistência adicionada com sucesso!")

            # Mostrar as assistências no campo
            st.subheader("Visualizar Assistências")
            fig = draw_pitch(st.session_state.events['assist'], 'assist', team_colors, team1_name, team2_name)
            st.pyplot(fig)

        with tab5:
            st.header("Adicionar Duelo Aéreo")
            player_name = st.text_input("Nome do Jogador", key="duel_player_name")
            minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="duel_minute")
            x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
            y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
            outcome = st.selectbox("Resultado", ["ganho", "perdido"], key="duel_outcome")
            team = st.selectbox("Equipe", [team1_name, team2_name], key="duel_team")

            if st.button("Adicionar Duelo Aéreo"):
                st.session_state.events['duel'].append({
                    'player_name': player_name,
                    'minute': minute,
                    'x': x,
                    'y': y,
                    'outcome': outcome,
                    'team': team,
                    'type': 'duel'
                })
                st.success("Duelo Aéreo adicionado com sucesso!")

            # Mostrar os duelos aéreos no campo
            st.subheader("Visualizar Duelos Aéreos")
            fig = draw_pitch(st.session_state.events['duel'], 'duel', team_colors, team1_name, team2_name)
            st.pyplot(fig)

# Seção para exportar os eventos para Excel
if st.session_state.events:
    st.sidebar.header("Exportar Dados")
    if st.sidebar.button("Exportar para Excel"):
        all_events_df = export_to_excel(st.session_state.events, selected_game)
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            all_events_df.to_excel(writer, sheet_name='Sheet1', index=False)
        towrite.seek(0)
        st.sidebar.download_button(
            label="Download Excel",
            data=towrite,
            file_name=f'{selected_game}_events.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
