import json

from app.extensions import SessionLocal
from app.models.motivation import Motivation
from app.models.request_log import RequestLog
from app.services.llm_service import generate_from_llm
from app.services.tourist_spot_service import search_spots_for_recommendations
from app.utils.parser import parse_recommendations_response

def create_motivations(theme: str, total: int):
    session = SessionLocal()

    try:
        recommendations = _build_local_recommendations(theme, total)
        _try_enrich_recommendations_with_llm(theme, recommendations)

        req_log = RequestLog(theme=theme)
        session.add(req_log)
        session.commit()

        saved = []

        for item in recommendations:
            name = (item.get("name") or "").strip()
            description = (item.get("description") or "").strip()
            reason = (item.get("reason") or "").strip()
            category = (item.get("category") or "").strip()

            if not name:
                continue

            payload = {
                "name": name,
                "description": description,
                "reason": reason,
                "category": category,
            }

            m = Motivation(
                text=json.dumps(payload, ensure_ascii=False),
                request_id=req_log.id
            )
            session.add(m)
            saved.append(payload)

        session.commit()

        return saved

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def get_all_motivations(page: int = 1, per_page: int = 100):
    session = SessionLocal()

    try:
        query = session.query(Motivation)

        total = query.count()

        data = (
            query
            .order_by(Motivation.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        result = [
            {
                "id": m.id,
                "text": m.text,
                "item": _parse_saved_item(m.text),
                "created_at": m.created_at.isoformat()
            }
            for m in data
        ]

        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "data": result
        }

    finally:
        session.close()


def _parse_saved_item(raw_text: str):
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    return {
        "name": raw_text,
        "description": raw_text,
        "reason": "",
        "category": "",
    }


def _build_local_recommendations(theme: str, total: int):
    spots = search_spots_for_recommendations(theme, total)

    results = []
    for spot in spots:
        results.append(
            {
                "name": spot["name"],
                "description": spot["description"],
                "reason": _build_reason(theme, spot),
                "category": spot["category"],
            }
        )

    return results


def _build_reason(theme: str, spot: dict):
    normalized_theme = (theme or "").strip()
    location = spot.get("location") or "Samosir"
    category = spot.get("category") or "wisata"
    return f"Karena Anda mencari '{normalized_theme}', {spot['name']} relevan untuk kategori {category.lower()} dan berada di area {location}."


def _try_enrich_recommendations_with_llm(theme: str, recommendations):
    if not recommendations:
        return

    spots_context = json.dumps(recommendations, ensure_ascii=False)
    prompt = f"""
    Kamu adalah asisten wisata Samosir.
    Gunakan daftar rekomendasi berikut sebagai sumber utama dan jangan mengganti nama tempatnya:
    {spots_context}

    Berdasarkan query "{theme}", perbaiki setiap "description" dan "reason" agar lebih natural, singkat, dan relevan.
    Balas JSON saja tanpa markdown.
    Format:
    {{
        "recommendations": [
            {{
                "name": "...",
                "description": "...",
                "reason": "...",
                "category": "..."
            }}
        ]
    }}
    """

    try:
        result = generate_from_llm(prompt)
        enriched = parse_recommendations_response(result)
    except Exception:
        return

    by_name = {
        (item.get("name") or "").strip().lower(): item
        for item in enriched
        if (item.get("name") or "").strip()
    }

    for item in recommendations:
        enriched_item = by_name.get(item["name"].strip().lower())
        if not enriched_item:
            continue
        description = (enriched_item.get("description") or "").strip()
        reason = (enriched_item.get("reason") or "").strip()
        category = (enriched_item.get("category") or "").strip()
        if description:
            item["description"] = description
        if reason:
            item["reason"] = reason
        if category:
            item["category"] = category
