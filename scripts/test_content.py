"""Integration checks use an isolated copy; user Markdown is never modified."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
import json
import re
import shutil
import struct
import subprocess
import sys
import time
import unittest

from prose import render, plain
from serve import Preview, handler_for

ROOT = Path(__file__).resolve().parents[1]

class ContentTests(unittest.TestCase):
    def test_markdown_and_bilingual_links(self):
        with TemporaryDirectory(prefix='portfolio-markdown-') as directory:
            root = Path(directory)
            for lang in ('zh', 'en'):
                path = root / 'content' / lang / 'sample.md'
                path.parent.mkdir(parents=True)
                path.write_text('## Heading\n\nFirst **bold** paragraph.\n\nSecond *italic* paragraph.\n\n- one\n- two\n\n> Note\n\n[About](about.html) [PDF](Files/test.pdf) [External](https://example.com)\n\n```python\nprint(1)\n```\n\n| A | B |\n|---|---|\n| 1 | 2 |', encoding='utf-8')
            html = render(root, 'en', 'sample')
            for expected in ('<h2>Heading</h2>', '<strong>bold</strong>', '<em>italic</em>', '<ul>', '<blockquote>', '<table>', 'language-python', 'href="about.html"', 'href="../Files/test.pdf"'):
                self.assertIn(expected, html)
            self.assertIn('href="Files/test.pdf"', render(root, 'zh', 'sample'))
            self.assertNotIn('<', plain(root, 'en', 'sample'))
            with self.assertRaisesRegex(ValueError, 'Missing Markdown'):
                render(root, 'zh', 'missing')
            with self.assertRaises(ValueError):
                render(root, 'zh', '../../outside')

    def test_watch_rebuild_failure_recovery_and_local_reload(self):
        with TemporaryDirectory(prefix='portfolio-preview-') as directory:
            root = Path(directory).resolve()
            for folder in ('content', 'site'):
                shutil.copytree(ROOT / folder, root / folder, ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'scripts').mkdir()
            for filename in ('build.py', 'prose.py'):
                shutil.copy2(ROOT / 'scripts' / filename, root / 'scripts' / filename)
            shutil.copytree(ROOT / 'scripts/vendor', root / 'scripts/vendor', ignore=shutil.ignore_patterns('__pycache__', 'bin'))
            # Layout-independent build test: only dimension headers are needed.
            (root / 'images').mkdir()
            png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 8 + struct.pack('>II', 640, 360)
            for image in (ROOT / 'images').iterdir():
                if image.is_file():
                    (root / 'images' / image.name).write_bytes(png)
            preview = Preview(root)
            self.assertTrue(preview.rebuild())
            watcher = Thread(target=preview.watch, daemon=True)
            watcher.start()
            self.assertTrue(preview.ready.wait(2))
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(preview))
            http = Thread(target=server.serve_forever, daemon=True)
            http.start()
            base = f'http://127.0.0.1:{server.server_port}'
            def wait_until(condition):
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if condition():
                        return
                    time.sleep(.05)
                self.fail('Timed out waiting for preview update')
            try:
                english = (root / 'en/about.html').read_bytes()
                source = root / 'content/zh/pages/about.md'
                before = preview.state()['version']
                source.write_text(source.read_text(encoding='utf-8') + '\n\n**Markdown live update test**\n', encoding='utf-8')
                wait_until(lambda: preview.state()['version'] != before)
                self.assertIn('<strong>Markdown live update test</strong>', (root / 'about.html').read_text(encoding='utf-8'))
                self.assertEqual(english, (root / 'en/about.html').read_bytes())
                self.assertNotIn('data-local-preview', (root / 'about.html').read_text(encoding='utf-8'))
                with urlopen(base + '/Mijinmo_Portfolio/about.html') as response:
                    local = response.read().decode('utf-8')
                    self.assertEqual(response.headers['Cache-Control'], 'no-store')
                self.assertIn('data-local-preview', local)
                script = re.search(r'<script data-local-preview>(.*?)</script>', local, re.S).group(1)
                subprocess.run(['node', '--check'], input=script, text=True, check=True, capture_output=True)
                # Execute the injected polling client against a mock DOM/status response.
                harness = r'''
const vm = require('node:vm');
const script = SCRIPT;
let tick, reloads = 0, response, box;
const context = {setInterval: fn => tick = fn, location: {reload: () => reloads++},
 document: {getElementById: () => box, createElement: () => ({style:{}, setAttribute(){}, remove(){box=null;}}), body: {appendChild: item => box=item}},
 fetch: async () => ({ok:true, json: async () => response})};
vm.runInNewContext(script, context);
(async () => {
 response = {version:'changed', error:'Missing Markdown file'};
 await tick(); if (!box || reloads !== 0) throw Error('Error state must preserve the page');
 response = {version:'changed', error:''};
 await tick(); if (reloads !== 1) throw Error('Successful update must reload');
})();'''.replace('SCRIPT', json.dumps(script))
                subprocess.run(['node', '-e', harness], check=True, capture_output=True)
                good = (root / 'about.html').read_bytes()
                before = preview.state()['version']
                missing = root / 'content/en/pages/about.md'
                saved = missing.read_bytes()
                missing.unlink()
                wait_until(lambda: bool(preview.state()['error']))
                self.assertEqual(before, preview.state()['version'])
                self.assertEqual(good, (root / 'about.html').read_bytes())
                with urlopen(base + '/__preview/status') as response:
                    self.assertIn('Missing Markdown', json.load(response)['error'])
                missing.write_bytes(saved)
                wait_until(lambda: preview.state()['version'] != before)
                self.assertEqual('', preview.state()['error'])
            finally:
                preview.stop.set()
                watcher.join(3)
                server.shutdown()
                server.server_close()
                http.join(3)

if __name__ == '__main__':
    unittest.main()
