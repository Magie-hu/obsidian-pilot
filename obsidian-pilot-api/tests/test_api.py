"""Obsidian Pilot API - Tests
Copyright (c) 2026 NingXiaoBan
Licensed under MIT License
"""
import unittest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add API source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "obsidian_pilot_api"))

from main import app

client = TestClient(app)


class TestAPI(unittest.TestCase):
    """Test API endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["service"], "Obsidian Pilot API")
    
    def test_health(self):
        """Test health check endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_init_vault(self):
        """Test vault initialization endpoint."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            response = client.post("/init", json={"vault_path": tmpdir})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")
    
    def test_classify_note(self):
        """Test note classification endpoint."""
        response = client.post("/classify", json={
            "content": "This is a test note about Python programming",
            "filename": "test-note.md"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("category", data)
        self.assertIn("tags", data)
    
    def test_route_query(self):
        """Test query routing endpoint."""
        response = client.post("/route", json={
            "query": "How do I set up a new vault?"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("recommended_model", data)
        self.assertIn("confidence", data)


if __name__ == "__main__":
    unittest.main()
