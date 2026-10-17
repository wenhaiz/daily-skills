/* Both preview and PNG export use these exact pixel coordinates. */
window.StudioRenderer = (() => {
  const WIDTH = 1242, HEIGHT = 1656;
  const FONT = '"Songti SC", "STSong", "Noto Serif CJK SC", "SimSun", serif';
  const BODY_FONT = '"PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif';
  const segmenter = new Intl.Segmenter('zh-CN', { granularity: 'grapheme' });
  function graphemes(text) {
    return Array.from(segmenter.segment(text), item => item.segment);
  }
  function textWidth(ctx, text, spacing) {
    if (!spacing) return ctx.measureText(text).width;
    const units = graphemes(text);
    return units.reduce((width, unit) => width + ctx.measureText(unit).width, 0) + Math.max(0, units.length - 1) * spacing;
  }
  function drawBodyLine(ctx, text, x, y, spacing) {
    if (!spacing) { ctx.fillText(text, x, y); return; }
    for (const unit of graphemes(text)) {
      ctx.fillText(unit, x, y);
      x += ctx.measureText(unit).width + spacing;
    }
  }
  function wrap(ctx, text, maxWidth, spacing = 0) {
    const lines = [];
    for (const paragraph of text.split('\n')) {
      let line = '';
      for (const { segment } of segmenter.segment(paragraph)) {
        if (line && textWidth(ctx, line + segment, spacing) > maxWidth) {
          // Keep Chinese closing punctuation off the beginning of a line.
          if (/^[，。！？；：、）》」』】]$/.test(segment)) {
            const units = Array.from(segmenter.segment(line), item => item.segment);
            const tail = units.pop();
            lines.push(units.join('')); line = tail;
          } else { lines.push(line); line = ''; }
        }
        line += segment;
      }
      lines.push(line);
    }
    return lines;
  }
  function underline(ctx, x, y, width, color, thickness = 19) {
    ctx.strokeStyle = color; ctx.lineWidth = thickness; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x, y);
    ctx.bezierCurveTo(x + width * .3, y - 14, x + width * .85, y - 28, x + width, y - 17);
    ctx.stroke();
  }
  function findHighlight(title, query, renderedText, lines) {
    const start = title.indexOf(query);
    if (start < 0) return null;
    const end = start + query.length;
    let cursor = 0;
    for (let index = 0; index < lines.length; index++) {
      const lineStart = renderedText.indexOf(lines[index], cursor);
      const lineEnd = lineStart + lines[index].length;
      if (start >= lineStart && end <= lineEnd) {
        return { index, start: start - lineStart, end: end - lineStart };
      }
      cursor = lineEnd;
    }
    return null;
  }
  function selectedUnderline(ctx, line, range, x, y, color, thickness = 19) {
    const prefixWidth = ctx.measureText(line.slice(0, range.start)).width;
    const endWidth = ctx.measureText(line.slice(0, range.end)).width;
    underline(ctx, x + prefixWidth, y, endWidth - prefixWidth, color, thickness);
  }
  const imageCache = new Map();
  async function loadImages(page) {
    await Promise.all((page.images ?? []).map(({ src }) => {
      if (!imageCache.has(src)) {
        const image = new Image();
        const ready = new Promise((resolve, reject) => {
          image.onload = () => resolve(image);
          image.onerror = () => { imageCache.delete(src); reject(new Error('图片读取失败，请重新插入图片。')); };
        });
        imageCache.set(src, { image, ready });
        image.src = src;
      }
      return imageCache.get(src).ready;
    }));
  }
  function drawImageCard(ctx, image, x, y, width, height) {
    const radius = Math.min(16, width / 2, height / 2);
    // Draw the shadow before clipping so it remains outside the image.
    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.10)';
    ctx.shadowBlur = 18; ctx.shadowOffsetY = 6;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.roundRect(x, y, width, height, radius); ctx.fill();
    ctx.restore();
    ctx.save();
    ctx.beginPath(); ctx.roundRect(x, y, width, height, radius); ctx.clip();
    ctx.drawImage(image, x, y, width, height);
    ctx.restore();
  }
  function dimensions(style) {
    return style.aspectRatio === '9:16' ? { width: 1280, height: 2124 } : { width: WIDTH, height: HEIGHT };
  }
  function draw(canvas, page, style) {
    const { width: WIDTH, height: HEIGHT } = dimensions(style);
    const ctx = canvas.getContext('2d');
    canvas.width = WIDTH; canvas.height = HEIGHT;
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, WIDTH, HEIGHT);
    ctx.fillStyle = '#080808'; ctx.textBaseline = 'top';
    const margin = (style.marginX ?? 90) + (page.type === 'cover' ? 60 : 0);
    const marginY = style.marginY ?? 110;
    const bottom = HEIGHT - marginY;
    const maxWidth = WIDTH - margin * 2;
    ctx.font = `20px ${FONT}`;
    const noteLines = page.note?.trim() ? wrap(ctx, page.note, maxWidth) : [];
    const noteHeight = noteLines.length ? 20 + (noteLines.length - 1) * 40 : 0;
    const noteTop = bottom - noteHeight;
    const contentBottom = noteLines.length ? noteTop - 44 : bottom;
    let overflow = contentBottom < marginY;
    let highlightWarning = '';
    let imageWarning = '';
    const query = (page.highlight ?? '').trim();
    const missingHighlight = '指定文字未匹配到标题中的单行内容，请检查文字或换行位置。';
    if (page.type === 'cover') {
      const titleSize = style.coverTitleSize ?? 112;
      const subtitleSize = style.coverSubtitleSize ?? 36;
      const titleStep = Math.round(titleSize * 162 / 112);
      const subtitleStep = Math.round(subtitleSize * 62 / 36);
      const underlineOffset = Math.round(titleSize * 126 / 112);
      ctx.font = `500 ${titleSize}px ${BODY_FONT}`;
      const lines = wrap(ctx, page.title, maxWidth);
      const highlight = query ? findHighlight(page.title, query, page.title, lines) : null;
      if (query && !highlight) highlightWarning = missingHighlight;
      let blockWidth = Math.max(0, ...lines.map(line => ctx.measureText(line).width));
      ctx.font = `${subtitleSize}px ${BODY_FONT}`;
      const subtitleLines = page.subtitle ? wrap(ctx, page.subtitle, maxWidth) : [];
      blockWidth = Math.max(blockWidth, ...subtitleLines.map(line => ctx.measureText(line).width));
      const blockX = (WIDTH - blockWidth) / 2;
      ctx.font = `500 ${titleSize}px ${BODY_FONT}`;
      const titleHeight = lines.length * titleStep;
      const subtitleHeight = subtitleLines.length ? 56 + subtitleLines.length * subtitleStep : 0;
      let y = Math.max(marginY, (marginY + contentBottom - titleHeight - subtitleHeight) / 2);
      lines.forEach((line, index) => {
        const lineWidth = ctx.measureText(line).width;
        if (highlight && index === highlight.index) {
          selectedUnderline(ctx, line, highlight, blockX, y + underlineOffset, style.accent, style.coverHighlightWidth ?? 30);
        } else if (!query && index === 0 && line.trim()) {
          const underlineWidth = Math.min(lineWidth, 360);
          underline(ctx, blockX + 6, y + underlineOffset, underlineWidth, style.accent, style.coverHighlightWidth ?? 30);
        }
        ctx.fillText(line, blockX, y);
        y += titleStep;
      });
      if (page.subtitle) {
        y += 48;
        ctx.font = `${subtitleSize}px ${BODY_FONT}`; ctx.fillStyle = '#777777';
        subtitleLines.forEach(line => { ctx.fillText(line, blockX, y + 12); y += subtitleStep; });
        ctx.fillStyle = '#080808';
      }
      overflow ||= y > contentBottom;
    } else {
      let y = marginY;
      if (page.title.trim()) {
        const titleSize = style.pageTitleSize ?? 56;
        const titleStep = Math.round(titleSize * 78 / 56);
        ctx.font = `500 ${titleSize}px ${BODY_FONT}`;
        const heading = page.title;
        const titleLines = wrap(ctx, heading, maxWidth);
        const highlight = query ? findHighlight(page.title, query, heading, titleLines) : null;
        if (query && !highlight) highlightWarning = missingHighlight;
        // Paint decoration first so title glyphs always remain on top.
        if (highlight) selectedUnderline(ctx, titleLines[highlight.index], highlight, margin, y + (highlight.index + 1) * titleStep, style.accent);
        else if (!query) underline(ctx, margin, y + titleLines.length * titleStep + 15, 180, style.accent);
        titleLines.forEach(line => {
          ctx.fillText(line, margin, y);
          y += titleStep;
        });
        y += 90;
      }
      ctx.font = `${style.bodySize}px ${BODY_FONT}`; ctx.fillStyle = '#333333';
      const lineHeight = style.bodySize * (style.lineHeight ?? 1.65);
      const spacing = style.letterSpacing ?? 0;
      // Image markers occupy a separate paragraph; images keep their aspect ratio.
      for (const paragraph of page.body.split('\n')) {
        const marker = /^\[图片(\d+)\]$/.exec(paragraph.trim());
        if (marker) {
          const item = page.images?.[Number(marker[1]) - 1];
          const image = item && imageCache.get(item.src)?.image;
          if (!image?.naturalWidth) { overflow = true; imageWarning = item ? '正在加载图片…' : `未找到图片${marker[1]}，请检查正文中的图片标记。`; continue; }
          const width = maxWidth * item.width / 100;
          const height = width * image.naturalHeight / image.naturalWidth;
          drawImageCard(ctx, image, margin + (maxWidth - width) / 2, y, width, height);
          y += height;
          if (item.caption?.trim()) {
            y += 40;
            ctx.font = `26px ${BODY_FONT}`; ctx.fillStyle = '#999999';
            for (const line of wrap(ctx, item.caption, width)) {
              ctx.fillText(line, margin + (maxWidth - ctx.measureText(line).width) / 2, y);
              y += 40;
            }
            ctx.font = `${style.bodySize}px ${BODY_FONT}`; ctx.fillStyle = '#333333';
          }
          y += style.bodySize * .8;
        } else {
          const list = /^\s*([-*+]|\d+[.)])\s+(.+)$/.exec(paragraph);
          const markerText = list ? (/^[-*+]$/.test(list[1]) ? '•' : list[1]) : '';
          const indent = list ? Math.max(style.bodySize * 1.25, ctx.measureText(markerText).width + 18) : 0;
          if (list) ctx.fillText(markerText, margin, y);
          const text = list ? list[2] : paragraph;
          for (const line of wrap(ctx, text, maxWidth - indent, spacing)) {
            if (line.trim()) { drawBodyLine(ctx, line, margin + indent, y, spacing); y += lineHeight; }
            else y += style.bodySize * .8;
          }
        }
      }
      overflow ||= y > contentBottom;
    }
    if (noteLines.length) {
      ctx.fillStyle = '#777777'; ctx.font = `20px ${FONT}`;
      noteLines.forEach((line, index) => ctx.fillText(line, margin, noteTop + index * 40));
    }
    const watermark = (style.watermarkText ?? '').trim();
    if (watermark) {
      // Use the bottom margin, separate from the content and reference area.
      ctx.save();
      ctx.font = `${style.watermarkSize ?? 24}px ${BODY_FONT}`;
      ctx.fillStyle = `rgba(0, 0, 0, ${(style.watermarkOpacity ?? 12) / 100})`;
      ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
      const inset = style.marginX ?? 90;
      ctx.fillText(watermark, WIDTH - inset, HEIGHT - 24, WIDTH - inset * 2);
      ctx.restore();
    }
    return { overflow, highlightWarning, imageWarning };
  }
  return { draw, loadImages, dimensions, WIDTH, HEIGHT };
})();
