import sys
import unittest


class PackageExportTests(unittest.TestCase):
    def test_package_import_does_not_eagerly_load_optional_clients(self):
        for module_name in tuple(sys.modules):
            if module_name == "src" or module_name.startswith("src."):
                sys.modules.pop(module_name)

        import src

        self.assertNotIn("src.poe_client", sys.modules)
        self.assertNotIn("src.story_generator", sys.modules)

        from src import DiversityTracker

        self.assertEqual("DiversityTracker", DiversityTracker.__name__)
        self.assertIn("src.diversity_tracker", sys.modules)
        self.assertNotIn("src.poe_client", sys.modules)


if __name__ == "__main__":
    unittest.main()
