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
    return sign.login()


# Load or save cookies
def load_or_save_cookies():
    cookies_file = os.path.join(DATA_DIR, "cookies.pkl")
    try:
        with open(cookies_file, "rb") as f:
            cookies = pickle.load(f)
    except FileNotFoundError:
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
    try:
        with open(conversation_file, "rb") as f:
            conversation = pickle.load(f)
    except FileNotFoundError:
        conversation = chatbot.new_conversation()
        save_conversation(conversation_file, conversation)
    else:
        # Check if the conversation ID exists in the conversation list
        conversation_list = chatbot.get_conversation_list()
        if conversation.id not in [conv.id for conv in conversation_list]:
            conversation = chatbot.new_conversation()
            save_conversation(conversation_file, conversation)
    return conversation


# Function to save conversation to file
def save_conversation(file_path, conversation):
    with open(file_path, "wb") as f:
        pickle.dump(conversation, f)


@socketio.on("message")
def process(msg):
    user_id = session.get("user_id")
    conversation = load_or_create_conversation(user_id)
    reply = chatbot.chat(msg, conversation=conversation).wait_until_done()
    send(reply)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = request.form["username"]
        session.permanent = True
        return redirect(url_for("main"))
    return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
def main():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    else:
        return render_template("index.html", name=session.get("user_id"))


if __name__ == "__main__":
    socketio.run(app)
