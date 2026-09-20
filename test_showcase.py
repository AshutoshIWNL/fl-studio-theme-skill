"""E2E Test for the GitHub Pages Showcase Page."""

import json
import unittest
from pathlib import Path


class TestShowcaseE2E(unittest.TestCase):

    def setUp(self):
        self.docs_dir = Path("docs")

    def test_themes_json_structure(self):
        themes_file = self.docs_dir / "themes.json"
        self.assertTrue(themes_file.exists(), "docs/themes.json is missing")

        with open(themes_file, "r", encoding="utf-8") as f:
            themes = json.load(f)

        self.assertEqual(len(themes), 17, f"Expected 17 themes, found {len(themes)}")

        required_keys = [
            "id", "name", "tagline", "description", "accent", "highlight",
            "mute", "option", "stepEven", "stepOdd", "backColor", "hue",
            "saturation", "lightness", "contrast", "screenshot", "animationName"
        ]
        for t in themes:
            for k in required_keys:
                self.assertIn(k, t, f"Missing key '{k}' in theme '{t.get('id')}'")
                self.assertTrue(str(t[k]).strip(), f"Empty value for '{k}' in '{t.get('id')}'")

    def test_animations_js_coverage(self):
        anim_file = self.docs_dir / "animations.js"
        self.assertTrue(anim_file.exists(), "docs/animations.js is missing")

        with open(anim_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("window.THEME_ANIMATIONS =", content)

        # Ensure all 17 themes from themes.json have corresponding animations
        with open(self.docs_dir / "themes.json", "r", encoding="utf-8") as f:
            themes = json.load(f)

        for t in themes:
            self.assertIn(f'"{t["id"]}":', content, f"Missing animation for theme '{t['id']}'")

    def test_index_html_integrity(self):
        index_file = self.docs_dir / "index.html"
        self.assertTrue(index_file.exists(), "docs/index.html is missing")

        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("themes.json", content)
        self.assertIn("animations.js", content)
        self.assertIn("FL Studio Theme Designer", content)
        self.assertIn("btn-mode-live", content)
        self.assertIn("btn-mode-screenshot", content)
        self.assertIn("daw-channel-rack", content)

    def test_http_server_serving(self):
        """Spins up a local HTTP server and simulates a browser loading the showcase."""
        import http.server
        import socketserver
        import threading
        import urllib.request

        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory="docs", **kwargs)
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
            port = httpd.server_address[1]
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            try:
                # 1. Fetch index.html
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html") as resp:
                    self.assertEqual(resp.status, 200)
                    body = resp.read().decode("utf-8")
                    self.assertIn("FL Studio Theme Designer", body)

                # 2. Fetch themes.json
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/themes.json") as resp:
                    self.assertEqual(resp.status, 200)
                    data = json.loads(resp.read().decode("utf-8"))
                    self.assertEqual(len(data), 17)

                # 3. Fetch animations.js
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/animations.js") as resp:
                    self.assertEqual(resp.status, 200)
                    anim_js = resp.read().decode("utf-8")
                    self.assertIn("window.THEME_ANIMATIONS", anim_js)

            finally:
                httpd.shutdown()
                server_thread.join()



if __name__ == "__main__":
    unittest.main()
