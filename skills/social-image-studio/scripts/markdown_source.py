"""Read a local Markdown source without rewriting it or fetching remote images."""
import base64
import hashlib
import json
import re
from pathlib import Path
from threading import Lock
from urllib.parse import unquote, urlsplit


# Include parser changes in revisions so open previews refresh after an update.
PARSER_VERSION = b'markdown-pages-v2\0'
MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
MAX_IMAGE_DATA_LENGTH = 1500000


class SourceError(ValueError):
    """A readable validation error that never includes source file contents."""


def text_length(value):
    # Match JavaScript's UTF-16 string length limits, including emoji.
    return len(value.encode('utf-16-le')) // 2


class MarkdownSource:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        self.source_id = hashlib.sha256(str(self.path).encode('utf-8')).hexdigest()
        self.vault = next((parent for parent in self.path.parents if (parent / '.obsidian').is_dir()), None)
        self._images = {}
        self._lock = Lock()

    def error_response(self, error):
        return {'sourceId': self.source_id, 'filename': self.path.name, 'error': str(error)}

    def _image(self, reference, caption, page_number, wiki=False):
        if text_length(caption) > 500:
            raise SourceError(f'第 {page_number} 页图片说明不能超过 500 字符。')
        reference = reference.strip()
        if reference.startswith('<') and reference.endswith('>'):
            reference = reference[1:-1]
        try:
            parsed = urlsplit(reference)
            relative = Path(unquote(parsed.path))
        except ValueError:
            raise SourceError(f'第 {page_number} 页图片路径无效。') from None
        if not reference or parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or relative.is_absolute():
            raise SourceError(f'第 {page_number} 页图片需使用本地相对路径，不支持网址。')
        try:
            path = (self.path.parent / relative).resolve()
        except (ValueError, OSError, RuntimeError):
            raise SourceError(f'第 {page_number} 页图片路径无效。') from None
        if wiki and not path.is_file() and self.vault:
            # Obsidian resolves a bare attachment name throughout the vault.
            # Ambiguous names must never silently select a different image.
            try:
                matches = [item for item in self.vault.rglob('*') if item.name == relative.name and item.is_file()]
            except OSError:
                raise SourceError('无法查找 Obsidian 图片，请检查资料库读取权限。') from None
            if len(matches) > 1:
                raise SourceError(f'图片「{relative.name}」在资料库中有多个同名文件，请使用相对路径。')
            if matches:
                path = matches[0].resolve()
        name = path.name
        try:
            stat = path.stat()
            fingerprint = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)
            cached = self._images.get(path)
            if cached and cached[0] == fingerprint:
                src, digest = cached[1:]
            else:
                # Bound reads before encoding, even when the file grows during a read.
                with path.open('rb') as handle:
                    data = handle.read(MAX_IMAGE_DATA_LENGTH + 1)
                if len(data) > MAX_IMAGE_DATA_LENGTH:
                    raise SourceError(f'图片「{name}」太大，请缩小图片后再试。')
                if data.startswith(b'\x89PNG\r\n\x1a\n'):
                    mime = 'png'
                elif data.startswith(b'\xff\xd8\xff'):
                    mime = 'jpeg'
                elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
                    mime = 'webp'
                else:
                    raise SourceError(f'图片「{name}」需为 PNG、JPEG 或 WebP 格式。')
                src = f'data:image/{mime};base64,' + base64.b64encode(data).decode('ascii')
                if len(src) > MAX_IMAGE_DATA_LENGTH:
                    raise SourceError(f'图片「{name}」太大，请缩小图片后再试。')
                digest = hashlib.sha256(data).hexdigest()
                self._images[path] = (fingerprint, src, digest)
        except (OSError, ValueError):
            raise SourceError(f'无法读取第 {page_number} 页图片「{name}」，请检查路径和权限。') from None
        return {'src': src, 'width': 100, 'caption': caption,
                'sourceKey': hashlib.sha256(str(path).encode('utf-8')).hexdigest()}, digest, path

    def read(self):
        with self._lock:
            try:
                with self.path.open('rb') as handle:
                    raw = handle.read(MAX_SOURCE_BYTES + 1)
            except OSError:
                raise SourceError('无法读取 Markdown 文件，请检查文件是否存在及读取权限。') from None
            if len(raw) > MAX_SOURCE_BYTES:
                raise SourceError('Markdown 文件不能超过 5 MB。')
            try:
                markdown = raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                raise SourceError('Markdown 文件需要使用 UTF-8 编码。') from None
            if not markdown.strip():
                raise SourceError('Markdown 文件为空，等待保存内容。')
            markdown = markdown.replace('\r\n', '\n')
            # Both explicit separators and level-two headings start a new page.
            # A heading immediately after a separator belongs to that new page.
            sections, current_lines = [], []
            for line in markdown.splitlines():
                separator = re.fullmatch(r'[ \t]*-(?:[ \t]*-){2,}[ \t]*', line)
                heading = re.match(r'^##[ \t]+', line)
                if separator or heading:
                    if any(item.strip() for item in current_lines):
                        sections.append('\n'.join(current_lines))
                    current_lines = []
                if not separator:
                    current_lines.append(line)
            if any(item.strip() for item in current_lines):
                sections.append('\n'.join(current_lines))
            if not sections:
                raise SourceError('Markdown 文件暂无页面内容，等待保存内容。')
            if len(sections) > 50:
                raise SourceError('最多支持 50 页，请减少分页或拆成多个文件。')
            pages, image_hashes, used_paths = [], [], set()
            for page_number, section in enumerate(sections, 1):
                page, hashes, paths = self._page(section, page_number)
                pages.append(page)
                image_hashes.extend(hashes)
                used_paths.update(paths)
            result = {
                'sourceId': self.source_id,
                'filename': self.path.name,
                'revision': hashlib.sha256(PARSER_VERSION + raw + ''.join(image_hashes).encode('ascii')).hexdigest(),
                'pages': pages,
            }
            if len(json.dumps(result, ensure_ascii=False).encode('utf-8')) > MAX_DOCUMENT_BYTES:
                raise SourceError('整份内容不能超过 20 MB，请减少图片或拆成多个文件。')
            # Drop images that have been removed from the source.
            self._images = {path: value for path, value in self._images.items() if path in used_paths}
            return result

    def _page(self, section, page_number):
        page = {key: '' for key in ('title', 'subtitle', 'body', 'note', 'highlight')}
        page['type'] = 'cover' if page_number == 1 else 'article'
        page['images'] = []
        highlights = re.findall(r'<!--\s*highlight:[ \t]*(.*?)\s*-->', section, flags=re.DOTALL)
        if len(highlights) > 1:
            raise SourceError(f'第 {page_number} 页只能指定一次 highlight。')
        if highlights:
            page['highlight'] = highlights[0].strip()
            section = re.sub(r'<!--\s*highlight:[ \t]*.*?\s*-->', '', section, flags=re.DOTALL)
        lines = section.strip().splitlines()
        if lines:
            title = re.fullmatch(r'#{1,2}[ \t]+(.*)', lines[0])
            if title:
                page['title'] = title.group(1).strip()
                lines.pop(0)
        for index, line in enumerate(lines):
            note_heading = re.fullmatch(r'###[ \t]+(?:参考资料|底部说明)[ \t]*', line)
            quoted_heading = re.fullmatch(r'>[ \t]*(?:参考资料|底部说明)[：:]?[ \t]*', line)
            if note_heading or quoted_heading:
                notes = lines[index + 1:]
                if quoted_heading:
                    notes = [re.sub(r'^>[ \t]?', '', item) for item in notes]
                page['note'] = re.sub(r'\[([^]\n]+)\]\(([^)\n]+)\)', r'\1（\2）', '\n'.join(notes)).strip()
                lines = lines[:index]
                break
        body, image_hashes, used_paths = [], [], set()
        for line in lines:
            image = re.fullmatch(r'[ \t]*!\[(.*?)\]\((.*?)\)(?:[ \t]*\{width=([^}]*)\})?[ \t]*', line)
            wiki_image = re.fullmatch(r'[ \t]*!\[\[([^]\n]+)\]\][ \t]*', line)
            if not image and not wiki_image:
                body.append(line)
                continue
            if page['type'] == 'cover':
                raise SourceError('封面不支持正文图片，请把图片放到正文页。')
            if len(page['images']) >= 8:
                raise SourceError(f'第 {page_number} 页最多支持 8 张图片。')
            if wiki_image:
                reference, separator, alias = wiki_image.group(1).partition('|')
                width = alias[:-1] if separator and alias.endswith('%') else None
                caption = alias if separator and width is None else ''
            else:
                reference, caption, width = image.group(2), image.group(1), image.group(3)
            item, digest, path = self._image(reference, caption, page_number, wiki=bool(wiki_image))
            if width is not None:
                if not width.isascii() or not width.isdecimal() or not 20 <= int(width) <= 100:
                    raise SourceError(f'第 {page_number} 页图片宽度需为 20–100 的整数百分比。')
                item['width'] = int(width)
            page['images'].append(item)
            image_hashes.append(digest)
            used_paths.add(path)
            body.append(f'[图片{len(page["images"])}]')
        field = 'subtitle' if page['type'] == 'cover' else 'body'
        page[field] = '\n'.join(body).strip()
        for key in ('title', 'subtitle'):
            page[key] = re.sub(r'<br\s*/?>', '\n', page[key], flags=re.IGNORECASE)
        for key in ('title', 'subtitle', 'body', 'note', 'highlight'):
            if text_length(page[key]) > 10000:
                raise SourceError(f'第 {page_number} 页的 {key} 字段不能超过 10000 字符，请拆成多页。')
        return page, image_hashes, used_paths
