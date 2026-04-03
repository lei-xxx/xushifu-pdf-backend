# PDF Compressor Backend (Ghostscript)

This is a small Flask API that compresses PDFs using Ghostscript.

## Endpoints

- `GET /health`
- `POST /compress` (form-data: `pdf` file, optional `quality` = screen|ebook|printer|prepress|default)

## Render (Docker)

This repo includes a `Dockerfile` and `render.yaml` for Render deployments.
