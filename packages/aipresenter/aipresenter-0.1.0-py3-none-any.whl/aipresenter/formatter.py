import uuid
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from .code_theme import get_css, get_js

class AIPresenter:
    def __init__(self):
        # Enable tables support in Markdown
        self.md = MarkdownIt("commonmark").enable("table")

    def _highlight_code(self, code, lang):
        try:
            lexer = get_lexer_by_name(lang)
        except:
            lexer = guess_lexer(code)
        
        formatter = HtmlFormatter(nowrap=True)
        highlighted = highlight(code, lexer, formatter)
        
        # Unique ID for JavaScript to find this specific block
        unique_id = f"code-{uuid.uuid4().hex[:8]}"
        
        # SVG Icon for the Copy Button
        copy_icon = """
        <svg viewBox="0 0 24 24">
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
        """
        
        return f"""
        <div class="code-container">
            <div class="editor-header">
                <div class="dots-container">
                    <div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div>
                </div>
                <div style="display:flex; gap:10px; align-items:center;">
                    <span class="lang-label">{lang.upper() if lang else 'TEXT'}</span>
                    <button class="copy-btn" onclick="copyToClipboard(this, '{unique_id}')" title="Copy to Clipboard">
                        {copy_icon}
                    </button>
                </div>
            </div>
            <div class="code-content" id="{unique_id}"><pre><code>{highlighted}</code></pre></div>
        </div>
        """

    def format(self, raw_text):
        # 1. Custom Parsing loop to detect code blocks manually
        # This gives us full control over the "Editor" styling
        parts = raw_text.split("```")
        final_html = ""
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Even parts are normal text
                if part.strip():
                    final_html += self.md.render(part)
            else:
                # Odd parts are code blocks
                lines = part.split("\n", 1)
                lang = lines[0].strip()
                # If there's code content, use it; otherwise empty string
                code = lines[1] if len(lines) > 1 else ""
                final_html += self._highlight_code(code, lang)

        # 2. Wrap everything in our Main Container + CSS + JS
        full_document = f"""
        <div class="ai-wrapper">
            {get_css()}
            {final_html}
            {get_js()}
        </div>
        """
        return full_document