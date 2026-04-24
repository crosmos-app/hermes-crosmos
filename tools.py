"""Tool handlers"""

import json
import os

import httpx

_BASE_URL = os.environ.get("CROSMOS_BASE_URL", "https://api.crosmos.dev/v1")
_API_KEY = os.environ.get("CROSMOS_API_KEY", "")
_DEFAULT_SPACE_ID = os.environ.get("CROSMOS_SPACE_ID", "")

_client = httpx.Client(
    base_url=_BASE_URL,
    headers={
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json",
    },
    timeout=30.0,
)


def crosmos_remember(args: dict, **kwargs) -> str:
    """Ingest content into the knowledge graph."""
    content = args.get("content", "").strip()
    space_id = args.get("space_id") or _DEFAULT_SPACE_ID

    if not content:
        return json.dumps({"error": "No content provided"})

    if not space_id:
        return json.dumps(
            {"error": "No space_id configured. Set CROSMOS_SPACE_ID or pass space_id."}
        )

    try:
        resp = _client.post(
            "/sources",
            json={
                "space_id": space_id,
                "sources": [{"content": content, "content_type": "text"}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(
            {
                "status": "accepted",
                "job_id": data.get("job_id"),
                "source_ids": data.get("source_ids", []),
                "message": f"Content ingested. Job {data.get('job_id', 'unknown')} is processing.",
            }
        )
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        )
    except Exception as e:
        return json.dumps({"error": f"Ingestion failed: {type(e).__name__}: {e}"})


def crosmos_recall(args: dict, **kwargs) -> str:
    """Search the knowledge graph for relevant memories."""
    query = args.get("query", "").strip()
    space_id = args.get("space_id") or _DEFAULT_SPACE_ID
    limit = min(max(args.get("limit", 10), 1), 50)
    include_source = args.get("include_source", True)

    if not query:
        return json.dumps({"error": "No query provided"})
    if not space_id:
        return json.dumps(
            {"error": "No space_id configured. Set CROSMOS_SPACE_ID or pass space_id."}
        )

    try:
        resp = _client.post(
            "/search",
            json={
                "query": query,
                "space_id": space_id,
                "limit": limit,
                "include_source": include_source,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates", [])
        results = []
        for c in candidates:
            entry = {
                "memory_id": c.get("memory_id"),
                "content": c.get("content"),
                "score": round(c.get("score", 0), 4),
                "type": c.get("memory_type"),
            }
            if include_source and c.get("source"):
                entry["source"] = c["source"]
            results.append(entry)

        return json.dumps(
            {
                "query": data.get("query"),
                "results": results,
                "total": data.get("total", len(results)),
                "took_ms": round(data.get("took_ms", 0)),
            }
        )
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        )
    except Exception as e:
        return json.dumps({"error": f"Search failed: {type(e).__name__}: {e}"})


def crosmos_forget(args: dict, **kwargs) -> str:
    """Soft-delete a memory."""
    memory_id = args.get("memory_id", "").strip()
    if not memory_id:
        return json.dumps({"error": "No memory_id provided"})

    try:
        resp = _client.delete(f"/memories/{memory_id}")
        if resp.status_code == 404:
            return json.dumps({"error": f"Memory {memory_id} not found"})
        resp.raise_for_status()
        return json.dumps({"status": "forgotten", "memory_id": memory_id})
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        )
    except Exception as e:
        return json.dumps({"error": f"Forget failed: {type(e).__name__}: {e}"})


def crosmos_graph_stats(args: dict, **kwargs) -> str:
    """Get knowledge graph statistics."""
    space_id = args.get("space_id") or _DEFAULT_SPACE_ID
    if not space_id:
        return json.dumps(
            {"error": "No space_id configured. Set CROSMOS_SPACE_ID or pass space_id."}
        )

    try:
        resp = _client.get("/graph/stats", params={"space_id": space_id})
        resp.raise_for_status()
        return json.dumps(resp.json())
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        )
    except Exception as e:
        return json.dumps({"error": f"Stats failed: {type(e).__name__}: {e}"})
