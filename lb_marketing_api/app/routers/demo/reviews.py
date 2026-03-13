from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ... import models, schemas
from ...auth import get_current_user
from ...config import settings
from ...services.demo.gbp_service import GBPService
from ...services.demo.claude_service import ClaudeService

router = APIRouter(prefix="/demo/engagements/{engagement_id}/reviews", tags=["demo"])


def get_gbp_service() -> GBPService:
    return GBPService()


def get_claude_service() -> ClaudeService:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")
    return ClaudeService(api_key=settings.ANTHROPIC_API_KEY)


def _get_engagement_or_403(
    engagement_id: int,
    current_user: models.User,
    db: Session,
) -> models.ClientEngagement:
    engagement = db.get(models.ClientEngagement, engagement_id)
    if not engagement:
        raise HTTPException(404, "Engagement not found")
    if engagement.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return engagement


@router.get("", response_model=List[schemas.ReviewRecordOut])
def list_reviews(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_engagement_or_403(engagement_id, current_user, db)
    return (
        db.query(models.ReviewRecord)
        .filter(models.ReviewRecord.engagement_id == engagement_id)
        .order_by(models.ReviewRecord.review_published_at.desc())
        .all()
    )


@router.post("/sync")
async def sync_reviews(
    engagement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engagement = _get_engagement_or_403(engagement_id, current_user, db)

    if not engagement.gbp_account_id or not engagement.gbp_location_id:
        raise HTTPException(
            400, "GBP account ID and location ID must be set on the engagement."
        )

    gbp = get_gbp_service()
    gbp_reviews = await gbp.list_reviews(
        engagement.gbp_account_id, engagement.gbp_location_id
    )

    new_count = 0
    updated_count = 0

    for rev in gbp_reviews:
        gbp_review_id = rev["reviewId"]
        existing = (
            db.query(models.ReviewRecord)
            .filter(
                models.ReviewRecord.engagement_id == engagement_id,
                models.ReviewRecord.gbp_review_id == gbp_review_id,
            )
            .first()
        )

        if not existing:
            published_at = None
            if rev.get("createTime"):
                try:
                    published_at = datetime.fromisoformat(
                        rev["createTime"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            reply = rev.get("reviewReply")
            record = models.ReviewRecord(
                engagement_id=engagement_id,
                gbp_review_id=gbp_review_id,
                reviewer_name=rev.get("reviewer", {}).get("displayName"),
                review_text=rev.get("comment"),
                star_rating=rev.get("starRating"),
                review_published_at=published_at,
                has_reply=reply is not None,
                reply_text=reply.get("comment") if reply else None,
            )
            db.add(record)
            new_count += 1
        else:
            reply = rev.get("reviewReply")
            if reply and not existing.has_reply:
                existing.has_reply = True
                existing.reply_text = reply.get("comment")
                updated_count += 1

    db.commit()
    return {"synced": len(gbp_reviews), "new": new_count, "updated": updated_count}


@router.post("/auto-reply", response_model=schemas.AutoReplyResult)
async def auto_reply(
    engagement_id: int,
    payload: schemas.AutoReplyRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engagement = _get_engagement_or_403(engagement_id, current_user, db)
    claude = get_claude_service()
    gbp = get_gbp_service()

    unanswered = (
        db.query(models.ReviewRecord)
        .filter(
            models.ReviewRecord.engagement_id == engagement_id,
            models.ReviewRecord.has_reply == False,  # noqa: E712
        )
        .all()
    )

    if not unanswered:
        return schemas.AutoReplyResult(
            processed=0, succeeded=0, failed=0, dry_run=payload.dry_run, results=[]
        )

    results: list[schemas.AutoReplyResultItem] = []
    succeeded = 0
    failed = 0

    for review in unanswered:
        item = schemas.AutoReplyResultItem(
            review_id=review.id,
            gbp_review_id=review.gbp_review_id,
            reviewer=review.reviewer_name or "Unknown",
            review_snippet=(review.review_text or "")[:120],
            generated_reply=None,
            posted=False,
            saved=False,
            error=None,
        )
        try:
            reply_text = await claude.generate_review_reply(
                business_name=engagement.business.name,
                reviewer_name=review.reviewer_name or "Valued Customer",
                review_text=review.review_text or "",
                star_rating=review.star_rating or "THREE",
                tone=payload.tone,
                industry=engagement.industry,
            )
            item.generated_reply = reply_text

            if not payload.dry_run:
                if engagement.gbp_account_id and engagement.gbp_location_id and review.gbp_review_id:
                    await gbp.post_reply(
                        engagement.gbp_account_id,
                        engagement.gbp_location_id,
                        review.gbp_review_id,
                        reply_text,
                    )
                    item.posted = True

                review.has_reply = True
                review.reply_text = reply_text
                review.reply_generated_by = "ai"
                review.reply_posted_at = datetime.utcnow()
                db.commit()
                item.saved = True

            succeeded += 1
        except Exception as exc:
            item.error = str(exc)
            failed += 1

        results.append(item)

    return schemas.AutoReplyResult(
        processed=len(unanswered),
        succeeded=succeeded,
        failed=failed,
        dry_run=payload.dry_run,
        results=results,
    )


@router.post("/{review_id}/reply")
async def reply_single(
    engagement_id: int,
    review_id: int,
    payload: schemas.AutoReplyRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engagement = _get_engagement_or_403(engagement_id, current_user, db)

    review = db.get(models.ReviewRecord, review_id)
    if not review or review.engagement_id != engagement_id:
        raise HTTPException(404, "Review not found")

    claude = get_claude_service()
    gbp = get_gbp_service()

    reply_text = await claude.generate_review_reply(
        business_name=engagement.business.name,
        reviewer_name=review.reviewer_name or "Valued Customer",
        review_text=review.review_text or "",
        star_rating=review.star_rating or "THREE",
        tone=payload.tone,
        industry=engagement.industry,
    )

    if not payload.dry_run:
        if engagement.gbp_account_id and engagement.gbp_location_id and review.gbp_review_id:
            await gbp.post_reply(
                engagement.gbp_account_id,
                engagement.gbp_location_id,
                review.gbp_review_id,
                reply_text,
            )

        review.has_reply = True
        review.reply_text = reply_text
        review.reply_generated_by = "ai"
        review.reply_posted_at = datetime.utcnow()
        db.commit()

    return {
        "review_id": review_id,
        "reply": reply_text,
        "saved": not payload.dry_run,
    }
