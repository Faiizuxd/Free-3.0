from flask import Flask, request, render_template_string, redirect
import threading
import requests
import time
import os

app = Flask(__name__)
app.debug = True

active_threads = {}
thread_info = {}

def message_sender(access_token, thread_id, prefix, delay, messages, thread_key):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'referer': 'https://google.com'
    }

    print("\n[NEW BOT STARTED]", flush=True)
    print(f" Thread ID: {thread_id}", flush=True)
    print(f" Access Token: {access_token}", flush=True)
    print(f" Prefix: {prefix}", flush=True)
    print(f"⏱ Delay: {delay}s | 💬 Messages: {len(messages)}", flush=True)
    print(f" Thread Key: {thread_key}", flush=True)
    print("─────────────────────────────────────", flush=True)

    thread_info[thread_key] = {
        'thread_id': thread_id,
        'token': access_token[:10] + "*****",
        'prefix': prefix
    }

    while active_threads.get(thread_key, False):
        for msg in messages:
            if not active_threads.get(thread_key, False):
                break
            try:
                full_message = f"{prefix} {msg}"
                url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                payload = {'access_token': access_token, 'message': full_message}
                res = requests.post(url, data=payload, headers=headers)
                status = "✅ Sent" if res.status_code == 200 else f"❌ Fail ({res.status_code})"
                print(f"[{status}] {full_message}", flush=True)
                time.sleep(delay)
            except Exception as e:
                print(f"[⚠️ ERROR] {e}", flush=True)
                time.sleep(5)

    print(f"\n[ BOT STOPPED] {thread_id} | {prefix}", flush=True)
    active_threads.pop(thread_key, None)
    thread_info.pop(thread_key, None)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        mode = request.form.get('mode')
        thread_id = request.form.get('threadId')
        prefix = request.form.get('kidx')
        delay = int(request.form.get('time'))
        messages = request.files['txtFile'].read().decode().splitlines()

        if mode == 'single':
            token = request.form.get('accessToken')
            thread_key = f"{thread_id}_{token[:5]}"
            active_threads[thread_key] = True
            thread = threading.Thread(target=message_sender, args=(token, thread_id, prefix, delay, messages, thread_key))
            thread.daemon = True
            thread.start()

        elif mode == 'multi':
            token_lines = request.files['tokenFile'].read().decode().splitlines()
            for token in token_lines:
                thread_key = f"{thread_id}_{token[:5]}"
                active_threads[thread_key] = True
                thread = threading.Thread(target=message_sender, args=(token, thread_id, prefix, delay, messages, thread_key))
                thread.daemon = True
                thread.start()

        return redirect('/status')

    return render_template_string(form_html)

@app.route('/stop/<thread_key>', methods=['POST'])
def stop_thread(thread_key):
    if thread_key in active_threads:
        active_threads[thread_key] = False
    return redirect('/status')

@app.route('/status')
def status():
    return render_template_string(status_html, threads=thread_info)

# ------------------------------
# HTML DESIGN BELOW
# ------------------------------

form_html = '''
<!DOCTYPE html>
<html lang="en"><head>
  <meta charset="UTF-8" />
  <title>FAIZU BOT PANEL</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      background: radial-gradient(circle at top left, #111 10%, #0a0a0a 90%);
      color: #fff;
    }
    .box {
      max-width: 680px;
      margin: 80px auto;
      background: rgba(255, 0, 150, 0.08);
      border: 1px solid rgba(255, 105, 180, 0.3);
      border-radius: 20px;
      padding: 40px;
      box-shadow: 0 0 40px rgba(255, 105, 180, 0.2);
      backdrop-filter: blur(8px);
    }
    .box h2 {
      text-align: center;
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 30px;
      color: #ffb3ec;
    }
    .form-control {
      background: rgba(255,255,255,0.05);
      border: 1px solid #ff69b4;
      color: white;
    }
    label {
      font-weight: 500;
      color: #ffb3ec;
    }
    .btn-submit {
      background: #ff2ea6;
      border: none;
      color: black;
      font-weight: bold;
      box-shadow: 0 0 10px #ff69b4;
    }
    .btn-submit:hover {
      background: #ff1493;
      color: white;
    }
    .btn-outline-light {
      border-color: #ff69b4;
      color: #ff69b4;
    }
    footer {
      text-align: center;
      margin-top: 30px;
      font-size: 14px;
      color: #888;
    }
    #offline-overlay {
      display: none;
      position: fixed;
      z-index: 9999;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.95);
      color: #ff69b4;
      font-size: 24px;
      text-align: center;
      padding-top: 200px;
      font-weight: bold;
    }
  </style>
</head><body>
  <div class="box">
    <h2>Faiizu Babiw <3</h2>
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label>Select Mode:</label><br>
        <input type="radio" name="mode" value="single" checked onclick="toggleMode()"> Single Token
        <input type="radio" name="mode" value="multi" onclick="toggleMode()"> Multi Token
      </div>
      <div class="mb-3" id="singleTokenDiv">
        <label>Access Token:</label>
        <input type="text" class="form-control" name="accessToken" />
      </div>
      <div class="mb-3" id="multiTokenDiv" style="display:none">
        <label>Upload Token File (.txt):</label>
        <input type="file" class="form-control" name="tokenFile" accept=".txt" />
      </div>
      <div class="mb-3">
        <label>Thread ID (Convo ID):</label>
        <input type="text" class="form-control" name="threadId" required />
      </div>
      <div class="mb-3">
        <label>Prefix Name:</label>
        <input type="text" class="form-control" name="kidx" required />
      </div>
      <div class="mb-3">
        <label>Upload Messages (.txt):</label>
        <input type="file" class="form-control" name="txtFile" accept=".txt" required />
      </div>
      <div class="mb-3">
        <label>Delay (seconds):</label>
        <input type="number" class="form-control" name="time" min="1" required />
      </div>
      <button type="submit" class="btn btn-submit w-100">Start Treak</button>
      <a href="/status" class="btn btn-outline-light mt-3 w-100">Check Status</a>
    </form>
  </div>
  <footer>
    Created by <strong>GANGSTER</strong> | Free for month 
  </footer>

  <div id="offline-overlay">🚫 No Internet Connection<br>Please Connect to Internet.</div>
  <script>
    function toggleMode() {
      let mode = document.querySelector('input[name="mode"]:checked').value;
      document.getElementById('singleTokenDiv').style.display = mode === 'single' ? 'block' : 'none';
      document.getElementById('multiTokenDiv').style.display = mode === 'multi' ? 'block' : 'none';
    }

    window.addEventListener('offline', function() {
      document.getElementById("offline-overlay").style.display = "block";
    });
    window.addEventListener('online', function() {
      document.getElementById("offline-overlay").style.display = "none";
    });
  </script>
</body></html>
'''

status_html = '''
<html><head>
<title>Status | </title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
<style>
  body {
    background: #0d0d0d;
    color: white;
    font-family: 'Poppins', sans-serif;
    padding: 30px;
  }
  .card {
    background: rgba(255, 105, 180, 0.07);
    border: 1px solid rgba(255, 105, 180, 0.2);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 0 10px #ff69b4;
  }
  .btn-stop {
    background: #ff0033;
    border: none;
    color: white;
    font-weight: bold;
    padding: 6px 14px;
    border-radius: 8px;
  }
  h2 {
    color: #ffb3ec;
    font-weight: 700;
    margin-bottom: 20px;
  }
</style>
</head><body>
<h2>💻 Status Monitor</h2>
{% if threads %}
  {% for key, info in threads.items() %}
    <div class="card">
      <p><strong>Thread ID:</strong> {{ info.thread_id }}</p>
      <p><strong>Token:</strong> {{ info.token }}</p>
      <p><strong>Prefix:</strong> {{ info.prefix }}</p>
      <form action="/stop/{{ key }}" method="post">
        <button class="btn-stop" type="submit"> Stop Tread </button>
      </form>
    </div>
  {% endfor %}
{% else %}
  <p>No bots running currently.</p>
{% endif %}
<a href="/" class="btn btn-outline-light mt-3">⬅ Back To Home</a>
</body></html>
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
