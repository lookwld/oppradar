#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交易机会 · 本地预览服务器

设计要点（都是安全考量，不是为了好看）：
  1. 只绑定 127.0.0.1 —— 同一局域网的其他设备也访问不到，外网更不可能；
  2. 端口默认由操作系统随机分配（监听 0 号端口，内核回填真实端口），
     所以端口号不确定、不写死、每次可能不同，难以被扫描定位；
  3. 关闭目录浏览，只对外提供本目录下的静态文件；
  4. 附加安全响应头（CSP 白名单只放币安行情接口、禁用 Referer、禁止嗅探）。

用法：
    python start.py               # 随机端口 + 自动打开浏览器
    python start.py --port 8787   # 固定端口（想让浏览器记住自选合约时用）
    python start.py --no-browser  # 只起服务，不自动开浏览器
"""
import argparse
import http.server
import os
import socketserver
import sys
import threading
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))

CSP = ("connect-src https://fapi.binance.com; "
       "img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
       "object-src 'none'; base-uri 'none'; form-action 'none'")


class Handler(http.server.SimpleHTTPRequestHandler):
    """静态文件处理器：加响应头、关目录列表、不写访问日志。"""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Permissions-Policy",
                         "geolocation=(), camera=(), microphone=(), payment=()")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(403, "Forbidden")
        return None

    def log_message(self, fmt, *args):
        pass                                   # 不记录访问日志，避免落盘残留


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    try:                                      # 被重定向 / 管道接管时也让提示立刻出现
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="交易机会 · 本地预览服务器")
    ap.add_argument("--port", type=int, default=0,
                    help="监听端口；0（默认）= 由系统随机分配")
    ap.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    a = ap.parse_args()

    index = os.path.join(ROOT, "index.html")
    if not os.path.exists(index):
        print("找不到 index.html，请把本脚本放在页面同一目录下。", file=sys.stderr)
        return 1

    # 端口 0 = 让操作系统挑一个空闲的随机端口
    with Server(("127.0.0.1", a.port), Handler) as httpd:
        port = httpd.server_address[1]
        url = "http://127.0.0.1:%d/" % port
        print("交易机会 · 本地预览")
        print("  地址：%s" % url)
        print("  绑定：仅本机 127.0.0.1（局域网与外网均不可达）")
        print("  端口：%s" % ("随机分配 %d" % port if a.port == 0 else "指定 %d" % port))
        print("  退出：按 Ctrl+C")
        print()
        if not a.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
