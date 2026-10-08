import re
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from app import create_app
from app.db import get_db


class LostAndFoundTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-key-only",
            "DATABASE": str(Path(self.directory.name) / "test.sqlite3"),
        })
        self.client = self.app.test_client()

    def post_item(self, **overrides):
        page = self.client.get("/items/new").get_data(as_text=True)
        token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)
        data = {
            "csrf_token": token,
            "title": "검은색 지갑",
            "category": "지갑·카드",
            "found_location": "도서관 2층",
            "storage_location": "학생지원실",
            "found_date": date.today().isoformat(),
            "description": "작은 검은색 지갑입니다.",
        }
        data.update(overrides)
        return self.client.post("/items/new", data=data)

    def item_count(self):
        with self.app.app_context():
            return get_db().execute("SELECT COUNT(*) FROM items").fetchone()[0]

    def test_empty_list_and_registration_detail(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("아직 등록된 분실물이 없습니다", response.get_data(as_text=True))
        result = self.post_item()
        self.assertEqual(result.status_code, 302)
        detail = self.client.get(result.location)
        self.assertEqual(detail.status_code, 200)
        self.assertIn("검은색 지갑", detail.get_data(as_text=True))
        self.assertIn("학생지원실", detail.get_data(as_text=True))
        self.assertEqual(self.item_count(), 1)

    def test_search_and_category_filter(self):
        self.post_item()
        self.post_item(title="파란 우산", category="기타", description="긴 우산")
        response = self.client.get("/", query_string={"q": "지갑", "category": "지갑·카드"})
        content = response.get_data(as_text=True)
        self.assertIn("검은색 지갑", content)
        self.assertNotIn("파란 우산", content)
        response = self.client.get("/", query_string={"q": "도서관", "category": "기타"})
        content = response.get_data(as_text=True)
        self.assertIn("파란 우산", content)
        self.assertNotIn("검은색 지갑", content)

    def test_literal_search_and_sql_parameters(self):
        self.post_item(title="100%_노트")
        self.post_item(title="일반 노트")
        response = self.client.get("/", query_string={"q": "%_"})
        content = response.get_data(as_text=True)
        self.assertIn("100%_노트", content)
        self.assertNotIn("일반 노트", content)
        response = self.client.get("/", query_string={"q": "' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("일반 노트", response.get_data(as_text=True))

    def test_invalid_forms_do_not_write(self):
        cases = [
            {"title": "   "}, {"title": "가" * 101},
            {"found_location": ""}, {"storage_location": ""},
            {"category": "없는 분류"}, {"description": "가" * 2001},
            {"found_date": "2026-02-30"}, {"found_date": ""},
            {"found_date": (date.today() + timedelta(days=1)).isoformat()},
        ]
        for invalid in cases:
            with self.subTest(invalid=invalid):
                self.assertEqual(self.post_item(**invalid).status_code, 422)
        self.assertEqual(self.item_count(), 0)

    def test_csrf_is_required(self):
        self.assertEqual(self.client.post("/items/new", data={"title": "지갑"}).status_code, 400)
        self.assertEqual(self.post_item(csrf_token="invalid-token").status_code, 400)
        self.assertEqual(self.item_count(), 0)

    def test_description_is_optional_and_text_is_escaped(self):
        result = self.post_item(title="<script>alert(1)</script>", description="")
        response = self.client.get(result.location)
        content = response.get_data(as_text=True)
        self.assertNotIn("<script>", content)
        self.assertIn("&lt;script&gt;", content)
        self.assertIn("추가 설명이 없습니다", content)

    def test_pagination_and_missing_pages(self):
        for number in range(13):
            self.post_item(title=f"물품 {number:02d}")
        first = self.client.get("/").get_data(as_text=True)
        second = self.client.get("/?page=2").get_data(as_text=True)
        self.assertIn("물품 12", first)
        self.assertNotIn("물품 00", first)
        self.assertIn("물품 00", second)
        self.assertNotIn("물품 12", second)
        for path in ("/?page=0", "/?page=3", "/items/9999", "/missing", "/?category=invalid"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_initialization_and_restart_preserve_data(self):
        self.post_item()
        result = self.app.test_cli_runner().invoke(args=["init-db"])
        self.assertEqual(result.exit_code, 0, result.output)
        restarted = create_app({
            "TESTING": True, "SECRET_KEY": "test-key-only",
            "DATABASE": self.app.config["DATABASE"],
        })
        response = restarted.test_client().get("/")
        self.assertIn("검은색 지갑", response.get_data(as_text=True))
        self.assertEqual(self.item_count(), 1)


if __name__ == "__main__":
    unittest.main()
