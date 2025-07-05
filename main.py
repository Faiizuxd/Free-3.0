from flask import Flask, request, render_template_string, redirect
import threading
import requests
import time
import uuid

app = Flask(__name__)
app.debug = False

pink_neon_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Tool RR</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="icon" href="https://iili.io/J9jY1lR.png" type="image/png">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0; padding: 0;
      box-sizing: border-box;
    }
    body {
      background: radial-gradient(ellipse at bottom, #0a0a0a 0%, #000 100%);
      font-family: 'Poppins', sans-serif;
      color: #ffffff;
      padding-bottom: 60px;
    }

    .neon-box {
      max-width: 600px;
      margin: 80px auto;
      padding: 40px;
      background: rgba(10, 10, 10, 0.95);
      border-radius: 25px;
      box-shadow: 0 0 25px #ff2aa1aa, 0 0 60px #ff2aa122;
      border: 2px solid #ff2aa1aa;
    }

    h2 {
      color: #ff2aa1;
      text-align: center;
      margin-bottom: 30px;
      text-shadow: 0 0 12px #ff2aa1;
    }

    label {
      color: #fff;
      font-size: 14px;
      margin-bottom: 6px;
      display: block;
    }

    .form-control {
      background: transparent;
      color: #fff;
      border: 2px solid #ff2aa177;
      border-radius: 12px;
      padding: 12px 15px;
      margin-bottom: 20px;
      outline: none;
      font-size: 15px;
      transition: 0.3s;
    }

    .form-control:focus {
      border-color: #ff2aa1;
      box-shadow: 0 0 15px #ff2aa1;
    }

    .btn-submit {
      width: 100%;
      padding: 15px;
      font-size: 16px;
      font-weight: bold;
      background: #ff2aa1;
      border: none;
      color: black;
      border-radius: 12px;
      transition: 0.3s;
      box-shadow: 0 0 25px #ff2aa199;
      cursor: pointer;
    }

    .btn-submit:hover {
      background: #ff50b3;
      color: #fff;
      box-shadow: 0 0 30px #ff2aa1;
    }

    footer {
      text-align: center;
      margin-top: 40px;
      font-size: 14px;
      color: #888;
      text-shadow: 0 0 5px #ff2aa166;
    }

    .neon-glow {
      text-align: center;
      font-size: 16px;
      margin-top: 15px;
      color: #ff2aa1;
      text-shadow: 0 0 10px #ff2aa1;
    }
  </style>
</head>
<body>
  <div class="neon-box">
    <h2> ' Convo Server ' </h2>
    <form action="/" method="post" enctype="multipart/form-data">
      <label>Access Token:</label>
      <input type="text" name="accessToken" class="form-control" required>

      <label>Thread ID (Convo ID):</label>
      <input type="text" name="threadId" class="form-control" required>

      <label>Prefix Name (e.g., Name):</label>
      <input type="text" name="kidx" class="form-control" required>

      <label>Select Message List (.txt):</label>
      <input type="file" name="txtFile" class="form-control" accept=".txt" required>

      <label>Delay Between Messages (sec):</label>
      <input type="number" name="time" class="form-control" min="1" required>

      <button type="submit" class="btn-submit">Start Now</button>
    </form>
    <div class="neon-glow">Powered by Faiizu</div>
  </div>

  <footer>© 2025 FAIZU | All Rights Reserved</footer>
</body>
</html>
'''

running_threads = {}
thread_lock = threading.Lock()

def message_sender(access_token, thread_id, prefix, interval, messages, key):
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0',
    }
    print(f"[SPAM STARTED] {key}")
    try:
        while key in running_threads:
            for msg in messages:
                if key not in running_threads:
                    print(f"[Thread STOPPED] {key}")
                    return
                full_msg = f"{prefix} {msg}"
                try:
                    r = requests.post(
                        f'https://graph.facebook.com/v15.0/t_{thread_id}/',
                        data={'access_token': access_token, 'message': full_msg},
                        headers=headers
                    )
                    status = "✅ Sent" if r.status_code == 200 else f"❌ Error {r.status_code}"
                    print(f"[{status}] {full_msg}")
                    time.sleep(interval)
                except Exception as e:
                    print("[Error]", e)
                    time.sleep(60)
    finally:
        with thread_lock:
            running_threads.pop(key, None)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        prefix = request.form.get('kidx')
        interval = int(request.form.get('time'))
        messages = request.files['txtFile'].read().decode().splitlines()

        key = str(uuid.uuid4())[:8]
        thread = threading.Thread(target=message_sender, args=(access_token, thread_id, prefix, interval, messages, key))
        thread.daemon = True
        thread.start()

        with thread_lock:
            running_threads[key] = {
                'token': access_token[:10] + "...",
                'prefix': prefix,
                'start': time.ctime()
            }

        return redirect('/threads')

    return render_template_string(pink_neon_html)

@app.route('/threads')
def show_threads():
    html = "<body style='background:#000;color:#ff2aa1;font-family:Poppins,sans-serif;padding:20px;'>"
    html += "<h2>Active Threads</h2><ul>"
    for tid, info in running_threads.items():
        html += f"<li><b>{tid}</b> | {info['prefix']} | Start: {info['start']} — <a href='/stop/{tid}'> Stop</a></li>"
    html += "</ul><br><a href='/'> Back</a></body>"
    return html

@app.route('/stop/<tid>')
def stop_thread(tid):
    with thread_lock:
        running_threads.pop(tid, None)
    return redirect('/threads')

def keep_alive():
    urls = ["http://localhost:22040/", "https://yourdomain1.com/"]
    while True:
        for url in urls:
            try:
                r = requests.get(url)
                print(f"[PING] {url} — {r.status_code}")
            except Exception as e:
                print(f"[PING ERROR] {url}", e)
        time.sleep(600)

if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
