# Lotion

Lotion is a wrapper for `notion-client` by [ramnes/notion-sdk-py: The official Notion API client library, but rewritten in Python! (sync + async)](https://github.com/ramnes/notion-sdk-py).

With Lotion, you can easily use the Notion API.

```python
from lotion import Lotion

lotion = Lotion.get_instance("NOTION_API_SECRET")
# or `lotion = Lotion.get_instance()` if you set it as `NOTION_SECRET`

pages = lotion.retrieve_database("1696567a3bbf803e9817c7ae1e398b71")
for page in pages:
    print(page.get_title().text)
```

## Install

```shell
pip install python-lotion
```

You must also create your integration, obtain a Notion API secret, and give your integration page permissions.

Reference: [Build your first integration](https://developers.notion.com/docs/create-a-notion-integration#create-your-integration-in-notion)

## Usage

Refer to [How to use Lotion](./docs/how_to_use_lotion.md).

If you have any questions, please create an issue.
