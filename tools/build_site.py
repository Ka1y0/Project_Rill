#!/usr/bin/env python3
"""Build a small static site from local Markdown using Python's standard library.

Supported Markdown: headings, paragraphs, lists, bold, code and explicit links.
Raw HTML is escaped. No JavaScript, package downloads or remote resources.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    'en': ('English', 'Home', 'Privacy', 'Support', 'Terms', 'AI services', 'Skip to content', 'Languages', 'Site edition', 'Unpublished review draft'),
    'zh-Hans': ('简体中文', '首页', '隐私政策', '支持', '条款', 'AI 服务', '跳转至正文', '语言', '站点版本', '未发布的审阅草案'),
    'zh-Hant': ('繁體中文', '首頁', '隱私政策', '支援', '條款', 'AI 服務', '跳至正文', '語言', '網站版本', '未發布的審閱草案'),
}
KINDS = ['index', 'privacy', 'support', 'terms', 'ai-services']

def inline(text):
    parts = []
    pattern = r'\[([^\]]+)\]\(([^\s)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`'
    end = 0
    for match in re.finditer(pattern, text):
        parts.append(escape(text[end:match.start()]))
        label, url, strong, code = match.groups()
        if url:
            if urlsplit(url).scheme not in ('', 'https', 'mailto') or url.startswith('//'):
                raise ValueError('Unsafe link scheme')
            parts.append('<a href="' + escape(url, quote=True) + '">' + escape(label) + '</a>')
        elif strong:
            parts.append('<strong>' + escape(strong) + '</strong>')
        else:
            parts.append('<code>' + escape(code) + '</code>')
        end = match.end()
    return ''.join(parts) + escape(text[end:])

def markdown(text):
    blocks, paragraph, listing = [], [], []
    def flush():
        if paragraph:
            blocks.append('<p>' + inline(' '.join(paragraph)) + '</p>'); paragraph.clear()
        if listing:
            blocks.append('<ul>' + ''.join('<li>' + inline(s) + '</li>' for s in listing) + '</ul>'); listing.clear()
    for line in text.splitlines() + ['']:
        if not line.strip(): flush()
        elif line.startswith('#'):
            flush(); match = re.fullmatch(r'(#{1,3}) (.+)', line)
            if not match: raise ValueError('Invalid heading')
            level = len(match[1]); blocks.append(f'<h{level}>' + inline(match[2]) + f'</h{level}>')
        elif line.startswith('- '):
            if paragraph: flush()
            listing.append(line[2:])
        else:
            if listing: flush()
            paragraph.append(line.strip())
    return '\n'.join(blocks)

def source_path(relative):
    path = ROOT / relative
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Source outside repository')
    return path

def rendered(config):
    pages = config['pages']; langs = config['languages']; outputs = {}
    for lang in langs:
        labels = LABELS[lang]; depth = '' if lang == 'en' else '../'
        for kind, sources in pages.items():
            if lang not in sources: raise ValueError('Incomplete language')
            file = kind + '.html'; prefix = '' if lang == 'en' else lang + '/'
            body = markdown(source_path(sources[lang]).read_text())
            title = config['product'] if kind == 'index' else f'{labels[KINDS.index(kind)+1]} · {config["product"]}'
            navigation = ''.join(f'<a href="{k}.html"' + (' aria-current="page"' if k == kind else '') + f'>{escape(labels[KINDS.index(k)+1])}</a>' for k in KINDS if k in pages)
            languages = ''.join('<a lang="' + l + '" hreflang="' + l + '" href="' + depth + ('' if l == 'en' else l + '/') + file + '"' + (' aria-current="page"' if l == lang else '') + '>' + LABELS[l][0] + '</a>' for l in langs)
            edition = escape(config['edition'])
            draft = f'<p class="notice">{escape(labels[9])} · {edition}</p>' if config.get('draft') else ''
            robots = '<meta name="robots" content="noindex, nofollow">' if config.get('draft') else ''
            canonical = '' if config.get('draft') else '<link rel="canonical" href="' + config['base_url'] + prefix + file + '">'
            outputs['docs/' + prefix + file] = f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<meta name="site-edition" content="{edition}">
<title>{escape(title)} · Chips Studio</title>
{robots}{canonical}
<link rel="stylesheet" href="{depth}assets/site.css">
</head>
<body>
<a class="skip" href="#content">{escape(labels[6])}</a>
<div class="shell">
<header><a class="brand" href="index.html">Chips Studio <span>/ {escape(config['product'])}</span></a>
<nav class="languages" aria-label="{escape(labels[7])}">{languages}</nav></header>
<nav class="pages" aria-label="{escape(config['product'])}">{navigation}</nav>
<main id="content" tabindex="-1">{draft}<article>{body}</article></main>
<footer><span>Chips Studio · {escape(config['product'])}</span><span>{escape(labels[8])} {edition}</span></footer>
</div>
</body>
</html>
'''
    outputs['docs/.nojekyll'] = ''
    outputs['docs/assets/site.css'] = source_path('site.css').read_text()
    return outputs

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.h1=0; self.lang=None; self.title=False; self.forbidden=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag == 'html': self.lang=attrs.get('lang')
        if tag == 'h1': self.h1+=1
        if tag == 'title': self.title=True
        if 'id' in attrs:
            if attrs['id'] in self.ids: self.forbidden.append('duplicate id')
            self.ids.add(attrs['id'])
        if tag in ('script','iframe','form','img','video','audio'): self.forbidden.append(tag)
        for key in ('href','src'):
            if key in attrs: self.links.append(attrs[key])
        if any(key.startswith('on') for key in attrs): self.forbidden.append('event handler')

def validate(config, outputs):
    errors=[]; docs=(ROOT/'docs').resolve(); external=set()
    actual={str(p.relative_to(ROOT)) for p in (ROOT/'docs').rglob('*') if p.is_file()}
    if actual != set(outputs): errors.append('Unexpected/missing generated files')
    for rel, expected in outputs.items():
        path=ROOT/rel
        if path.is_symlink(): errors.append(rel+': symlink')
        if not path.exists() or path.read_text()!=expected: errors.append(rel+': generated content drift')
        if not rel.endswith('.html'): continue
        page=Page(); page.feed(expected)
        if page.h1!=1 or not page.title or page.lang not in config['languages'] or page.forbidden: errors.append(rel+': invalid document structure')
        for link in page.links:
            u=urlsplit(link)
            if u.scheme:
                if u.scheme not in ('https','mailto'): errors.append(rel+': unsafe URL')
                external.add(link); continue
            if link.startswith('/') or link.startswith('//'): errors.append(rel+': root-relative link')
            target=(path.parent/unquote(u.path)).resolve() if u.path else path.resolve()
            if not target.is_relative_to(docs) or not target.is_file(): errors.append(rel+': broken local link '+link)
            if u.fragment:
                other=Page();other.feed(target.read_text())
                if u.fragment not in other.ids: errors.append(rel+': missing fragment '+link)
        if not config.get('draft') and re.search(r'\b(TODO|TBD|HUMAN_INPUT_REQUIRED|placeholder|DRAFT)\b|awaiting publisher|待填写',expected,re.I): errors.append(rel+': draft marker')
    result={'status':'PASS' if not errors else 'FAIL','edition':config['edition'],'draft':bool(config.get('draft')),'html_pages':sum(p.endswith('.html') for p in outputs),'checked_files':len(outputs),'external_links':sorted(external),'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if errors else 0

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    config=json.loads((ROOT/'site.json').read_text());outputs=rendered(config)
    if not args.check:
        for rel,data in outputs.items():
            path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data)
    return validate(config,outputs)

if __name__=='__main__': sys.exit(main())
