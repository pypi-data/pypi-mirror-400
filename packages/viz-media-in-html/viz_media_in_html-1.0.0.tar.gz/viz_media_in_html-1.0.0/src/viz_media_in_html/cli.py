from __future__ import annotations

import argparse
import socket
import sys
import webbrowser
from ipaddress import ip_address
from pathlib import Path

from .core import collect_media, group_by_category
from .html import render_html
from .server import find_free_port, make_handler, serve


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="媒体文件浏览工具（HTML + 本地 HTTP 服务，默认不暴露真实路径）")
    p.add_argument("--input", required=True, help='媒体文件路径模式（如 "**/*.jpg"）或 txt 列表文件（如 "list.txt"）')
    p.add_argument("--html", default="index.html", help="写出 HTML 文件名（默认: index.html）")
    p.add_argument("--bind", default="0.0.0.0", help="HTTP 绑定地址（默认: 0.0.0.0，局域网可访问）")
    p.add_argument("--port", type=int, default=18000, help="HTTP 起始端口（默认: 18000）")
    p.add_argument("--per-page-img", type=int, default=1000, help="每页显示的图片数量（默认: 1000）")
    p.add_argument("--per-page-video", type=int, default=100, help="每页显示的视频数量（默认: 100）")
    p.add_argument("--open", action="store_true", help="启动后自动打开浏览器")
    p.add_argument("--title", default=None, help="页面标题（可选）")
    return p


def _local_ipv4_candidates() -> list[str]:
    """
    返回尽可能完整的本机 IPv4 地址列表（不含 0.0.0.0）。
    仅用标准库：兼容 Linux/Windows。
    """
    out: set[str] = set()

    # hostname -> addrs
    try:
        host = socket.gethostname()
        for fam, _, _, _, sockaddr in socket.getaddrinfo(host, None):
            if fam == socket.AF_INET and sockaddr and sockaddr[0]:
                out.add(sockaddr[0])
    except Exception:
        pass

    # UDP “外连探测”得到主路由口的本机地址（不会真的发包）
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            out.add(s.getsockname()[0])
        finally:
            s.close()
    except Exception:
        pass

    # 清洗：只保留合法 IPv4，丢弃 0.0.0.0
    cleaned: set[str] = set()
    for ip in out:
        try:
            obj = ip_address(ip)
            if obj.version == 4 and str(obj) != "0.0.0.0":
                cleaned.add(str(obj))
        except Exception:
            continue

    # 优先把常用 loopback 放前面（也算“可访问网址”之一）
    ordered = sorted(cleaned, key=lambda x: (0 if x.startswith("127.") else 1, x))
    return ordered


def _build_access_urls(*, bind: str, port: int, html: str) -> list[str]:
    suffix = f"/{html.lstrip('/')}"

    # 浏览器一般不该访问 0.0.0.0，本质是“监听所有地址”
    if bind in ("0.0.0.0", ""):
        hosts = ["localhost", "127.0.0.1", *_local_ipv4_candidates()]
    else:
        hosts = [bind]
        if bind == "127.0.0.1":
            hosts = ["localhost", "127.0.0.1"]

    seen: set[str] = set()
    urls: list[str] = []
    for h in hosts:
        u = f"http://{h}:{port}{suffix}"
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    items = collect_media(args.input, cwd=Path.cwd())
    if not items:
        print("警告: 没有找到媒体文件")
        return 1

    categories = group_by_category(items)
    html_content = render_html(
        items=items,
        categories=categories,
        images_per_page=args.per_page_img,
        videos_per_page=args.per_page_video,
        title=args.title,
    )

    # 写出 HTML（不含真实路径）；注意：该 HTML 依赖服务端的 /media/<id> 路由
    try:
        out_html = Path(args.html)
        out_html.write_text(html_content, encoding="utf-8")
        print(f"HTML 文件已生成: {out_html}")
    except Exception as e:
        print(f"警告: 写出 HTML 失败（不影响服务启动）: {e}")

    try:
        port = find_free_port(args.port, bind=args.bind)
    except RuntimeError as e:
        print(f"错误: {e}")
        return 1

    urls = _build_access_urls(bind=args.bind, port=port, html=args.html)
    print("可访问地址（任选其一打开）：")
    for u in urls:
        print(f"  - {u}")
    if args.bind in ("0.0.0.0", ""):
        print("提示: 你正在监听 0.0.0.0（局域网可访问），请注意防火墙/安全策略。")

    media_map = {it.id: it.abs_path for it in items}
    handler_cls = make_handler(html_content=html_content, media_map=media_map, html_filename=args.html)

    print("按 Ctrl+C 停止服务器")
    if args.open:
        try:
            # 0.0.0.0 不能作为浏览器访问目标；优先用 loopback 打开
            open_url = urls[0] if urls else f"http://127.0.0.1:{port}/{args.html}"
            webbrowser.open(open_url, new=2)
        except Exception:
            pass

    try:
        serve(bind=args.bind, port=port, handler_cls=handler_cls)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


