# Análise de Dados no Futebol

Este é um projeto desenvolvido com [Streamlit](https://streamlit.io/) que permite a visualização e análise de eventos de jogos de futebol, como passes, remates, recuperações, assistências e duelos aéreos. A aplicação permite a entrada manual de dados, a visualização dos eventos num campo de futebol e a exportação dos dados para um ficheiro Excel.

## Funcionalidades

- **Adicionar Jogo**: Permite criar um novo jogo para a análise dos eventos.
- **Remover Jogo**: Possibilita a remoção de jogos previamente adicionados.
- **Inserir Eventos**: Permite adicionar eventos de vários tipos (passes, remates, recuperações, assistências, duelos aéreos) com detalhes como o nome do jogador, minuto, coordenadas no campo e outros detalhes específicos do evento.
- **Visualizar Eventos**: Exibe os eventos adicionados num campo de futebol através de gráficos.
- **Exportar Dados**: Exporta os eventos para um ficheiro Excel.

## Instalação

Para utilizar esta aplicação, siga os passos abaixo:

1. Clone o repositório para o seu ambiente local:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   ```
2. Aceda à pasta do projeto:
   ```bash
   cd nome-do-projeto
   ```
3. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Como Usar

1. **Adicionar Jogo**: No painel lateral, introduza o nome do jogo e clique em "Adicionar Jogo".
2. **Selecionar Jogo**: Escolha o jogo na lista de jogos disponíveis no painel lateral.
3. **Adicionar Eventos**: Navegue pelas diferentes abas ("Passes", "Remates", "Recuperações", "Assistências", "Duelos Aéreos") para adicionar os eventos correspondentes.
4. **Visualizar Eventos**: Após adicionar os eventos, visualize-os diretamente na interface como pontos e setas sobre um campo de futebol.
5. **Exportar para Excel**: Clique no botão para exportar todos os eventos para um ficheiro Excel.

## Personalização

- **Cores dos Eventos**: As cores dos eventos variam de acordo com a equipa ("casa" ou "fora") e o tipo de evento.
- **Tipos de Eventos**:
  - **Passes**: Pode escolher entre "passe normal", "passe quebra linhas", "variação do CJ" e "passe em profundidade".
  - **Remates**: Inclui "golo", "defesa", "para fora" e "bloqueado".
  - **Recuperações**: Inclui "recuperação", "interceção" e "desarme".
  - **Assistências**: Inclui "cruzamento" e "passe atrasado".
  - **Duelos Aéreos**: Pode indicar se o duelo foi "ganho" ou "perdido".

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto é licenciado sob a licença MIT. Consulte o ficheiro LICENSE para mais detalhes.

# Football Data Analysis Web Application

This is a web application built using Streamlit that allows users to analyze football match data by adding, visualizing, and exporting different events such as passes, shots, recoveries, assists, and aerial duels on a football pitch. The application also supports exporting the data to an Excel file.

## Features

- **Add Game**: Users can create new game sessions by entering a game name.
- **Delete Game**: Allows users to remove existing game sessions.
- **Event Management**: Users can add and view different types of football events, including:
  - **Passes**: Records passes with start and end coordinates, player name, minute, and type of pass.
  - **Shots**: Records shots with coordinates, player name, minute, expected goal probability (xG), and outcome.
  - **Recoveries**: Records ball recoveries with coordinates, player name, minute, and type of recovery.
  - **Assists**: Records assists with start and end coordinates, player name, minute, and type of assist.
  - **Aerial Duels**: Records aerial duels with coordinates, player name, minute, and outcome (won/lost).
- **Pitch Visualization**: Visualize the events directly on a football pitch with color-coded representations based on the event type and team.
- **Export to Excel**: Export all recorded events for a selected game to an Excel file for further analysis.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/football-data-analysis.git
   cd football-data-analysis
   ```

2. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```sh
   streamlit run app.py
   ```

4. **Access the application:**  
   Open your web browser and go to `http://localhost:8501`.

## Usage

1. **Add a New Game:**
   - Enter a unique name for the game in the sidebar and click "Add new game".

2. **Select or Delete a Game:**
   - Use the dropdown to select a game to view or delete.

3. **Add Events:**
   - Select a tab corresponding to the event type (Passes, Shots, Recoveries, Assists, Aerial Duels).
   - Enter the required details for the event and click the "Add" button.
   - The event will be visualized on the pitch.

4. **Export Events to Excel:**
   - After adding events, click the "Export to excel" button to download all events as an Excel file.

## Customization

- **Event Types and Colors**: The event types and corresponding colors for visualization are defined in dictionaries within the code. You can modify these colors and add new event types if necessary.
- **Pitch Configuration**: The pitch layout is generated using the `mplsoccer` library. You can customize the appearance by modifying the pitch drawing settings in the `draw_pitch` function.

## Requirements

- **Python 3.x**
- **Streamlit**
- **matplotlib**
- **mplsoccer**
- **pandas**

## Contributing

If you have any suggestions, bug fixes, or enhancements, feel free to open an issue or submit a pull request. Contributions are always welcome!

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
