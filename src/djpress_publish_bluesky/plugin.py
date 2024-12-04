"""DJ Press plugin to publish posts to Bluesky."""

import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

import httpx
from djpress.conf import settings as djpress_settings
from djpress.plugins import DJPressPlugin

logger = logging.getLogger(__name__)


class Plugin(DJPressPlugin):
    name = "djpress_publish_bluesky"

    def setup(self, registry) -> None:
        registry.register_hook("post_save_post", self.publish_post)

    def publish_post(self, post):
        # Get the settings from the config dictionary
        handle = self.config.get("handle")  # Required
        password = self.config.get("app_password")  # Required
        site_url = self.config.get("site_url")  # Required
        pds_url = self.config.get("pds_url", "https://bsky.social")  # Optional
        post_message = self.config.get("post_message", "🚀 I created a new blog post!")  # Optional

        # Check for required settings and log a warning if any are missing
        missing_configs = [key for key in ["handle", "app_password", "site_url"] if not self.config.get(key)]
        if missing_configs:
            logger.warning("Bluesky plugin is not configured correctly. Missing config: %s", " ".join(missing_configs))
            return

        # The title and description are used for the embed in the post. The URI is the link to the post including the
        # site URL.
        title = djpress_settings.BLOG_TITLE
        description = post.title
        uri = urljoin(site_url, post.url)

        # We keep track of which posts have been published to Bluesky already by adding the post id to the data with a
        # key called "published_posts". This way we can check if the post has already been published to Bluesky.
        data = self.get_data()
        published_posts = data.get("published_posts", [])
        if post.id in published_posts:
            return

        # Try logging in to Blueskey to get the session object which will contain the accessJwt token.
        try:
            session = bsky_login_session(pds_url, handle, password)
        except (httpx.ConnectError, httpx.HTTPStatusError) as exc:
            logger.warning("Login to Bluesky failed: %s", exc)
            return

        # Create the post object to be sent to Bluesky
        bsky_post = get_bsky_post_embed(
            message=post_message,
            uri=uri,
            title=title,
            description=description,
        )

        # Try posting to Bluesky
        try:
            post_to_bsky(session, pds_url, bsky_post)
        except httpx.HTTPStatusError as exc:
            logger.warning("Posting to Bluesky failed: %s", exc)
            return

        published_posts.append(post.id)
        data["published_posts"] = published_posts
        self.save_data(data)


def bsky_login_session(pds_url: str, handle: str, password: str) -> dict:
    resp = httpx.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def post_to_bsky(session: dict, pds_url: str, post: str) -> None:
    resp = httpx.post(
        pds_url + "/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    resp.raise_for_status()
    return resp.json()


def get_bsky_post_embed(message: str, uri: str, title: str, description: str = "") -> dict:
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    post = {
        "$type": "app.bsky.feed.post",
        "text": message,
        "createdAt": created_at,
        "embed": {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": uri,
                "title": title,
                "description": description,
            },
        },
    }
    return post
