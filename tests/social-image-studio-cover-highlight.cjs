const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '../skills/social-image-studio/assets');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const context = vm.createContext({ TextEncoder, structuredClone, URLSearchParams, localStorage: {getItem: () => null} });
vm.runInContext(app.slice(0, app.indexOf('let doc = validateDocument(defaultDocument);')), context);
const legacy = {version:1, style:{accent:'#4294d5',bodySize:40}, pages:[{type:'cover',title:'封面'}]};
const normalized = context.validateDocument(legacy);
assert.equal(normalized.style.coverHighlightWidth, 30);
normalized.style.coverHighlightWidth = 38;
normalized.styleProfiles['3:4'].coverHighlightWidth = 38;
normalized.styleProfiles['9:16'].coverHighlightWidth = 25;
const restored = context.validateDocument(JSON.parse(JSON.stringify(normalized)));
assert.equal(restored.style.coverHighlightWidth, 38);
assert.equal(restored.styleProfiles['9:16'].coverHighlightWidth, 25);
for (const value of [7, 61, 12.5, '30']) assert.throws(() => context.validateDocument({...legacy, style:{...legacy.style,coverHighlightWidth:value}}));

const window = {};
vm.runInNewContext(fs.readFileSync(path.join(root, 'renderer.js'), 'utf8'), {window, Intl});
function draw(type, highlight, thickness) {
  const events = [];
  const ctx = {
    measureText: text => ({width: Array.from(text).length * 50}),
    fillRect() {}, beginPath() {}, moveTo() {}, bezierCurveTo() {},
    stroke() { events.push(['stroke',this.lineWidth]); },
    fillText(text) { events.push(['text',text]); }
  };
  window.StudioRenderer.draw({getContext:() => ctx}, {type,title:'封面高亮',highlight,subtitle:'',body:'',note:''}, {bodySize:40,accent:'#4294d5',coverHighlightWidth:thickness});
  assert.equal(events[0][0], 'stroke'); // Decoration remains beneath title text.
  return events.find(event => event[0] === 'stroke')[1];
}
assert.equal(draw('cover','',undefined),30);
assert.equal(draw('cover','高亮',38),38);
assert.equal(draw('cover','',38),38);
assert.equal(draw('article','高亮',38),19);
assert.equal(draw('article','',38),19);
console.log('PASS 封面高亮：默认/自选粗细、正文不变、层级、旧草稿兼容、两套样式保存恢复');
