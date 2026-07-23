var CORS_PROXIES = [
    "https://api.allorigins.win/raw?url=",
    "https://corsproxy.io/?"
];

var RSS_SOURCES = [
    { url: "https://feeds.arstechnica.com/arstechnica/technology-lab", name: "Ars Technica" },
    { url: "https://www.technologyreview.com/feed/", name: "MIT Technology Review" },
    { url: "https://venturebeat.com/feed/", name: "VentureBeat" },
    { url: "https://www.unite.ai/feed/", name: "Unite.AI" },
    { url: "https://www.ifanr.com/feed", name: "爱范儿" },
    { url: "https://www.pingwest.com/feed", name: "品玩" }
];

var MODULE_KEYWORDS = {
    "\u653f\u58f0\u4f20\u9012": ["\u653f\u7b56", "\u6cd5\u89c4", "\u56fd\u52a1\u9662", "\u5de5\u4fe1\u90e8", "\u53d1\u6539\u59d4", "\u76d1\u7ba1", "\u5907\u6848", "\u6cbb\u7406", "\u89c4\u5212", "\u6807\u51c6", "\u90e8\u59d4", "\u653f\u5e9c", "\u6cd5\u5f8b", "\u6761\u4f8b"],
    "\u4ed6\u5c71\u4e4b\u77f3": ["\u6df1\u5733", "\u4e0a\u6d77", "\u5317\u4eac", "\u676d\u5dde", "\u8bd5\u70b9", "\u793a\u8303\u533a", "\u533a\u57df", "\u5730\u65b9", "\u57ce\u5e02", "\u7279\u533a", "\u65b0\u533a", "\u7ca4\u6e2f\u6fb3"],
    "\u4ea7\u4e1a\u52a8\u6001": ["\u53d1\u5e03", "\u63a8\u51fa", "\u878d\u8d44", "\u6536\u8d2d", "\u4e0a\u5e02", "\u4ea7\u54c1", "\u6280\u672f", "\u7a81\u7834", "\u6a21\u578b", "\u7b97\u529b", "\u82af\u7247", "\u5f00\u6e90", "\u5546\u7528", "\u4f01\u4e1a", "\u516c\u53f8"],
    "\u7efc\u5408\u5173\u6ce8": ["\u4f26\u7406", "\u5b89\u5168", "\u533b\u7597", "\u6559\u80b2", "\u5c31\u4e1a", "\u793e\u4f1a", "\u7814\u7a76", "\u8bba\u6587", "\u5cf0\u4f1a", "\u4f1a\u8bae", "\u4eba\u624d", "\u5e94\u7528"]
};

var MODULE_DESC = {
    "\u653f\u58f0\u4f20\u9012": "\u653f\u5e9c\u653f\u7b56\u3001\u6cd5\u89c4\u3001\u9876\u5c42\u8bbe\u8ba1\u3001\u90e8\u59d4\u52a8\u6001",
    "\u4ed6\u5c71\u4e4b\u77f3": "\u5916\u5730\u533a/\u57ce\u5e02\u7ecf\u9a8c\u3001\u8bd5\u70b9\u793a\u8303\u3001\u533a\u57df\u53d1\u5c55",
    "\u4ea7\u4e1a\u52a8\u6001": "\u4f01\u4e1a\u4ea7\u54c1\u53d1\u5e03\u3001\u6280\u672f\u7a81\u7834\u3001\u5e02\u573a\u878d\u8d44\u3001\u884c\u4e1a\u4f1a\u8bae",
    "\u7efc\u5408\u5173\u6ce8": "\u5176\u4ed6 AI \u76f8\u5173\u65b0\u95fb"
};

var MODULE_ORDER = ["\u653f\u58f0\u4f20\u9012", "\u4ed6\u5c71\u4e4b\u77f3", "\u4ea7\u4e1a\u52a8\u6001", "\u7efc\u5408\u5173\u6ce8"];

var allNewsItems = [];

function init() {
    updateDate();
    showDownloadButtons(false);
    console.log("AI News Navigator Ready");
}

function fetchLiveNews() {
    var btn = document.getElementById("btnFetch");
    btn.disabled = true;
    btn.textContent = "\u6b63\u5728\u6293\u53d6\u4e2d...";
    showLoading(true);

    var promises = RSS_SOURCES.map(function(source) {
        return fetchSingleFeed(source).catch(function(e) {
            console.warn("Failed: " + source.name + " - " + e.message);
            return [];
        });
    });

    Promise.all(promises).then(function(results) {
        var allItems = [];
        for (var i = 0; i < results.length; i++) {
            allItems = allItems.concat(results[i]);
        }

        allNewsItems = filterThisWeek(allItems);
        var data = buildDataStructure(allNewsItems);
        renderAll(data);

        btn.disabled = false;
        btn.textContent = "\u5237\u65b0\u7b80\u62a5";
        showLoading(false);
        showDownloadButtons(true);
    }).catch(function(e) {
        console.error("Fetch failed:", e);
        btn.disabled = false;
        btn.textContent = "\u83b7\u53d6\u672c\u5468AI\u7b80\u62a5";
        showLoading(false);
        alert("\u6293\u53d6\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u540e\u91cd\u8bd5");
    });
}

function fetchSingleFeed(source) {
    var proxyUrl = CORS_PROXIES[0] + encodeURIComponent(source.url);
    return fetch(proxyUrl).then(function(response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.text();
    }).then(function(xmlText) {
        return parseRSS(xmlText, source.name);
    }).catch(function() {
        var proxyUrl2 = CORS_PROXIES[1] + encodeURIComponent(source.url);
        return fetch(proxyUrl2).then(function(r) {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.text();
        }).then(function(xmlText) {
            return parseRSS(xmlText, source.name);
        });
    });
}

function parseRSS(xmlText, sourceName) {
    var parser = new DOMParser();
    var doc = parser.parseFromString(xmlText, "text/xml");
    var items = doc.querySelectorAll("item");
    var result = [];

    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var title = getTagText(item, "title");
        var link = getTagText(item, "link");
        var desc = getTagText(item, "description") || getTagText(item, "content:encoded") || "";
        var pubDate = getTagText(item, "pubDate") || getTagText(item, "dc:date") || "";

        if (title && title.trim()) {
            result.push({
                title: title.trim(),
                source: sourceName,
                summary: cleanHTML(desc).substring(0, 250),
                link: link,
                publishedAt: pubDate
            });
        }
    }
    return result;
}

function getTagText(parent, tagName) {
    var els = parent.getElementsByTagName(tagName);
    if (els.length > 0 && els[0].textContent) {
        return els[0].textContent;
    }
    return "";
}

function cleanHTML(text) {
    if (!text) return "";
    var tmp = document.createElement("div");
    tmp.innerHTML = text;
    return (tmp.textContent || tmp.innerText || "").replace(/\s+/g, " ").trim();
}

function filterThisWeek(items) {
    var now = new Date();
    var weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    var result = [];

    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (!item.publishedAt) {
            result.push(item);
            continue;
        }
        try {
            var d = new Date(item.publishedAt);
            if (!isNaN(d.getTime()) && d >= weekAgo) {
                result.push(item);
            }
        } catch (e) {
            result.push(item);
        }
    }
    return result;
}

function categorize(title, summary) {
    var text = (title + " " + summary).toLowerCase();
    var best = "\u7efc\u5408\u5173\u6ce8";
    var bestScore = 0;

    for (var i = 0; i < MODULE_ORDER.length; i++) {
        var name = MODULE_ORDER[i];
        var score = 0;
        var keywords = MODULE_KEYWORDS[name];
        for (var j = 0; j < keywords.length; j++) {
            if (text.indexOf(keywords[j]) >= 0) score++;
        }
        if (score > bestScore) {
            bestScore = score;
            best = name;
        }
    }
    return best;
}

function scoreItem(item) {
    var text = item.title + " " + item.summary;
    var score = 0;
    var highWords = ["\u7a81\u7834", "\u91cd\u5927", "\u91cc\u7a0b\u7891", "\u9996\u4e2a", "\u5f00\u6e90", "\u91cd\u78c5", "\u53d1\u5e03", "\u63a8\u51fa", "\u8ba4\u8bc1", "\u83b7\u6279", "\u9996\u6b21", "\u9886\u5148", "\u5927\u5e45", "\u5347\u7ea7"];
    for (var i = 0; i < highWords.length; i++) {
        if (text.indexOf(highWords[i]) >= 0) score += 2;
    }
    if (item.link) score += 1;
    return score;
}

function generateOverview(items) {
    var scored = items.map(function(item) {
        return { item: item, score: scoreItem(item) };
    });
    scored.sort(function(a, b) { return b.score - a.score; });

    var top = scored.slice(0, 6);
    return top.map(function(s) {
        var summary = s.item.summary;
        if (summary.length > 80) summary = summary.substring(0, 80) + "...";
        return s.item.title + "\uff1a" + summary;
    });
}

function buildDataStructure(items) {
    var modules = {};
    for (var i = 0; i < MODULE_ORDER.length; i++) {
        modules[MODULE_ORDER[i]] = [];
    }

    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var moduleName = categorize(item.title, item.summary);
        if (modules[moduleName] && modules[moduleName].length < 5) {
            modules[moduleName].push(item);
        }
    }

    var overview = generateOverview(items);

    var now = new Date();
    var year = now.getFullYear();
    var weekNum = getWeekNumber(now);

    return {
        week: year + "\u5e74\u7b2c" + weekNum + "\u5468",
        dateRange: getWeekDateRange(),
        overview: overview,
        modules: MODULE_ORDER.map(function(name) {
            return {
                name: name,
                description: MODULE_DESC[name],
                news: modules[name]
            };
        })
    };
}

function getWeekNumber(d) {
    var onejan = new Date(d.getFullYear(), 0, 1);
    return Math.ceil(((d - onejan) / 86400000 + onejan.getDay() + 1) / 7);
}

function getWeekDateRange() {
    var now = new Date();
    var start = new Date(now.getTime() - now.getDay() * 24 * 60 * 60 * 1000);
    var end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
    return formatDate(start) + " \u81f3 " + formatDate(end);
}

function formatDate(d) {
    return d.getFullYear() + "-" + padZero(d.getMonth() + 1) + "-" + padZero(d.getDate());
}

function padZero(n) {
    return n < 10 ? "0" + n : "" + n;
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

function renderAll(data) {
    var main = document.getElementById("mainContent");
    var html = "";

    if (data.overview && data.overview.length > 0) {
        html += '<div class="overview-section">';
        html += '<h2 class="module-title overview-title">\u5168\u5c40\u603b\u89c8</h2>';
        html += '<p class="overview-desc">\u672c\u5468\u6700\u91cd\u8981 AI \u65b0\u95fb\u901f\u89c8</p>';
        html += '<ul class="overview-list">';
        for (var i = 0; i < data.overview.length; i++) {
            html += '<li class="overview-item">' + escapeHtml(data.overview[i]) + '</li>';
        }
        html += '</ul>';
        html += '</div>';
    }

    for (var i = 0; i < data.modules.length; i++) {
        var module = data.modules[i];
        html += '<div class="module-section">';
        html += '<h2 class="module-title">' + escapeHtml(module.name) + '</h2>';

        if (module.news && module.news.length > 0) {
            for (var j = 0; j < module.news.length; j++) {
                html += renderNewsItem(module.news[j]);
            }
        } else {
            html += '<div class="news-item"><p class="no-news">\u672c\u5468\u6682\u65e0\u76f8\u5173\u65b0\u95fb</p></div>';
        }
        html += '</div>';
    }

    main.innerHTML = html;
}

function renderNewsItem(item) {
    var html = '<div class="news-item">';
    html += '<div class="news-header">';
    html += '<span class="news-title">' + escapeHtml(item.title) + '</span>';
    html += '<span class="badge badge-source">' + escapeHtml(item.source) + '</span>';
    html += '</div>';
    html += '<p class="news-summary">' + escapeHtml(item.summary) + '</p>';
    if (item.link) {
        html += '<a href="' + escapeHtml(item.link) + '" target="_blank" rel="noopener" class="news-link">\u9605\u8bfb\u539f\u6587 \u2192</a>';
    }
    html += '</div>';
    return html;
}

function updateDate() {
    var now = new Date();
    var weekDays = ["\u65e5", "\u4e00", "\u4e8c", "\u4e09", "\u56db", "\u4e94", "\u516d"];
    var dateStr = now.getFullYear() + "\u5e74" + (now.getMonth() + 1) + "\u6708" + now.getDate() + "\u65e5 \u661f\u671f" + weekDays[now.getDay()];
    var el = document.getElementById("dateDisplay");
    if (el) el.textContent = dateStr;
    var footer = document.getElementById("footerDate");
    if (footer) footer.textContent = dateStr;
}

function showLoading(show) {
    var main = document.getElementById("mainContent");
    if (show) {
        main.innerHTML = '<div class="loading"><div class="spinner"></div><p>\u6b63\u5728\u4ece\u591a\u4e2a RSS \u6e90\u6293\u53d6 AI \u65b0\u95fb...</p></div>';
    }
}

function showDownloadButtons(show) {
    var pdfBtn = document.getElementById("btnDownloadPdf");
    var mp4Btn = document.getElementById("btnDownloadMp4");
    var listenBtn = document.getElementById("btnListen");
    if (pdfBtn) pdfBtn.style.display = show ? "inline-flex" : "none";
    if (mp4Btn) mp4Btn.style.display = show ? "inline-flex" : "none";
    if (listenBtn) listenBtn.style.display = show ? "inline-flex" : "none";
}

function downloadPdf() {
    window.print();
}

function downloadMp4() {
    var link = document.createElement("a");
    link.href = "downloads/ai_news_brief.mp4";
    link.download = "ai_news_brief.mp4";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

var isListening = false;
var speechSynthesis = window.speechSynthesis || window.webkitSpeechSynthesis;
var currentUtterance = null;

function toggleListen() {
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

function startListening() {
    if (allNewsItems.length === 0) {
        alert("\u8bf7\u5148\u83b7\u53d6\u65b0\u95fb\u7b80\u62a5");
        return;
    }
    var text = generateSpeechText();
    if (!text) return;

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = "zh-CN";
    currentUtterance.rate = 1.0;

    currentUtterance.onstart = function() {
        isListening = true;
        updateListenButton(true);
    };
    currentUtterance.onend = function() {
        isListening = false;
        updateListenButton(false);
    };
    currentUtterance.onerror = function() {
        isListening = false;
        updateListenButton(false);
    };

    speechSynthesis.speak(currentUtterance);
}

function stopListening() {
    speechSynthesis.cancel();
    isListening = false;
    updateListenButton(false);
}

function updateListenButton(listening) {
    var btn = document.getElementById("btnListen");
    var icon = document.getElementById("audioIcon");
    var text = document.getElementById("audioText");
    if (listening) {
        btn.classList.add("listening");
        icon.textContent = "\ud83d\udd07";
        text.textContent = "\u505c\u6b62\u6717\u8bfb";
    } else {
        btn.classList.remove("listening");
        icon.textContent = "\ud83d\udd0a";
        text.textContent = "\u6717\u8bfb\u7b80\u62a5";
    }
}

function generateSpeechText() {
    var text = "AI \u65b0\u95fb\u5468\u62a5\u3002";
    for (var i = 0; i < allNewsItems.length; i++) {
        text += allNewsItems[i].title + "\u3002";
        text += allNewsItems[i].summary + "\u3002";
    }
    return text;
}

window.onload = init;
