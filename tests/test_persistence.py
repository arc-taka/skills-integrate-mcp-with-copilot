import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import app as activities_app


class ActivityPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "activities.sqlite"
        self.database_path_patch = patch.object(
            activities_app, "DATABASE_PATH", self.database_path
        )
        self.database_path_patch.start()
        activities_app.initialize_database()

    def tearDown(self):
        self.database_path_patch.stop()
        self.temp_dir.cleanup()

    def test_seeded_activities_and_participants_are_available(self):
        activities = activities_app.get_activities()

        self.assertIn("Chess Club", activities)
        self.assertIn(
            "michael@mergington.edu",
            activities["Chess Club"]["participants"],
        )

    def test_signup_survives_database_reinitialization(self):
        email = "student@mergington.edu"
        activities_app.signup_for_activity("Chess Club", email)

        activities_app.initialize_database()

        self.assertIn(
            email,
            activities_app.get_activities()["Chess Club"]["participants"],
        )

    def test_unregister_survives_database_reinitialization(self):
        email = "michael@mergington.edu"
        activities_app.unregister_from_activity("Chess Club", email)

        activities_app.initialize_database()

        self.assertNotIn(
            email,
            activities_app.get_activities()["Chess Club"]["participants"],
        )

    def test_duplicate_signup_keeps_existing_error(self):
        with self.assertRaises(activities_app.HTTPException) as error:
            activities_app.signup_for_activity(
                "Chess Club", "michael@mergington.edu"
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Student is already signed up")

    def test_unknown_activity_keeps_existing_error(self):
        with self.assertRaises(activities_app.HTTPException) as error:
            activities_app.signup_for_activity(
                "Unknown Club", "student@example.com"
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Activity not found")


if __name__ == "__main__":
    unittest.main()
