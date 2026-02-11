from typing import Annotated, List
import base64
import hashlib
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import (
    LinkCreate,
    LinkInfo,
    LinkResolveResponse,
    LinkStatsItem,
    LinkMonthBreakdownItem,
)
from database import engine, SessionLocal
import db_models


app = FastAPI()
db_models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


dp_dependency = Annotated[SessionLocal, Depends(get_db)]


def _generate_short_code(target_url: str, salt: str = "", length: int = 8) -> str:
    """Generate a deterministic short code from the target URL and optional salt."""
    hasher = hashlib.sha256()
    hasher.update((target_url + salt).encode("utf-8"))
    digest = hasher.digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return encoded[:length]


EARNING_PER_CLICK = Decimal("0.05")


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/links", response_model=LinkInfo)
def create_short_link(payload: LinkCreate, request: Request, db: dp_dependency):
    """Create or retrieve a short URL for the given target URL."""
    target_url = payload.target_url.strip()

    # Return existing short URL if this target already exists
    existing = db.query(db_models.LinkModel).filter(db_models.LinkModel.target_url == target_url).first()
    if existing:
        short_url = f"{request.base_url}{existing.short_code}"
        return LinkInfo(short_url=short_url, short_code=existing.short_code)

    # Generate a new short code with collision handling
    salt_counter = 0
    while True:
        salt = str(salt_counter) if salt_counter > 0 else ""
        short_code = _generate_short_code(target_url, salt=salt)

        # If the code is already used for a different URL, try another salt
        existing_code = db.query(db_models.LinkModel).filter(db_models.LinkModel.short_code == short_code).first()
        if existing_code and existing_code.target_url != target_url:
            salt_counter += 1
            continue

        new_link = db_models.LinkModel(
            target_url=target_url,
            short_code=short_code,
            total_clicks=0,
            total_earnings=Decimal("0"),
        )
        db.add(new_link)

        try:
            db.commit()
            db.refresh(new_link)
            break
        except IntegrityError:
            # In case of a race or constraint violation, retry with a new salt
            db.rollback()
            salt_counter += 1

    short_url = f"{request.base_url}{new_link.short_code}"
    return LinkInfo(short_url=short_url, short_code=new_link.short_code)


@app.get("/stats", response_model=List[LinkStatsItem])
def get_stats(db: dp_dependency):
    """Return per-link stats including totals and monthly breakdown."""
    links = db.query(db_models.LinkModel).all()
    if not links:
        return []

    link_ids = [link.id for link in links]

    # Aggregate clicks per link per month in a single query
    click_rows = (
        db.query(
            db_models.LinkClickModel.link_id,
            func.to_char(func.date_trunc("month", db_models.LinkClickModel.clicked_at), "YYYY-MM").label("month"),
            func.count().label("clicks"),
        )
        .filter(db_models.LinkClickModel.link_id.in_(link_ids))
        .group_by(
            db_models.LinkClickModel.link_id,
            func.date_trunc("month", db_models.LinkClickModel.clicked_at),
        )
        .all()
    )

    breakdown_by_link: dict[int, list[LinkMonthBreakdownItem]] = {}
    for row in click_rows:
        earnings = float(row.clicks) * float(EARNING_PER_CLICK)
        item = LinkMonthBreakdownItem(month=row.month, clicks=row.clicks, earnings=earnings)
        breakdown_by_link.setdefault(row.link_id, []).append(item)

    stats: list[LinkStatsItem] = []
    for link in links:
        monthly_breakdown = breakdown_by_link.get(link.id, [])
        total_earnings = float(link.total_earnings) if link.total_earnings is not None else 0.0
        stats.append(
            LinkStatsItem(
                short_code=link.short_code,
                target_url=link.target_url,
                total_clicks=link.total_clicks or 0,
                total_earnings=total_earnings,
                monthly_breakdown=monthly_breakdown,
            )
        )

    return stats


@app.get("/{short_code}", response_model=LinkResolveResponse)
def resolve_short_code(short_code: str, db: dp_dependency):
    """Resolve a short code to its original target URL and record the click."""
    link = db.query(db_models.LinkModel).filter(db_models.LinkModel.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Record click event
    click = db_models.LinkClickModel(link_id=link.id)
    db.add(click)

    # Update aggregate counters
    link.total_clicks = (link.total_clicks or 0) + 1
    if link.total_earnings is None:
        link.total_earnings = Decimal("0")
    link.total_earnings += EARNING_PER_CLICK

    db.commit()
    db.refresh(link)

    return LinkResolveResponse(target_url=link.target_url)

