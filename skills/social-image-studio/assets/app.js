const $ = id => document.getElementById(id);
let storageKey = 'social-image-studio-v1';
const DEFAULT_STYLE_PROFILES = {
  "3:4": {
    "accent": "#319fff",
    "bodySize": 42,
    "coverTitleSize": 112,
    "coverSubtitleSize": 36,
    "pageTitleSize": 56,
    "lineHeight": 1.55,
    "marginX": 90,
    "marginY": 100,
    "letterSpacing": 2.75,
    "aspectRatio": "3:4"
  },
  "9:16": {
    "accent": "#319fff",
    "bodySize": 44,
    "coverTitleSize": 112,
    "coverSubtitleSize": 36,
    "pageTitleSize": 56,
    "lineHeight": 1.55,
    "marginX": 110,
    "marginY": 140,
    "letterSpacing": 2.75,
    "aspectRatio": "9:16"
  }
};
const DEFAULT_STYLE = DEFAULT_STYLE_PROFILES['3:4'];
const styleFields = Object.keys(DEFAULT_STYLE);
const defaultDocument = {
  version: 1,
  style: { ...DEFAULT_STYLE },
  styleProfiles: structuredClone(DEFAULT_STYLE_PROFILES),
  pages: [
    { type: 'cover', title: '6 个方向\n帮你安排练琴', subtitle: '', body: '', note: '' },
    { type: 'article', title: '技术', subtitle: '', note: '', body: '技术练习更像体育训练，包含手指灵活度和伸展度、左右手的配合、拨弦速度和准确度、推弦音准、击勾弦等等。\n\n每个人的身体条件不同，有些人弹快比较容易，有些人手指的伸展度很好，需要投入的技术练习也不一样。\n\n技术可能是最容易被过度练习的领域。有人觉得必须把某个练习练到某个速度才行，但技术越往后提升，往往越费时间，要考虑这些投入能否帮你更好地演奏想弹的音乐。\n\n比如，拨弦的准确度值得经常检查；如果曲目里有推弦，就要留意推弦的音准。其他技术练习也可以结合曲目动态调整。\n\n开始一个技术练习前，先问问：它能帮我解决什么问题？如果还不清楚，可以先弄明白练习目的，再决定投入多少时间。' },
    { type: 'article', title: '曲目', subtitle: '', note: '', body: '让练习围绕一首你真正想弹的歌展开。\n\n先把整首歌拆成几个小段，找出最影响连贯演奏的地方。每次只处理一个具体问题，再回到音乐里验证。\n\n练得慢一点，也可以听见节奏、力度和句子的方向。能稳定地弹完，比偶尔弹对一次更有意义。' }
  ]
};
let current = 0;
let exporting = false;
const fields = ['type', 'title', 'subtitle', 'body', 'note', 'highlight'];
const MAX_DOCUMENT_BYTES = 20 * 1024 * 1024;
function checkDocumentSize(value) {
  if (new TextEncoder().encode(JSON.stringify(value, null, 2)).length > MAX_DOCUMENT_BYTES) throw new Error('整份内容不能超过 20 MB，请减少图片或拆成多个文件。');
}
function validateDocument(value, includeProfiles = true) {
  checkDocumentSize(value);
  if (!value || value.version !== 1 || !Array.isArray(value.pages) || value.pages.length < 1 || value.pages.length > 50) throw new Error('内容需要包含 1–50 页，version 为 1。');
  if (!value.style || !/^#[0-9a-f]{6}$/i.test(value.style.accent) || !Number.isInteger(value.style.bodySize) || value.style.bodySize < 28 || value.style.bodySize > 48) throw new Error('样式需要有效的强调色和 28–48 的正文字号。');
  const lineHeight = value.style.lineHeight ?? DEFAULT_STYLE.lineHeight;
  if (typeof lineHeight !== 'number' || !Number.isFinite(lineHeight) || lineHeight < 1.2 || lineHeight > 2.2) throw new Error('正文行距需要在 1.2–2.2 倍之间。');
  const marginX = value.style.marginX ?? DEFAULT_STYLE.marginX;
  if (!Number.isInteger(marginX) || marginX < 60 || marginX > 240) throw new Error('左右边距需要在 60–240 px 之间。');
  const marginY = value.style.marginY ?? DEFAULT_STYLE.marginY;
  if (!Number.isInteger(marginY) || marginY < 60 || marginY > 360) throw new Error('上下边距需要在 60–360 px 之间。');
  const letterSpacing = value.style.letterSpacing ?? DEFAULT_STYLE.letterSpacing;
  if (typeof letterSpacing !== 'number' || !Number.isFinite(letterSpacing) || letterSpacing < 0 || letterSpacing > 6) throw new Error('正文字间距需要在 0–6 px 之间。');
  const aspectRatio = value.style.aspectRatio ?? '3:4';
  if (!['3:4', '9:16'].includes(aspectRatio)) throw new Error('图片比例需为 3:4 或 9:16。');
  const titleSizes = {};
  for (const [field, label, min, max] of [
    ['coverTitleSize', '封面标题', 64, 160],
    ['coverSubtitleSize', '封面副标题', 20, 60],
    ['pageTitleSize', '正文页标题', 36, 88]
  ]) {
    const size = value.style[field] ?? DEFAULT_STYLE[field];
    if (!Number.isInteger(size) || size < min || size > max) throw new Error(`${label}字号需为 ${min}–${max} px 的整数。`);
    titleSizes[field] = size;
  }
  const pages = value.pages.map(page => {
    if (!page || !['cover', 'article'].includes(page.type)) throw new Error('页面类型必须为 cover 或 article。');
    const clean = { type: page.type };
    // Retain the legacy emoji value for existing seed fingerprints; it is no longer rendered.
    for (const field of ['title', 'subtitle', 'body', 'emoji', 'note', 'highlight']) {
      const text = page[field] ?? '';
      if (typeof text !== 'string' || text.length > 10000) throw new Error('每个文字字段需为字符串，长度不超过 10000。');
      clean[field] = text;
    }
    const images = page.images ?? [];
    if (!Array.isArray(images) || images.length > 8) throw new Error('每页最多支持 8 张图片。');
    clean.images = images.map(item => {
      if (!item || typeof item.src !== 'string' || item.src.length > 1500000 || !/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$/.test(item.src)) throw new Error('图片需为有效的 PNG、JPEG 或 WebP 数据，单张不超过 1 MB。');
      const width = item.width ?? 100;
      if (!Number.isInteger(width) || width < 20 || width > 100) throw new Error('图片宽度需要在 20–100% 之间。');
      const caption = item.caption ?? '';
      if (typeof caption !== 'string' || caption.length > 500) throw new Error('图片说明需为字符串，最多 500 字符。');
      return { src: item.src, width, caption };
    });
    return clean;
  });
  const normalized = { version: 1, style: { accent: value.style.accent, bodySize: value.style.bodySize, lineHeight, marginX, marginY, letterSpacing, aspectRatio, ...titleSizes }, pages };
  if (includeProfiles) {
    if (value.styleProfiles !== undefined && (!value.styleProfiles || typeof value.styleProfiles !== 'object' || Array.isArray(value.styleProfiles))) throw new Error('样式配置需为对象。');
    normalized.styleProfiles = {};
    for (const ratio of ['3:4', '9:16']) {
      const profile = value.styleProfiles?.[ratio] ?? normalized.style;
      normalized.styleProfiles[ratio] = validateDocument({ version: 1, style: { ...profile, aspectRatio: ratio }, pages: [{ type: 'article' }] }, false).style;
    }
    normalized.styleProfiles[aspectRatio] = { ...normalized.style };
  }
  checkDocumentSize(normalized);
  return normalized;
}
let doc = validateDocument(defaultDocument);
function persist() {
  try { localStorage.setItem(storageKey, JSON.stringify(doc)); $('storage-status').textContent = '草稿已自动保存'; }
  catch { $('storage-status').textContent = '浏览器无法保存草稿，请用「保存内容」备份。'; }
}
let draggedPage = null;
function clearDragState() {
  draggedPage = null;
  for (const button of $('pages').children) button.classList.remove('dragging', 'drop-before', 'drop-after');
}
function movePage(from, to) {
  if (from === to || from < 0 || to < 0 || to >= doc.pages.length) return;
  const selected = doc.pages[current];
  const [page] = doc.pages.splice(from, 1);
  doc.pages.splice(to, 0, page);
  current = doc.pages.indexOf(selected);
  persist(); syncEditor();
}
function showPages() {
  $('pages').replaceChildren();
  doc.pages.forEach((page, index) => {
    const button = document.createElement('button');
    button.className = 'page-button' + (index === current ? ' active' : '');
    button.draggable = true;
    button.title = '拖动排序；也可按 Alt + ↑ / ↓ 移动';
    button.setAttribute('aria-keyshortcuts', 'Alt+ArrowUp Alt+ArrowDown');
    button.ondragstart = event => {
      draggedPage = page; button.classList.add('dragging');
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', String(index + 1));
    };
    button.ondragover = event => {
      if (!draggedPage || draggedPage === page) return;
      event.preventDefault(); event.dataTransfer.dropEffect = 'move';
      for (const item of $('pages').children) item.classList.remove('drop-before', 'drop-after');
      const after = event.clientY > button.getBoundingClientRect().top + button.offsetHeight / 2;
      button.classList.add(after ? 'drop-after' : 'drop-before');
    };
    button.ondragleave = () => button.classList.remove('drop-before', 'drop-after');
    button.ondragend = clearDragState;
    button.ondrop = event => {
      if (!draggedPage) return;
      event.preventDefault();
      const from = doc.pages.indexOf(draggedPage), target = doc.pages.indexOf(page);
      const after = event.clientY > button.getBoundingClientRect().top + button.offsetHeight / 2;
      const to = target + (after ? 1 : 0) - (from < target + (after ? 1 : 0) ? 1 : 0);
      clearDragState(); movePage(from, to);
    };
    button.onkeydown = event => {
      if (!event.altKey || !['ArrowUp', 'ArrowDown'].includes(event.key)) return;
      event.preventDefault();
      const from = doc.pages.indexOf(page), to = from + (event.key === 'ArrowUp' ? -1 : 1);
      if (to < 0 || to >= doc.pages.length) return;
      movePage(from, to); $('pages').children[to].focus();
    };
    button.setAttribute('aria-current', index === current ? 'page' : 'false');
    const number = document.createElement('small'); number.textContent = String(index + 1).padStart(2, '0') + ' / ' + (page.type === 'cover' ? '封面' : '正文');
    const title = document.createElement('span'); title.textContent = page.title.replaceAll('\n', ' ') || '未命名页面';
    button.append(number, title); button.onclick = () => { current = index; syncEditor(); };
    $('pages').append(button);
  });
  $('delete').disabled = doc.pages.length === 1;
  $('add').disabled = doc.pages.length >= 50;
}
let renderRevision = 0;
function render() {
  const revision = ++renderRevision;
  const page = doc.pages[current];
  const size = StudioRenderer.dimensions(doc.style);
  $('canvas-size').textContent = `${doc.style.aspectRatio === '3:4' ? '3:4 竖版 · ' : '竖版 · '}${size.width} × ${size.height} px`;
  const imagePage = page.type === 'article' && page.images?.length;
  if (imagePage) {
    StudioRenderer.loadImages(page).then(() => {
      if (revision !== renderRevision) return;
      const loaded = StudioRenderer.draw($('canvas'), page, doc.style);
      $('overflow').textContent = loaded.imageWarning || (loaded.overflow ? '内容超出安全区域。请减少内容、缩小图片，或拆成多页后导出。' : '');
      $('export').disabled = exporting || loaded.overflow;
      $('style-overflow').textContent = $('overflow').textContent;
    }).catch(error => {
      if (revision !== renderRevision) return;
      $('overflow').textContent = error.message; $('export').disabled = true;
    });
  }
  const result = StudioRenderer.draw($('canvas'), page, doc.style);
  $('canvas').setAttribute('aria-label', `${page.title}。${page.type === 'article' ? page.body : page.subtitle}`);
  $('preview-title').textContent = `第 ${current + 1} 页 · ${page.type === 'cover' ? '封面' : '正文'}`;
  $('overflow').textContent = result.imageWarning || (result.overflow ? '内容超出安全区域。请减少文字、调小字号或行距，或拆成多页后导出。' : '');
  $('export').disabled = exporting || result.overflow;
  $('export-all').disabled = exporting;
  const isCover = page.type === 'cover';
  $('body-label').hidden = isCover;
  $('image-editor').hidden = isCover;
  $('title-label').textContent = isCover ? '封面标题' : '正文标题（可留空）';
  $('subtitle-label-text').textContent = '副标题';
  $('subtitle-label').hidden = !isCover;
  $('highlight-label').hidden = !page.title.trim();
  $('highlight-status').textContent = result.highlightWarning;
  $('highlight-status').hidden = !page.title.trim();
  for (const field of ['coverTitleSize', 'coverSubtitleSize', 'pageTitleSize']) $(field + '-value').textContent = doc.style[field] + ' px';
  $('font-size-value').textContent = doc.style.bodySize + ' px';
  $('line-height-value').textContent = doc.style.lineHeight.toFixed(2) + ' 倍';
  $('margin-value').textContent = '两边各 ' + doc.style.marginX + ' px';
  $('vertical-margin-value').textContent = '上下各 ' + doc.style.marginY + ' px';
  $('letter-spacing-value').textContent = doc.style.letterSpacing.toFixed(2) + ' px';
  $('style-overflow').textContent = $('overflow').textContent;
}
function syncEditor() {
  for (const field of fields) $(field).value = doc.pages[current][field] ?? '';
  for (const field of styleFields) $(field).value = doc.style[field];
  showImages(); showPages(); render();
}
for (const field of fields) {
  if (field !== 'type') $(field).maxLength = 10000;
  $(field).addEventListener('input', () => {
    const page = doc.pages[current], previous = page[field];
    page[field] = $(field).value;
    try { checkDocumentSize(doc); }
    catch (error) { page[field] = previous; $(field).value = previous ?? ''; $('feedback').textContent = error.message; return; }
    persist(); showPages(); render();
  });
}
for (const field of styleFields) {
  $(field).addEventListener('input', () => {
    const previousStyle = { ...doc.style };
    const previousProfiles = structuredClone(doc.styleProfiles);
    if (field === 'aspectRatio') {
      doc.styleProfiles[doc.style.aspectRatio] = { ...doc.style };
      doc.style = { ...doc.styleProfiles[$(field).value] };
    } else {
      doc.style[field] = field === 'accent' ? $(field).value : Number($(field).value);
    }
    doc.styleProfiles[doc.style.aspectRatio] = { ...doc.style };
    try { checkDocumentSize(doc); }
    catch (error) {
      doc.style = previousStyle; doc.styleProfiles = previousProfiles;
      syncEditor(); $('feedback').textContent = error.message; return;
    }
    persist(); syncEditor();
  });
}
function showImages() {
  $('image-list').replaceChildren();
  (doc.pages[current].images ?? []).forEach((item, index) => {
    const row = document.createElement('div'); row.className = 'image-row';
    const thumbnail = document.createElement('img'); thumbnail.src = item.src; thumbnail.alt = `图片${index + 1}`;
    const label = document.createElement('label');
    const text = document.createElement('span'); text.textContent = `图片${index + 1} · 宽度 ${item.width}%`;
    const slider = document.createElement('input'); slider.type = 'range'; slider.min = 20; slider.max = 100; slider.step = 5; slider.value = item.width;
    slider.setAttribute('aria-label', `图片${index + 1}宽度`);
    slider.oninput = () => {
      const previous = item.width; item.width = Number(slider.value);
      try { checkDocumentSize(doc); }
      catch (error) { item.width = previous; slider.value = previous; $('feedback').textContent = error.message; return; }
      text.textContent = `图片${index + 1} · 宽度 ${item.width}%`; persist(); render();
    };
    const remove = document.createElement('button'); remove.textContent = '删除'; remove.setAttribute('aria-label', `删除图片${index + 1}`);
    remove.onclick = () => {
      const page = doc.pages[current];
      page.images.splice(index, 1);
      page.body = page.body.split('\n').filter(line => line.trim() !== `[图片${index + 1}]`).map(line => line.replace(/^\s*\[图片(\d+)\]\s*$/, (match, number) => Number(number) > index + 1 ? `[图片${Number(number) - 1}]` : match)).join('\n');
      persist(); syncEditor();
    };
    label.append(text, slider); row.append(thumbnail, label, remove);
    const captionLabel = document.createElement('label'); captionLabel.textContent = `图片${index + 1}说明`;
    const caption = document.createElement('textarea'); caption.rows = 2; caption.maxLength = 500; caption.placeholder = '可留空，在图片下方显示'; caption.value = item.caption ?? '';
    caption.oninput = () => {
      const previous = item.caption; item.caption = caption.value;
      try { checkDocumentSize(doc); }
      catch (error) { item.caption = previous; caption.value = previous ?? ''; $('feedback').textContent = error.message; return; }
      persist(); render();
    };
    captionLabel.append(caption); $('image-list').append(row, captionLabel);
  });
}
let imageInsertion = null;
$('add-image').onclick = () => {
  const page = doc.pages[current];
  if ((page.images?.length ?? 0) >= 8) { $('feedback').textContent = '每页最多支持 8 张图片。'; return; }
  imageInsertion = { page, start: $('body').selectionStart, end: $('body').selectionEnd, body: page.body };
  $('image-file').click();
};
$('image-file').onchange = async () => {
  const file = $('image-file').files[0], insertion = imageInsertion;
  if (!file || !insertion) return;
  $('add-image').disabled = true;
  try {
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 20 * 1024 * 1024) throw new Error('请选择 20 MB 以内的 PNG、JPEG 或 WebP 图片。');
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 1600 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement('canvas'); canvas.width = Math.max(1, Math.round(bitmap.width * scale)); canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const ctx = canvas.getContext('2d'); ctx.fillStyle = 'white'; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height); bitmap.close();
    const src = canvas.toDataURL('image/jpeg', .85);
    if (src.length > 1500000) throw new Error('图片压缩后仍超过 1 MB，请缩小图片后再试。');
    const page = insertion.page;
    if (!doc.pages.includes(page) || page.type !== 'article') throw new Error('页面已切换，请在正文页重新插入。');
    page.images ??= [];
    if (page.images.length >= 8) throw new Error('每页最多支持 8 张图片。');
    const marker = `[图片${page.images.length + 1}]`;
    const unchanged = page.body === insertion.body;
    const start = unchanged ? insertion.start : page.body.length;
    const end = unchanged ? insertion.end : start;
    const before = page.body.slice(0, start), after = page.body.slice(end);
    const nextBody = before + (before && !before.endsWith('\n') ? '\n' : '') + marker + (after.startsWith('\n') ? '' : '\n') + after;
    if (nextBody.length > 10000) throw new Error('正文已达到长度上限，请先减少文字。');
    const nextImages = [...page.images, { src, width: 100, caption: '' }];
    checkDocumentSize({ ...doc, pages: doc.pages.map(item => item === page ? { ...page, body: nextBody, images: nextImages } : item) });
    page.body = nextBody; page.images = nextImages;
    persist(); syncEditor(); $('feedback').textContent = '图片已插入，可调整宽度或移动正文中的图片标记。';
  } catch (error) { $('feedback').textContent = error.message; }
  finally { $('image-file').value = ''; $('add-image').disabled = false; }
};
function positionStyleMenu() {
  const menu = $('style-menu');
  if (!menu.matches(':popover-open')) return;
  const anchor = $('open-style').getBoundingClientRect();
  const inset = 16;
  const top = anchor.bottom + 10;
  const left = Math.max(inset, Math.min(anchor.left, window.innerWidth - menu.offsetWidth - inset));
  menu.style.left = left + 'px';
  menu.style.top = top + 'px';
  menu.style.maxHeight = Math.max(120, window.innerHeight - top - inset) + 'px';
}
$('style-menu').addEventListener('toggle', positionStyleMenu);
window.addEventListener('resize', positionStyleMenu);
window.addEventListener('scroll', positionStyleMenu, true);
$('add').onclick = () => {
  if (doc.pages.length >= 50) return;
  doc.pages.push({ type: 'article', title: '新的页面', subtitle: '', body: '', note: '' });
  try { checkDocumentSize(doc); }
  catch (error) { doc.pages.pop(); $('feedback').textContent = error.message; return; }
  current = doc.pages.length - 1; persist(); syncEditor();
};
$('delete').onclick = () => {
  if (doc.pages.length === 1 || !confirm('删除当前页面？此操作无法撤销。')) return;
  doc.pages.splice(current, 1); current = Math.min(current, doc.pages.length - 1); persist(); syncEditor();
};
async function download(blob, name) {
  const link = document.createElement('a');
  link.href = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('导出文件读取失败。'));
    reader.readAsDataURL(blob);
  });
  link.download = name; link.textContent = '下载 ' + name;
  $('downloads').replaceChildren(link);
  link.click();
}
$('save').onclick = () => { download(new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json' }), 'social-pages.json'); $('feedback').textContent = '内容已保存为 JSON，可导入继续编辑。'; };
$('import').onclick = () => $('file').click();
$('file').onchange = async () => {
  const file = $('file').files[0]; if (!file) return;
  try {
    if (file.size > MAX_DOCUMENT_BYTES) throw new Error('文件不能超过 20 MB。');
    const next = validateDocument(JSON.parse(await file.text()));
    if (!confirm('导入会替换当前全部页面。继续导入？')) return;
    doc = next; current = 0; persist(); syncEditor(); $('feedback').textContent = '内容已导入。';
  } catch (error) { $('feedback').textContent = '导入失败：' + error.message; }
  finally { $('file').value = ''; }
};
async function pageBlob(page, index, style) {
  const canvas = document.createElement('canvas');
  if (page.type === 'article') await StudioRenderer.loadImages(page);
  const { overflow } = StudioRenderer.draw(canvas, page, style);
  if (overflow) throw new Error(`第 ${index + 1} 页内容过长，请先调整后再导出。`);
  return new Promise((resolve, reject) => canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('PNG 生成失败。')), 'image/png'));
}
function zipFilename(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
  return `social-images-${values.year}${values.month}${values.day}-${values.hour}${values.minute}${values.second}.zip`;
}
async function exportImages(all) {
  if (exporting) return;
  const snapshot = structuredClone(doc), selected = current;
  exporting = true; render(); $('feedback').textContent = '正在生成图片…';
  try {
    await document.fonts.ready;
    if (all) {
      const files = [];
      for (let i = 0; i < snapshot.pages.length; i++) {
        files.push({ name: `page-${String(i + 1).padStart(2, '0')}.png`, blob: await pageBlob(snapshot.pages[i], i, snapshot.style) });
      }
      await download(await makeZip(files), zipFilename());
    } else await download(await pageBlob(snapshot.pages[selected], selected, snapshot.style), `page-${String(selected + 1).padStart(2, '0')}.png`);
    const size = StudioRenderer.dimensions(snapshot.style);
    $('feedback').textContent = `导出完成，每张图片为 ${size.width} × ${size.height} px。`;
  } catch (error) { $('feedback').textContent = error.message; }
  finally { exporting = false; render(); }
}
$('export').onclick = () => exportImages(false);
$('export-all').onclick = () => exportImages(true);
async function initialize() {
  try {
    const response = await fetch('initial.json', { cache: 'no-store', signal: AbortSignal.timeout(5000) });
    if (response.status === 200) {
      const rawSeed = await response.json();
      const seed = validateDocument(rawSeed);
      // Preserve existing draft keys for seed files created before optional style controls.
      const fingerprint = structuredClone(seed);
      if (rawSeed.styleProfiles === undefined) delete fingerprint.styleProfiles;
      for (const field of ['lineHeight', 'marginX', 'marginY', 'letterSpacing', 'aspectRatio', 'coverTitleSize', 'coverSubtitleSize', 'pageTitleSize']) {
        if (rawSeed.style[field] === undefined) delete fingerprint.style[field];
      }
      if (rawSeed.styleProfiles) {
        for (const ratio of ['3:4', '9:16']) {
          for (const field of ['coverTitleSize', 'coverSubtitleSize', 'pageTitleSize']) {
            if (rawSeed.styleProfiles[ratio]?.[field] === undefined) delete fingerprint.styleProfiles[ratio][field];
          }
        }
      }
      fingerprint.pages.forEach((page, index) => {
        if (rawSeed.pages[index].highlight === undefined) delete page.highlight;
        if (rawSeed.pages[index].images === undefined) delete page.images;
        else page.images.forEach((item, imageIndex) => {
          if (rawSeed.pages[index].images[imageIndex].caption === undefined) delete item.caption;
        });
      });
      const bytes = new TextEncoder().encode(JSON.stringify(fingerprint));
      const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
      storageKey += '-' + Array.from(digest, byte => byte.toString(16).padStart(2, '0')).join('');
      doc = seed;
    }
  } catch { $('feedback').textContent = '初始内容读取失败，正在恢复本地草稿。'; }
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) doc = validateDocument(JSON.parse(stored));
  } catch { $('feedback').textContent = '草稿读取失败，请导入已备份的内容。'; }
  doc = validateDocument(doc);
  syncEditor();
  // System fonts are sufficient for the first paint; never block the editor on fonts.
  document.fonts.ready.then(render).catch(() => {});
}
initialize().catch(error => {
  $('feedback').textContent = '页面初始化失败：' + error.message;
});
