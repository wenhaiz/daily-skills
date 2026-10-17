const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const app = fs.readFileSync(path.join(__dirname, '../skills/social-image-studio/assets/app.js'), 'utf8');
const start = app.indexOf('function sourcePageKey(');
const end = app.indexOf("$('source-highlight').oninput", start);
const context = vm.createContext({});
vm.runInContext(app.slice(start, end), context);
const { sourcePageKey: key, migrateSourceHighlights: migrate } = context;
const page = (title, body = '') => ({ type: 'article', title, body, subtitle: '', note: '' });
function check(previous, next, oldIndex, newIndex, text) {
  const saved = { [key(oldIndex, previous)]: text };
  const migrated = migrate(previous, next, saved);
  assert.equal(migrated[key(newIndex, next)], text);
  // The same data is restored after serialization and a fresh initialization.
  const restored = migrate([], next, JSON.parse(JSON.stringify(migrated)));
  assert.equal(restored[key(newIndex, next)], text);
}

check([page('标题', '正文')], [page('新标题', '正文')], 0, 0, '标题');
check([page('标题', '正文')], [page('新标题', '新正文')], 0, 0, '标题');
check([page('标题', '正文')], [page('标题', '新正文')], 0, 0, '');
check([page('同名', '一'), page('同名', '二')], [page('同名', '新一'), page('同名', '二')], 0, 0, '同名');
check([page('同名', '一'), page('同名', '二')], [page('同名', '二'), page('同名', '一')], 0, 1, '同');
check([page('一', '正文一'), page('二', '正文二')], [page('二', '正文二'), page('新一', '正文一')], 0, 1, '一');
check([page('一'), page('二')], [page('新增'), page('一'), page('二')], 1, 2, '二');
const previous = [page('删除页'), page('保留页')];
const next = [page('新页面'), page('保留页')];
const stored = { [key(0, previous)]: '删除页', [key(1, previous)]: '保留' };
const migrated = migrate(previous, next, stored);
assert.equal(migrated[key(1, next)], '保留');
assert.equal(migrated[key(0, next)], '删除页'); // Same-position replacement keeps layout, even if text no longer matches.
console.log('PASS Markdown 高亮：标题/正文修改、空值、同名页、调序、插页和保存恢复');
