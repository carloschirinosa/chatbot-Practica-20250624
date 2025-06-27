import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "COLOCHO: This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")

import json
import streamlit as st
from openai import OpenAI

# --- Función para cargar la configuración (asumiendo que ya la tienes) ---
def load_config(config_file="config.json"):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        st.error(f"Error: El archivo de configuración '{config_file}' no fue encontrado. Asegúrate de que exista en la misma carpeta que tu script o especifica la ruta correcta.")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: No se pudo decodificar el archivo JSON '{config_file}'. Verifica su formato.")
        return None
    except Exception as e:
        st.error(f"Error inesperado al leer el archivo de configuración: {e}")
        return None

# --- Cargar la clave de OpenAI desde config.json ---
config = load_config()
openai_api_key = None
if config:
    try:
        openai_api_key = config["openai_api"]["key"]
        if not openai_api_key:
            st.warning("La clave de OpenAI no está definida en config.json. Por favor, revísala.")
    except KeyError:
        st.error("La clave 'openai_api' o 'key' no fue encontrada en tu config.json. Verifica la estructura.")
    except Exception as e:
        st.error(f"Error inesperado al acceder a la clave de OpenAI: {e}")

openai_api_key ="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"
# --- Inicialización de variables de estado de sesión para las conversaciones ---
if "conversations" not in st.session_state:
    st.session_state.conversations = {} # Diccionario para almacenar todas las conversaciones
    st.session_state.current_chat_id = None # ID de la conversación actual
    st.session_state.next_chat_id = 0 # Contador para IDs únicos

# --- Función para iniciar una nueva conversación ---
def start_new_chat():
    new_id = st.session_state.next_chat_id
    st.session_state.conversations[f"chat_{new_id}"] = [] # Inicializa una lista vacía para los mensajes
    st.session_state.current_chat_id = f"chat_{new_id}"
    st.session_state.next_chat_id += 1
    # Reinicia los mensajes mostrados en la conversación actual
    st.session_state.messages = []
    st.rerun() # Fuerza una recarga para limpiar el chat principal

# --- Lógica principal de la aplicación ---

st.title("Asistente de IA con Dejo Colombiano 🇨🇴")

if not openai_api_key:
    st.info("Por favor, agrega tu clave de OpenAI API en `config.json` para continuar.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # --- Sidebar para las conversaciones ---
    with st.sidebar:
        st.header("Mis Conversaciones")

        # Botón para nueva conversación
        if st.button("➕ Nueva Conversación", use_container_width=True):
            start_new_chat()

        st.markdown("---")
        st.subheader("Historial")

        # Mostrar conversaciones existentes
        if not st.session_state.conversations:
            st.info("¡Aún no hay conversaciones! Inicia una nueva.")
        else:
            # Ordenar las conversaciones para que la más reciente aparezca primero
            sorted_chat_ids = sorted(st.session_state.conversations.keys(), key=lambda x: int(x.split('_')[1]), reverse=True)

            for chat_id in sorted_chat_ids:
                # Usa el primer mensaje del usuario o un título genérico
                if st.session_state.conversations[chat_id]:
                    # Intenta tomar el contenido del primer mensaje del usuario
                    first_msg_content = "Nueva conversación"
                    for msg in st.session_state.conversations[chat_id]:
                        if msg["role"] == "user" and msg["content"]:
                            first_msg_content = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                            break # Una vez que encontramos el primer mensaje del usuario, salimos
                else:
                    first_msg_content = "Conversación vacía"

                # Crea un botón para cargar la conversación
                if st.button(f"💬 {first_msg_content}", key=f"load_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = st.session_state.conversations[chat_id]
                    st.rerun() # Fuerza una recarga para mostrar la conversación seleccionada

        # Si no hay una conversación actual, iniciar una por defecto al cargar la app
        if st.session_state.current_chat_id is None and st.session_state.conversations:
            # Cargar la conversación más reciente al inicio si existe
            st.session_state.current_chat_id = sorted_chat_ids[0]
            st.session_state.messages = st.session_state.conversations[st.session_state.current_chat_id]
        elif st.session_state.current_chat_id is None and not st.session_state.conversations:
            # Si no hay ninguna conversación, crear una nueva al inicio
            start_new_chat()


    # --- Lógica de la conversación principal ---
    if st.session_state.current_chat_id:
        st.write(f"Estás en: **{st.session_state.current_chat_id.replace('chat_', 'Conversación ')}**") # Muestra el ID de la conversación actual

        # Display the existing chat messages for the current conversation
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input field
        if prompt := st.chat_input("¿Qué más, mi parcero?"):
            # Add user message to current conversation and display
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.conversations[st.session_state.current_chat_id].append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            # Asegúrate de que el mensaje del sistema solo se envíe una vez por conversación si es parte del "dejo"
            # Una forma es asegurarte que el primer mensaje de la conversación sea el del sistema
            
            # Construye la lista de mensajes para la API incluyendo el mensaje del sistema
            messages_for_api = [
                {"role": "system", "content": "Eres un asistente que responde con un tono amable y usa expresiones coloquiales de Colombia. Habla como si fueras de Bogotá o la región andina colombiana."},
                *st.session_state.messages # Los mensajes de la sesión ya incluirán los del usuario y el asistente
            ]

            stream = client.chat.completions.create(
                model="gpt-3.5-turbo", # O "gpt-4-o-mini"
                messages=messages_for_api,
                stream=True,
            )

            # Stream the response and store it
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversations[st.session_state.current_chat_id].append({"role": "assistant", "content": response})

    else:
        st.info("Selecciona una conversación del historial o inicia una nueva para empezar.")
