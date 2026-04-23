import json

from app.extensions import SessionLocal
from app.models.motivation import Motivation
from app.models.request_log import RequestLog
from app.services.llm_service import generate_from_llm
from app.utils.parser import parse_recommendations_response

def create_motivations(theme: str, total: int):
    session = SessionLocal()

    try:
        prompt = f"""
        Kamu adalah AI rekomendasi wisata untuk Pulau Samosir dan kawasan Danau Toba.
        Berdasarkan query "{theme}", buat {total} rekomendasi wisata yang paling relevan di Samosir.
        Gunakan bahasa Indonesia.
        Balas dengan rekomendasi yang konkret dan terasa seperti panduan wisata.
        Balas JSON saja tanpa markdown.
        Format:
        {{
            "recommendations": [
                {{
                    "name": "...",
                    "description": "...",
                    "reason": "...",
                    "category": "Alam/Budaya/Sejarah/Kuliner"
                }}
            ]
        }}
        """
        result = generate_from_llm(prompt)
        recommendations = parse_recommendations_response(result)

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
