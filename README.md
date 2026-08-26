# PDF RAG API

## Run locally

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

The default metadata database is SQLite at `./storage/rag.db`.

The API is available at `http://localhost:8000` and its OpenAPI UI is at `/docs`.

- `GET /health/live`
- `GET /health/ready`
- `POST /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `POST /api/v1/documents/{document_id}/questions`
- `DELETE /api/v1/documents/{document_id}`

Ollama must have `qwen2.5:0.5b` and `nomic-embed-text` available locally.
