# Python · i18n.py · Plaza Wallet · Windows · Python 3.10+
"""UI translations. Portuguese source strings follow the gettext convention."""
LANGUAGES = {"pt-BR": "Português (Brasil)", "en": "English", "es": "Español"}

# Source, English, Spanish. Keep format placeholders identical in every language.
ROWS = [
    ("Escolha seu idioma", "Choose your language", "Elige tu idioma"),
    ("Como você quer usar o Plaza Wallet?", "How would you like to use Plaza Wallet?", "¿En qué idioma quieres usar Plaza Wallet?"),
    ("Continuar", "Continue", "Continuar"),
    ("Você pode trocar o idioma a qualquer momento.", "You can change the language at any time.", "Puedes cambiar el idioma en cualquier momento."),
    ("Idioma", "Language", "Idioma"),
    ("Selecione a pasta de instalação do jogo", "Select the game's installation folder", "Selecciona la carpeta de instalación del juego"),
    ("Aguardando o jogo", "Waiting for the game", "Esperando el juego"),
    ("Instale o conector e abra uma partida para começar.", "Install the connector and load a game to get started.", "Instala el conector y carga una partida para empezar."),
    ("Nenhuma variável selecionada", "No variable selected", "Ninguna variable seleccionada"),
    ("DESATIVADO", "DISABLED", "DESACTIVADO"),
    ("◈   Carteira", "◈   Wallet", "◈   Cartera"),
    ("CONTROLE LOCAL", "LOCAL CONTROL", "CONTROL LOCAL"),
    ("01  Conectar\n\n02  Encontrar saldo\n\n03  Ativar reposição", "01  Connect\n\n02  Read balance\n\n03  Enable refill", "01  Conectar\n\n02  Consultar saldo\n\n03  Activar recarga"),
    ("Sua carteira. Sem limites.", "Your wallet. No limits.", "Tu cartera. Sin límites."),
    ("Escolha o saldo e mantenha o dinheiro sempre disponível.", "Set your balance and keep money available.", "Elige el saldo y mantén tu dinero disponible."),
    ("01 / CONEXÃO", "01 / CONNECTION", "01 / CONEXIÓN"),
    ("Escolher pasta", "Choose folder", "Elegir carpeta"),
    ("Instalar conector", "Install connector", "Instalar conector"),
    ("Remover", "Remove", "Eliminar"),
    ("02 / ENCONTRAR SALDO", "02 / READ BALANCE", "02 / CONSULTAR SALDO"),
    ("Ler jogo", "Read game", "Leer juego"),
    ("Filtre por nome ou pelo valor atual do dinheiro.", "Filter by name or current balance.", "Filtra por nombre o por el saldo actual."),
    ("VARIÁVEL", "VARIABLE", "VARIABLE"),
    ("VALOR", "VALUE", "VALOR"),
    ("03 / DINHEIRO INFINITO", "03 / UNLIMITED MONEY", "03 / DINERO INFINITO"),
    ("Saldo mínimo", "Minimum balance", "Saldo mínimo"),
    ("Ativar reposição ∞", "Enable refill ∞", "Activar recarga ∞"),
    ("Desativar", "Disable", "Desactivar"),
    ("Primeiro uso: instale com o jogo fechado; depois abra e carregue uma partida.", "First use: install with the game closed, then launch it and load a save.", "Primer uso: instala con el juego cerrado; después ábrelo y carga una partida."),
    ("Pasta do MILF's Plaza", "MILF's Plaza folder", "Carpeta de MILF's Plaza"),
    ("Conector ativo", "Connector active", "Conector activo"),
    ("Desative a reposição antes de trocar de pasta.", "Disable refill before changing folders.", "Desactiva la recarga antes de cambiar de carpeta."),
    ("Pasta selecionada. Instale o conector com o jogo fechado.", "Folder selected. Install the connector with the game closed.", "Carpeta seleccionada. Instala el conector con el juego cerrado."),
    ("Pasta inválida", "Invalid folder", "Carpeta no válida"),
    ("Feche o jogo", "Close the game", "Cierra el juego"),
    ("Feche o jogo antes de instalar ou atualizar o conector.", "Close the game before installing or updating the connector.", "Cierra el juego antes de instalar o actualizar el conector."),
    ("Conector instalado. Abra o jogo, carregue sua partida e clique em Ler jogo.", "Connector installed. Launch the game, load a save and click Read game.", "Conector instalado. Abre el juego, carga tu partida y pulsa Leer juego."),
    ("Falha ao instalar", "Installation failed", "Error de instalación"),
    ("Feche o jogo antes de remover o conector.", "Close the game before removing the connector.", "Cierra el juego antes de eliminar el conector."),
    ("Conector removido. Cópia guardada em {path}", "Connector removed. Backup saved to {path}", "Conector eliminado. Copia guardada en {path}"),
    ("Falha ao remover", "Removal failed", "Error al eliminar"),
    ("Abra o jogo com o conector instalado e carregue sua partida.", "Launch the game with the connector installed and load your save.", "Abre el juego con el conector instalado y carga tu partida."),
    ("Aguardando confirmação do jogo…", "Waiting for confirmation from the game…", "Esperando la confirmación del juego…"),
    ("Falha de comunicação", "Communication failed", "Error de comunicación"),
    ("Selecione a variável que corresponde ao dinheiro da sua partida.", "Select the money variable in your game.", "Selecciona la variable de dinero de tu partida."),
    ("Saldo inválido", "Invalid balance", "Saldo no válido"),
    ("Digite um inteiro entre 1 e 999999999, sem separadores.", "Enter a whole number from 1 to 999999999, without separators.", "Introduce un entero entre 1 y 999999999, sin separadores."),
    ("●  Jogo conectado", "●  Game connected", "●  Juego conectado"),
    ("REPOSIÇÃO ATIVA", "REFILL ACTIVE", "RECARGA ACTIVA"),
    ("Reposição confirmada pelo jogo.", "Refill confirmed by the game.", "Recarga confirmada por el juego."),
    ("Conectado. {count} variáveis lidas. Selecione o dinheiro pelo nome e valor.", "Connected. {count} variables read. Select the balance by name and value.", "Conectado. {count} variables leídas. Selecciona el dinero por nombre y valor."),
    ("○  Aguardando o jogo", "○  Waiting for the game", "○  Esperando el juego"),
    ("SEM CONEXÃO", "OFFLINE", "SIN CONEXIÓN"),
    ("O jogo não confirmou o comando. Volte à partida e tente novamente.", "The game did not confirm the command. Return to your game and try again.", "El juego no confirmó el comando. Vuelve a la partida e inténtalo de nuevo."),
    ("Reposição ativa", "Refill active", "Recarga activa"),
    ("A reposição continuará até fechar o jogo. Fechar apenas o painel?", "Refill will continue until the game closes. Close only the panel?", "La recarga continuará hasta cerrar el juego. ¿Cerrar solo el panel?"),
    ("Pasta lembrada. Carregue uma partida e clique em Ler jogo.", "Folder restored. Load a save and click Read game.", "Carpeta recordada. Carga una partida y pulsa Leer juego."),
    ("Não foi possível salvar suas preferências. {detail}", "Could not save your preferences. {detail}", "No se pudieron guardar tus preferencias. {detail}"),
    ("Falha na operação. Detalhes do sistema: {detail}", "Operation failed. System details: {detail}", "Error en la operación. Detalles del sistema: {detail}"),
    ("Selecione a pasta do jogo Ren'Py, com as subpastas game e renpy.", "Select the Ren'Py game folder containing the game and renpy subfolders.", "Selecciona la carpeta del juego Ren'Py que contiene las subcarpetas game y renpy."),
    ("O arquivo zz_plaza_wallet.rpy precisa ficar junto do aplicativo.", "Keep zz_plaza_wallet.rpy in the same folder as the application.", "El archivo zz_plaza_wallet.rpy debe estar junto a la aplicación."),
    ("Ja existe um mod com esse nome, de outra origem. Nada foi alterado.", "An unrelated mod already uses this filename. Nothing was changed.", "Ya existe otro mod con este nombre. No se modificó nada."),
    ("Existe um .rpyc sem o fonte correspondente. Remova esse conflito manualmente.", "A .rpyc file exists without its source. Resolve this conflict manually.", "Existe un archivo .rpyc sin su código fuente. Resuelve este conflicto manualmente."),
    ("O mod Plaza Wallet nao foi encontrado nesta pasta.", "The Plaza Wallet mod was not found in this folder.", "No se encontró el mod Plaza Wallet en esta carpeta."),
    ("Caminho de variavel invalido.", "Invalid variable path.", "Ruta de variable no válida."),
    ("Nome de variavel invalido.", "Invalid variable name.", "Nombre de variable no válido."),
    ("Variavel interna do motor nao pode ser alterada.", "Internal engine variables cannot be modified.", "No se pueden modificar las variables internas del motor."),
    ("A variavel selecionada nao e um numero.", "The selected variable is not a number.", "La variable seleccionada no es un número."),
    ("Variavel ausente neste momento. Carregue o save correto.", "Variable unavailable. Load the correct save.", "Variable no disponible. Carga la partida correcta."),
    ("Saldo deve estar entre 1 e 999999999.", "Balance must be between 1 and 999999999.", "El saldo debe estar entre 1 y 999999999."),
    ("Carregue uma partida antes de ativar.", "Load a save before enabling refill.", "Carga una partida antes de activar la recarga."),
    ("Comando desconhecido.", "Unknown command.", "Comando desconocido."),
]

CATALOGS = {language: {row[0]: row[index] for row in ROWS}
            for index, language in enumerate(LANGUAGES)}


def translate(language, message, **values):
    catalog = CATALOGS.get(language, CATALOGS["en"])
    return catalog.get(message, message).format(**values)


def number(language, value):
    if value is None:
        return "—"
    text = f"{value:,.2f}" if isinstance(value, float) and not value.is_integer() else f"{int(value):,}"
    if language != "en":
        text = text.replace(",", "_").replace(".", ",").replace("_", ".")
    return text
