"""DJ Press plugin to publish posts to Bluesky."""

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import httpx
from djpress.conf import settings as djpress_settings
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import POST_SAVE_POST

if TYPE_CHECKING:
    from djpress.models import Post

logger = logging.getLogger(__name__)


class Plugin(DJPressPlugin):
    name = "djpress_publish_bluesky"
    hooks = [(POST_SAVE_POST, "publish_post")]

    def publish_post(self, post: "Post") -> "Post":
        # Get the settings from the settings dictionary
        handle = self.settings.get("handle", "")  # Required
        password = self.settings.get("app_password", "")  # Required
        site_url = self.settings.get("site_url", "")  # Required
        pds_url = self.settings.get("pds_url", "https://bsky.social")  # Optional
        post_message = self.settings.get("post_message", "🚀 I created a new blog post!")  # Optional

        # Check for required settings and log a warning if any are missing
        missing_configs = [key for key in ["handle", "app_password", "site_url"] if not self.settings.get(key)]
        if missing_configs:
            logger.warning(
                "Bluesky plugin is not configured correctly. Missing settings: %s", " ".join(missing_configs)
            )
            return post

        # The title and description are used for the embed in the post. The URI is the link to the post including the
        # site URL.
        title = str(djpress_settings.SITE_TITLE)
        description = post.title
        uri = urljoin(site_url, post.url)

        # We keep track of which posts have been published to Bluesky already by adding the post id to the data with a
        # key called "published_posts". This way we can check if the post has already been published to Bluesky.
        data = self.get_data()
        published_posts = data.get("published_posts", [])
        if post.pk in published_posts:
            return post

        # Try logging in to Blueskey to get the session object which will contain the accessJwt token.
        try:
            session = bsky_login_session(pds_url, handle, password)
        except (httpx.ConnectError, httpx.HTTPStatusError) as exc:
            logger.warning("Login to Bluesky failed: %s", exc)
            return post

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
            return post

        published_posts.append(post.pk)
        data["published_posts"] = published_posts
        self.save_data(data)

        return post


def bsky_login_session(pds_url: str, handle: str, password: str) -> dict:
    resp = httpx.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def post_to_bsky(session: dict, pds_url: str, post: dict) -> None:
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
