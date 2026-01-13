from __future__ import annotations

import glob
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


VIDEO_EXTS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv", ".m4v"}


@dataclass(frozen=True)
class MediaItem:
    id: str
    abs_path: Path
    name: str
    category: str
    is_video: bool


def _is_video_by_name(name: str) -> bool:
    return Path(name).suffix.lower() in VIDEO_EXTS


def _redact_path(p: str) -> str:
    # 避免把用户本地目录结构打印到控制台
    try:
        return Path(p).name or "<unknown>"
    except Exception:
        return "<unknown>"


def _parse_txt_line(line: str) -> Tuple[str, str]:
    """
    支持：
    - path
    - path<tab>category
    - path<space>category（仅分割第一个空格）
    """
    line = line.strip()
    if not line:
        return "", ""
    if "\t" in line:
        p, cat = line.split("\t", 1)
        return p.strip(), (cat.strip() or "未分类")
    if " " in line:
        p, cat = line.split(" ", 1)
        return p.strip(), (cat.strip() or "未分类")
    return line, "未分类"


def collect_media(input_spec: str, *, cwd: Path | None = None) -> List[MediaItem]:
    """
    从 txt 列表或 glob 模式收集媒体文件。
    - 不在返回数据中暴露原始路径字符串（只保留 abs_path 供服务端使用，HTML 里只用 id/name）
    """
    if cwd is None:
        cwd = Path.cwd()

    input_spec = input_spec or ""
    media: List[Tuple[Path, str]] = []  # (abs_path, category)

    if input_spec.lower().endswith(".txt"):
        txt_path = Path(input_spec)
        if not txt_path.is_absolute():
            txt_path = (cwd / txt_path).resolve()
        if not txt_path.exists():
            raise FileNotFoundError(f"txt 文件不存在: {_redact_path(str(txt_path))}")

        base_dir = txt_path.parent
        with txt_path.open("r", encoding="utf-8") as f:
            for raw in f:
                p_str, cat = _parse_txt_line(raw)
                if not p_str:
                    continue
                p = Path(p_str)
                if not p.is_absolute():
                    p = (base_dir / p).resolve()
                else:
                    p = p.resolve()
                if p.exists():
                    media.append((p, cat))
                else:
                    # 仅打印文件名，避免泄露本地路径
                    print(f"警告: 文件不存在，跳过: {_redact_path(p_str)}")
    else:
        # glob 模式：相对 cwd 执行
        # Python 的 glob 在 Windows/Linux 均可用
        pattern = input_spec
        if not pattern:
            raise ValueError("缺少 --input")
        globbed = glob.glob(pattern, recursive=True)
        for p_str in globbed:
            p = Path(p_str)
            if not p.is_absolute():
                p = (cwd / p).resolve()
            else:
                p = p.resolve()
            if p.exists():
                media.append((p, "未分类"))

    if not media:
        return []

    # 去重并排序：先按文件名分组，再按绝对路径稳定排序（不输出）
    uniq: Dict[str, Tuple[Path, str]] = {}
    # key 用绝对路径的规范字符串（仅内部使用）
    for p, cat in media:
        key = os.fspath(p)
        if key not in uniq:
            uniq[key] = (p, cat)

    items = list(uniq.values())
    items.sort(key=lambda t: (t[0].name.lower(), os.fspath(t[0]).lower()))

    out: List[MediaItem] = []
    for idx, (p, cat) in enumerate(items):
        name = p.name
        out.append(
            MediaItem(
                id=str(idx),
                abs_path=p,
                name=name,
                category=cat or "未分类",
                is_video=_is_video_by_name(name),
            )
        )
    return out


def group_by_category(items: Iterable[MediaItem]) -> Dict[str, List[MediaItem]]:
    grouped: Dict[str, List[MediaItem]] = {}
    for it in items:
        grouped.setdefault(it.category or "未分类", []).append(it)
    for cat in list(grouped.keys()):
        grouped[cat].sort(key=lambda x: x.name.lower())
    return dict(sorted(grouped.items(), key=lambda kv: kv[0]))


