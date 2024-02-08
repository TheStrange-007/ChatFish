import os
import pickle
from flask import Flask, render_template, redirect, request, session, url_for
from flask_socketio import SocketIO, send
from dotenv import load_dotenv
from hugchat import hugchat
from hugchat.login import Login

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Directory to store user conversations and cookies
DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# Log in to Hugging Face and obtain authorization
def login_to_hugging_face():
    email = os.getenv("EMAIL")
    passwd = os.getenv("PASSWD")
    sign = Login(email, passwd)
    cookies = sign.login()
    return cookies


# Load or save cookies
def load_or_save_cookies():
    cookies_file = os.path.join(DATA_DIR, "cookies.pkl")
    try:
        with open(cookies_file, "rb") as f:
            cookies = pickle.load(f)

    except (FileNotFoundError, Exception):
        cookies = login_to_hugging_face()
        with open(cookies_file, "wb") as f:
            pickle.dump(cookies, f)
    return cookies


# Initialize the Hugging Face Chatbot
cookies = load_or_save_cookies()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())


# Function to load or create a conversation for a user
def load_or_create_conversation(user_id):
    conversation_file = os.path.join(DATA_DIR, f"{user_id}_conversation.pkl")
    if os.path.exists(conversation_file):
        with open(conversation_file, "rb") as f:
            conversation = pickle.load(f)
    else:
        conversation = chatbot.new_conversation()
        with open(conversation_file, "wb") as f:
            pickle.dump(conversation, f)
    return conversation


@socketio.on("message")
def process(msg):
    user_id = session.get("user_id")
    conversation = load_or_create_conversation(user_id)
    reply = chatbot.query(msg, conversation=conversation)

    reply = chatbot.query(msg, conversation=conversation)

    send(str(reply))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = request.form["username"]
        session.permanent = True
        return redirect(url_for("main"))

    return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
def main():
    # login and chatapp loading
    if not session.get("user_id"):
        return redirect(url_for("login"))
    else:
        return render_template("index.html", name=session.get("user_id"))


if __name__ == "__main__":
    socketio.run(app)
