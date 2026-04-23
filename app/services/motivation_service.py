from app.extensions import SessionLocal
from app.models.motivation import Motivation
from app.models.request_log import RequestLog

def _build_motivation_texts(theme: str, total: int):
    clean_theme = theme.strip()
    templates = [
        "Tema {theme} tidak butuh langkah besar, cukup satu langkah konsisten hari ini.",
        "Saat proses terasa berat, ingat bahwa {theme} tetap tumbuh dari usaha kecil yang diulang.",
        "Fokus pada kemajuan di tema {theme}, bukan pada rasa takut yang datang lebih dulu.",
        "Setiap kegagalan dalam {theme} adalah data untuk mencoba dengan cara yang lebih tepat.",
        "Jangan tunggu sempurna untuk mulai, karena {theme} justru kuat saat kamu terus bergerak.",
        "Disiplin dalam {theme} akan membawa hasil bahkan ketika motivasi sedang rendah.",
        "Kalau hari ini terasa lambat, tetap lanjutkan {theme}; pelan tetap lebih baik daripada berhenti.",
        "Keberanian terbesar dalam {theme} sering dimulai dari keputusan sederhana untuk tidak menyerah.",
        "Beri dirimu ruang untuk belajar, karena perjalanan {theme} memang dibangun dari proses.",
        "Konsistensi pada {theme} hari ini adalah hadiah terbaik untuk dirimu di masa depan.",
    ]
    return [templates[i % len(templates)].format(theme=clean_theme) for i in range(total)]

def create_motivations(theme: str, total: int):
    session = SessionLocal()

    try:
        motivations = _build_motivation_texts(theme, total)

        req_log = RequestLog(theme=theme)
        session.add(req_log)
        session.commit()

        saved = []

        for text in motivations:
            m = Motivation(
                text=text,
                request_id=req_log.id
            )
            session.add(m)
            saved.append(text)

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
