"""Open a native file picker only for explicit requests from the local editor."""
import re
import subprocess
import sys
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit


PICKER_TIMEOUT = 120
CHOOSE_MARKDOWN_SCRIPT = '''
set selectedFile to choose file with prompt "选择要预览的 Markdown 文件" of type {"md", "markdown"}
return POSIX path of selectedFile
'''


class PickerError(Exception):
    def __init__(self, message, status=500):
        super().__init__(message)
        self.status = status


def validate_picker_request(headers, port):
    """Require a body-free, same-origin POST to this loopback server."""
    host = headers.get('Host', '')
    allowed_hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
    if host not in allowed_hosts or headers.get('X-Studio-Request') != 'file-picker':
        raise PickerError('只能从本地工作台选择文件。', 403)
    try:
        origin = urlsplit(headers.get('Origin', ''))
        valid_origin = (origin.scheme == 'http' and origin.netloc == host
                        and not origin.path and not origin.query and not origin.fragment)
    except ValueError:
        valid_origin = False
    if not valid_origin:
        raise PickerError('文件选择请求来源无效，请在本地工作台中重试。', 403)
    if headers.get('Transfer-Encoding') or headers.get('Content-Length', '0') != '0':
        raise PickerError('文件选择请求不能包含正文。', 400)


class MarkdownFilePicker:
    def __init__(self):
        self._lock = Lock()

    def choose(self):
        if sys.platform != 'darwin':
            raise PickerError('当前系统暂不支持文件选择，请在启动服务时使用 --markdown 指定文件。', 501)
        if not self._lock.acquire(blocking=False):
            raise PickerError('文件选择窗口已经打开，请先完成或取消选择。', 409)
        try:
            try:
                result = subprocess.run(
                    ['osascript', '-e', CHOOSE_MARKDOWN_SCRIPT],
                    capture_output=True, text=True, check=True, timeout=PICKER_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                raise PickerError('选择文件已超时，请重新选择。', 504) from None
            except subprocess.CalledProcessError as error:
                detail = error.stderr or ''
                if re.search(r'\(-128\)\s*$', detail):
                    return None
                if re.search(r'\(-1743\)\s*$', detail):
                    raise PickerError('系统未允许打开文件选择窗口，请检查 macOS 权限后重试。') from None
                raise PickerError('无法打开文件选择窗口，请重试。') from None
            except OSError:
                raise PickerError('无法启动系统文件选择器，请重试。') from None
            # AppleScript appends one newline; preserve spaces in file names.
            value = result.stdout.removesuffix('\n')
            path = Path(value)
            if not value or not path.is_absolute() or path.suffix.lower() not in ('.md', '.markdown'):
                raise PickerError('请选择 .md 或 .markdown 文件。', 422)
            return str(path)
        finally:
            self._lock.release()
