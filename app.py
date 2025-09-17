from flask import Flask
import threading
from bot import main  # On importe la fonction main() de bot.py

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

def run_bot():
    main()  # Lance ton bot

if __name__ == "__main__":
    # On lance ton bot dans un thread séparé
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
