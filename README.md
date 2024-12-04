# DJ Press Bluesky Publisher

A plugin for [DJ Press](https://pypi.org/project/djpress/) that automatically publishes your blog posts to your
Bluesky account. When you publish a new post on your DJ Press site, this plugin will create a corresponding post on
your Bluesky account with a customisable message.

## Features

- 🚀 Automatic posting to Bluesky when blog posts are published
- 📝 Customisable post message
- ✅ Keeps track of posts that have already been posted to Bluesky, so you don't get multiple posts for the same blog post.

## Requirements

- Python >= 3.10
- Django >= 4.2
- DJ Press >= 0.12.1
- httpx>=0.28.0

## Installation

1. Install the package using pip:

    ```bash
    pip install djpress-publish-bluesky
    ```

2. Add the plugin to your `DJPRESS_SETTINGS` in `settings.py`:

    ```python
    DJPRESS_SETTINGS = {
        # ... existing settings
        "PLUGINS": [
            # ... existing plugins
            "djpress_publish_bluesky",
        ]
    }
    ```

3. Add the plugin settings to your `DJPRESS_SETTINGS` in `settings.py`:

    ```python
    DJPRESS_SETTINGS = {
        # ... existing settings
        "PLUGIN_SETTINGS": {
            # ... existing plugins
            "djpress_publish_Bluesky": {
                "handle": "username.bksy.social",  # check your Bluesky account profile for the full handle
                "app_password": "...",  # create an app password and preferably load from an environment variable or secrets manager
                "site_url": "https://example.com",  # the URL to your site so we can create the links properly
                "post_message": "🚀 I created a new blog post!",  # this can be ommitted if you're happy with the default message shown here
                "pds_url": "https://bsky.social",  # this can be ommitted if using the default bsky.social app
            }
        }
    }
    ```

## Configuration

### Getting Your Bluesky Password

1. Log into your Bluesky account
2. Go to Settings > Privacy and Security > App passwords
3. Click "Add App Password"
4. Give it a name (e.g., "My DJ Press Blog")
5. Don't give it any additional permissions
6. Copy and save the password into your `DJPRESS_SETTINGS` as described above.

## Usage

Once configured, the plugin works automatically. When you publish a new blog post, it will be posted to your Bluesky
account using the configured message.

**Note** that a published post will only be published to Bluesky once - the first time it is saved and with
`is_published = True`. This plugin keeps track of which posts have been published to Bluesky and won't publish them
again. The list of published posts is stored in the plugin storage model.

## Troubleshooting

If posts aren't appearing on Bluesky:

1. Check the Django logs for warning messages
2. Verify your handle and app password is correct
3. Ensure the plugin is enabled in settings
4. Confirm your Bluesky pds_url is correct
5. Check that your posts are marked as published

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Credits

Created by Stuart Maxwell
Powered by [DJ Press](https://github.com/yourusername/djpress)
