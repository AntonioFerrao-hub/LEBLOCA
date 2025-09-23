from __future__ import annotations

from datetime import datetime
from typing import Iterable

from flask import current_app

from .models import GoogleAccount, ReviewSnapshot, db


class GoogleReviewsClient:
    """Facade for integrating with the Google Business Profile API."""

    def __init__(self, account: GoogleAccount):
        self.account = account

    def fetch_reviews(self) -> Iterable[dict]:
        current_app.logger.info(
            "Simulando coleta de avaliações para a conta %s", self.account.display_name
        )
        sample_reviews = [
            {
                "reviewId": "sample-1",
                "reviewer": {"displayName": "Maria Souza"},
                "starRating": 5,
                "comment": "Excelente atendimento!",
                "updateTime": datetime.utcnow().isoformat(),
            },
            {
                "reviewId": "sample-2",
                "reviewer": {"displayName": "João Silva"},
                "starRating": 3,
                "comment": "Bom, mas pode melhorar.",
                "updateTime": datetime.utcnow().isoformat(),
            },
        ]
        return sample_reviews


def sync_reviews(account: GoogleAccount) -> list[ReviewSnapshot]:
    client = GoogleReviewsClient(account)
    external_reviews = client.fetch_reviews()

    synced_reviews: list[ReviewSnapshot] = []
    for review in external_reviews:
        review_id = review.get("reviewId")
        if not review_id:
            continue

        snapshot = ReviewSnapshot.query.filter_by(
            google_account_id=account.id, review_id=review_id
        ).first()

        if snapshot is None:
            snapshot = ReviewSnapshot(
                google_account_id=account.id,
                review_id=review_id,
            )

        snapshot.reviewer_name = (review.get("reviewer") or {}).get("displayName")
        snapshot.rating = review.get("starRating") or 0
        snapshot.comment = review.get("comment")
        update_time = review.get("updateTime")
        snapshot.review_time = (
            datetime.fromisoformat(update_time.replace("Z", "+00:00"))
            if update_time
            else None
        )
        db.session.add(snapshot)
        synced_reviews.append(snapshot)

    db.session.commit()

    return synced_reviews


__all__ = ["sync_reviews", "GoogleReviewsClient"]
