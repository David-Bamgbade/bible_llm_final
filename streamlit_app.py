# import streamlit as st
# import requests
# import socketio
# import threading
# import time
#
# # --- Configuration ---
# BASE_URL = "http://127.0.0.1:5000"  # Your backend URL
#
# # --- Initialize Session State ---
# if "jwt_token" not in st.session_state:
#     st.session_state.jwt_token = None
# if "user_info" not in st.session_state:
#     st.session_state.user_info = {}
# if "chat_messages" not in st.session_state:
#     st.session_state.chat_messages = []
# if "socketio_connected" not in st.session_state:
#     st.session_state.socketio_connected = False
# if "sent_notifications" not in st.session_state:
#     st.session_state.sent_notifications = []
#
# # --- Sidebar Authentication ---
# auth_option = st.sidebar.radio("Authentication", ["Register", "Login", "Continue as Guest"])
# if auth_option == "Register":
#     st.sidebar.subheader("Register")
#     reg_username = st.sidebar.text_input("Username", key="reg_username")
#     reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
#     if st.sidebar.button("Register"):
#         resp = requests.post(f"{BASE_URL}/register", json={"username": reg_username, "password": reg_password})
#         if resp.status_code == 201:
#             st.sidebar.success("Registration successful! Please log in.")
#         else:
#             st.sidebar.error(resp.json().get("error", "Registration failed."))
# elif auth_option == "Login":
#     st.sidebar.subheader("Login")
#     login_username = st.sidebar.text_input("Username", key="login_username")
#     login_password = st.sidebar.text_input("Password", type="password", key="login_password")
#     if st.sidebar.button("Login"):
#         resp = requests.post(f"{BASE_URL}/login", json={"username": login_username, "password": login_password})
#         if resp.status_code == 200:
#             data = resp.json()
#             st.session_state.jwt_token = data["access_token"]
#             st.session_state.user_info = {"user_id": data["user_id"], "username": data["username"]}
#             st.sidebar.success("Login successful!")
#         else:
#             st.sidebar.error(resp.json().get("error", "Login failed."))
# else:
#     st.sidebar.write("Continuing as Guest.")
#
# # --- SocketIO Client Setup ---
# sio = socketio.Client()
#
#
# @sio.event
# def connect():
#     st.write("Connected to chat server.")
#
#
# @sio.event
# def disconnect():
#     st.write("Disconnected from chat server.")
#
#
# @sio.on("chat")
# def on_chat(data):
#     st.session_state.chat_messages.append(f"{data['timestamp']} - {data.get('user_id', 'Guest')}: {data['message']}")
#     st.experimental_rerun()
#
#
# @sio.on("sent")
# def on_sent(data):
#     st.session_state.sent_notifications.append(data["msg"])
#     st.experimental_rerun()
#
#
# def start_socketio(token):
#     # # Construct the connection URL with the token.
#     # url = f"{BASE_URL}?token={token}"
#     # st.write("Connecting to:", url)  # For debugging; remove in production.
#     # try:
#     #     # Explicitly connect on the default namespace.
#     #     sio.connect(url, namespaces=["/"])
#     #     sio.wait()
#     # except Exception as e:
#     #     st.write("SocketIO connection error:", e)
#
#     url = f"{BASE_URL}?token={token}"
#     st.write("Connecting to:", url)  # For debugging; remove in production.
#     try:
#         sio.connect(url, namespaces=["/"])
#         # Wait briefly to ensure connection is established.
#         time.sleep(2)
#         st.write("SocketIO connected:", sio.connected)
#     except Exception as e:
#         st.write("SocketIO connection error:", e)
#
#
# # Only start SocketIO if a valid token exists and no connection has been made.
# if st.session_state.get("jwt_token") and not st.session_state.get("socketio_connected"):
#     token = st.session_state.jwt_token  # JWT token generated on login
#     threading.Thread(target=start_socketio, args=(token,), daemon=True).start()
#     st.session_state.socketio_connected = True
#
# # --- Main Chat Interface ---
# st.title("Real-Time Bible Chat")
# if st.session_state.user_info:
#     st.write("Logged in as:", st.session_state.user_info.get("username"))
# else:
#     st.write("Chatting as Guest (chats are temporary).")
#
# chat_input = st.text_input("Enter your message:", key="chat_input")
# recipient_input = st.text_input("Send to (leave blank for public):", key="recipient_input")
# if st.button("Send"):
#     payload = {
#         "message": st.session_state.chat_input,
#         "username": st.session_state.user_info.get("username", "Guest")
#     }
#     if st.session_state.user_info:
#         payload["user_id"] = st.session_state.user_info.get("user_id")
#     if recipient_input.strip():
#         payload["recipient"] = recipient_input.strip()
#     if sio.connected:
#         sio.emit("chat", payload)
#     else:
#         st.error("Not connected to chat server yet.")
#
# st.subheader("Chat History")
# for msg in st.session_state.chat_messages:
#     st.write(msg)
#
# st.subheader("Notifications")
# for notif in st.session_state.sent_notifications:
#     st.write(notif)
#
# # --- Bible AI Q/A Interface ---
# st.title("📖 Ask the Bible AI")
# st.write("Ask a question, and the AI will answer based on the Bible.")
# response_type = st.radio("Select response type:", ("Text", "Voice"), index=0)
# question = st.text_input("Enter your question:")
# if st.button("Ask"):
#     if question:
#         with st.spinner("Thinking..."):
#             payload = {
#                 "question": question,
#                 "response_type": response_type.lower()  # "text" or "voice"
#             }
#             response = requests.post(f"{BASE_URL}/ask", json=payload)
#             if response.status_code == 200:
#                 if response_type.lower() == "voice":
#                     st.audio(response.content, format="audio/mp3")
#                 else:
#                     answer = response.json().get("answer", "No answer found.")
#                     st.success(f"Answer: {answer}")
#             else:
#                 st.error("Failed to get a response. Check if Flask is running.")
#     else:
#         st.warning("Please enter a question before clicking Ask.")

#
# import streamlit as st
# import requests
# import socketio
# import threading
# import time
#
# # --- Configuration ---
# BASE_URL = "http://127.0.0.1:5000"  # Your backend URL
#
# # --- Initialize Session State for multi-page navigation ---
# if "page" not in st.session_state:
#     # If a query parameter is present, use it. Otherwise, default to "auth".
#     params = st.query_params.to_dict()
#     st.session_state.page = params.get("page", "auth")
#
# if "jwt_token" not in st.session_state:
#     st.session_state.jwt_token = None
# if "user_info" not in st.session_state:
#     st.session_state.user_info = {}
# if "chat_messages" not in st.session_state:
#     st.session_state.chat_messages = []
# if "socketio_connected" not in st.session_state:
#     st.session_state.socketio_connected = False
# if "sent_notifications" not in st.session_state:
#     st.session_state.sent_notifications = []
#
# # --- SocketIO Client Setup ---
# sio = socketio.Client()
#
# @sio.event
# def connect():
#     st.write("Connected to chat server.")
#
# @sio.event
# def disconnect():
#     st.write("Disconnected from chat server.")
#
# @sio.on("chat")
# def on_chat(data):
#     st.session_state.chat_messages.append(
#         f"{data['timestamp']} - {data.get('user_id', 'Guest')}: {data['message']}"
#     )
#     st.experimental_rerun()
#
# @sio.on("sent")
# def on_sent(data):
#     st.session_state.sent_notifications.append(data["msg"])
#     st.experimental_rerun()
#
# def start_socketio(token):
#     url = f"{BASE_URL}?token={token}"
#     st.write("Connecting to:", url)  # For debugging; remove in production.
#     try:
#         sio.connect(url, namespaces=["/"])
#         # Wait briefly to ensure connection is established.
#         time.sleep(2)
#         st.write("SocketIO connected:", sio.connected)
#     except Exception as e:
#         st.write("SocketIO connection error:", e)
#
# # Only start SocketIO if a valid token exists and no connection has been made.
# if st.session_state.get("jwt_token") and not st.session_state.get("socketio_connected"):
#     token = st.session_state.jwt_token  # JWT token generated on login
#     threading.Thread(target=start_socketio, args=(token,), daemon=True).start()
#     st.session_state.socketio_connected = True
#
# # --- Define Page Functions ---
# def login_page():
#     st.header("Login")
#     login_username = st.text_input("Username", key="login_username")
#     login_password = st.text_input("Password", type="password", key="login_password")
#     if st.button("Login"):
#         resp = requests.post(
#             f"{BASE_URL}/login",
#             json={"username": login_username, "password": login_password},
#         )
#         if resp.status_code == 200:
#             data = resp.json()
#             st.session_state.jwt_token = data["access_token"]
#             st.session_state.user_info = {"user_id": data["user_id"], "username": data["username"]}
#             st.success("Login successful!")
#             st.session_state.page = "bible_ai"
#             # Update query parameters to reflect the new page.
#             st.query_params.from_dict({"page": "bible_ai"})
#             st.stop()  # Stop the current run so the new page will load.
#         else:
#             try:
#                 error_msg = resp.json().get("error", "Login failed.")
#             except Exception:
#                 error_msg = "Login failed."
#             st.error(error_msg)
#
# def bible_ai_page():
#     st.header("Bible AI Q/A")
#     st.write("Ask a question and get an answer based on the Bible.")
#     response_type = st.radio("Response type:", ("Text", "Voice"), key="response_type")
#     question = st.text_input("Enter your question:", key="bible_ai_question")
#     if st.button("Ask"):
#         if question:
#             with st.spinner("Thinking..."):
#                 payload = {"question": question, "response_type": response_type.lower()}
#                 response = requests.post(f"{BASE_URL}/ask", json=payload)
#                 if response.status_code == 200:
#                     if response_type.lower() == "voice":
#                         st.audio(response.content, format="audio/mp3")
#                     else:
#                         answer = response.json().get("answer", "No answer found.")
#                         st.success(f"Answer: {answer}")
#                 else:
#                     st.error("Failed to get a response. Check if backend is running.")
#         else:
#             st.warning("Please enter a question.")
#     # Navigation button to Chat page.
#     if st.button("Go to Chat"):
#         st.session_state.page = "chat"
#         st.query_params.from_dict({"page": "chat"})
#         st.stop()
#
# def chat_page():
#     st.header("Real-Time Bible Chat")
#     if st.session_state.user_info:
#         st.write("Logged in as:", st.session_state.user_info.get("username"))
#     else:
#         st.write("Chatting as Guest (chats are temporary).")
#     chat_input = st.text_input("Enter your message:", key="chat_input")
#     recipient_input = st.text_input("Send to (leave blank for public):", key="recipient_input")
#     if st.button("Send Message"):
#         payload = {"message": st.session_state.chat_input,
#                    "username": st.session_state.user_info.get("username", "Guest")}
#         if st.session_state.user_info:
#             payload["user_id"] = st.session_state.user_info.get("user_id")
#         if recipient_input.strip():
#             payload["recipient"] = recipient_input.strip()
#         if sio.connected:
#             sio.emit("chat", payload)
#         else:
#             st.error("Not connected to chat server yet.")
#     st.subheader("Chat History")
#     for msg in st.session_state.chat_messages:
#         st.write(msg)
#     st.subheader("Notifications")
#     for notif in st.session_state.sent_notifications:
#         st.write(notif)
#     # Navigation button to go back to Bible AI Q/A.
#     if st.button("Back to Bible AI Q/A"):
#         st.session_state.page = "bible_ai"
#         st.query_params.from_dict({"page": "bible_ai"})
#         st.stop()
#
# # --- Define Navigation using st.navigation and st.Page ---
# login_pg = st.Page(login_page, title="Login", icon="🔑")
# bible_ai_pg = st.Page(bible_ai_page, title="Bible AI", icon="📖")
# chat_pg = st.Page(chat_page, title="Chat", icon="💬")
#
# if st.session_state.role is None:
#     pages = {"Authentication": [login_pg]}
# else:
#     pages = {"Main": [bible_ai_pg, chat_pg]}
#
# nav = st.navigation(pages)
# nav.run()

# import streamlit as st
# import requests
# import socketio
# import threading
# import time
#
# # --- Configuration ---
# BASE_URL = "http://127.0.0.1:5000"  # Your backend URL
#
# # --- Initialize Session State for multi-page navigation ---
# if "page" not in st.session_state:
#     st.session_state.page = "auth"  # Default page is authentication
#
# if "jwt_token" not in st.session_state:
#     st.session_state.jwt_token = None
# if "user_info" not in st.session_state:
#     st.session_state.user_info = {}
# if "role" not in st.session_state:
#     st.session_state.role = None
# if "chat_messages" not in st.session_state:
#     st.session_state.chat_messages = []
# if "socketio_connected" not in st.session_state:
#     st.session_state.socketio_connected = False
# if "sent_notifications" not in st.session_state:
#     st.session_state.sent_notifications = []
#
# # --- SocketIO Client Setup ---
# sio = socketio.Client()
#
# @sio.event
# def connect():
#     st.write("Connected to chat server.")
#
# @sio.event
# def disconnect():
#     st.write("Disconnected from chat server.")
#
# @sio.on("chat")
# def on_chat(data):
#     st.session_state.chat_messages.append(
#         f"{data['timestamp']} - {data.get('user_id', 'Guest')}: {data['message']}"
#     )
#     st.experimental_rerun()
#
# @sio.on("sent")
# def on_sent(data):
#     st.session_state.sent_notifications.append(data["msg"])
#     st.experimental_rerun()
#
# def start_socketio(token):
#     url = f"{BASE_URL}?token={token}"
#     st.write("Connecting to:", url)  # For debugging; remove in production.
#     try:
#         sio.connect(url, namespaces=["/"])
#         time.sleep(2)  # Wait briefly to ensure connection is established.
#         st.write("SocketIO connected:", sio.connected)
#     except Exception as e:
#         st.write("SocketIO connection error:", e)
#
# # Start SocketIO if a token exists and connection hasn't been made.
# if st.session_state.get("jwt_token") and not st.session_state.get("socketio_connected"):
#     token = st.session_state.jwt_token
#     threading.Thread(target=start_socketio, args=(token,), daemon=True).start()
#     st.session_state.socketio_connected = True
#
# # --- Define Page Functions ---
#
# def login_page():
#     st.header("Login")
#     login_username = st.text_input("Username", key="login_username")
#     login_password = st.text_input("Password", type="password", key="login_password")
#     if st.button("Login"):
#         resp = requests.post(f"{BASE_URL}/login", json={"username": login_username, "password": login_password})
#         if resp.status_code == 200:
#             data = resp.json()
#             st.session_state.jwt_token = data["access_token"]
#             st.session_state.user_info = {"user_id": data["user_id"], "username": data["username"]}
#             st.session_state.role = "user"  # Mark user as logged in.
#             st.success("Login successful!")
#             st.session_state.page = "bible_ai"  # Route to Bible AI page.
#             st.experimental_rerun()
#         else:
#             try:
#                 error_msg = resp.json().get("error", "Login failed.")
#             except Exception:
#                 error_msg = "Login failed."
#             st.error(error_msg)
#
# def register_page():
#     st.header("Register")
#     reg_username = st.text_input("Username", key="reg_username")
#     reg_password = st.text_input("Password", type="password", key="reg_password")
#     if st.button("Register"):
#         resp = requests.post(f"{BASE_URL}/register", json={"username": reg_username, "password": reg_password})
#         if resp.status_code == 201:
#             st.success("Registration successful! Please log in.")
#             # Optionally, redirect automatically to the login page.
#             st.session_state.page = "login"
#             st.experimental_rerun()
#         else:
#             try:
#                 error_msg = resp.json().get("error", "Registration failed.")
#             except Exception:
#                 error_msg = "Registration failed."
#             st.error(error_msg)
#
# def bible_ai_page():
#     st.header("Bible AI Q/A")
#     st.write("Ask a question and get an answer based on the Bible.")
#     response_type = st.radio("Response type:", ("Text", "Voice"), key="response_type")
#     question = st.text_input("Enter your question:", key="bible_ai_question")
#     if st.button("Ask"):
#         if question:
#             with st.spinner("Thinking..."):
#                 payload = {"question": question, "response_type": response_type.lower()}
#                 response = requests.post(f"{BASE_URL}/ask", json=payload)
#                 if response.status_code == 200:
#                     if response_type.lower() == "voice":
#                         st.audio(response.content, format="audio/mp3")
#                     else:
#                         answer = response.json().get("answer", "No answer found.")
#                         st.success(f"Answer: {answer}")
#                 else:
#                     st.error("Failed to get a response. Check if backend is running.")
#         else:
#             st.warning("Please enter a question.")
#     if st.button("Go to Chat"):
#         st.session_state.page = "chat"
#         st.experimental_rerun()
#
# def chat_page():
#     st.header("Real-Time Bible Chat")
#     if st.session_state.user_info:
#         st.write("Logged in as:", st.session_state.user_info.get("username"))
#     else:
#         st.write("Chatting as Guest (chats are temporary).")
#     chat_input = st.text_input("Enter your message:", key="chat_input")
#     recipient_input = st.text_input("Send to (leave blank for public):", key="recipient_input")
#     if st.button("Send Message"):
#         payload = {
#             "message": st.session_state.chat_input,
#             "username": st.session_state.user_info.get("username", "Guest")
#         }
#         if st.session_state.user_info:
#             payload["user_id"] = st.session_state.user_info.get("user_id")
#         if recipient_input.strip():
#             payload["recipient"] = recipient_input.strip()
#         if sio.connected:
#             sio.emit("chat", payload)
#         else:
#             st.error("Not connected to chat server yet.")
#     st.subheader("Chat History")
#     for msg in st.session_state.chat_messages:
#         st.write(msg)
#     st.subheader("Notifications")
#     for notif in st.session_state.sent_notifications:
#         st.write(notif)
#     if st.button("Back to Bible AI Q/A"):
#         st.session_state.page = "bible_ai"
#         st.experimental_rerun()
#
# # --- Define Navigation using st.navigation and st.Page ---
# login_pg = st.Page(login_page, title="Login", icon="🔑")
# register_pg = st.Page(register_page, title="Register", icon="📝")
# bible_ai_pg = st.Page(bible_ai_page, title="Bible AI", icon="📖")
# chat_pg = st.Page(chat_page, title="Chat", icon="💬")
#
# # Build the navigation menu.
# if st.session_state.role is None:
#     # If not logged in, show both Login and Register pages.
#     pages = {"Authentication": [login_pg, register_pg]}
# else:
#     pages = {"Main": [bible_ai_pg, chat_pg]}
#
# nav = st.navigation(pages)
# nav.run()

import streamlit as st
import requests
import socketio
import threading
import time

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"  # Your backend URL

# --- Initialize Session State for multi-page navigation ---
if "page" not in st.session_state:
    st.session_state.page = "auth"  # Default page is authentication

if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "role" not in st.session_state:
    st.session_state.role = None  # role remains None until login succeeds
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "socketio_connected" not in st.session_state:
    st.session_state.socketio_connected = False
if "sent_notifications" not in st.session_state:
    st.session_state.sent_notifications = []

# --- SocketIO Client Setup ---
sio = socketio.Client()


@sio.event
def connect():
    st.write("Connected to chat server.")


@sio.event
def disconnect():
    st.write("Disconnected from chat server.")


@sio.on("chat")
def on_chat(data):
    st.session_state.chat_messages.append(
        f"{data['timestamp']} - {data.get('user_id', 'Guest')}: {data['message']}"
    )
    try:
        st.experimental_rerun()
    except AttributeError:
        st.query_params.from_dict({"page": st.session_state.page})
        st.stop()


@sio.on("sent")
def on_sent(data):
    st.session_state.sent_notifications.append(data["msg"])
    try:
        st.experimental_rerun()
    except AttributeError:
        st.query_params.from_dict({"page": st.session_state.page})
        st.stop()


def start_socketio(token):
    url = f"{BASE_URL}?token={token}"
    st.write("Connecting to:", url)  # For debugging; remove in production.
    try:
        sio.connect(url, namespaces=["/"])
        time.sleep(2)  # Wait briefly to ensure connection is established.
        st.write("SocketIO connected:", sio.connected)
    except Exception as e:
        st.write("SocketIO connection error:", e)


if st.session_state.get("jwt_token") and not st.session_state.get("socketio_connected"):
    token = st.session_state.jwt_token
    threading.Thread(target=start_socketio, args=(token,), daemon=True).start()
    st.session_state.socketio_connected = True


# --- Define Page Functions ---

def login_page():
    st.header("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        resp = requests.post(
            f"{BASE_URL}/login",
            json={"username": login_username, "password": login_password},
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.jwt_token = data["access_token"]
            st.session_state.user_info = {
                "user_id": data["user_id"],
                "username": data["username"],
            }
            st.session_state.role = "user"  # Mark user as logged in.
            st.success("Login successful!")
            st.session_state.page = "bible_ai"  # Route to main app page.
            st.write(f"Logged in as: {data['username']}")
            try:
                st.experimental_rerun()
            except AttributeError:
                st.query_params.from_dict({"page": "bible_ai"})
                st.stop()
        else:
            try:
                error_msg = resp.json().get("error", "Login failed.")
            except Exception:
                error_msg = "Login failed."
            st.error(error_msg)


def register_page():
    st.header("Register")
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    if st.button("Register"):
        resp = requests.post(
            f"{BASE_URL}/register",
            json={"username": reg_username, "password": reg_password},
        )
        if resp.status_code == 201:
            st.success("Registration successful! Please log in.")
            st.session_state.page = "login"  # Route to login page after registration.
            try:
                st.experimental_rerun()
            except AttributeError:
                st.query_params.from_dict({"page": "login"})
                st.stop()
        else:
            try:
                error_msg = resp.json().get("error", "Registration failed.")
            except Exception:
                error_msg = "Registration failed."
            st.error(error_msg)


def bible_ai_page():
    st.header("Bible AI Q/A")
    st.write("Logged in as:", st.session_state.user_info["username"])
    response_type = st.radio("Response type:", ("Text", "Voice"), key="response_type")
    question = st.text_input("Enter your question:", key="bible_ai_question")
    if st.button("Ask"):
        if question:
            with st.spinner("Thinking..."):
                payload = {"question": question, "response_type": response_type.lower()}
                response = requests.post(f"{BASE_URL}/ask", json=payload)
                if response.status_code == 200:
                    if response_type.lower() == "voice":
                        st.audio(response.content, format="audio/mp3")
                    else:
                        answer = response.json().get("answer", "No answer found.")
                        st.success(f"Answer: {answer}")
                else:
                    st.error("Failed to get a response. Check if backend is running.")
        else:
            st.warning("Please enter a question.")


def chat_page():
    st.header("Real-Time Bible Chat")
    if st.session_state.user_info:
        st.write("Logged in as:", st.session_state.user_info.get("username"))
    else:
        st.write("Chatting as Guest (chats are temporary).")
    chat_input = st.text_input("Enter your message:", key="chat_input")
    recipient_input = st.text_input("Send to (leave blank for public):", key="recipient_input")
    if st.button("Send Message"):
        payload = {
            "message": st.session_state.chat_input,
            "username": st.session_state.user_info.get("username", "Guest"),
        }
        if st.session_state.user_info:
            payload["user_id"] = st.session_state.user_info.get("user_id")
        if recipient_input.strip():
            payload["recipient"] = recipient_input.strip()
        if sio.connected:
            sio.emit("chat", payload)
        else:
            st.error("Not connected to chat server yet.")
    st.subheader("Chat History")
    for msg in st.session_state.chat_messages:
        st.write(msg)
    st.subheader("Notifications")
    for notif in st.session_state.sent_notifications:
        st.write(notif)


# --- Define Navigation using st.navigation and st.Page ---
login_pg = st.Page(login_page, title="Login", icon="🔑", default=(st.session_state.page in ["auth", "login"]))
register_pg = st.Page(register_page, title="Register", icon="📝", default=(st.session_state.page == "register"))
bible_ai_pg = st.Page(bible_ai_page, title="Bible AI", icon="📖", default=(st.session_state.page == "bible_ai"))
chat_pg = st.Page(chat_page, title="Chat", icon="💬", default=(st.session_state.page == "chat"))

if st.session_state.role is None:
    pages = {"Authentication": [login_pg, register_pg]}
else:
    pages = {"Main": [bible_ai_pg, chat_pg]}

nav = st.navigation(pages)
nav.run()
