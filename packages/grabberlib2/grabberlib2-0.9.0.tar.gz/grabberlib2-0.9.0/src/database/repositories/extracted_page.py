from ..models import ExtractedPage
from ..repositories.base import BaseRepository


class ExtractedPageRepository(BaseRepository[ExtractedPage]):
    """ExtractedPage repository provides all the database operations for the ExtractedPage model."""

    def __init__(self, model: type[ExtractedPage]) -> None:
        super().__init__(ExtractedPage)

    async def was_already_posted_in_channel(self, url: str, channel: str) -> bool:
        """Check if the page was already sent to the channel."""
        first_qs = await self.filter_by(url__icontains=url, channel=channel)

        if not first_qs:
            result = await self.filter_by(url__icontains=url)

        return bool(first_qs) if first_qs else bool(result)
