from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import AccessibilityCheck, Review, SavedPlace, User, Venue
from .schemas import ReviewCreate, RouteOut, SavedCreate, UserOut, VenueOut, VenueListOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AccessNow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

def venue_score(db: Session, venue: Venue) -> int:
    checks = db.scalars(select(AccessibilityCheck).where(AccessibilityCheck.venue_id == venue.id)).all()
    if not checks:
        return 0
    return round(sum(c.percent for c in checks) / len(checks))

def venue_tags(venue: Venue) -> list[str]:
    return [x.strip() for x in venue.tags.split(",") if x.strip()]

def venue_list(db: Session, venue: Venue) -> VenueListOut:
    count = db.scalar(select(func.count(Review.id)).where(Review.venue_id == venue.id)) or 0
    return VenueListOut(
        id=venue.id, name=venue.name, address=venue.address, type=venue.type,
        icon=venue.icon, verified=venue.verified, score=venue_score(db, venue),
        review_count=count, tags=venue_tags(venue), map_x=venue.map_x, map_y=venue.map_y
    )

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "accessnow-api"}

@app.get("/api/venues", response_model=list[VenueListOut])
def list_venues(search: str | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(Venue).order_by(Venue.id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where((Venue.name.ilike(like)) | (Venue.address.ilike(like)) | (Venue.type.ilike(like)))
    return [venue_list(db, v) for v in db.scalars(stmt).all()]

@app.get("/api/venues/{venue_id}", response_model=VenueOut)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.get(Venue, venue_id)
    if not venue:
        raise HTTPException(404, "Venue not found")
    latest = db.scalar(
        select(Review).where(Review.venue_id == venue_id).order_by(Review.created_at.desc()).limit(1)
    )
    base = venue_list(db, venue)
    latest_out = None
    if latest:
        latest_out = {
            "id": latest.id, "rating": latest.rating, "category": latest.category,
            "body": latest.body, "author": latest.user.name, "created_at": latest.created_at
        }
    return VenueOut(
        **base.model_dump(),
        accessibility=[AccessibilityCheck.model_validate(x, from_attributes=True) for x in venue.accessibility],
        latest_review=latest_out
    )

@app.get("/api/venues/{venue_id}/route", response_model=RouteOut)
def route_to_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.get(Venue, venue_id)
    if not venue:
        raise HTTPException(404, "Venue not found")
    return RouteOut(
        venue_name=venue.name, minutes=12, miles=0.6,
        alternative_minutes=10, alternative_miles=0.5,
        alert="No reported lift outages or blocked curb cuts on this demo route."
    )

@app.post("/api/venues/{venue_id}/reviews", response_model=dict, status_code=201)
def create_review(venue_id: int, payload: ReviewCreate, db: Session = Depends(get_db)):
    venue = db.get(Venue, venue_id)
    user = db.get(User, payload.user_id)
    if not venue or not user:
        raise HTTPException(404, "Venue or user not found")
    review = Review(venue_id=venue_id, user_id=user.id, rating=payload.rating,
                    category=payload.category, body=payload.body)
    db.add(review)
    user.review_count += 1
    db.commit()
    db.refresh(review)
    return {"id": review.id, "status": "queued_for_moderation"}

@app.get("/api/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.get("/api/users/{user_id}/saved", response_model=list[VenueListOut])
def get_saved(user_id: int, db: Session = Depends(get_db)):
    saved = db.scalars(select(SavedPlace).where(SavedPlace.user_id == user_id).order_by(SavedPlace.created_at.desc())).all()
    return [venue_list(db, s.venue) for s in saved]

@app.post("/api/saved", status_code=201)
def save_place(payload: SavedCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id) or not db.get(Venue, payload.venue_id):
        raise HTTPException(404, "User or venue not found")
    existing = db.scalar(select(SavedPlace).where(
        SavedPlace.user_id == payload.user_id, SavedPlace.venue_id == payload.venue_id
    ))
    if existing:
        return {"id": existing.id, "status": "already_saved"}
    item = SavedPlace(user_id=payload.user_id, venue_id=payload.venue_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": "saved"}

@app.delete("/api/saved/{saved_id}", status_code=204)
def delete_saved(saved_id: int, db: Session = Depends(get_db)):
    item = db.get(SavedPlace, saved_id)
    if not item:
        raise HTTPException(404, "Saved place not found")
    db.delete(item)
    db.commit()

@app.get("/")
def index():
    if not FRONTEND.exists():
        raise HTTPException(404, "Frontend not installed")
    return FileResponse(FRONTEND)

@app.get("/{asset:path}")
def assets(asset: str):
    path = FRONTEND.parent / asset
    if path.exists() and path.is_file():
        return FileResponse(path)
    raise HTTPException(404, "Asset not found")
