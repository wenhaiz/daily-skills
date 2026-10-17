const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '../skills/social-image-studio/assets');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const context = vm.createContext({TextEncoder, structuredClone, URLSearchParams, localStorage:{getItem:() => null}});
vm.runInContext(app.slice(0, app.indexOf('let doc = validateDocument(defaultDocument);')), context);
const legacy = {version:1, style:{accent:'#4294d5',bodySize:40},pages:[{type:'cover',title:'封面'}]};
const document = context.validateDocument(legacy);
assert.equal(document.style.watermarkText, '');
assert.equal(document.style.watermarkOpacity, 12);
document.style.watermarkText = '@我的账号';
document.style.watermarkOpacity = 15;
document.styleProfiles['9:16'].watermarkText = '@长图';
const restored = context.validateDocument(JSON.parse(JSON.stringify(document)));
assert.equal(restored.style.watermarkText, '@我的账号');
assert.equal(restored.style.watermarkOpacity, 15);
assert.equal(restored.styleProfiles['9:16'].watermarkText, '@长图');
for (const extra of [{watermarkText:'a'.repeat(81)}, {watermarkText:'两\n行'}, {watermarkText:123}, {watermarkOpacity:31}, {watermarkSize:19}]) {
  assert.throws(() => context.validateDocument({...legacy,style:{...legacy.style,...extra}}));
}
const window = {};
vm.runInNewContext(fs.readFileSync(path.join(root, 'renderer.js'), 'utf8'), {window,Intl});
for (const type of ['cover','article']) for (const aspectRatio of ['3:4','9:16']) {
  const events = [], stack = [];
  const ctx = {
    measureText:text => ({width:Array.from(text).length * 20}),
    fillRect() {},beginPath() {},moveTo() {},bezierCurveTo() {},stroke() {},
    save() { stack.push({textAlign:this.textAlign,textBaseline:this.textBaseline}); },
    restore() { Object.assign(this, stack.pop()); },
    fillText(text,x,y,maxWidth) { events.push({text,x,y,maxWidth,color:this.fillStyle,font:this.font,baseline:this.textBaseline,align:this.textAlign}); }
  };
  const canvas = {getContext:() => ctx};
  const page = {type,title:'标题',body:'正文',subtitle:'副标题',note:'参考资料'};
  const style = {...restored.style,aspectRatio,marginY:60,watermarkSize:32};
  window.StudioRenderer.draw(canvas,page,style);
  const watermark = events.at(-1), note = events.find(event => event.text === '参考资料');
  assert.equal(watermark.text,'@我的账号');
  assert.equal(watermark.color,'rgba(0, 0, 0, 0.15)');
  assert.equal(watermark.y,canvas.height - 24);
  assert.equal(watermark.x,canvas.width - style.marginX);
  assert.equal(watermark.maxWidth,canvas.width - style.marginX * 2);
  assert.equal(watermark.align,'right'); assert.equal(watermark.baseline,'bottom');
  assert.ok(note.y + 20 < watermark.y - 32); // Smallest margin still separates watermark from references.
  events.length = 0;
  window.StudioRenderer.draw(canvas,page,{...style,watermarkText:'   '});
  assert.ok(!events.some(event => event.text === '@我的账号'));
}
console.log('PASS 水印：所有页型和尺寸、浅色/位置、参考资料避让、关闭、旧样式兼容及保存恢复');
