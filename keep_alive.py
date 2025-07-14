from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает!"

def keep_alive():
    from threading import Thread
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080}).start()
