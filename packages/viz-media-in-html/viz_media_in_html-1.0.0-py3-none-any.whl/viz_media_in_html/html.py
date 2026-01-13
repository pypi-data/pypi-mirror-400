from __future__ import annotations

import json
from typing import Dict, List

from .core import MediaItem


def render_html(
    *,
    items: List[MediaItem],
    categories: Dict[str, List[MediaItem]],
    images_per_page: int,
    videos_per_page: int,
    title: str | None = None,
) -> str:
    # HTML/JS 内只包含 id/name/category/is_video，不包含真实路径
    files_payload = [
        {"id": it.id, "name": it.name, "category": it.category, "is_video": it.is_video}
        for it in items
    ]
    categories_payload = {
        cat: [{"id": it.id, "name": it.name, "category": it.category, "is_video": it.is_video} for it in lst]
        for cat, lst in categories.items()
    }
    media_data = {"files": files_payload, "categories": categories_payload}
    page_title = title or f"媒体文件浏览（共 {len(items)} 个）"

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{page_title}</title>
    <style>
        body {{ font-family: sans-serif; background: #f5f5f5; margin: 0; padding: 0; }}
        .main-container {{
            padding-left: 20px;
            padding-right: 20px;
            padding-bottom: 40px;
            transition: padding 0.3s;
        }}
        .header-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 15px;
            background: #fff;
            border-bottom: 1px solid #ddd;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .header-right {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .margin-btn {{
            padding: 5px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: #fff;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }}
        .margin-btn:hover {{
            background: #e0e0e0;
        }}
        .auto-play-group {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin-right: 10px;
            padding: 4px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #fafafa;
        }}
        .auto-play-group label {{
            font-size: 12px;
            color: #555;
            cursor: pointer;
        }}
        .auto-play-group input[type="number"] {{
            width: 45px;
            padding: 3px 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
            font-size: 12px;
            text-align: center;
        }}
        .auto-play-btn {{
            padding: 4px 10px;
            border: none;
            border-radius: 4px;
            background: #6c757d;
            color: white;
            cursor: pointer;
            font-size: 12px;
        }}
        .auto-play-btn.active {{
            background: #28a745;
        }}
        .auto-play-btn:hover {{
            opacity: 0.9;
        }}
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 12px 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 6px;
            font-size: 14px;
            z-index: 2000;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            pointer-events: none;
        }}
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
        .toolbar input {{
            width: 200px;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 13px;
        }}
        .tabs {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            margin: 10px 5px;
            gap: 6px;
        }}
        .tab-button {{
            padding: 6px 14px;
            border: none;
            border-radius: 6px 6px 0 0;
            background: #e0e0e0;
            color: #666;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .tab-button:hover {{
            background: #d0d0d0;
        }}
        .tab-button.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
            padding: 10px;
        }}
        .item {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .filename {{
            margin-top: 6px;
            font-size: 12px;
            color: #555;
            word-break: break-all;
            text-align: center;
        }}
        img, video {{
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.2s;
        }}
        img:hover, video:hover {{
            transform: scale(1.05);
        }}
        video {{
            background: #000;
        }}
        .media-type {{
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        }}
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0.5rem;
            gap: 8px;
        }}
        .pagination button {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            background: #007bff;
            color: white;
            cursor: pointer;
            font-size: 13px;
        }}
        .pagination button:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .page-jump {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .page-jump input {{
            width: 50px;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
            text-align: center;
            font-size: 13px;
        }}
        .page-jump button {{
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            background: #28a745;
            color: white;
            cursor: pointer;
            font-size: 13px;
        }}
        #lightbox {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            flex-direction: column;
        }}
        #lightbox img, #lightbox video {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(255,255,255,0.3);
            object-fit: contain;
        }}
        .lightbox-controls {{
            position: absolute;
            top: 50%;
            width: 100%;
            display: flex;
            justify-content: space-between;
            transform: translateY(-50%);
            padding: 0 20px;
        }}
        .lightbox-btn {{
            background: rgba(255,255,255,0.3);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            color: white;
            cursor: pointer;
        }}
        .lightbox-btn:hover {{
            background: rgba(255,255,255,0.6);
        }}
        .close-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.3);
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 20px;
            color: white;
            cursor: pointer;
        }}
        .close-btn:hover {{
            background: rgba(255,255,255,0.6);
        }}

        .footer {{
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 6px 10px;
            text-align: center;
            font-size: 12px;
            color: #888;
            background: rgba(245, 245, 245, 0.95);
            border-top: 1px solid #e5e5e5;
            backdrop-filter: blur(6px);
            z-index: 1500;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="header-left">
            <span style="font-weight:bold;color:#333;">共 {len(items)} 个媒体</span>
            <div class="toolbar">
                <input type="text" id="search" placeholder="输入关键字过滤文件名...">
            </div>
        </div>
        <div class="header-right">
            <div class="auto-play-group">
                <label>自动翻页</label>
                <input type="number" id="auto-interval" value="3" min="1" max="60" title="翻页间隔（秒）">
                <span style="font-size:12px;color:#666;">秒</span>
                <button class="auto-play-btn" id="auto-play-btn">启用</button>
            </div>
            <button class="margin-btn" id="decrease-margin" title="减小页边距">◀</button>
            <button class="margin-btn" id="increase-margin" title="增大页边距">▶</button>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <div class="main-container" id="main-container">
        <div class="tabs" id="category-tabs"></div>
        <div id="media-container"></div>
        <div class="pagination">
            <button id="prev">上一页</button>
            <span id="page-info"></span>
            <button id="next">下一页</button>
            <div class="page-jump">
                <input type="number" id="page-input" min="1" placeholder="页码">
                <button id="goto-page">跳转</button>
            </div>
        </div>
    </div>

    <div id="lightbox">
        <button class="close-btn">&times;</button>
        <div id="lightbox-content"></div>
        <div class="lightbox-controls">
            <button class="lightbox-btn" id="prev-media">&#8249;</button>
            <button class="lightbox-btn" id="next-media">&#8250;</button>
        </div>
    </div>

    <div class="footer">作者：dreamer</div>

    <script>
        const mediaData = {json.dumps(media_data, ensure_ascii=False)};
        const categories = mediaData.categories;  // cat -> items
        const perPageImg = {images_per_page};
        const perPageVideo = {videos_per_page};

        let currentCategory = null;
        let currentPageByCategory = {{}};
        let filteredMediaByCategory = {{}};
        let currentIndex = -1;
        let allFilteredMedia = [];
        let currentMargin = 20;
        let autoPlayTimer = null;
        let autoPlayEnabled = false;

        function showToast(message, duration = 2000) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, duration);
        }}

        function getSrc(item) {{
            return `/media/${{encodeURIComponent(item.id)}}`;
        }}

        function isVideoItem(item) {{
            if (typeof item.is_video === 'boolean') return item.is_video;
            const name = (item.name || '').toLowerCase();
            return name.endsWith('.mp4') || name.endsWith('.avi') || name.endsWith('.mov') || name.endsWith('.wmv')
                || name.endsWith('.flv') || name.endsWith('.webm') || name.endsWith('.mkv') || name.endsWith('.m4v');
        }}

        function updateMargin(delta) {{
            currentMargin = Math.max(0, Math.min(1800, currentMargin + delta));
            const container = document.getElementById('main-container');
            container.style.paddingLeft = currentMargin + 'px';
            container.style.paddingRight = currentMargin + 'px';
        }}
        document.getElementById('increase-margin').addEventListener('click', () => updateMargin(20));
        document.getElementById('decrease-margin').addEventListener('click', () => updateMargin(-20));

        function getPerPage(categoryMedia) {{
            if (!categoryMedia || categoryMedia.length === 0) return perPageImg;
            const videoCount = categoryMedia.filter(item => isVideoItem(item)).length;
            const imgCount = categoryMedia.length - videoCount;
            return videoCount > imgCount ? perPageVideo : perPageImg;
        }}

        function initTabs() {{
            const tabsContainer = document.getElementById("category-tabs");
            const sortedCategories = Object.keys(categories).sort();

            sortedCategories.forEach((category, index) => {{
                const tabButton = document.createElement("button");
                tabButton.className = "tab-button";
                if (index === 0) {{
                    tabButton.classList.add("active");
                    currentCategory = category;
                }}
                const count = (categories[category] || []).length;
                tabButton.textContent = `${{category}} (${{count}})`;
                tabButton.addEventListener("click", () => switchCategory(category));
                tabsContainer.appendChild(tabButton);

                currentPageByCategory[category] = 1;
                filteredMediaByCategory[category] = [...(categories[category] || [])];
            }});
        }}

        function switchCategory(category) {{
            currentCategory = category;
            document.querySelectorAll(".tab-button").forEach(btn => {{
                btn.classList.remove("active");
                if (btn.textContent.startsWith(category)) {{
                    btn.classList.add("active");
                }}
            }});
            if (!currentPageByCategory[category]) currentPageByCategory[category] = 1;
            renderPage(currentPageByCategory[category]);
        }}

        function renderPage(page) {{
            if (!currentCategory) return;
            const container = document.getElementById("media-container");
            container.innerHTML = "";

            const categoryMedia = filteredMediaByCategory[currentCategory] || [];
            const perPage = getPerPage(categoryMedia);
            const totalPages = Math.max(1, Math.ceil(categoryMedia.length / perPage));
            const start = (page - 1) * perPage;
            const end = Math.min(start + perPage, categoryMedia.length);
            const pageItems = categoryMedia.slice(start, end);

            document.getElementById('page-input').max = totalPages;

            const gridContainer = document.createElement("div");
            gridContainer.className = "container";

            pageItems.forEach((item, idx) => {{
                const globalIndex = allFilteredMedia.findIndex(m => m.id === item.id);
                const itemIndex = globalIndex >= 0 ? globalIndex : start + idx;

                const itemDiv = document.createElement("div");
                itemDiv.className = "item";
                itemDiv.style.position = "relative";

                const isVideo = isVideoItem(item);
                const mediaElement = isVideo ? document.createElement("video") : document.createElement("img");
                mediaElement.src = getSrc(item);
                mediaElement.loading = "lazy";
                mediaElement.controls = isVideo;
                mediaElement.addEventListener("click", () => showLightbox(item, itemIndex));

                const typeLabel = document.createElement("div");
                typeLabel.className = "media-type";
                typeLabel.textContent = isVideo ? "VIDEO" : "IMAGE";

                const caption = document.createElement("div");
                caption.className = "filename";
                caption.textContent = item.name || "";

                itemDiv.appendChild(mediaElement);
                itemDiv.appendChild(typeLabel);
                itemDiv.appendChild(caption);
                gridContainer.appendChild(itemDiv);
            }});

            container.appendChild(gridContainer);

            document.getElementById("page-info").innerText =
                `第 ${{page}} 页 / 共 ${{totalPages}} 页 （共 ${{categoryMedia.length}} 个）`;
            document.getElementById("prev").disabled = page === 1;
            document.getElementById("next").disabled = page === totalPages;

            currentPageByCategory[currentCategory] = page;
        }}

        function applySearch(keyword) {{
            const kw = keyword ? keyword.toLowerCase() : '';
            Object.keys(categories).forEach(category => {{
                const src = categories[category] || [];
                if (!kw) {{
                    filteredMediaByCategory[category] = [...src];
                }} else {{
                    filteredMediaByCategory[category] = src.filter(item => {{
                        return (item.name || '').toLowerCase().includes(kw);
                    }});
                }}
                currentPageByCategory[category] = 1;
            }});

            allFilteredMedia = [];
            Object.values(filteredMediaByCategory).forEach(items => {{
                allFilteredMedia.push(...items);
            }});

            if (currentCategory) {{
                renderPage(currentPageByCategory[currentCategory]);
            }}
        }}

        document.getElementById("prev").addEventListener("click", () => {{
            if (!currentCategory) return;
            const currentPage = currentPageByCategory[currentCategory] || 1;
            if (currentPage > 1) renderPage(currentPage - 1);
        }});
        document.getElementById("next").addEventListener("click", () => {{
            if (!currentCategory) return;
            const categoryMedia = filteredMediaByCategory[currentCategory] || [];
            const perPage = getPerPage(categoryMedia);
            const totalPages = Math.ceil(categoryMedia.length / perPage);
            const currentPage = currentPageByCategory[currentCategory] || 1;
            if (currentPage < totalPages) renderPage(currentPage + 1);
        }});
        document.getElementById("search").addEventListener("input", (e) => {{
            applySearch(e.target.value);
        }});

        document.getElementById("goto-page").addEventListener("click", () => {{
            if (!currentCategory) return;
            const pageInput = document.getElementById("page-input");
            const targetPage = parseInt(pageInput.value);
            if (isNaN(targetPage) || targetPage < 1) return;

            const categoryMedia = filteredMediaByCategory[currentCategory] || [];
            const perPage = getPerPage(categoryMedia);
            const totalPages = Math.max(1, Math.ceil(categoryMedia.length / perPage));
            if (targetPage <= totalPages) renderPage(targetPage);
            else alert('页码超出范围，最大页码: ' + totalPages);
        }});

        document.getElementById("page-input").addEventListener("keydown", (e) => {{
            if (e.key === "Enter") {{
                document.getElementById("goto-page").click();
            }}
        }});

        // Lightbox
        const lightbox = document.getElementById("lightbox");
        const lightboxContent = document.getElementById("lightbox-content");
        const closeBtn = document.querySelector(".close-btn");

        function showLightbox(item, index) {{
            currentIndex = index;
            lightboxContent.innerHTML = "";

            const isVideo = isVideoItem(item);
            const mediaElement = isVideo ? document.createElement("video") : document.createElement("img");
            mediaElement.src = getSrc(item);
            mediaElement.controls = isVideo;
            mediaElement.autoplay = isVideo;
            lightboxContent.appendChild(mediaElement);
            lightbox.style.display = "flex";
        }}

        function getMediaItem(index) {{
            if (index >= 0 && index < allFilteredMedia.length) return allFilteredMedia[index];
            return null;
        }}

        function closeLightbox() {{
            lightbox.style.display = "none";
            lightboxContent.innerHTML = "";
            currentIndex = -1;
        }}

        closeBtn.addEventListener("click", closeLightbox);
        document.getElementById("prev-media").addEventListener("click", (e) => {{
            e.stopPropagation();
            if (currentIndex > 0) {{
                currentIndex--;
                showLightbox(getMediaItem(currentIndex), currentIndex);
            }}
        }});
        document.getElementById("next-media").addEventListener("click", (e) => {{
            e.stopPropagation();
            if (currentIndex < allFilteredMedia.length - 1) {{
                currentIndex++;
                showLightbox(getMediaItem(currentIndex), currentIndex);
            }}
        }});
        lightbox.addEventListener("click", (e) => {{
            if (e.target === lightbox) closeLightbox();
        }});

        function startAutoPlay() {{
            const interval = parseInt(document.getElementById('auto-interval').value) || 3;
            autoPlayEnabled = true;
            document.getElementById('auto-play-btn').textContent = '停止';
            document.getElementById('auto-play-btn').classList.add('active');
            showToast(`自动翻页已启用，间隔 ${{interval}} 秒`);

            autoPlayTimer = setInterval(() => {{
                if (!currentCategory) return;
                const categoryMedia = filteredMediaByCategory[currentCategory] || [];
                const perPage = getPerPage(categoryMedia);
                const totalPages = Math.ceil(categoryMedia.length / perPage);
                const currentPage = currentPageByCategory[currentCategory] || 1;
                if (currentPage < totalPages) renderPage(currentPage + 1);
                else renderPage(1);
            }}, interval * 1000);
        }}

        function stopAutoPlay() {{
            if (autoPlayTimer) {{
                clearInterval(autoPlayTimer);
                autoPlayTimer = null;
            }}
            autoPlayEnabled = false;
            document.getElementById('auto-play-btn').textContent = '启用';
            document.getElementById('auto-play-btn').classList.remove('active');
            showToast('自动翻页已关闭');
        }}

        function toggleAutoPlay() {{
            if (autoPlayEnabled) stopAutoPlay();
            else startAutoPlay();
        }}

        document.getElementById('auto-play-btn').addEventListener('click', toggleAutoPlay);
        document.getElementById('auto-interval').addEventListener('change', () => {{
            if (autoPlayEnabled) {{
                stopAutoPlay();
                startAutoPlay();
            }}
        }});

        document.addEventListener("keydown", (e) => {{
            const activeEl = document.activeElement;
            const isInputFocused = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA');

            if (autoPlayEnabled && !isInputFocused) {{
                stopAutoPlay();
                return;
            }}

            if (lightbox.style.display === "flex") {{
                if (e.key === "Escape") {{
                    closeLightbox();
                }} else if (e.key === "ArrowLeft" && currentIndex > 0) {{
                    currentIndex--;
                    showLightbox(getMediaItem(currentIndex), currentIndex);
                }} else if (e.key === "ArrowRight" && currentIndex < allFilteredMedia.length - 1) {{
                    currentIndex++;
                    showLightbox(getMediaItem(currentIndex), currentIndex);
                }}
            }} else if (!isInputFocused) {{
                if (e.key === "ArrowLeft") {{
                    document.getElementById("prev").click();
                }} else if (e.key === "ArrowRight" || e.key === " ") {{
                    e.preventDefault();
                    document.getElementById("next").click();
                }}
            }}
        }});

        // init
        initTabs();
        allFilteredMedia = [];
        Object.values(filteredMediaByCategory).forEach(items => {{
            allFilteredMedia.push(...items);
        }});
        if (currentCategory) renderPage(currentPageByCategory[currentCategory]);
    </script>
</body>
</html>
"""


