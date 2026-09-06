"""Preview with Markdown watching and local-only browser reload."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit
from threading import Event, RLock, Thread
import argparse
import io
import json
import os
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '/Mijinmo_Portfolio/'

class Preview:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.lock = RLock()
        self.version = uuid.uuid4().hex
        self.error = ''
        self.stop = Event()
        self.ready = Event()

    def snapshot(self):
        files = []
        for directory, pattern in [('content', '*.md'), ('site', '*.py'), ('scripts', '*.py'), ('assets/css', '*.css'), ('assets/js', '*.js')]:
            for path in (self.root / directory).rglob(pattern):
                if 'vendor' not in path.parts:
                    try:
                        stat = path.stat()
                        files.append((str(path), stat.st_mtime_ns, stat.st_size))
                    except FileNotFoundError:
                        pass
        return tuple(sorted(files))

    def rebuild(self):
        with self.lock:
            result = subprocess.run([sys.executable, str(self.root / 'scripts/build.py')], cwd=self.root,
                                    capture_output=True, text=True, encoding='utf-8', errors='replace',
                                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            if result.returncode:
                self.error = (result.stderr or result.stdout)[-6000:]
                print('Preview build failed; keeping the last successful pages.\n' + self.error, flush=True)
                return False
            self.error = ''
            self.version = uuid.uuid4().hex
            print('Preview updated.', flush=True)
            return True

    def watch(self):
        previous = self.snapshot()
        self.ready.set()
        while not self.stop.wait(.3):
            current = self.snapshot()
            if current != previous:
                while not self.stop.wait(.3):
                    latest = self.snapshot()
                    if latest == current:
                        break
                    current = latest
                if self.stop.is_set():
                    return
                self.rebuild()
                previous = current

    def state(self):
        with self.lock:
            return {'version': self.version, 'error': self.error}

def handler_for(preview):
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def translate_path(self, path):
            path = unquote(urlsplit(path).path)
            path = path[len(PREFIX):] if path.startswith(PREFIX) else path.lstrip('/')
            target = (preview.root / path).resolve()
            if not target.is_relative_to(preview.root) or any(part.startswith('.') for part in target.relative_to(preview.root).parts):
                return str(preview.root / '__not_found__')
            return str(target)

        def send_bytes(self, body, content_type):
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            return io.BytesIO(body)

        def send_head(self):
            if urlsplit(self.path).path in ('/__preview/status', PREFIX + '__preview/status'):
                return self.send_bytes(json.dumps(preview.state()).encode('utf-8'), 'application/json')
            path = Path(self.translate_path(self.path))
            if path.is_dir():
                path = path / 'index.html'
            if path.is_file() and path.suffix == '.html':
                with preview.lock:
                    html = path.read_text(encoding='utf-8')
                    version = json.dumps(preview.version)
                script = r'''<script data-local-preview>
(() => {
  const version = VERSION;
  let pending = false;
  setInterval(async () => {
    if (pending) return;
    pending = true;
    try {
      const response = await fetch('/__preview/status', {cache: 'no-store'});
      if (!response.ok) return;
      const state = await response.json();
      let box = document.getElementById('local-preview-error');
      if (state.error) {
        if (!box) {
          box = document.createElement('pre');
          box.id = 'local-preview-error'; box.setAttribute('role', 'alert');
          box.style.cssText = 'position:fixed;bottom:0;left:0;right:0;max-height:40vh;overflow:auto;z-index:20000;background:#fff4ef;color:#702010;padding:20px;margin:0;white-space:pre-wrap;font:13px/1.5 monospace';
          document.body.appendChild(box);
        }
        box.textContent = '预览更新失败 / Preview update failed\n' + state.error;
      } else if (state.version !== version) {
        location.reload();
      } else if (box) box.remove();
    } catch (_) { /* Keep the current page while the server restarts. */ }
    finally { pending = false; }
  }, 750);
})();
</script>'''.replace('VERSION', version)
                html = html.replace('</body>', script + '</body>')
                return self.send_bytes(html.encode('utf-8'), 'text/html; charset=utf-8')
            return super().send_head()

        def log_message(self, fmt, *args):
            if '__preview/status' not in self.path:
                super().log_message(fmt, *args)
    return Handler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=4173)
    args = parser.parse_args()
    preview = Preview()
    preview.rebuild()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(preview))
    watcher = Thread(target=preview.watch, daemon=True)
    watcher.start()
    print(f'Preview: http://127.0.0.1:{args.port}{PREFIX} (Markdown auto-reload enabled)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        preview.stop.set()
        server.server_close()
        watcher.join(timeout=2)

if __name__ == '__main__':
    main()
