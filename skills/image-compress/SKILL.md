---
name: image-compress
description: Compress PNG images with a lossless-first workflow and optional light lossy fallback. Use when Codex needs to shrink single PNG files, whole asset directories, app image folders, or exported design assets; when the user asks to batch-compress PNGs; or when image size must drop without repeatedly reprocessing already-compressed, unchanged historical files.
---

# Image Compress

Use `scripts/compress_pngs.py` for actual work. Keep the default behavior lossless first:

1. Run `oxipng -o 4` on target PNG files.
2. Only when the user accepts slight quality loss and the file is still large, run `pngquant --quality=80-95 --skip-if-larger`.
3. Skip files that were already compressed by this workflow and have not changed since the last successful run.

## Workflow

### 1. Check dependencies

Run `command -v oxipng` and `command -v pngquant` before compression.

- If `oxipng` is missing, stop and ask the user whether to install it.
- If lossy fallback may be needed and `pngquant` is missing, ask the user whether to install it.
- Only install after explicit user approval. Prefer `brew install oxipng pngquant`, or install only the missing tool.

### 2. Choose the mode

Use lossless-only mode by default.

- Use this when the user says `压缩图片` but does not permit quality loss.
- Command shape:

```bash
python3 ~/.codex/skills/image-compress/scripts/compress_pngs.py path/to/file-or-dir
```

Enable lossy fallback only when the user clearly allows slight quality loss.

- Keep `oxipng -o 4` as the first pass.
- Let `pngquant` run only on files whose post-oxipng size is still above the threshold.
- Command shape:

```bash
python3 ~/.codex/skills/image-compress/scripts/compress_pngs.py path/to/file-or-dir --allow-lossy
```

If the user wants a different threshold for "still large", pass `--lossy-above-bytes`.

## Cache and repeat runs

The script writes a manifest file named `.image-compress-cache.json` into the scan root.

- Treat a file as unchanged when the cached `mtime_ns` and `size` still match.
- If stat data changed, compare `sha256`; skip again when content is actually unchanged.
- Update the cache only after a successful compression or verified skip.
- Do not delete the cache unless the user asks to reset history.

This is the main guard against reprocessing old PNGs that were already compressed and not modified later.

## Output expectations

Report, at minimum:

- how many PNGs were scanned
- how many were skipped from cache
- how many changed after `oxipng`
- how many changed after `pngquant`
- how many had no further gain
- any files that failed

If the user asks for Git-safe behavior, review the changed files before staging and do not touch unrelated binary assets.
