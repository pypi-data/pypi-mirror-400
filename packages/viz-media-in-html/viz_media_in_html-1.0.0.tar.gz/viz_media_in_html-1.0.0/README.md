## viz-media-in-html

把本地图片/视频做成一个可交互的 HTML 画廊，并启动一个本地 HTTP 服务来浏览：支持分类、搜索、分页、Lightbox、键盘快捷键、自动翻页。

这个包默认**不在 HTML/控制台输出中暴露真实本地路径**：页面内的媒体资源通过 `/media/<id>` 访问。

### 安装

```bash
pip install viz-media-in-html
```

### 使用

- **glob 模式**（推荐）

```bash
viz-media-in-html --input "**/*.jpg" --port 18000 --open
```

- **txt 列表模式**
  - 每行：`路径[空格或TAB]类别`（类别可省略）

```bash
viz-media-in-html --input list.txt --open
```

### 常用参数

- `--bind`：绑定地址，默认 `0.0.0.0`（局域网可访问；注意防火墙/安全）
- `--port`：起始端口，若被占用会自动向上寻找可用端口
- `--html`：可选，写出一个静态 HTML 文件（默认 `index.html`）
- `--per-page-img / --per-page-video`：分页大小
- `--open`：启动后自动打开浏览器

### 发布到 PyPI（示例）

```bash
python -m pip install -U build twine
python -m build
python -m twine upload dist/*
```


