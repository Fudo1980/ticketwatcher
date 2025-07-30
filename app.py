from flask import Flask, request, render_template
import threading
import time
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def send_email(to_email, subject, body):
    from_email = "jens.rudig@gmail.com"          # ⬅️ deine Gmail-Adresse hier eintragen
    password = "uney dxei bxwb vcpy"                # ⬅️ dein 16-stelliger App-Code von Google

    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    html_part = MIMEText(body, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("📧 E-Mail gesendet an", to_email)
    except Exception as e:
        print("❌ E-Mail-Fehler:", e)

def monitor(url, search_text, interval, duration, email, phone):
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            response = requests.get(url, timeout=10)
            content = response.text

            if search_text.lower() in content.lower():
                print(f"✅ Text gefunden: '{search_text}' auf {url}")
                if email:
                    send_email(
                        email,
                        "✅ Ticket gefunden!",
                        f"""
                        <html>
                        <body>
                        <p>Der Text <strong>{search_text}</strong> wurde auf der Seite gefunden.</p>
                        <p><a href="{url}" target="_blank">➡️ Hier zur überwachten Seite</a></p>
                        </body>
                        </html>
                        """
                    )
                break
            else:
                print(f"❌ Noch nicht gefunden: '{search_text}'")
        except Exception as e:
            print(f"⚠️ Fehler beim Abruf: {e}")

        time.sleep(interval)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_monitoring():
    url = request.form['url']
    search_text = request.form['search_text']
    interval = int(request.form['interval'])
    duration = int(request.form['duration']) * 24 * 60 * 60  # Tage → Sekunden
    email = request.form.get('email')
    phone = request.form.get('phone')

    thread = threading.Thread(target=monitor, args=(url, search_text, interval, duration, email, phone))
    thread.start()

    return f"Überwachung gestartet für: {url}<br><a href='/'>Zurück</a>"

if __name__ == '__main__':
    app.run(debug=True)
