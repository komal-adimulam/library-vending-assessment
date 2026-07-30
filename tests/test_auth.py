import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import verify_password
from app.db import get_db
from app.main import app
from app.models import Base, User


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

        def override_get_db():
            db = self.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def signup(self, user_id="PATRON-100", email="reader@example.com"):
        return self.client.post(
            "/auth/signup",
            json={
                "user_id": user_id,
                "email": email,
                "full_name": "Jane Reader",
                "password": "correct-horse-battery-staple",
            },
        )

    def test_signup_hashes_password_and_signin_returns_a_token(self):
        response = self.signup()
        self.assertEqual(response.status_code, 201)
        token = response.json()["access_token"]
        self.assertTrue(token)

        with self.Session() as db:
            user = db.query(User).filter_by(user_id="PATRON-100").one()
            self.assertNotEqual(user.password_hash, "correct-horse-battery-staple")
            self.assertTrue(verify_password("correct-horse-battery-staple", user.password_hash))

        signin = self.client.post(
            "/auth/signin",
            json={"email": "reader@example.com", "password": "correct-horse-battery-staple"},
        )
        self.assertEqual(signin.status_code, 200)
        self.assertEqual(signin.json()["token_type"], "bearer")

    def test_rejects_invalid_credentials_and_duplicate_signup(self):
        self.assertEqual(self.signup().status_code, 201)
        self.assertEqual(self.signup().status_code, 400)
        response = self.client.post(
            "/auth/signin", json={"email": "reader@example.com", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_mutations_and_loans_require_the_owner_token(self):
        self.assertEqual(self.client.post("/books", json={}).status_code, 401)
        token = self.signup().json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        book = self.client.post(
            "/books",
            json={"book_id": "BOOK-100", "title": "Auth Testing", "author": "Library", "copies_total": 1},
            headers=headers,
        )
        self.assertEqual(book.status_code, 201)
        loan = self.client.post(
            "/loans",
            json={"user_id": "PATRON-100", "book_id": "BOOK-100"},
            headers=headers,
        )
        self.assertEqual(loan.status_code, 201)
        forbidden = self.client.post(
            "/loans",
            json={"user_id": "PATRON-999", "book_id": "BOOK-100"},
            headers=headers,
        )
        self.assertEqual(forbidden.status_code, 403)


if __name__ == "__main__":
    unittest.main()
