def get_css():
    """Returns premium CSS for a Gemini-like UI with icon-based buttons."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;700&display=swap');

        :root {
            --bg-card: #ffffff;
            --text-primary: #1f1f1f;
            --text-secondary: #424242;
            --accent-color: #4facfe;
            --code-bg: #1e1e1e;
            --border-radius: 12px;
        }

        .ai-wrapper {
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            line-height: 1.7;
            font-size: 16px;
        }

        /* --- TYPOGRAPHY --- */
        .ai-wrapper h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(90deg, #0052D4, #4364F7, #6FB1FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        .ai-wrapper h2 {
            font-size: 22px;
            color: #333;
            border-left: 4px solid var(--accent-color);
            padding-left: 12px;
            margin-top: 25px;
        }

        .ai-wrapper p { margin-bottom: 15px; color: var(--text-secondary); }

        /* --- KEY POINTS & LISTS --- */
        .ai-wrapper ul, .ai-wrapper ol {
            background: #f8f9fa;
            border-radius: var(--border-radius);
            padding: 20px 40px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }
        .ai-wrapper li { margin-bottom: 8px; }

        /* --- CODE EDITOR --- */
        .code-container {
            background: var(--code-bg);
            border-radius: var(--border-radius);
            margin: 25px 0;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            position: relative;
        }
        
        .editor-header {
            background: #2d2d2d;
            padding: 8px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .dots-container { display: flex; gap: 6px; }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
        .red { background: #ff5f56; } .yellow { background: #ffbd2e; } .green { background: #27c93f; }
        
        .lang-label { color: #888; font-size: 11px; font-family: 'JetBrains Mono', monospace; letter-spacing: 1px; }

        /* --- COPY BUTTON (ICON STYLE) --- */
        .copy-btn {
            background: transparent;
            border: 1px solid #444;
            color: #ccc;
            border-radius: 6px;
            cursor: pointer;
            padding: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            width: 32px;
            height: 32px;
        }
        .copy-btn:hover {
            background: #333;
            color: white;
            border-color: #666;
        }
        .copy-btn svg {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }
        
        /* The "Copied!" green state */
        .copy-success {
            border-color: #2ecc71 !important;
            color: #2ecc71 !important;
        }

        .code-content {
            padding: 15px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #d4d4d4;
        }
        /* Pygments Overrides for better contrast */
        .code-content pre { margin: 0; }

        /* --- TABLES --- */
        .ai-wrapper table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        .ai-wrapper th { background: #f1f3f5; padding: 12px; text-align: left; font-weight: 600; }
        .ai-wrapper td { padding: 12px; border-bottom: 1px solid #eee; }
        
        /* --- BLOCKQUOTES --- */
        .ai-wrapper blockquote {
            border-left: 4px solid #6c5ce7;
            background: #f4f0ff;
            margin: 20px 0;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #555;
        }
    </style>
    """

def get_js():
    """Returns the JavaScript to make the Copy Button work with icon switching."""
    return """
    <script>
    function copyToClipboard(button, codeId) {
        const codeBlock = document.getElementById(codeId);
        const text = codeBlock.innerText;
        
        navigator.clipboard.writeText(text).then(() => {
            const originalHTML = button.innerHTML;
            button.classList.add('copy-success');
            
            // Switch to Checkmark Icon
            button.innerHTML = `
                <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            `;
            
            // Revert after 2 seconds
            setTimeout(() => {
                button.classList.remove('copy-success');
                button.innerHTML = originalHTML;
            }, 2000);
        });
    }
    </script>
    """