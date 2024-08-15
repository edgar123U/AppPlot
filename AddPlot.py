import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Função para desenhar o campo e eventos
def draw_pitch(events, event_type):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', goal_type="box", corner_arcs=True)
    
    # Configurar a figura com espaço para a legenda
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    # Dicionários de cores para passes, remates, recuperações, assistências e duelos
    assist_colors = {
        'casa': {'cruzamento': 'orange', 'passe atrasado': 'blue'},
        'fora': {'cruzamento': 'purple', 'passe atrasado': 'cyan'}
    }

    shot_colors = {
        'casa': {'golo': 'red', 'defesa': 'blue', 'para fora': 'green', 'bloqueado': 'brown'},
        'fora': {'golo': 'green', 'defesa': 'blue', 'para fora': 'black', 'bloqueado': 'orange'}
    }

    recovery_colors = {
        'casa': 'green',
        'fora': 'orange'
    }

    duel_colors = {
        'casa': {'ganho': 'green', 'perdido': 'red'},
        'fora': {'ganho': 'blue', 'perdido': 'yellow'}
    }

    pass_colors = {
        'casa': {'passe quebra linhas': 'red', 'variação do CJ': 'blue', 'passe em profundidade': 'green', 'passe normal': 'black'},
        'fora': {'passe quebra linhas': 'orange', 'variação do CJ': 'cyan', 'passe em profundidade': 'purple', 'passe normal': 'gray'}
    }

    # Adicionar eventos ao campo
    for event in events:
        if event['type'] == event_type:
            team = event.get('team')
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                color = pass_colors[team].get(event.get('pass_type'), 'black')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'shot':
                color = shot_colors[team].get(event.get('outcome'), 'red')
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'recovery':
                color = recovery_colors[team]
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                color = assist_colors[team].get(event.get('assist_type'), 'orange')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=color, width=2)
            elif event_type == 'duel':
                color = duel_colors[team].get(event.get('outcome'), 'gray')
                pitch.scatter(event['x'], event['y'], ax=ax, color=color, s=150, marker='^')

    # Adicionar legendas fora do campo
    if event_type == 'assist':
        legend_handles = [plt.Line2D([0], [0], color=color, lw=2, label=f'{team} - {label}') 
                          for team, colors in assist_colors.items() for label, color in colors.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Assistências')
    elif event_type == 'shot':
        legend_handles = [plt.Line2D([0], [0], color=color, marker='o', lw=0, label=f'{team} - {label}') 
                          for team, colors in shot_colors.items() for label, color in colors.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Remates')
    elif event_type == 'duel':
        legend_handles = [plt.Line2D([0], [0], color=color, marker='^', lw=0, label=f'{team} - {label}') 
                          for team, colors in duel_colors.items() for label, color in colors.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Duelos Aéreos')
    elif event_type == 'pass':
        legend_handles = [plt.Line2D([0], [0], color=color, lw=2, label=f'{team} - {label}') 
                          for team, colors in pass_colors.items() for label, color in colors.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Passes')

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
        pass_type = st.selectbox("Tipo de Passe", ["passe normal", "passe quebra linhas", "variação do CJ", "passe em profundidade"])
        team = st.selectbox("Equipe", ["casa", "fora"], key="pass_team")

        if st.button("Adicionar Passe"):
            event = {'player': player_name, 'minute': minute, 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'pass_type': pass_type, 'team': team, 'type': 'pass'}
            st.session_state.events['pass'].append(event)
            st.success("Passe adicionado com sucesso!")

        st.subheader("Visualizar Passes")
        pass_fig = draw_pitch(st.session_state.events['pass'], 'pass')
        st.pyplot(pass_fig)

    with tab2:
        st.header("Adicionar Remate")
        player_name = st.text_input("Nome do Jogador", key="shot_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="shot_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
        outcome = st.selectbox("Resultado", ["golo", "defesa", "para fora", "bloqueado"])
        team = st.selectbox("Equipe", ["casa", "fora"], key="shot_team")

        if st.button("Adicionar Remate"):
            event = {'player': player_name, 'minute': minute, 'x': x, 'y': y, 'outcome': outcome, 'team': team, 'type': 'shot'}
            st.session_state.events['shot'].append(event)
            st.success("Remate adicionado com sucesso!")

        st.subheader("Visualizar Remates")
        shot_fig = draw_pitch(st.session_state.events['shot'], 'shot')
        st.pyplot(shot_fig)

    with tab3:
        st.header("Adicionar Recuperação")
        player_name = st.text_input("Nome do Jogador", key="recovery_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="recovery_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
        team = st.selectbox("Equipe", ["casa", "fora"], key="recovery_team")

        if st.button("Adicionar Recuperação"):
            event = {'player': player_name, 'minute': minute, 'x': x, 'y': y, 'team': team, 'type': 'recovery'}
            st.session_state.events['recovery'].append(event)
            st.success("Recuperação adicionada com sucesso!")

        st.subheader("Visualizar Recuperações")
        recovery_fig = draw_pitch(st.session_state.events['recovery'], 'recovery')
        st.pyplot(recovery_fig)

    with tab4:
        st.header("Adicionar Assistência")
        player_name = st.text_input("Nome do Jogador", key="assist_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="assist_minute")
        x = st.number_input("Coordenada X Inicial", min_value=0.0, max_value=120.0, step=0.1, key="assist_x")
        y = st.number_input("Coordenada Y Inicial", min_value=0.0, max_value=80.0, step=0.1, key="assist_y")
        end_x = st.number_input("Coordenada X Final", min_value=0.0, max_value=120.0, step=0.1, key="assist_end_x")
        end_y = st.number_input("Coordenada Y Final", min_value=0.0, max_value=80.0, step=0.1, key="assist_end_y")
        assist_type = st.selectbox("Tipo de Assistência", ["cruzamento", "passe atrasado"])
        team = st.selectbox("Equipe", ["casa", "fora"], key="assist_team")

        if st.button("Adicionar Assistência"):
            event = {'player': player_name, 'minute': minute, 'x': x, 'y': y, 'end_x': end_x, 'end_y': end_y, 'assist_type': assist_type, 'team': team, 'type': 'assist'}
            st.session_state.events['assist'].append(event)
            st.success("Assistência adicionada com sucesso!")

        st.subheader("Visualizar Assistências")
        assist_fig = draw_pitch(st.session_state.events['assist'], 'assist')
        st.pyplot(assist_fig)

    with tab5:
        st.header("Adicionar Duelo Aéreo")
        player_name = st.text_input("Nome do Jogador", key="duel_player_name")
        minute = st.number_input("Minuto do Evento", min_value=0, max_value=120, step=1, key="duel_minute")
        x = st.number_input("Coordenada X", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
        y = st.number_input("Coordenada Y", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
        outcome = st.selectbox("Resultado", ["ganho", "perdido"])
        team = st.selectbox("Equipe", ["casa", "fora"], key="duel_team")

        if st.button("Adicionar Duelo Aéreo"):
            event = {'player': player_name, 'minute': minute, 'x': x, 'y': y, 'outcome': outcome, 'team': team, 'type': 'duel'}
            st.session_state.events['duel'].append(event)
            st.success("Duelo Aéreo adicionado com sucesso!")

        st.subheader("Visualizar Duelos Aéreos")
        duel_fig = draw_pitch(st.session_state.events['duel'], 'duel')
        st.pyplot(duel_fig)

    # Botão para exportar os eventos para Excel
    st.header("Exportar Eventos para Excel")
    if st.button("Exportar para Excel"):
        excel_data = export_to_excel(st.session_state.events, selected_game)
        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
            excel_data.to_excel(writer, index=False, sheet_name="Eventos")
        excel_bytes.seek(0)
        st.download_button(label="Baixar Planilha de Eventos", data=excel_bytes, file_name=f'{selected_game}_eventos.xlsx')
