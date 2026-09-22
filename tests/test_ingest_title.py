"""真实批次暴露的订阅横幅误作标题问题。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ingest_source import extract_html_title


def test_newsletter_banner_is_not_article_title():
    html = '<html><head><meta property="og:title" content="Agent evals &amp; testing"></head><body>Get the developer newsletter<h1>Agent evals</h1></body></html>'
    assert extract_html_title(html) == 'Agent evals & testing'


def test_heading_fallback_and_missing_title():
    assert extract_html_title('<h1>Building <em>effective</em> agents</h1>') == 'Building effective agents'
    assert extract_html_title('<p>Get the developer newsletter</p>') == ''
