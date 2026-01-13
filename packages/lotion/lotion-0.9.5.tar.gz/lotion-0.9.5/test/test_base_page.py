import json
from unittest import TestCase

from lotion.base_page import BasePage
from lotion.properties.title import Title


class TestBasePage(TestCase):
    def test_ページを作成する(self):
        # When
        actual = BasePage.create(properties=[], blocks=[])

        # Then
        self.assertEqual([], actual.properties.values)

    def test_タイトルとリンクをSlack形式で出力する(self):
        # isinstanceのためにパスを揃える
        import sys

        sys.path.append("notion_api")

        # Given
        base_page = BasePage.create(
            properties=[Title.from_plain_text(name="名前", text="タイトル")],
        )
        base_page.update_id_and_url(page_id="dummy-id", url="http://example.com")

        # When
        actual = base_page.title_for_slack()

        # Then
        self.assertEqual("<http://example.com|タイトル>", actual)

    def test_webhookからのリクエストボディを処理できる(self):
        given = json.load(open("test/base_page_test/pattern1.json"))
        print(given)

        actual = BasePage.from_data(given)
        print(actual)
        self.assertEqual(given["id"], actual.id)

    def test_コピーを作成する(self):
        # Given
        base_page = BasePage.create(
            properties=[Title.from_plain_text(name="名前", text="タイトル")],
        )
        base_page.update_id_and_url(page_id="dummy-id", url="http://example.com")

        # When
        actual = base_page.copy()

        # Then
        self.assertIsNone(actual.id_)
        self.assertIsNone(actual.url_)
        self.assertEqual(base_page.properties.values, actual.properties.values)
        self.assertEqual(base_page.block_children, actual.block_children)
        self.assertNotEqual(base_page, actual)

    def test_オリジナルのBasePageを作成する(self):
        class OriginalPage(BasePage):
            pass

        # Given
        original_page = OriginalPage.create(
            properties=[Title.from_plain_text(name="名前", text="タイトル")],
        )
        copied_original_page = original_page.copy()

        self.assertIsInstance(original_page, OriginalPage)
        self.assertIsInstance(copied_original_page, OriginalPage)
