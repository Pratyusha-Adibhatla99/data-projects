from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, sys, subprocess, traceback, time, re, threading, atexit

sys.path.insert(0, os.path.dirname(__file__))
from mat_processor import WirelessDataProcessor
from csv_processor import CSVProcessor

app = Flask(__name__, static_folder='../frontend')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# ─── paths ──────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR     = os.path.join(PROJECT_ROOT, 'channels_release')
UPLOAD_DIR   = os.path.join(PROJECT_ROOT, 'uploads')
ALLOWED_EXTENSIONS = {'mat', 'csv'}
NOTEBOOK_PORT = 8888

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ─── Jupyter state ──────────────────────────────────────────
_nb_proc  = None   # subprocess.Popen | None
_nb_token = None   # extracted token string | None

def _is_nb_running():
    return _nb_proc is not None and _nb_proc.poll() is None

def _extract_token(text):
    m = re.search(r'token=([a-f0-9]+)', text)
    return m.group(1) if m else None

def _kill_notebook():
    global _nb_proc
    if _nb_proc and _nb_proc.poll() is None:
        _nb_proc.terminate()
        try:
            _nb_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _nb_proc.kill()
        _nb_proc = None

atexit.register(_kill_notebook)

# ─── helpers ────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def get_all_filenames():
    s = set()
    if os.path.exists(DATA_DIR):
        s.update(f for f in os.listdir(DATA_DIR)   if f.endswith(('.mat','.csv')))
    if os.path.exists(UPLOAD_DIR):
        s.update(f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.mat','.csv')))
    return s

# ════════════════════════════════════════════════════════════
# EXISTING ROUTES (files / stats / upload / delete / analyze)
# ════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/files')
def list_files():
    try:
        data_files   = [f for f in os.listdir(DATA_DIR)   if f.endswith(('.mat','.csv'))] if os.path.exists(DATA_DIR)   else []
        upload_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.mat','.csv'))] if os.path.exists(UPLOAD_DIR) else []
        file_list = []
        for fname in sorted(data_files):
            ext = get_file_type(fname)
            ftype = 'csv' if ext=='csv' else ('channels' if 'channels' in fname else ('timestamps' if 'timestamps' in fname else 'mat'))
            file_list.append({'name':fname,'size':os.path.getsize(os.path.join(DATA_DIR,fname)),
                              'type':ftype,'extension':ext,'source':'original','can_delete':False})
        for fname in sorted(upload_files):
            ext = get_file_type(fname)
            ftype = 'csv' if ext=='csv' else ('channels' if 'channels' in fname else ('timestamps' if 'timestamps' in fname else 'mat'))
            file_list.append({'name':fname,'size':os.path.getsize(os.path.join(UPLOAD_DIR,fname)),
                              'type':ftype,'extension':ext,'source':'uploaded','can_delete':True})
        return jsonify({'success':True,'files':file_list,'count':len(file_list)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success':False,'error':str(e)})

@app.route('/api/stats')
def get_stats():
    try:
        data_files   = [f for f in os.listdir(DATA_DIR)   if f.endswith(('.mat','.csv'))] if os.path.exists(DATA_DIR)   else []
        upload_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.mat','.csv'))] if os.path.exists(UPLOAD_DIR) else []
        all_files = data_files + upload_files
        total_size = sum(os.path.getsize(os.path.join(DATA_DIR,f)) for f in data_files) + \
                     sum(os.path.getsize(os.path.join(UPLOAD_DIR,f)) for f in upload_files)
        return jsonify({'success':True,'stats':{
            'total_files':len(all_files),
            'channels_files':len([f for f in all_files if 'channels' in f]),
            'timestamps_files':len([f for f in all_files if 'timestamps' in f]),
            'csv_files':len([f for f in all_files if f.endswith('.csv')]),
            'total_size_mb':total_size/(1024*1024),
            'uploaded_files':len(upload_files)
        }})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success':False,'error':str(e)})

@app.route('/api/upload', methods=['POST','OPTIONS'])
def upload_file():
    if request.method=='OPTIONS': return '',204
    try:
        if 'file' not in request.files:
            return jsonify({'success':False,'error':'No file provided'}),400
        file = request.files['file']
        if file.filename=='':
            return jsonify({'success':False,'error':'No file selected'}),400
        if not allowed_file(file.filename):
            return jsonify({'success':False,'error':'Only .mat and .csv files are allowed'}),400
        filename = secure_filename(file.filename)
        if filename in get_all_filenames():
            return jsonify({'success':False,'error':f'"{filename}" already exists.'}),400
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        size = os.path.getsize(filepath)
        print(f"✅ Uploaded: {filename} ({size} bytes)")
        return jsonify({'success':True,'message':'File uploaded successfully','filename':filename,'size':size})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success':False,'error':str(e)}),500

@app.route('/api/delete/<filename>', methods=['DELETE','OPTIONS'])
def delete_file(filename):
    if request.method=='OPTIONS': return '',204
    try:
        fp = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(fp):
            return jsonify({'success':False,'error':'File not found in uploads'}),404
        os.remove(fp)
        print(f"🗑️  Deleted: {filename}")
        return jsonify({'success':True,'message':f'"{filename}" deleted'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success':False,'error':str(e)}),500

@app.route('/api/analyze/<filename>')
def analyze_file(filename):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'success':False,'error':'File not found'})
        ext = get_file_type(filename)
        if ext=='csv':
            return jsonify({'success':True,'metadata':CSVProcessor(filepath).extract_metadata()})
        # MAT
        processor = WirelessDataProcessor(filepath)
        data = processor.read_file()
        metadata = {'filename':filename,'file_size':os.path.getsize(filepath),'file_type':'MAT','variables':{}}
        for vname, vdata in data.items():
            info = {'shape':list(vdata.shape),'dtype':str(vdata.dtype),'size':int(vdata.size),'ndim':int(vdata.ndim)}
            if vdata.dtype.kind in ['i','f']:
                info.update({'min':float(vdata.min()),'max':float(vdata.max()),'mean':float(vdata.mean())})
            metadata['variables'][vname] = info
        return jsonify({'success':True,'metadata':metadata})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success':False,'error':str(e)})
# JUPYTER NOTEBOOK  — launch / status / stop


@app.route('/api/notebook/launch', methods=['POST'])
def launch_notebook():
    global _nb_proc, _nb_token

    # ── already running? ──
    if _is_nb_running():
        return jsonify({'success':True,'status':'running',
                        'url': f'http://localhost:{NOTEBOOK_PORT}/?token={_nb_token}' if _nb_token else None,
                        'token':_nb_token})

    cmd = [
        sys.executable, '-m', 'jupyter', 'notebook',
        '--port', str(NOTEBOOK_PORT),
        '--notebook-dir', PROJECT_ROOT,
        '--no-browser',
        '--ip', '0.0.0.0',
        '--log-level', 'INFO'
    ]
    print(f"🚀 Launching Jupyter… {' '.join(cmd)}")

    try:
        _nb_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, cwd=PROJECT_ROOT)
    except FileNotFoundError:
        _nb_proc = None
        return jsonify({'success':False,
                        'error':'jupyter not installed. Run:  conda activate wireless_env && pip install notebook'}), 500

    # ── wait up to 8s for the token line ──
    _nb_token = None
    deadline  = time.time() + 8
    while time.time() < deadline:
        line = _nb_proc.stdout.readline()
        if not line:   # process died
            break
        print(f"  [jupyter] {line.rstrip()}")
        tok = _extract_token(line)
        if tok:
            _nb_token = tok
            print(f"✅ Jupyter ready — token extracted")
            break

    # ── daemon thread keeps draining stdout (and catches late token) ──
    def _drain():
        global _nb_token
        try:
            for line in _nb_proc.stdout:
                print(f"  [jupyter] {line.rstrip()}")
                if _nb_token is None:
                    t = _extract_token(line)
                    if t:
                        _nb_token = t
                        print(f"✅ Jupyter token (delayed): {t}")
        except Exception:
            pass

    threading.Thread(target=_drain, daemon=True).start()

    if _nb_token:
        return jsonify({'success':True,'status':'running',
                        'url':f'http://localhost:{NOTEBOOK_PORT}/?token={_nb_token}','token':_nb_token})
    # still starting — frontend will poll status
    return jsonify({'success':True,'status':'starting','url':None,'token':None,
                    'message':'Jupyter is starting… check status shortly.'})

@app.route('/api/notebook/status')
def notebook_status():
    if _is_nb_running():
        return jsonify({'success':True,'status':'running',
                        'url':f'http://localhost:{NOTEBOOK_PORT}/?token={_nb_token}' if _nb_token else None,
                        'token':_nb_token})
    return jsonify({'success':True,'status':'stopped','url':None,'token':None})

@app.route('/api/notebook/stop', methods=['DELETE'])
def stop_notebook():
    global _nb_proc, _nb_token
    if _nb_proc and _nb_proc.poll() is None:
        _nb_proc.terminate()
        try:
            _nb_proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            _nb_proc.kill()
        print("🛑 Jupyter stopped.")
    _nb_proc  = None
    _nb_token = None
    return jsonify({'success':True,'status':'stopped'})

# ════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Wireless Data Platform")
    print("=" * 60)
    print(f"📁 Data:      {DATA_DIR}")
    print(f"📤 Uploads:   {UPLOAD_DIR}")
    print(f"🌐 Browser:   http://localhost:5001")
    print(f"📓 Notebook:  http://localhost:{NOTEBOOK_PORT}  (launch via UI)")
    print(f"📂 Formats:   .mat  .csv")
    print(f"📦 Max size:  500 MB")
    print(f"🔒 Dupes:     blocked")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5001)