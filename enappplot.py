import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import io

# Function to draw the pitch and events
def draw_pitch(events, event_type):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', goal_type="box", corner_arcs=True)
    
    # Set up the figure with space for the legend
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    # Colour dictionaries for passes, shots, recoveries, assists, and duels
    assist_colours = {
        'home': {'cross': 'orange', 'cutback': 'blue'},
        'away': {'cross': 'purple', 'cutback': 'cyan'}
    }

    shot_colours = {
        'home': {'goal': 'red', 'saved': 'blue', 'off target': 'green', 'blocked': 'brown'},
        'away': {'goal': 'green', 'saved': 'blue', 'off target': 'black', 'blocked': 'orange'}
    }

    recovery_colours = {
        'home': {'interception': 'green', 'tackle': 'blue', 'recovery': 'orange'},
        'away': {'interception': 'purple', 'tackle': 'cyan', 'recovery': 'yellow'}
    }

    duel_colours = {
        'home': {'won': 'green', 'lost': 'red'},
        'away': {'won': 'blue', 'lost': 'yellow'}
    }

    pass_colours = {
        'home': {'line-breaking pass': 'red', 'switch of play': 'blue', 'through pass': 'green', 'normal pass': 'black'},
        'away': {'line-breaking pass': 'orange', 'switch of play': 'cyan', 'through pass': 'purple', 'normal pass': 'gray'}
    }

    # Add events to the pitch
    for event in events:
        if event['type'] == event_type:
            team = event.get('team')
            if event_type == 'pass' and 'end_x' in event and 'end_y' in event:
                colour = pass_colours[team].get(event.get('pass_type'), 'black')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=colour, width=2)
            elif event_type == 'shot':
                colour = shot_colours[team].get(event.get('outcome'), 'red')
                pitch.scatter(event['x'], event['y'], ax=ax, color=colour, s=100)
            elif event_type == 'recovery':
                colour = recovery_colours[team].get(event.get('recovery_type'), 'orange')
                pitch.scatter(event['x'], event['y'], ax=ax, color=colour, s=100)
            elif event_type == 'assist' and 'end_x' in event and 'end_y' in event:
                colour = assist_colours[team].get(event.get('assist_type'), 'orange')
                pitch.arrows(event['x'], event['y'], event['end_x'], event['end_y'], ax=ax, color=colour, width=2)
            elif event_type == 'duel':
                colour = duel_colours[team].get(event.get('outcome'), 'gray')
                pitch.scatter(event['x'], event['y'], ax=ax, color=colour, s=150, marker='^')

    # Add legends outside the pitch
    if event_type == 'assist':
        legend_handles = [plt.Line2D([0], [0], color=colour, lw=2, label=f'{team} - {label}') 
                          for team, colours in assist_colours.items() for label, colour in colours.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Assists')
    elif event_type == 'shot':
        legend_handles = [plt.Line2D([0], [0], color=colour, marker='o', lw=0, label=f'{team} - {label}') 
                          for team, colours in shot_colours.items() for label, colour in colours.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Shots')
    elif event_type == 'duel':
        legend_handles = [plt.Line2D([0], [0], color=colour, marker='^', lw=0, label=f'{team} - {label}') 
                          for team, colours in duel_colours.items() for label, colour in colours.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Aerial Duels')
    elif event_type == 'pass':
        legend_handles = [plt.Line2D([0], [0], color=colour, lw=2, label=f'{team} - {label}') 
                          for team, colours in pass_colours.items() for label, colour in colours.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Passes')
    elif event_type == 'recovery':
        legend_handles = [plt.Line2D([0], [0], color=colour, marker='o', lw=0, label=f'{team} - {label}') 
                          for team, colours in recovery_colours.items() for label, colour in colours.items()]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5), title='Recoveries')

    return fig


# Initialise session state
if 'games' not in st.session_state:
    st.session_state.games = []
if 'events' not in st.session_state:
    st.session_state.events = {'pass': [], 'shot': [], 'recovery': [], 'assist': [], 'duel': []}
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = {'pass': None, 'shot': None, 'recovery': None, 'assist': None, 'duel': None}
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None

# Function to export events to Excel
def export_to_excel(events, game_name):
    df_list = []
    for event_type, events_list in events.items():
        df = pd.DataFrame(events_list)
        df['type'] = event_type
        df['game'] = game_name
        df_list.append(df)
    
    all_events_df = pd.concat(df_list, ignore_index=True)
    return all_events_df

# Function to remove a game
def remove_game(game_name):
    if game_name in st.session_state.games:
        st.session_state.games.remove(game_name)
        if st.session_state.selected_game == game_name:
            st.session_state.selected_game = None
        st.session_state.events = {'pass': [], 'shot': [], 'recovery': [], 'assist': [], 'duel': []}
        st.success(f"Game '{game_name}' successfully removed!")
    else:
        st.error("Game not found.")

# Set up the page with a football icon
st.set_page_config(
    page_title="Football Data Analysis",
    page_icon="icons8-soccer-ball-50.png"
)

st.title("Annotate Events on the Football Pitch")

# Section to add new games
st.sidebar.header("Add New Game")
game_name = st.text_input("Game Name")
if st.button("Add Game"):
    if game_name:
        st.session_state.games.append(game_name)
        st.success(f"Game '{game_name}' successfully added!")

# Section to remove games
st.sidebar.header("Remove Game")
if st.session_state.games:
    game_to_remove = st.selectbox("Choose a game to remove", st.session_state.games)
    if st.button("Remove Game"):
        if game_to_remove:
            remove_game(game_to_remove)
else:
    st.write("No games available to remove.")

# Select the game to display events
st.sidebar.header("Select Game")
selected_game = st.selectbox("Choose a game", st.session_state.games)
st.session_state.selected_game = selected_game

if selected_game:
    st.title(f"Events for game: {selected_game}")

    # Separate inputs and graphics for each event type
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Passes", "Shots", "Recoveries", "Assists", "Aerial Duels"])

    with tab1:
        st.header("Add Pass")
        player_name = st.text_input("Player Name", key="pass_player_name")
        minute = st.number_input("Minute", min_value=0, max_value=120, step=1, key="pass_minute")
        x = st.number_input("Starting X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="pass_x")
        y = st.number_input("Starting Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="pass_y")
        end_x = st.number_input("Ending X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="pass_end_x")
        end_y = st.number_input("Ending Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="pass_end_y")
        pass_type = st.selectbox("Pass Type", ["line-breaking pass", "switch of play", "through pass", "normal pass"])
        team = st.selectbox("Team", ["home", "away"])
        if st.button("Add Pass"):
            pass_event = {
                "player_name": player_name,
                "minute": minute,
                "x": x,
                "y": y,
                "end_x": end_x,
                "end_y": end_y,
                "pass_type": pass_type,
                "team": team,
                "type": "pass"
            }
            st.session_state.events['pass'].append(pass_event)
            st.success("Pass event added successfully!")

    with tab2:
        st.header("Add Shot")
        player_name = st.text_input("Player Name", key="shot_player_name")
        minute = st.number_input("Minute", min_value=0, max_value=120, step=1, key="shot_minute")
        x = st.number_input("X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="shot_x")
        y = st.number_input("Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="shot_y")
        outcome = st.selectbox("Outcome", ["goal", "saved", "off target", "blocked"])
        team = st.selectbox("Team", ["home", "away"])
        if st.button("Add Shot"):
            shot_event = {
                "player_name": player_name,
                "minute": minute,
                "x": x,
                "y": y,
                "outcome": outcome,
                "team": team,
                "type": "shot"
            }
            st.session_state.events['shot'].append(shot_event)
            st.success("Shot event added successfully!")

    with tab3:
        st.header("Add Recovery")
        player_name = st.text_input("Player Name", key="recovery_player_name")
        minute = st.number_input("Minute", min_value=0, max_value=120, step=1, key="recovery_minute")
        x = st.number_input("X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="recovery_x")
        y = st.number_input("Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="recovery_y")
        recovery_type = st.selectbox("Recovery Type", ["interception", "tackle", "recovery"])
        team = st.selectbox("Team", ["home", "away"])
        if st.button("Add Recovery"):
            recovery_event = {
                "player_name": player_name,
                "minute": minute,
                "x": x,
                "y": y,
                "recovery_type": recovery_type,
                "team": team,
                "type": "recovery"
            }
            st.session_state.events['recovery'].append(recovery_event)
            st.success("Recovery event added successfully!")

    with tab4:
        st.header("Add Assist")
        player_name = st.text_input("Player Name", key="assist_player_name")
        minute = st.number_input("Minute", min_value=0, max_value=120, step=1, key="assist_minute")
        x = st.number_input("Starting X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="assist_x")
        y = st.number_input("Starting Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="assist_y")
        end_x = st.number_input("Ending X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="assist_end_x")
        end_y = st.number_input("Ending Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="assist_end_y")
        assist_type = st.selectbox("Assist Type", ["cross", "cutback"])
        team = st.selectbox("Team", ["home", "away"])
        if st.button("Add Assist"):
            assist_event = {
                "player_name": player_name,
                "minute": minute,
                "x": x,
                "y": y,
                "end_x": end_x,
                "end_y": end_y,
                "assist_type": assist_type,
                "team": team,
                "type": "assist"
            }
            st.session_state.events['assist'].append(assist_event)
            st.success("Assist event added successfully!")

    with tab5:
        st.header("Add Aerial Duel")
        player_name = st.text_input("Player Name", key="duel_player_name")
        minute = st.number_input("Minute", min_value=0, max_value=120, step=1, key="duel_minute")
        x = st.number_input("X Coordinate", min_value=0.0, max_value=120.0, step=0.1, key="duel_x")
        y = st.number_input("Y Coordinate", min_value=0.0, max_value=80.0, step=0.1, key="duel_y")
        outcome = st.selectbox("Outcome", ["won", "lost"])
        team = st.selectbox("Team", ["home", "away"])
        if st.button("Add Aerial Duel"):
            duel_event = {
                "player_name": player_name,
                "minute": minute,
                "x": x,
                "y": y,
                "outcome": outcome,
                "team": team,
                "type": "duel"
            }
            st.session_state.events['duel'].append(duel_event)
            st.success("Aerial duel event added successfully!")

    # Section to export events to Excel
    st.sidebar.header("Export Events")
    if st.button("Export to Excel"):
        excel_df = export_to_excel(st.session_state.events, st.session_state.selected_game)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            excel_df.to_excel(writer, index=False, sheet_name='Events')
            writer.save()
        output.seek(0)
        st.download_button(label="Download Events as Excel", data=output, file_name=f"{st.session_state.selected_game}_events.xlsx")

    # Display the pitch and the events
    st.header("Visualise Events on the Pitch")
    event_type_to_visualise = st.selectbox("Select event type to visualise", ["pass", "shot", "recovery", "assist", "duel"])
    if st.session_state.events[event_type_to_visualise]:
        pitch_fig = draw_pitch(st.session_state.events[event_type_to_visualise], event_type_to_visualise)
        st.pyplot(pitch_fig)
    else:
        st.write(f"No {event_type_to_visualise} events added yet.")
else:
    st.write("Please select a game to display events.")
