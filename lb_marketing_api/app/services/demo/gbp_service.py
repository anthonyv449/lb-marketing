"""
GBP (Google Business Profile) service — STUBBED for development.
Replace stub methods with real Google My Business API calls when credentials are available.
Real API docs: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews
"""


class GBPService:

    async def list_reviews(self, gbp_account_id: str, gbp_location_id: str) -> list[dict]:
        """
        STUB: Returns mock reviews to simulate GBP API response.
        Real implementation: GET {REVIEWS_BASE}/{gbp_account_id}/{gbp_location_id}/reviews
        Returns list of review dicts matching GBP API shape:
          { reviewId, reviewer: { displayName }, comment, starRating, createTime, reviewReply }
        """
        return [
            {
                "reviewId": "mock-review-001",
                "reviewer": {"displayName": "Sarah M."},
                "comment": "Absolutely loved my balayage — the colour is exactly what I wanted. Best experience!",
                "starRating": "FIVE",
                "createTime": "2026-03-01T14:00:00Z",
                "reviewReply": None,
            },
            {
                "reviewId": "mock-review-002",
                "reviewer": {"displayName": "James T."},
                "comment": "Waited 40 minutes past my appointment. The result was fine but the wait was frustrating.",
                "starRating": "TWO",
                "createTime": "2026-03-03T10:30:00Z",
                "reviewReply": None,
            },
            {
                "reviewId": "mock-review-003",
                "reviewer": {"displayName": "Priya K."},
                "comment": "Great atmosphere and friendly staff. My cut was a little uneven but they fixed it.",
                "starRating": "THREE",
                "createTime": "2026-03-05T16:45:00Z",
                "reviewReply": {"comment": "Thank you for the feedback, Priya!"},
            },
        ]

    async def post_reply(
        self,
        gbp_account_id: str,
        gbp_location_id: str,
        review_id: str,
        reply_text: str,
    ) -> dict:
        """
        STUB: Simulates posting a reply to GBP. Always succeeds.
        Real implementation: PUT {REVIEWS_BASE}/{gbp_account_id}/{gbp_location_id}/reviews/{review_id}/reply
        """
        return {"comment": reply_text}
