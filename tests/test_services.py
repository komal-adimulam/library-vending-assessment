import unittest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import services
from app.models import Base, Book, Loan


class ServicesTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        with self.engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_create_loan_rejects_unknown_user_before_reserving_inventory(self):
        book = Book(
            book_id="BOOK-1",
            title="Clean Code",
            author="Robert C. Martin",
            copies_total=2,
            copies_available=2,
        )
        self.session.add(book)
        self.session.commit()

        with self.assertRaises(ValueError) as ctx:
            services.create_loan(self.session, "USER-404", "BOOK-1")

        self.assertIn("User USER-404 not found", str(ctx.exception))
        self.assertEqual(self.session.query(Loan).count(), 0)
        self.assertEqual(
            self.session.query(Book).filter(Book.book_id == "BOOK-1").one().copies_available,
            2,
        )


if __name__ == "__main__":
    unittest.main()
