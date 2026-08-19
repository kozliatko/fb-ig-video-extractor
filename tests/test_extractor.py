"""Tests for detecting the source from a URL and the video length limit."""
import os

import extractor
from extractor import _resolve_cookies, duration_error, extract_source


class TestExtractSource:
    def test_facebook(self):
        assert extract_source("https://www.facebook.com/reel/123") == "facebook"

    def test_fb_watch_share_link(self):
        assert extract_source("https://fb.watch/abc123/") == "facebook"

    def test_instagram_reel(self):
        assert extract_source("https://www.instagram.com/reel/ABC/") == "instagram"

    def test_instagram_post(self):
        assert extract_source("https://www.instagram.com/p/ABC/") == "instagram"

    def test_tiktok(self):
        assert extract_source("https://www.tiktok.com/@user/video/123") == "tiktok"

    def test_tiktok_share_link(self):
        assert extract_source("https://vm.tiktok.com/ZM123abc/") == "tiktok"

    def test_youtube_shorts(self):
        assert extract_source("https://www.youtube.com/shorts/xyz") == "youtube"

    def test_youtube_short_link(self):
        assert extract_source("https://youtu.be/xyz") == "youtube"

    def test_unknown(self):
        assert extract_source("https://vimeo.com/12345") == "unknown"


class TestDurationError:
    def test_short_video_ok(self):
        assert duration_error({"duration": 90}) is None

    def test_at_limit_ok(self):
        assert duration_error({"duration": extractor.MAX_VIDEO_MINUTES * 60}) is None

    def test_too_long_rejected(self):
        err = duration_error({"duration": 2 * 3600})
        assert err is not None
        assert "příliš dlouhé" in err
        assert "120 min" in err

    def test_unknown_duration_passes(self):
        # a live stream / missing metadata must not block the video
        assert duration_error({}) is None
        assert duration_error({"duration": None}) is None

    def test_limit_zero_disables_check(self, monkeypatch):
        monkeypatch.setattr(extractor, "MAX_VIDEO_MINUTES", 0)
        assert duration_error({"duration": 10 * 3600}) is None


class TestResolveCookies:
    def _clear_env(self, monkeypatch):
        monkeypatch.setattr(extractor, "_cookie_path_cache", None)
        for var in ("COOKIES_FILE", "INSTAGRAM_COOKIES", "INSTAGRAM_SESSIONID"):
            monkeypatch.delenv(var, raising=False)

    def test_none_configured(self, monkeypatch):
        self._clear_env(monkeypatch)
        assert _resolve_cookies() is None

    def test_sessionid_builds_netscape_cookie_file(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("INSTAGRAM_SESSIONID", "abc123")
        path = _resolve_cookies()
        assert path and os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert ".instagram.com" in content
        assert "sessionid" in content
        assert "abc123" in content

    def test_instagram_cookies_takes_priority_over_sessionid(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("INSTAGRAM_COOKIES", "# Netscape HTTP Cookie File\nfull export")
        monkeypatch.setenv("INSTAGRAM_SESSIONID", "abc123")
        path = _resolve_cookies()
        content = open(path, encoding="utf-8").read()
        assert content == "# Netscape HTTP Cookie File\nfull export"
