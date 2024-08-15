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
