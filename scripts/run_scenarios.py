#!/usr/bin/env python3
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class ScenarioRunner:
    def __init__(self, base_url: str, user_id: str, book_id: str):
        self.base_url = base_url
        self.user_id = user_id
        self.book_id = book_id

    def ensure_user(self):
        """Ensure patron exists."""
        print(f"Ensuring patron exists for {self.user_id}...")
        response = requests.get(f"{self.base_url}/users/{self.user_id}")
        if response.status_code == 404:
            print(f"Creating patron {self.user_id}...")
            requests.post(
                f"{self.base_url}/users",
                json={
                    "user_id": self.user_id,
                    "email": f"{self.user_id.lower()}@example.com",
                    "full_name": f"Test Patron {self.user_id}",
                    "phone": "+91-9876543210"
                }
            )

    def ensure_book(self, copies_total: int = 20):
        """Ensure a book with plenty of copies exists (used for the retry scenario)."""
        print(f"Ensuring book exists for {self.book_id}...")
        response = requests.get(f"{self.base_url}/books/{self.book_id}")
        if response.status_code == 404:
            print("Creating book...")
            requests.post(
                f"{self.base_url}/books",
                json={
                    "book_id": self.book_id,
                    "title": "Concurrency Test Copy",
                    "author": "Test Author",
                    "copies_total": copies_total
                }
            )

    def checkout_retry(self):
        """Scenario: checkout with timeout and client retry, same idempotency key."""
        print("\n=== Running checkout_retry scenario ===")
        self.ensure_user()
        self.ensure_book(copies_total=20)

        idempotency_key = f"retry-test-{int(time.time())}"
        payload = {
            "user_id": self.user_id,
            "book_id": self.book_id,
            "idempotency_key": idempotency_key
        }

        print(f"Attempt 1: Checking out with idempotency_key={idempotency_key}")
        try:
            response1 = requests.post(f"{self.base_url}/loans", json=payload, timeout=1.0)
            print(f"Attempt 1 response: {response1.status_code} - {response1.json()}")
        except requests.exceptions.Timeout:
            print("Attempt 1: Request timed out")

        print("\nAttempt 2: Retrying same checkout...")
        try:
            response2 = requests.post(f"{self.base_url}/loans", json=payload, timeout=10.0)
            print(f"Attempt 2 response: {response2.status_code} - {response2.json()}")
        except requests.exceptions.Timeout:
            print("Attempt 2: Request timed out")

        time.sleep(1)

        print(f"\nFetching all loans for {self.user_id}...")
        response = requests.get(f"{self.base_url}/loans?user_id={self.user_id}")
        loans = response.json()

        matching = [l for l in loans if l.get('idempotency_key') == idempotency_key]
        print(f"Loans with idempotency_key={idempotency_key}: {len(matching)}")
        for loan in matching:
            print(f"  - Loan ID: {loan['id']}, Book: {loan['book_id']}")

    def concurrent_checkout(self):
        """Scenario: many patrons try to check out the same low-stock book at once."""
        print("\n=== Running concurrent_checkout scenario ===")

        limited_book_id = f"{self.book_id}-LIMITED"
        copies = 5
        print(f"Creating a book with only {copies} copies: {limited_book_id}")
        requests.post(
            f"{self.base_url}/books",
            json={
                "book_id": limited_book_id,
                "title": "Scarce Copy",
                "author": "Test Author",
                "copies_total": copies
            }
        )

        num_requests = 25
        print(f"\nFiring {num_requests} concurrent checkout requests for {copies} available copies...")

        def checkout(i):
            patron_id = f"LOADTEST-{i}"
            requests.post(
                f"{self.base_url}/users",
                json={
                    "user_id": patron_id,
                    "email": f"{patron_id.lower()}@example.com",
                    "full_name": f"Load Test {i}",
                }
            )
            try:
                response = requests.post(
                    f"{self.base_url}/loans",
                    json={"user_id": patron_id, "book_id": limited_book_id}
                )
                return response.status_code == 201
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(checkout, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        successful = sum(results)
        print(f"Successful checkouts: {successful}/{num_requests} (only {copies} should have succeeded)")

        time.sleep(0.5)
        book = requests.get(f"{self.base_url}/books/{limited_book_id}").json()
        print(f"\nFinal copies_available: {book['copies_available']} (should never be negative)")
        print(f"copies_total: {book['copies_total']}")
        if successful > copies:
            print(f"OVERBOOKED: {successful} checkouts succeeded for only {copies} copies")

    def false_success(self):
        """Scenario: API returns success on a constraint violation."""
        print("\n=== Running false_success scenario ===")
        self.ensure_user()

        invalid_payload = {
            "user_id": self.user_id,
            "book_id": "DOES-NOT-EXIST",
        }

        print("Checking out a book that does not exist in the catalog...")
        response = requests.post(f"{self.base_url}/loans", json=invalid_payload)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")

    def main_flow(self):
        """Scenario: a normal borrow -> return cycle."""
        print("\n=== Running main_flow scenario ===")
        self.ensure_user()
        self.ensure_book(copies_total=3)

        print("\nChecking out book...")
        response = requests.post(
            f"{self.base_url}/loans",
            json={"user_id": self.user_id, "book_id": self.book_id},
            timeout=10.0
        )
        print(f"Checkout response: {response.status_code} - {response.json()}")

        if response.status_code == 201:
            loan_id = response.json()["loan_id"]
            time.sleep(0.3)
            print(f"\nReturning loan {loan_id}...")
            return_response = requests.post(f"{self.base_url}/loans/{loan_id}/return")
            print(f"Return response: {return_response.status_code} - {return_response.json()}")


def main():
    parser = argparse.ArgumentParser(description="Run API test scenarios")
    parser.add_argument("--scenario", default="all",
                         choices=["checkout_retry", "concurrent_checkout", "false_success", "main_flow", "all"],
                         help="Scenario to run")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--user-id", default="PATRON-001", help="Patron ID to use")
    parser.add_argument("--book-id", default="BOOK-001", help="Book ID to use")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat the scenario")

    args = parser.parse_args()

    runner = ScenarioRunner(args.base_url, args.user_id, args.book_id)

    scenarios = {
        "checkout_retry": runner.checkout_retry,
        "concurrent_checkout": runner.concurrent_checkout,
        "false_success": runner.false_success,
        "main_flow": runner.main_flow,
        "all": runner.main_flow,
    }

    for i in range(args.repeat):
        if args.repeat > 1:
            print(f"\n{'=' * 60}")
            print(f"Iteration {i + 1}/{args.repeat}")
            print(f"{'=' * 60}")

        scenarios[args.scenario]()

        if i < args.repeat - 1:
            time.sleep(1)


if __name__ == "__main__":
    main()
