"""
███╗   ███╗██╗██╗     ██╗      ██████╗ ███████╗███████╗██╗  ██╗██████╗ ███████╗
████╗ ████║██║██║     ██║      ██╔══██╗██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝
██╔████╔██║██║██║     ██║█████╗██████╔╝█████╗  █████╗  ███████║██████╔╝█████╗  
██║╚██╔╝██║██║██║     ██║╚════╝██╔══██╗██╔══╝  ██╔══╝  ██╔══██║██╔══██╗██╔══╝  
██║ ╚═╝ ██║██║███████╗███████╗ ██║  ██║███████╗███████╗██║  ██║██║  ██║███████╗
╚═╝     ╚═╝╚═╝╚══════╝╚══════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

[النظام: MILLISECOND BOOT AI]
[الميزات: Lazy Loading + 1GB RAM Cache + Self-Healing + 16-Core Optimization]
"""

import asyncio
import os
import re
import logging
import time
import random
# (ملاحظة: لا نستدعي المكتبات الثقيلة هنا لتسريع الإقلاع)

# === إعدادات اللوج ===
def LOGGER(name): return logging.getLogger(name)
LOG = LOGGER("YouTube_Core")
logging.basicConfig(level=logging.ERROR)

# === دوال المساعدة (Mock Utils) ===
try:
    from BrandrdXMusic.utils.formatters import time_to_seconds
except ImportError:
    def time_to_seconds(t): return 0

class Config:
    DOWNLOAD_PATH = "downloads"
    # استغلال الـ 16 نواة بالكامل
    MAX_WORKERS = 200 
    SERVERS = [
        {"url": "https://shrutibots.site", "weight": 10},
        {"url": "https://myapi-i-bwca.fly.dev", "weight": 100},
    ]

if not os.path.exists(Config.DOWNLOAD_PATH):
    os.makedirs(Config.DOWNLOAD_PATH)

# =======================================================================
# 🧠 CyberBrain: العقل المدبر (يعمل عند الحاجة فقط)
# =======================================================================
class CyberBrain:
    def __init__(self):
        # الترتيب: سرعة قصوى (Aria) -> تخفي (Android) -> توافق (iOS)
        self.strategies = ["TURBO_ARIA", "STEALTH_ANDROID", "LEGACY_IOS"]
        
    def analyze(self, error_msg: str) -> str:
        e = str(error_msg).lower()
        if any(x in e for x in ["403", "forbidden", "refused", "errorcode=22"]):
            return "NETWORK_BAN"
        if any(x in e for x in ["sign in", "cookies", "private"]):
            return "AUTH_ERROR"
        if any(x in e for x in ["fragment", "empty", "0 byte", "directory"]):
            return "DATA_CORRUPTION"
        return "UNKNOWN"

    def next_strategy(self, current, diagnosis):
        # لو المشكلة شبكة (403) مع Aria، الحل هو الهروب لـ Native Android
        if diagnosis == "NETWORK_BAN" and current == "TURBO_ARIA":
            return "STEALTH_ANDROID"
        try:
            idx = self.strategies.index(current)
            if idx + 1 < len(self.strategies): return self.strategies[idx + 1]
        except: pass
        return None

# =======================================================================
# 🚀 الكلاس الرئيسي (مصمم للإقلاع الفوري)
# =======================================================================
class YouTubeAPI:
    def __init__(self):
        # لا نقوم بأي عمليات ثقيلة هنا لضمان الإقلاع في Milliseconds
        self.base = "https://www.youtube.com/watch?v="
        self.brain = None # سيتم تحميله لاحقاً
        self.pool = None  # سيتم تحميله لاحقاً
        self._aria_checked = False
        self._has_aria = False

    async def _lazy_init(self):
        """تحميل الأدوات الثقيلة فقط عند أول استخدام"""
        if not self.pool:
            from concurrent.futures import ThreadPoolExecutor
            self.pool = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)
        if not self.brain:
            self.brain = CyberBrain()
        if not self._aria_checked:
            self._has_aria = os.system("which aria2c > /dev/null 2>&1") == 0
            self._aria_checked = True

    def _cleanup(self, path=None):
        """تنظيف ذكي للملفات"""
        try:
            if path and os.path.exists(path) and os.path.getsize(path) == 0:
                os.remove(path)
            # تنظيف المخلفات العامة
            for f in os.listdir(Config.DOWNLOAD_PATH):
                p = os.path.join(Config.DOWNLOAD_PATH, f)
                if f.endswith((".part", ".aria2", ".ytdl")):
                    os.remove(p)
        except: pass

    def get_cookie(self):
        paths = ["BRANDBODA/cookies/BrandedXMusic.txt", "cookies.txt", "cookies/cookies.txt"]
        for p in paths:
            if os.path.exists(p): return p
        return None

    # -----------------------------------------------------------------
    # 📥 محرك التحميل الذكي
    # -----------------------------------------------------------------
    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, **kwargs) -> str:
        await self._lazy_init() # تفعيل المحرك الآن
        
        # استدعاء yt_dlp هنا فقط (Lazy Import) لتسريع تشغيل البوت
        from yt_dlp import YoutubeDL

        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        
        vid_id = str(int(time.time()))
        if "v=" in link: vid_id = link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in link: vid_id = link.split("youtu.be/")[1].split("?")[0]

        ext = "mp4" if (video or songvideo) else "m4a"
        final_path = os.path.join(Config.DOWNLOAD_PATH, f"{vid_id}.{ext}")

        # فحص سريع
        if os.path.exists(final_path) and os.path.getsize(final_path) > 1024:
            return final_path, True

        current_strategy = "TURBO_ARIA"
        
        while current_strategy:
            LOG.info(f"⚡ Strategy: {current_strategy}")
            opts = self._get_opts(current_strategy, vid_id, video or songvideo)
            
            try:
                def execute():
                    with YoutubeDL(opts) as ydl: ydl.download([link])
                
                await loop.run_in_executor(self.pool, execute)
                
                if os.path.exists(final_path) and os.path.getsize(final_path) > 1024:
                    return final_path, True
                else:
                    raise Exception("Zero Byte File")

            except Exception as e:
                diagnosis = self.brain.analyze(str(e))
                LOG.error(f"⚠️ Error: {diagnosis}")
                self._cleanup(final_path)
                current_strategy = self.brain.next_strategy(current_strategy, diagnosis)

        # Fallback API
        try:
            return await self._api_fallback(link, vid_id, final_path, video or songvideo), True
        except: return None, False

    def _get_opts(self, strategy, vid_id, is_video):
        opts = {
            "cookiefile": self.get_cookie(),
            "outtmpl": os.path.join(Config.DOWNLOAD_PATH, f"{vid_id}.%(ext)s"),
            "geo_bypass": True, "nocheckcertificate": True, "quiet": True, "source_address": "0.0.0.0"
        }
        
        # 🔥 إعدادات Aria2 للسيرفرات العملاقة (49GB RAM)
        aria_args = [
            "-c", "-x", "8", "-s", "8", "-k", "5M",
            "--disk-cache=1024M", # كاش 1 جيجا في الرام!
            "--file-allocation=none", # إقلاع فوري للتحميل
            "--header=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        if strategy == "TURBO_ARIA" and self._has_aria:
            opts["external_downloader"] = "aria2c"
            opts["external_downloader_args"] = aria_args
            opts["extractor_args"] = {"youtube": {"player_client": ["android", "web"]}}
        
        elif strategy == "STEALTH_ANDROID":
            opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
            
        elif strategy == "LEGACY_IOS":
            opts["extractor_args"] = {"youtube": {"player_client": ["ios"]}}

        opts["format"] = "best[ext=mp4]/best" if is_video else "bestaudio[ext=m4a]/bestaudio"
        return opts

    # === دوال API والبحث ===
    async def _api_fallback(self, link, vid_id, path, is_video):
        import aiohttp, ssl # Lazy Import
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        url = None
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx)) as s:
            for srv in sorted(Config.SERVERS, key=lambda x: x["weight"], reverse=True):
                try:
                    async with s.head(srv["url"], timeout=2) as r:
                        if r.status < 500: url = srv["url"]; break
                except: continue
        if not url: return None
        t = "video" if is_video else "audio"
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx)) as s:
            async with s.get(f"{url}/download", params={"url": vid_id, "type": t}, timeout=10) as r:
                if r.status != 200: return None
                d = await r.json()
                if not d.get("url"): return None
                async with s.get(d["url"], timeout=600) as stream:
                    if stream.status == 200:
                        with open(path, "wb") as f:
                            async for chunk in stream.content.iter_chunked(65536): f.write(chunk)
                        return path
        return None

    # دوال الواجهة (مثل Title, Duration)
    async def track(self, link: str, videoid=None):
        from youtubesearchpython.__future__ import VideosSearch # Lazy Import
        if videoid: link = self.base + link
        try:
            results = VideosSearch(link.split("&")[0], limit=1)
            data = (await results.next())["result"][0]
            return {"title": data["title"], "duration_min": data["duration"], "thumb": data["thumbnails"][0]["url"].split("?")[0], "vidid": data["id"]}, data["id"]
        except: return {"title": "Error", "duration_min": "0:00", "thumb": ""}, "error"

    async def details(self, link, videoid=None):
        d, i = await self.track(link, videoid)
        if i == "error": return None
        return d["title"], d["duration_min"], time_to_seconds(d["duration_min"]), d["thumb"], i
    
    # واجهات سريعة للبوت
    async def title(self, l, v=None): return (await self.details(l, v))[0]
    async def duration(self, l, v=None): return (await self.details(l, v))[1]
    async def thumbnail(self, l, v=None): return (await self.details(l, v))[3]
    
    async def url(self, message_1):
        from pyrogram.enums import MessageEntityType
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        return (message.text or message.caption)[entity.offset : entity.offset + entity.length]
        return None
    
    async def exists(self, link: str, videoid=None):
        if videoid: link = self.base + link
        return bool(re.search(r"(?:youtube\.com|youtu\.be)", link))

# =======================================================================
YouTube = YouTubeAPI()
