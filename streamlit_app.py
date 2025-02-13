import streamlit as st
import requests
import socketio
import threading
import time

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"  # Your backend URL

# --- Initialize Session State ---
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "socketio_connected" not in st.session_state:
    st.session_state.socketio_connected = False
if "sent_notifications" not in st.session_state:
    st.session_state.sent_notifications = []

# --- Sidebar Authentication ---
auth_option = st.sidebar.radio("Authentication", ["Register", "Login", "Continue as Guest"])
if auth_option == "Register":
    st.sidebar.subheader("Register")
    reg_username = st.sidebar.text_input("Username", key="reg_username")
    reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
    if st.sidebar.button("Register"):
        resp = requests.post(f"{BASE_URL}/register", json={"username": reg_username, "password": reg_password})
        if resp.status_code == 201:
            st.sidebar.success("Registration successful! Please log in.")
        else:
            st.sidebar.error(resp.json().get("error", "Registration failed."))
elif auth_option == "Login":
    st.sidebar.subheader("Login")
    login_username = st.sidebar.text_input("Username", key="login_username")
    login_password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Login"):
        resp = requests.post(f"{BASE_URL}/login", json={"username": login_username, "password": login_password})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.jwt_token = data["access_token"]
            st.session_state.user_info = {"user_id": data["user_id"], "username": data["username"]}
            st.sidebar.success("Login successful!")
        else:
            st.sidebar.error(resp.json().get("error", "Login failed."))
else:
    st.sidebar.write("Continuing as Guest.")

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
    st.session_state.chat_messages.append(f"{data['timestamp']} - {data.get('user_id', 'Guest')}: {data['message']}")
    st.experimental_rerun()


@sio.on("sent")
def on_sent(data):
    st.session_state.sent_notifications.append(data["msg"])
    st.experimental_rerun()


def start_socketio(token):
    # # Construct the connection URL with the token.
    # url = f"{BASE_URL}?token={token}"
    # st.write("Connecting to:", url)  # For debugging; remove in production.
    # try:
    #     # Explicitly connect on the default namespace.
    #     sio.connect(url, namespaces=["/"])
    #     sio.wait()
    # except Exception as e:
    #     st.write("SocketIO connection error:", e)

    url = f"{BASE_URL}?token={token}"
    st.write("Connecting to:", url)  # For debugging; remove in production.
    try:
        sio.connect(url, namespaces=["/"])
        # Wait briefly to ensure connection is established.
        time.sleep(2)
        st.write("SocketIO connected:", sio.connected)
    except Exception as e:
        st.write("SocketIO connection error:", e)


# Only start SocketIO if a valid token exists and no connection has been made.
if st.session_state.get("jwt_token") and not st.session_state.get("socketio_connected"):
    token = st.session_state.jwt_token  # JWT token generated on login
    threading.Thread(target=start_socketio, args=(token,), daemon=True).start()
    st.session_state.socketio_connected = True

# --- Main Chat Interface ---
st.title("Real-Time Bible Chat")
if st.session_state.user_info:
    st.write("Logged in as:", st.session_state.user_info.get("username"))
else:
    st.write("Chatting as Guest (chats are temporary).")

chat_input = st.text_input("Enter your message:", key="chat_input")
recipient_input = st.text_input("Send to (leave blank for public):", key="recipient_input")
if st.button("Send"):
    payload = {
        "message": st.session_state.chat_input,
        "username": st.session_state.user_info.get("username", "Guest")
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

# --- Bible AI Q/A Interface ---
st.title("📖 Ask the Bible AI")
st.write("Ask a question, and the AI will answer based on the Bible.")
response_type = st.radio("Select response type:", ("Text", "Voice"), index=0)
question = st.text_input("Enter your question:")
if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            payload = {
                "question": question,
                "response_type": response_type.lower()  # "text" or "voice"
            }
            response = requests.post(f"{BASE_URL}/ask", json=payload)
            if response.status_code == 200:
                if response_type.lower() == "voice":
                    st.audio(response.content, format="audio/mp3")
                else:
                    answer = response.json().get("answer", "No answer found.")
                    st.success(f"Answer: {answer}")
            else:
                st.error("Failed to get a response. Check if Flask is running.")
    else:
        st.warning("Please enter a question before clicking Ask.")
