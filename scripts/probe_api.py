#!/usr/bin/env python3
"""probe_api.py — 接口存活探针

代替 AI 手工 curl 验证接口。按统一约定发送
  POST {"action": "<action>", "data": {...}}
或 GET（action 与 data 字段拼入 query string），
并检查返回体 code 是否在期望集合内。

URL 解析规则（-u 可省略）:
  1. -u 以 http:// 或 https:// 开头 → 原样使用；
  2. -u 为相对路径（如 /api/ping）→ 拼接环境变量 PROBE_API_BASE；
  3. -u 省略 → 直接使用 PROBE_API_BASE。

用法:
    python probe_api.py -u <URL> -a <action> [-m GET] [-d '<json>'] [-e 0,2002] [-H "k: v"] [-t 10] [-v]
    PROBE_API_BASE=https://api.example.com python probe_api.py -u /api/ping -a ping

退出码: 0 = code 命中期望; 1 = 网络/HTTP 错误; 2 = code 未命中期望/参数错误。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def resolve_url(url):
    """解析最终请求地址：绝对 URL 原样返回；相对路径或省略时拼 PROBE_API_BASE。"""
    if url and url.startswith(("http://", "https://")):
        return url
    base = os.environ.get("PROBE_API_BASE", "").strip()
    if not base:
        print("[ERROR] 相对路径或省略 -u 时需要环境变量 PROBE_API_BASE")
        return None
    if not url:
        return base
    return base.rstrip("/") + "/" + url.lstrip("/")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-u", "--url", default=None, help="接口地址（绝对 URL 或相对路径；省略则用 PROBE_API_BASE）")
    ap.add_argument("-a", "--action", required=True, help="action 名")
    ap.add_argument("-m", "--method", choices=["POST", "GET"], default="POST", help="请求方法（默认 POST）")
    ap.add_argument("-d", "--data", default="{}", help="data JSON 字符串")
    ap.add_argument("-e", "--expect", default="0", help="期望 code 集合，逗号分隔（默认 0）")
    ap.add_argument("-H", "--header", action="append", default=[], help="额外请求头，可多次")
    ap.add_argument("-t", "--timeout", type=float, default=10.0, help="超时秒数（默认 10）")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印完整响应体")
    args = ap.parse_args()

    url = resolve_url(args.url)
    if url is None:
        return 2

    try:
        payload = json.loads(args.data)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] -d 不是合法 JSON: {exc}")
        return 2
    if not isinstance(payload, dict):
        print("[ERROR] -d 必须是 JSON 对象（dict）")
        return 2

    headers = {}
    if args.method == "POST":
        body = json.dumps({"action": args.action, "data": payload}).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        # GET：action 与 data 字段拼入 query string；非标量值序列化为 JSON 字符串
        query = {"action": args.action}
        for k, v in payload.items():
            query[k] = v if isinstance(v, (str, int, float, bool)) else json.dumps(v, ensure_ascii=False)
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(query)
        body = None

    for h in args.header:
        if ":" not in h:
            print(f"[ERROR] 请求头格式应为 'Key: Value': {h}")
            return 2
        k, v = h.split(":", 1)
        headers[k.strip()] = v.strip()

    req = urllib.request.Request(url, data=body, headers=headers, method=args.method)
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            http_status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print(f"[FAIL] HTTP {exc.code}: {raw[:300]}")
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"[FAIL] 网络错误: {exc}")
        return 1

    try:
        result = json.loads(raw)
        code = result.get("code")
        msg = result.get("msg")
    except json.JSONDecodeError:
        print(f"[FAIL] 返回不是 JSON（HTTP {http_status}）: {raw[:300]}")
        return 2

    expected = {int(x) for x in args.expect.split(",")}
    ok = code in expected
    tag = "[ OK ]" if ok else "[FAIL]"
    print(f"{tag} HTTP {http_status}　action={args.action}　code={code}　msg={msg}　期望={sorted(expected)}")
    if args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
