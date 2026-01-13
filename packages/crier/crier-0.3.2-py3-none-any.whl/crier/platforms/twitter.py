"""Twitter/X platform implementation (copy-paste mode).

Twitter's API requires complex OAuth setup and elevated access.
This implementation generates tweet text for manual posting instead.
"""

from typing import Any

from .base import Article, Platform, PublishResult


class Twitter(Platform):
    """Twitter/X copy-paste mode.

    Instead of posting via API, generates formatted tweet text
    that you can copy and paste into Twitter manually.

    No API key required - use any placeholder value.
    """

    name = "twitter"
    max_content_length = 280  # Twitter character limit

    def __init__(self, api_key: str):
        """API key is ignored - this is copy-paste mode."""
        super().__init__(api_key)

    def _format_tweet(self, article: Article) -> str:
        """Format article as a tweet."""
        parts = [article.title]

        if article.tags:
            hashtags = " ".join(f"#{tag.replace('-', '_')}" for tag in article.tags[:3])
            parts.append(hashtags)

        if article.canonical_url:
            parts.append(article.canonical_url)

        return "\n\n".join(parts)

    def publish(self, article: Article) -> PublishResult:
        """Generate tweet text for manual posting.

        Prints the formatted tweet to console for copy-pasting.
        """
        tweet = self._format_tweet(article)

        # Check content length
        if error := self._check_content_length(tweet):
            return PublishResult(
                success=False,
                platform=self.name,
                error=error,
            )

        # Print the tweet with clear formatting for copying
        print("\n" + "=" * 50)
        print("COPY THIS TWEET:")
        print("=" * 50)
        print(tweet)
        print("=" * 50)
        print(f"({len(tweet)} characters)")
        print("Post at: https://twitter.com/compose/tweet")
        print("=" * 50 + "\n")

        return PublishResult(
            success=True,
            platform=self.name,
            article_id="manual",
            url="https://twitter.com/compose/tweet",
        )

    def update(self, article_id: str, article: Article) -> PublishResult:
        """Generate updated tweet text."""
        return self.publish(article)

    def list_articles(self, limit: int = 10) -> list[dict[str, Any]]:
        """Not available in copy-paste mode."""
        return []

    def get_article(self, article_id: str) -> dict[str, Any] | None:
        """Not available in copy-paste mode."""
        return None

    def delete(self, article_id: str) -> bool:
        """Not available in copy-paste mode."""
        raise NotImplementedError("Manual mode - delete tweets at twitter.com")
