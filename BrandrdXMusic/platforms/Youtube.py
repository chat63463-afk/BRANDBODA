"""
███████╗███████╗██████╗ ██╗  ██╗██╗███╗   ██╗███████╗████████╗███████╗██╗███╗   ██╗
██╔════╝██╔════╝██╔══██╗██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝██║████╗  ██║
███████╗█████╗  ██████╔╝███████║██║██╔██╗ ██║███████╗   ██║   █████╗  ██║██╔██╗ ██║
╚════██║██╔══╝  ██╔══██╗██╔══██║██║██║╚██╗██║╚════██║   ██║   ██╔══╝  ██║██║╚██╗██║
███████║███████╗██║  ██║██║  ██║██║██║ ╚████║███████║   ██║   ███████╗██║██║ ╚████║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝╚═╝  ╚═══╝

[النظام: المدمرة الشاملة - The Destroyer Edition V2]
[الميزات: Anti-Ban Hydra System + Multi-Client Spoofing + Smart Cookie Path]
[الحالة: Overclocked & Unlocked]
"""

import asyncio
import os
import re
import json
import time
import random
import logging
import ssl
import aiohttp
import shutil
from typing import Union, List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, Playlist
from yt_dlp import YoutubeDL

# =======================================================================
# ⚙️ 1. إعدادات السيرفر واللوج
# =======================================================================
try:
    from BrandrdXMusic.utils.database import is_on_off
    from BrandrdXMusic.utils.formatters import time_to_seconds
    from BrandrdXMusic import LOGGER
except ImportError:
    logging.basicConfig(level=logging.ERROR)
    def LOGGER(name): return logging.getLogger(name)
    async def is_on_off(x): return True
    def time_to_seconds(t): return 0

# إسكات المكتبات المزعجة
logging.getLogger("yt_dlp").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
LOG = LOGGER("YouTube_Destroyer")

class Config:
    DOWNLOAD_PATH = "downloads"
    MAX_WORKERS = 50 # زيادة عدد العمال للسرعة القصوى
    SERVERS = [
        {"url": "https://shrutibots.site", "weight": 10},
        {"url": "https://myapi-i-bwca.fly.dev", "weight": 100},
    ]

if not os.path.exists(Config.DOWNLOAD_PATH):
    os.makedirs(Config.DOWNLOAD_PATH)

# =======================================================================
# 🧠 2. نظام الكاش
# =======================================================================
_cache: Dict[str, Tuple[float, List[Dict]]] = {}
_cache_lock = asyncio.Lock()
YOUTUBE_META_TTL = 3600

# =======================================================================
# 🛠️ 3. أدوات ذكية (الكوكيز والمسارات)
# =======================================================================

def get_cookie():
    """
    نظام تحديد الكوكيز الذكي - يبحث في مسارك الخاص أولاً
    """
    # 1. المسار الخاص بك (الأولوية القصوى)
    custom_path = "BRANDBODA/cookies/BrandedXMusic.txt"
    if os.path.exists(custom_path):
        return custom_path

    # 2. المسار الجذري (الافتراضي)
    if os.path.exists("cookies.txt"):
        return "cookies.txt"

    # 3. البحث العشوائي في مجلد cookies
    if os.path.exists("cookies"):
        files = [f for f in os.listdir("cookies") if f.endswith(".txt")]
        if files: return os.path.join("cookies", random.choice(files))
    
    return None

def clean_file(path):
    try:
        if os.path.exists(path): os.remove(path)
        for ext in [".aria2", ".part", ".ytdl", ".meta"]:
            if os.path.exists(path + ext): os.remove(path + ext)
    except: pass

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

# =======================================================================
# 🚀 4. الكلاس الرئيسي (The Monster Class)
# =======================================================================
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.pool = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)
        self.has_aria2 = os.system("which aria2c > /dev/null 2>&1") == 0

        # تنظيف أولي سريع
        try:
            for f in os.listdir(Config.DOWNLOAD_PATH):
                if f.endswith(".part"): os.remove(os.path.join(Config.DOWNLOAD_PATH, f))
        except: pass

    # -----------------------------------------------------------------
    # 🔗 معالجة الروابط
    # -----------------------------------------------------------------
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset: break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None if offset in (None,) else text[offset : offset + length]

    # -----------------------------------------------------------------
    # 🔍 البحث (سريع جداً مع الكاش)
    # -----------------------------------------------------------------
    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        link = link.split("&")[0]

        async with _cache_lock:
            if link in _cache:
                ts, val = _cache[link]
                if time.time() - ts < YOUTUBE_META_TTL:
                    return val[0], val[1]

        try:
            results = VideosSearch(link, limit=1)
            data = (await results.next())["result"][0]
            track_details = {
                "title": data["title"],
                "link": data["link"],
                "vidid": data["id"],
                "duration_min": data["duration"],
                "thumb": data["thumbnails"][0]["url"].split("?")[0],
                "cookiefile": get_cookie(),
            }
            async with _cache_lock:
                _cache[link] = (time.time(), (track_details, data["id"]))
            return track_details, data["id"]
        except Exception:
            return {"title": "Error", "link": link, "vidid": "error", "duration_min": "0:00", "thumb": ""}, "error"

    async def details(self, link: str, videoid: Union[bool, str] = None):
        d, i = await self.track(link, videoid)
        if i == "error": return None
        return d["title"], d["duration_min"], time_to_seconds(d["duration_min"]), d["thumb"], i

    async def title(self, link: str, videoid: Union[bool, str] = None):
        d, _ = await self.track(link, videoid)
        return d.get("title")

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        d, _ = await self.track(link, videoid)
        return d.get("duration_min")

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        d, _ = await self.track(link, videoid)
        return d.get("thumb")

    # -----------------------------------------------------------------
    # 📥 محرك التحميل النووي (Hydra Engine)
    # -----------------------------------------------------------------
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()

        if "v=" in link: vid_id = link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in link: vid_id = link.split("youtu.be/")[1].split("?")[0]
        else: vid_id = str(int(time.time()))

        safe_title = re.sub(r'[\\/*?:"<>|]', "", title if title else vid_id)
        final_path_ext = "mp4" if (video or songvideo) else "m4a"
        final_path = os.path.join(Config.DOWNLOAD_PATH, f"{vid_id}.{final_path_ext}")

        # التحقق السريع في الملفات الموجودة
        if os.path.exists(final_path):
            return final_path, True

        # === استراتيجيات التجاوز (The Bypass Strategies) ===
        # نحاول بـ 3 طرق: أندرويد (الأقوى)، ثم iOS، ثم الويب
        strategies = ["android", "ios", "web"]
        
        # إعدادات Aria2 للسرعة القصوى
        aria2_args = [
            "-x", "16", "-s", "16", "-k", "1M", "--max-connection-per-server=16"
        ]

        def get_opts(strategy_name):
            cookie = get_cookie()
            opts = {
                "cookiefile": cookie,
                "outtmpl": f"downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                # إجبار IPv4 لتفادي حظر الداتا سنتر
                "source_address": "0.0.0.0", 
            }
            
            # تفعيل Aria2 إذا وجد
            if self.has_aria2:
                opts["external_downloader"] = "aria2c"
                opts["external_downloader_args"] = aria2_args

            # تخصيص العميل (Client Spoofing)
            if strategy_name == "android":
                opts["extractor_args"] = {
                    "youtube": {
                        "player_client": ["android", "web"],
                        "player_skip": ["configs", "webpage"],
                    }
                }
            elif strategy_name == "ios":
                opts["extractor_args"] = {"youtube": {"player_client": ["ios"]}}
            
            # تحديد الصيغة
            if video or songvideo:
                opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
                opts["merge_output_format"] = "mp4"
            else:
                opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
            
            return opts

        # === حلقة المحاولة (Retry Loop) ===
        for strategy in strategies:
            try:
                def run_dl():
                    opts = get_opts(strategy)
                    with YoutubeDL(opts) as ydl:
                        ydl.download([link])
                
                # تنفيذ التحميل
                await loop.run_in_executor(self.pool, run_dl)
                
                # التحقق من نجاح التحميل (البحث عن الملف بأي امتداد محتمل)
                for f in os.listdir(Config.DOWNLOAD_PATH):
                    if f.startswith(vid_id) and not f.endswith(".part"):
                        return os.path.join(Config.DOWNLOAD_PATH, f), True
                        
            except Exception as e:
                # لو فشلت استراتيجية نكمل للي بعدها
                continue

        # === الحل الأخير: API Fallback ===
        try:
            res = await self._api_download_fallback(link, vid_id, final_path, video or songvideo)
            if res: return res, True
        except:
            pass

        return None, False

    async def _api_download_fallback(self, link, vid_id, path, is_video):
        """تحميل الطوارئ من سيرفرات خارجية"""
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
                dl_url = d.get("url")
                if not dl_url: return None
                
                async with s.get(dl_url, timeout=600) as stream:
                    if stream.status == 200:
                        with open(path, "wb") as f:
                            async for chunk in stream.content.iter_chunked(65536):
                                f.write(chunk)
                        return path
        return None

    # -----------------------------------------------------------------
    # 📺 وظائف إضافية
    # -----------------------------------------------------------------
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        # محاولة استخراج رابط مباشر
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", str(get_cookie()), # تحويل None لـ str لتفادي الخطأ
            "-g", "-f", "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        cmd = (
            f"yt-dlp -i --compat-options no-youtube-unavailable-videos "
            f"--get-id --flat-playlist --playlist-end {limit} --skip-download '{link}' "
            f"2>/dev/null"
        )
        playlist = await shell_cmd(cmd)
        return [key for key in playlist.split("\n") if key]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        
        opts = {"quiet": True, "cookiefile": get_cookie()}
        ydl = YoutubeDL(opts)
        
        with ydl:
            formats_available = []
            try:
                r = ydl.extract_info(link, download=False)
                for format in r.get("formats", []):
                    if not format.get("filesize"): continue
                    formats_available.append({
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format.get("format_note", ""),
                        "yturl": link,
                        "cookiefile": get_cookie(),
                    })
            except: pass
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            a = VideosSearch(link, limit=10)
            result = (await a.next()).get("result")
            r = result[query_type]
            return r["title"], r["duration"], r["thumbnails"][0]["url"].split("?")[0], r["id"]
        except:
            return "Error", "0", "", "error"

# =======================================================================
# 🏁 التصدير النهائي
# =======================================================================
YouTube = YouTubeAPI()
