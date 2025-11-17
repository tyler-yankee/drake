import os
import signal
import subprocess
import tempfile
from textwrap import dedent
import threading
import time
import unittest
from urllib.request import urlopen
from urllib.error import URLError

from pydrake.geometry import _start_meshcat_deepnote

class TestNginxProxy(unittest.TestCase):

    # TODO: might be able to re-use _is_listening here?
    @staticmethod
    def wait_for_http(port, path="/", timeout=5):
        url = f"http://localhost:{port}{path}"
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urlopen(url) as f:
                    return True
            except URLError:
                time.sleep(0.1)
        return False

    @classmethod
    def setUpClass(cls):
        cls.backend_port = 9000 # TODO
        cls.backend_thread = threading.Thread(
            target=_start_meshcat_deepnote(),
            args=(cls.backend_port,), # TODO: doesn't take a port argument...
            daemon=True,
        )
        cls.backend_thread.start()

        if not cls.wait_for_http(cls.backend_port):
            raise RuntimeError("Failed to start Meshcat")

        cls.tempdir = tempfile.TemporaryDirectory()
        cls.nginx_conf = os.path.join(cls.tempdir.name, "nginx.conf")
        # TODO: the real function calls setup/deepnote/install_nginx, which
        # ends up calling `service nginx start` and mucking with the fs. we
        # *cannot* do that here.
        with open(cls.nginx_conf, 'w') as f:
            f.write(dedent(f"""
            server {{
            listen 8080 default_server;
            listen [::]:8080 default_server;
            root /var/www/html;
            server_name _;
            location ~ /(7[0-9][0-9][0-9])/(.*) {{
                proxy_pass http://127.0.0.1:$1/$2;
            }}
            proxy_read_timeout 600;
            proxy_connect_timeout 600;
            proxy_send_timeout 600;
            send_timeout 600;
            }}
            """))

        cls.nginx_proc = subprocess.Popen(
            [
                "nginx",
                "-c",
                cls.nginx_conf,
                "-g",
                "daemon off;",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not cls.wait_for_http(8080):
            cls.tearDownClass()
            raise RuntimeError("nginx failed to start")

    @classmethod
    def tearDownClass(cls):
        if cls.nginx_proc.poll() is None:
            cls.nginx_proc.send_signal(signal.SIGTERM)
            try:
                cls.nginx_proc.wait(3)
            except subprocess.TimeoutExpired:
                cls.nginx_proc.kill()
        cls.tempdir.cleanup()

    def test_meshcat_proxy(self):
        with urlopen("http://127.0.0.1:8080/test") as response:
            content_type = response.getheader("Content-Type")
            some_data = response.read(4096)
            # Finish reading everything, but discard it.
            response.read()
        # This also serves as a regresion test of the C++ code, where parsing
        # the Content-Type is difficult within its unit test infrastructure.
        self.assertIn("text/html", content_type)
        self.assertIn("DOCTYPE html", some_data.decode("utf-8"))
