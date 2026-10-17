const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const app = fs.readFileSync(path.join(__dirname, '../skills/social-image-studio/assets/app.js'), 'utf8');
const start = app.indexOf('function showSelectedSource()');
const end = app.indexOf('function updateSourceChoice()', start);
async function run(response, expectedPath, expectedError = '') {
  const elements = Object.fromEntries(['source-path', 'selected-source-name', 'choose-source-file', 'apply-source', 'source-choice', 'source-choice-error'].map(id => [id, { value: '', textContent: '', disabled: false }]));
  elements['source-path'].value = '/旧文件.md';
  const context = vm.createContext({
    $: id => elements[id], AbortSignal, switchingSource: false, choosingSource: false,
    fetch: async (url, options) => {
      assert.equal(url, 'choose-markdown');
      assert.equal(options.method, 'POST');
      assert.equal(options.headers['X-Studio-Request'], 'file-picker');
      assert.equal(elements['apply-source'].disabled, true);
      if (response instanceof Error) throw response;
      return response;
    }
  });
  vm.runInContext(app.slice(start, end), context);
  await elements['choose-source-file'].onclick();
  assert.equal(elements['source-path'].value, expectedPath);
  assert.equal(elements['source-choice-error'].textContent, expectedError);
  for (const id of ['choose-source-file', 'apply-source', 'source-choice']) assert.equal(elements[id].disabled, false);
  if (!expectedError && response.status === 200) {
    assert.equal(elements['selected-source-name'].textContent, '新文章 🎸.md');
    assert.equal(elements['selected-source-name'].title, expectedPath);
  }
}
(async () => {
  await run({status:200, ok:true, json:async () => ({path:'/笔记/新文章 🎸.md'})}, '/笔记/新文章 🎸.md');
  await run({status:204}, '/旧文件.md');
  await run({status:409, ok:false, json:async () => ({error:'选择窗口已打开'})}, '/旧文件.md', '选择窗口已打开');
  await run(new Error('连接失败'), '/旧文件.md', '连接失败');
  console.log('PASS 文件选择：中文路径、取消、并发错误、连接失败和按钮恢复');
})().catch(error => { console.error(error); process.exitCode = 1; });
