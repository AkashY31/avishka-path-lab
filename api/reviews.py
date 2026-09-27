"""Reviews API — submit and retrieve patient ratings."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.db import get_db
from database.models import Review

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    name: str
    phone: str | None = None
    rating: int
    comment: str | None = None
    test_taken: str | None = None
    location: str | None = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name is required.")
        return v.strip()


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/submit")
def submit_review(req: ReviewRequest, db: Session = Depends(get_db)):
    review = Review(
        name=req.name,
        phone=req.phone,
        rating=req.rating,
        comment=req.comment.strip() if req.comment else None,
        test_taken=req.test_taken,
        location=req.location,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"success": True, "message": "Thank you for your feedback!", "id": review.id}


@router.get("/list")
def list_reviews(limit: int = 20, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.is_approved == True)
        .order_by(Review.created_at.desc())
        .limit(min(limit, 50))
        .all()
    )
    return {
        "reviews": [
            {
                "id":         r.id,
                "name":       r.name,
                "rating":     r.rating,
                "comment":    r.comment,
                "test_taken": r.test_taken,
                "location":   r.location,
                "created_at": r.created_at.strftime("%d %b %Y"),
            }
            for r in reviews
        ]
    }


@router.get("/stats")
def review_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Review.id)).filter(Review.is_approved == True).scalar() or 0
    avg   = db.query(func.avg(Review.rating)).filter(Review.is_approved == True).scalar()
    avg   = round(float(avg), 1) if avg else 0.0

    breakdown = {}
    for star in range(1, 6):
        count = db.query(func.count(Review.id)).filter(
            Review.is_approved == True, Review.rating == star
        ).scalar() or 0
        breakdown[star] = count

    return {"total": total, "average": avg, "breakdown": breakdown}
