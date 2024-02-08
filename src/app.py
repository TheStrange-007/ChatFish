from flask import Flask, render_template, redirect, request, session, url_for
import os
from flask_socketio import SocketIO, send
from dotenv import load_dotenv
from hugchat import hugchat
from hugchat.login import Login

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app)

# Log in to Hugging Face and obtain authorization
def login_to_hugging_face():
    email = os.getenv('EMAIL')
    passwd = os.getenv('PASSWD')
    sign = Login(email, passwd)
    cookies = sign.login()
    return cookies

# Initialize the Hugging Face Chatbot
cookies = login_to_hugging_face()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

@socketio.on('message')
def process(msg):
    reply = chatbot.query(msg)
    print(reply)
    send(reply.text)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session["name"] = request.form["username"]
        return redirect(url_for("main"))

    return render_template("login.html")

@app.route('/', methods=['GET', 'POST'])
def main():
    # login and chatapp loading
    if not session.get("name"):
        return redirect(url_for("login"))
    else:
        return render_template("index.html", name=session.get("name"))

if __name__ == '__main__':
    socketio.run(app)
