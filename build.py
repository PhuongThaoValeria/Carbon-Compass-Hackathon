import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')

FILES = ['style.css', 'app.js']

def ensure_clean_dist():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
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

def main():
    ensure_clean_dist()
    build_index()
    copy_assets()
    print('Build completed. Output folder:', DIST)

if __name__ == '__main__':
    main()