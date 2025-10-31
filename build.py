import os
import shutil
import re

def extract_pdf_text(pdf_path):
    try:
        import PyPDF2
    except Exception:
        return None
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            texts = []
            # Extract up to first 10 pages to avoid overly long content
            for i, page in enumerate(reader.pages[:10]):
                t = page.extract_text() or ''
                texts.append(t)
            text = '\n'.join(texts)
            # Basic cleanup: collapse whitespace
            text = re.sub(r'\r', '', text)
            text = re.sub(r'[\t ]+', ' ', text)
            text = re.sub(r'\n{2,}', '\n\n', text)
            return text.strip()
    except Exception:
        return None

def to_paragraphs(text):
    if not text: return []
    parts = [p.strip() for p in text.split('\n') if p.strip()]
    # Limit total length roughly
    combined = []
    length = 0
    for p in parts:
        combined.append(p)
        length += len(p)
        if length > 8000:
            break
    return combined

def render_blog_page(title, paragraphs):
    body_html = '\n'.join(f'<p>{escape_html(p)}</p>' for p in paragraphs) if paragraphs else '<p>Unable to extract text. Please download the PDF below.</p>'
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape_html(title)} - Carbon Compass</title>
  <link rel="icon" type="image/png" href="/image/cacbonfavicon.png?v=3" />
  <link rel="stylesheet" href="/style.css?v=3" />
</head>
<body>
  <header>
    <div class="brand">
      <img src="/image/cacbonlogo.png?v=3" alt="Carbon Compass logo" />
      <div>
        <h1>Carbon Compass</h1>
        <p>Upload a file to analysis</p>
      </div>
    </div>
    <nav class="menu">
      <a href="/" class="menu-link">Home</a>
      <a href="/about.html" class="menu-link{ ' active' if title=='About' else '' }">About</a>
      <a href="/cbam.html" class="menu-link{ ' active' if title=='CBAM' else '' }">CBAM</a>
      <a href="/faq.html" class="menu-link{ ' active' if title=='FAQ' else '' }">FAQ</a>
    </nav>
  </header>
  <main class="container">
    <section class="card">
      <h2>{escape_html(title)}</h2>
      <div class="blog-content">
        {body_html}
        <div style="margin-top:16px">
          <a href="/{escape_html(title)}.pdf" target="_blank">Tải PDF gốc</a>
        </div>
      </div>
    </section>
  </main>
</body>
</html>'''

def escape_html(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')

FILES = ['style.css', 'app.js', 'About.pdf', 'CBAM.pdf', 'FAQ.pdf']

def ensure_clean_dist():
    # Preserve existing dist folder to keep manually edited pages.
    # Only ensure the directory exists without deleting its contents.
    os.makedirs(DIST, exist_ok=True)

def build_index():
    src = os.path.join(ROOT, 'index.html')
    dst = os.path.join(DIST, 'index.html')
    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()
    # Inject API base if provided via environment for static hosting
    api_base = os.environ.get('API_BASE')
    if api_base:
        html = html.replace('window.API_BASE = ""', f'window.API_BASE = "{api_base}"')
    # Use relative asset paths in dist
    html = html.replace('href="/style.css', 'href="style.css')
    html = html.replace('src="/app.js', 'src="app.js')
    html = html.replace('href="/image/', 'href="image/')
    html = html.replace('src="/image/', 'src="image/')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)

def copy_assets():
    for name in FILES:
        shutil.copy2(os.path.join(ROOT, name), os.path.join(DIST, name))
    # copy image directory if exists
    img_src = os.path.join(ROOT, 'image')
    img_dst = os.path.join(DIST, 'image')
    if os.path.isdir(img_src):
        if os.path.exists(img_dst):
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)

def build_blog_pages():
    items = [
        ('About', os.path.join(ROOT, 'About.pdf'), os.path.join(DIST, 'about.html')),
        ('CBAM', os.path.join(ROOT, 'CBAM.pdf'), os.path.join(DIST, 'cbam.html')),
        ('FAQ', os.path.join(ROOT, 'FAQ.pdf'), os.path.join(DIST, 'faq.html')),
    ]
    for title, pdf_path, out_html in items:
        # If the output HTML already exists (manually edited), keep it intact.
        if os.path.exists(out_html):
            # Skip regeneration to preserve manual edits
            continue
        text = extract_pdf_text(pdf_path)
        paragraphs = to_paragraphs(text)
        html = render_blog_page(title, paragraphs)
        with open(out_html, 'w', encoding='utf-8') as f:
            f.write(html)

def main():
    ensure_clean_dist()
    build_index()
    build_blog_pages()
    copy_assets()
    print('Build completed. Output folder:', DIST)

if __name__ == '__main__':
    main()