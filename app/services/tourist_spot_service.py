import re

from app.extensions import SessionLocal
from app.models.tourist_spot import TouristSpot


DEFAULT_SPOTS = [
    {
        "name": "Air Terjun Efrata",
        "category": "Alam",
        "description": "Air terjun bertingkat yang dikelilingi tebing hijau, populer untuk menikmati suasana sejuk dan panorama lembah.",
        "location": "Sosor Dolok, Harian, Samosir",
        "latitude": 2.5574,
        "longitude": 98.6234,
        "image_url": "",
        "rating": 4.8,
    },
    {
        "name": "Bukit Holbung (Bukit Teletubbies)",
        "category": "Alam",
        "description": "Perbukitan hijau bergelombang dengan pemandangan Danau Toba yang luas, cocok untuk trekking singkat dan fotografi.",
        "location": "Hariara Pohan, Harian, Samosir",
        "latitude": 2.6031,
        "longitude": 98.6874,
        "image_url": "",
        "rating": 4.9,
    },
    {
        "name": "Pantai Pasir Putih Parbaba",
        "category": "Alam",
        "description": "Pantai air tawar berpasir putih yang tenang, cocok untuk berenang, bermain air, dan liburan keluarga.",
        "location": "Huta Bolon, Pangururan, Samosir",
        "latitude": 2.6174,
        "longitude": 98.7193,
        "image_url": "",
        "rating": 4.7,
    },
    {
        "name": "Batu Hoda",
        "category": "Alam",
        "description": "Tepi danau dengan formasi batu unik, area santai, dan spot foto favorit saat sore hari.",
        "location": "Cinta Dame, Simanindo, Samosir",
        "latitude": 2.6673,
        "longitude": 98.8511,
        "image_url": "",
        "rating": 4.6,
    },
    {
        "name": "Aek Rangat Pangururan",
        "category": "Alam",
        "description": "Pemandian air panas alami di kaki bukit yang cocok untuk relaksasi sambil menikmati lanskap sekitar.",
        "location": "Pangururan, Samosir",
        "latitude": 2.6155,
        "longitude": 98.7152,
        "image_url": "",
        "rating": 4.6,
    },
    {
        "name": "Desa Wisata Tomok",
        "category": "Budaya",
        "description": "Kawasan wisata budaya Batak yang terkenal dengan makam raja kuno, suvenir, dan cerita sejarah lokal.",
        "location": "Tomok, Simanindo, Samosir",
        "latitude": 2.6584,
        "longitude": 98.8576,
        "image_url": "",
        "rating": 4.6,
    },
    {
        "name": "Museum Huta Bolon Simanindo",
        "category": "Sejarah",
        "description": "Kompleks rumah adat Batak dan museum budaya yang sering menampilkan pertunjukan Sigale-gale.",
        "location": "Simanindo, Samosir",
        "latitude": 2.6008,
        "longitude": 98.7923,
        "image_url": "",
        "rating": 4.8,
    },
    {
        "name": "Bukit Sibea-bea",
        "category": "Alam",
        "description": "Bukit dan jalan berkelok dengan panorama Danau Toba yang dramatis, cocok untuk perjalanan scenic.",
        "location": "Harian Boho, Samosir",
        "latitude": 2.5803,
        "longitude": 98.6582,
        "image_url": "",
        "rating": 4.8,
    },
    {
        "name": "Tuktuk Siadong",
        "category": "Kuliner",
        "description": "Kawasan wisata yang ramai dengan kafe, restoran, penginapan, dan akses tepi danau yang santai.",
        "location": "Tuktuk Siadong, Simanindo, Samosir",
        "latitude": 2.6598,
        "longitude": 98.8604,
        "image_url": "",
        "rating": 4.5,
    },
    {
        "name": "Makam Raja Sidabutar",
        "category": "Sejarah",
        "description": "Situs bersejarah Batak di Tomok yang menjadi tujuan utama untuk memahami warisan raja-raja lokal.",
        "location": "Tomok, Simanindo, Samosir",
        "latitude": 2.6579,
        "longitude": 98.8569,
        "image_url": "",
        "rating": 4.5,
    },
]


def seed_tourist_spots():
    session = SessionLocal()
    try:
        for item in DEFAULT_SPOTS:
            existing = session.query(TouristSpot).filter(TouristSpot.name == item["name"]).first()
            if existing:
                continue
            session.add(TouristSpot(**item))
        session.commit()
    finally:
        session.close()


def get_all_spots(page: int = 1, per_page: int = 20, category=None, search=None):
    session = SessionLocal()
    try:
        query = session.query(TouristSpot)

        if category:
            query = query.filter(TouristSpot.category.ilike(category.strip()))

        if search:
            ranked = _rank_spots(query.all(), search)
            total = len(ranked)
            sliced = ranked[(page - 1) * per_page: page * per_page]
            return {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page else 0,
                "data": [_serialize_spot(item) for item in sliced],
            }

        total = query.count()
        data = (
            query.order_by(TouristSpot.rating.desc(), TouristSpot.id.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page else 0,
            "data": [_serialize_spot(item) for item in data],
        }
    finally:
        session.close()


def get_spot_detail(spot_id: int):
    session = SessionLocal()
    try:
        spot = session.query(TouristSpot).filter(TouristSpot.id == spot_id).first()
        return _serialize_spot(spot) if spot else None
    finally:
        session.close()


def get_categories():
    session = SessionLocal()
    try:
        rows = (
            session.query(TouristSpot.category)
            .distinct()
            .order_by(TouristSpot.category.asc())
            .all()
        )
        return [row[0] for row in rows if row[0]]
    finally:
        session.close()


def search_spots_for_recommendations(theme: str, total: int = 3):
    session = SessionLocal()
    try:
        ranked = _rank_spots(session.query(TouristSpot).all(), theme)
        if not ranked:
            ranked = (
                session.query(TouristSpot)
                .order_by(TouristSpot.rating.desc(), TouristSpot.id.asc())
                .limit(max(total, 3))
                .all()
            )
        return [_serialize_spot(item) for item in ranked[:total]]
    finally:
        session.close()


def _serialize_spot(spot: TouristSpot):
    return {
        "id": spot.id,
        "name": spot.name,
        "category": spot.category,
        "description": spot.description,
        "location": spot.location,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
        "image_url": spot.image_url,
        "rating": spot.rating,
        "created_at": spot.created_at.isoformat() if spot.created_at else None,
    }


def _rank_spots(spots, query: str):
    normalized_query = (query or "").strip().lower()
    if not normalized_query:
        return sorted(spots, key=lambda item: (-float(item.rating or 0), item.id))

    terms = [term for term in re.split(r"\W+", normalized_query) if term]
    ranked = []

    for spot in spots:
        score = _score_spot(spot, normalized_query, terms)
        if score > 0:
            ranked.append((score, float(spot.rating or 0), spot))

    ranked.sort(key=lambda item: (-item[0], -item[1], item[2].id))
    return [item[2] for item in ranked]


def _score_spot(spot: TouristSpot, normalized_query: str, terms):
    haystacks = {
        "name": (spot.name or "").lower(),
        "category": (spot.category or "").lower(),
        "description": (spot.description or "").lower(),
        "location": (spot.location or "").lower(),
    }
    score = 0

    if normalized_query in haystacks["name"]:
        score += 10
    if normalized_query in haystacks["category"]:
        score += 7
    if normalized_query in haystacks["description"] or normalized_query in haystacks["location"]:
        score += 5

    for term in terms:
        if term in haystacks["name"]:
            score += 4
        if term in haystacks["category"]:
            score += 3
        if term in haystacks["description"]:
            score += 2
        if term in haystacks["location"]:
            score += 2

    if "air terjun" in normalized_query and "air terjun" in haystacks["name"]:
        score += 8
    if "pantai" in normalized_query and "pantai" in haystacks["name"]:
        score += 8
    if "kuliner" in normalized_query and (
        "kuliner" in haystacks["category"] or "restoran" in haystacks["description"] or "kafe" in haystacks["description"]
    ):
        score += 8
    if "budaya" in normalized_query and (
        "budaya" in haystacks["category"] or "adat" in haystacks["description"] or "sigale-gale" in haystacks["description"]
    ):
        score += 8
    if "sejarah" in normalized_query and (
        "sejarah" in haystacks["category"] or "makam" in haystacks["description"] or "warisan" in haystacks["description"]
    ):
        score += 8

    return score
