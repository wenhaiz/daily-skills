"""Native chooser tests; subprocess is mocked and no system UI is opened."""
import subprocess
import sys
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / 'skills/social-image-studio/scripts'))
from file_picker import (CHOOSE_MARKDOWN_SCRIPT, PICKER_TIMEOUT, MarkdownFilePicker,
                         PickerError, validate_picker_request)


def request_headers(**changes):
    values = {
        'Host': '127.0.0.1:8765', 'Origin': 'http://127.0.0.1:8765',
        'X-Studio-Request': 'file-picker', 'Content-Length': '0',
    }
    values.update(changes)
    headers = Message()
    for key, value in values.items():
        if value is not None:
            headers[key] = value
    return headers


class RequestTests(unittest.TestCase):
    def test_local_origin(self):
        validate_picker_request(request_headers(), 8765)
        validate_picker_request(request_headers(**{
            'Host': 'localhost:8765', 'Origin': 'http://localhost:8765',
            'Content-Length': None,
        }), 8765)

    def test_rejects_untrusted_origins_and_host(self):
        cases = [
            {'Origin': None}, {'Origin': 'null'},
            {'Origin': 'http://evil.example:8765'},
            {'Origin': 'http://127.0.0.1:8766'},
            {'Origin': 'http://localhost:8765'},
            {'Origin': 'http://127.0.0.1:8765/path'},
            {'Origin': 'https://127.0.0.1:8765'},
            {'Host': 'evil.example:8765', 'Origin': 'http://evil.example:8765'},
            {'X-Studio-Request': None},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(PickerError) as caught:
                validate_picker_request(request_headers(**changes), 8765)
            self.assertEqual(caught.exception.status, 403)

    def test_rejects_body(self):
        for changes in ({'Content-Length': '1'}, {'Content-Length': '-1'},
                        {'Content-Length': 'invalid'}, {'Transfer-Encoding': 'chunked'}):
            with self.subTest(changes=changes), self.assertRaises(PickerError) as caught:
                validate_picker_request(request_headers(**changes), 8765)
            self.assertEqual(caught.exception.status, 400)


@patch('file_picker.sys.platform', 'darwin')
class ChooserTests(unittest.TestCase):
    @patch('file_picker.subprocess.run')
    def test_returns_path_without_reading_file(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '/tmp/中文 文件.md\n', '')
        self.assertEqual(MarkdownFilePicker().choose(), '/tmp/中文 文件.md')
        run.assert_called_once_with(
            ['osascript', '-e', CHOOSE_MARKDOWN_SCRIPT], capture_output=True,
            text=True, check=True, timeout=PICKER_TIMEOUT,
        )

    @patch('file_picker.subprocess.run')
    def test_cancel_returns_none_and_releases_lock(self, run):
        run.side_effect = subprocess.CalledProcessError(1, [], stderr='User canceled. (-128)\n')
        picker = MarkdownFilePicker()
        self.assertIsNone(picker.choose())
        self.assertFalse(picker._lock.locked())

    @patch('file_picker.subprocess.run')
    def test_errors_are_readable_and_release_lock(self, run):
        cases = [
            (subprocess.TimeoutExpired([], 120), 504, '超时'),
            (subprocess.CalledProcessError(1, [], stderr='Not authorized. (-1743)\n'), 500, '权限'),
            (subprocess.CalledProcessError(1, [], stderr='unexpected'), 500, '无法打开'),
            (OSError('missing osascript'), 500, '无法启动'),
        ]
        for error, status, message in cases:
            run.side_effect = error
            picker = MarkdownFilePicker()
            with self.subTest(error=error), self.assertRaises(PickerError) as caught:
                picker.choose()
            self.assertEqual(caught.exception.status, status)
            self.assertIn(message, str(caught.exception))
            self.assertFalse(picker._lock.locked())

    @patch('file_picker.subprocess.run')
    def test_invalid_result(self, run):
        for value in ('relative.md\n', '/tmp/image.png\n', ''):
            run.return_value = subprocess.CompletedProcess([], 0, value, '')
            with self.subTest(value=value), self.assertRaises(PickerError) as caught:
                MarkdownFilePicker().choose()
            self.assertEqual(caught.exception.status, 422)

    @patch('file_picker.subprocess.run')
    def test_busy(self, run):
        picker = MarkdownFilePicker()
        picker._lock.acquire()
        try:
            with self.assertRaises(PickerError) as caught:
                picker.choose()
            self.assertEqual(caught.exception.status, 409)
            run.assert_not_called()
        finally:
            picker._lock.release()

    @patch('file_picker.subprocess.run')
    def test_non_mac(self, run):
        with patch('file_picker.sys.platform', 'linux'):
            with self.assertRaises(PickerError) as caught:
                MarkdownFilePicker().choose()
        self.assertEqual(caught.exception.status, 501)
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
