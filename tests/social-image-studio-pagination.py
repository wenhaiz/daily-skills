"""Verify explicit Markdown pagination without changing user documents."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / 'skills/social-image-studio/scripts'))
from markdown_source import MarkdownSource


class PaginationTests(unittest.TestCase):
    def parse(self, content):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'pages.md'
            source.write_text(content, encoding='utf-8')
            return MarkdownSource(source).read()['pages']

    def test_supported_separators_start_untitled_continuation(self):
        for separator in ('---', '------', '- - -', '  -\t-\t-  '):
            with self.subTest(separator=separator):
                pages = self.parse(f'# 封面\n\n## 正文\n第一页\n\n{separator}\n\n第二页')
                self.assertEqual(len(pages), 3)
                self.assertEqual(pages[1]['body'], '第一页')
                self.assertEqual(pages[2]['title'], '')
                self.assertEqual(pages[2]['body'], '第二页')

    def test_inline_hyphens_and_list_items_are_not_separators(self):
        for content in ('前文---后文', '--', '- 练习 5 分钟', '- - 练习'):
            with self.subTest(content=content):
                pages = self.parse(f'# 封面\n\n## 正文\n{content}')
                self.assertEqual(len(pages), 2)
                self.assertEqual(pages[1]['body'], content)

    def test_repeated_separator_and_following_heading_do_not_add_empty_page(self):
        pages = self.parse('---\n# 封面\n---\n------\n## 正文\n内容\n---')
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[1]['title'], '正文')
        self.assertEqual(pages[1]['body'], '内容')


if __name__ == '__main__':
    unittest.main()
