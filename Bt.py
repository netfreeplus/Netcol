import telebot
import requests
import json
import sys
from colorama import init, Fore, Style
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inicializar colorama para el formato de colores en la consola
init(autoreset=True)

# Pedir el token del bot al usuario
print(Fore.YELLOW + Style.BRIGHT + "Por favor, introduce tu token de Telegram:")
TOKEN = input(Fore.GREEN + Style.BRIGHT + "> ")

# Inicializar el bot con el token proporcionado
bot = telebot.TeleBot(TOKEN)

# Comando /start - Mensaje de bienvenida
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn_bin = InlineKeyboardButton("Consultar BIN", callback_data="consultar_bin")
    markup.add(btn_bin)
    bot.send_message(message.chat.id, 
                     "¡Bienvenido al Bot de consulta de BIN! Usa /bin seguido del número BIN para obtener información sobre una tarjeta.\n" +
                     "O presiona el botón a continuación para realizar una consulta.", 
                     reply_markup=markup)

# Comando /help - Mostrar ayuda
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """
Lista de comandos disponibles:
- /start: Iniciar el bot y mostrar bienvenida.
- /help: Mostrar esta ayuda.
- /about: Información sobre el bot.
- /bin [número BIN]: Consultar información sobre un BIN.
    """)

# Comando /about - Mostrar información del bot
@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, "Este bot fue creado para la consulta de BINs. Proyecto para la universidad.")

# Manejador de consultas BIN
@bot.message_handler(commands=['bin'])
def handle_bin(message):
    bin_input = message.text[len("/bin "):].strip()
    
    # Validaciones del BIN
    if not bin_input.isdigit() or not (6 <= len(bin_input) <= 8):
        bot.send_message(message.chat.id, "Debes colocar /bin seguido de un BIN numérico de entre 6 y 8 dígitos.")
        return
    
    # Llamada a la API para obtener datos del BIN
    try:
        response = requests.get(f"https://data.handyapi.com/bin/{bin_input}")
        response.raise_for_status()
        api = response.json()

        # Si la API responde con éxito
        if api["Status"] == "SUCCESS":
            paisNombre = api["Country"]["Name"]
            marca = api["Scheme"]
            tipo = api["Type"]
            nivel = api["CardTier"]
            banco = api["Issuer"]

            # Enviar respuesta en formato Markdown
            bot.send_message(message.chat.id, f"""
**Información solicitada:**
- **BIN**: `{bin_input}`
- **Nivel**: `{nivel}`
- **Tipo**: `{tipo}`
- **Marca**: `{marca}`
- **País**: `{paisNombre}`
- **Banco**: `{banco}`
            """, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, 'Por favor, ingresa un BIN válido.')

    # Manejo de errores de conexión o respuesta
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"Error al conectar con la API: {str(e)}")
    except json.JSONDecodeError:
        bot.send_message(message.chat.id, "Error al procesar la respuesta de la API.")

# Manejador de botones
@bot.callback_query_handler(func=lambda call: call.data == "consultar_bin")
def consultar_bin(call):
    bot.send_message(call.message.chat.id, "Por favor, introduce el BIN después de /bin")

# Función para iniciar el bot y escuchar comandos
def start_bot():
    print(Fore.CYAN + Style.BRIGHT + "El bot está funcionando correctamente. Esperando comandos...")

    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(Fore.MAGENTA + Style.BRIGHT + f"Se perdió la conexión: {e}")
        print(Fore.RED + Style.BRIGHT + "La conexión se perdió. Por favor, reinicia el script manualmente.")
        sys.exit()

# Función principal
if __name__ == "__main__":
    start_bot()
