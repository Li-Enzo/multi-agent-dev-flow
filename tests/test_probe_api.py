"""probe_api.py 回归用例：POST/GET、PROBE_API_BASE 解析、退出码语义。"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

pytestmark = pytest.mark.usefixtures("http_server")


class _Handler(BaseHTTPRequestHandler):
    def _reply(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        # /api/secure 前缀模拟需鉴权端点：Authorization 头不对按约定回 1002
        if self.path.startswith("/api/secure"):
            return self.headers.get("Authorization") == "Bearer good"
        return True

    def _write_op(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")  # 先读尽 body，避免连接 RST
        if not self._authorized():
            return self._reply({"code": 1002, "msg": "未登录 / token 失效"})
        self._reply({"code": 0, "msg": "write ok", "echo": req})

    def do_POST(self):
        self._write_op()

    def do_PUT(self):
        self._write_op()

    def do_GET(self):
        from urllib.parse import parse_qs, urlparse
        q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        self._reply({"code": 0, "msg": "get ok", "echo": q})

    def log_message(self, *args):
        pass


@pytest.fixture()
def http_server():
    """起一个 127.0.0.1 临时端口的服务器，yield 基础地址后关闭。"""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    thread.join(timeout=5)


def test_post_ok(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-a", "test.action",
                   "-d", '{"k": 1}', "-e", "0")
    assert r.returncode == 0
    assert "[ OK ]" in r.stdout


def test_post_code_mismatch_exit_2(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-a", "a", "-e", "500")
    assert r.returncode == 2
    assert "[FAIL]" in r.stdout


def test_get_query_string(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/q", "-m", "GET",
                   "-a", "user.info", "-d", '{"uid": 42, "q": "中文 空格"}')
    assert r.returncode == 0
    assert "user.info" in r.stdout


def test_probe_api_base_join_relative(run_script, http_server):
    r = run_script("probe_api.py", "-u", "/api/ping", "-a", "ping",
                   env_extra={"PROBE_API_BASE": http_server})
    assert r.returncode == 0


def test_probe_api_base_omitted_url(run_script, http_server):
    r = run_script("probe_api.py", "-a", "base.only",
                   env_extra={"PROBE_API_BASE": f"{http_server}/api"})
    assert r.returncode == 0


def test_relative_url_without_base_exit_2(run_script):
    r = run_script("probe_api.py", "-u", "/ping", "-a", "ping")
    assert r.returncode == 2
    assert "PROBE_API_BASE" in r.stdout


def test_network_error_exit_1(run_script):
    r = run_script("probe_api.py", "-u", "http://127.0.0.1:9/none", "-a", "a")
    assert r.returncode == 1


def test_invalid_data_json_exit_2(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-a", "a", "-d", "{bad")
    assert r.returncode == 2


def test_put_ok(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-m", "PUT",
                   "-a", "item.update", "-d", '{"id": 1}', "-e", "0")
    assert r.returncode == 0
    assert "[ OK ]" in r.stdout


def test_put_code_mismatch_exit_2(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-m", "PUT",
                   "-a", "a", "-e", "500")
    assert r.returncode == 2
    assert "[FAIL]" in r.stdout


def test_custom_header_auth_pass(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/secure/ping", "-a", "secure.ping",
                   "-H", "Authorization: Bearer good", "-e", "0")
    assert r.returncode == 0


def test_auth_header_missing_rejected(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/secure/ping", "-a", "secure.ping")
    assert r.returncode == 2
    assert "1002" in r.stdout


def test_put_with_auth_header(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/secure/item", "-m", "PUT",
                   "-a", "secure.update", "-d", '{"id": 1}',
                   "-H", "Authorization: Bearer good")
    assert r.returncode == 0


def test_malformed_header_exit_2(run_script, http_server):
    r = run_script("probe_api.py", "-u", f"{http_server}/api/echo", "-a", "a",
                   "-H", "no-colon-here")
    assert r.returncode == 2
    assert "请求头格式" in r.stdout
