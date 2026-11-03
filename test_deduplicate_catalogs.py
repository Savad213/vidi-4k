import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from deduplicate_catalogs import catalog_items, deduplicate, save


class DeduplicationTests(unittest.TestCase):
    def test_sources_search_pagination_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogs = [{"id": "specific", "type": "movie"},
                        {"id": "xfhq_4k_uhd", "type": "movie"}]
            save(root / "manifest.json", {"version": "1.0.0", "catalogs": catalogs})
            for key, url in [("a", "https://example.invalid/one"),
                             ("alias", "https://example.invalid/one"),
                             ("b", "https://example.invalid/two"),
                             ("search_only", "https://example.invalid/three")]:
                save(root / "stream/movie" / (key + ".json"), {"streams": [{"url": url}]})
                save(root / "meta/movie" / (key + ".json"), {"meta": {"id": key}})
            def item(key): return {"id": key, "type": "movie", "name": key}
            save(root / "catalog/movie/specific.json", {"metas": [item("a")]})
            save(root / "catalog/movie/specific/search=test.json", {"metas": [item("search_only")]})
            save(root / "catalog/movie/xfhq_4k_uhd.json", {"metas": [item("alias"), item("b")]})
            save(root / "catalog/movie/xfhq_4k_uhd/skip=100.json", {"metas": [item("a")]})
            playback = {str(p): p.read_bytes() for folder in ("stream", "meta")
                        for p in (root / folder).rglob("*.json")}
            with contextlib.redirect_stdout(io.StringIO()):
                result = deduplicate(root)
            self.assertEqual(result["after_listings"], 3)
            self.assertEqual([m["id"] for m in catalog_items(root, catalogs[0])], ["a", "search_only"])
            self.assertEqual([m["id"] for m in catalog_items(root, catalogs[1])], ["b"])
            self.assertEqual(json.loads((root / "catalog/movie/xfhq_4k_uhd/skip=100.json").read_text()), {"metas": []})
            self.assertTrue(all(Path(p).read_bytes() == data for p, data in playback.items()))
            first = {str(p): p.read_bytes() for p in root.rglob("*.json")}
            with contextlib.redirect_stdout(io.StringIO()):
                deduplicate(root)
            self.assertEqual(first, {str(p): p.read_bytes() for p in root.rglob("*.json")})


if __name__ == "__main__":
    unittest.main()
