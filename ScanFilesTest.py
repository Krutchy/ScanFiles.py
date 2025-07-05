import unittest
import tempfile
import os
import shutil
from ScanFiles import LoadTermList, GetAvailableFilename, WriteOutput, GetAllFiles, BuildAutomaton, ScanFiles

class ScanFilesTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.term_file = os.path.join(self.test_dir, "terms.txt")
        with open(self.term_file, "w", encoding='utf-8') as f:
            f.write("apple (apple) (apple)1 (Apple) Apple banana orange grape\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_LoadTermList_case_insensitive(self):
        terms = LoadTermList(self.term_file, case_sensitive=False)
        self.assertIn("apple", terms)
        self.assertIn("(apple)", terms)
        self.assertIn("(apple)1", terms)
        self.assertIn("banana", terms)
        self.assertIn("orange", terms)
        self.assertIn("grape", terms)
        self.assertEqual(terms["banana"], [])
        self.assertNotIn("Apple", terms)
        self.assertNotIn("(Apple)", terms)
        self.assertNotIn("pumpkin", terms)

    def test_LoadTermList_case_sensitive(self):
        terms = LoadTermList(self.term_file, case_sensitive=True)
        self.assertIn("apple", terms)
        self.assertIn("Apple", terms)
        self.assertIn("(Apple)", terms)

    def test_GetAllFiles(self):
        test_file = os.path.join(self.test_dir, "a.txt")
        with open(test_file, "w"): pass
        files = GetAllFiles(self.test_dir)
        self.assertIn(test_file, files)

    def test_BuildAutomaton(self):
        terms = {"cat": [], "dog": []}
        automaton = BuildAutomaton(terms, case_sensitive=False)
        matches = list(automaton.iter("a cat and a dog"))
        self.assertEqual(len(matches), 2)

    def test_ScanFiles(self):
        file_path = os.path.join(self.test_dir, "sample.txt")
        with open(file_path, "w") as f:
            f.write("An orange is not an apple.\nBanana is yellow.\n")

        terms = LoadTermList(self.term_file, case_sensitive=False)
        ScanFiles(file_path, terms, case_sensitive=False)
        self.assertEqual(len(terms["apple"]), 1)
        self.assertEqual(terms["banana"][0][1], 2)

        terms = {"apple": [], "Apple": []}
        file_path = os.path.join(self.test_dir, "case_test.txt")
        with open(file_path, "w") as f:
            f.write("Apple is tasty.\napple pie is common.\n")

        ScanFiles(file_path, terms, case_sensitive=True)
        self.assertEqual(len(terms["apple"]), 1)
        self.assertEqual(len(terms["Apple"]), 1)

        # Test #: Terms enclosed in quotes or parentheses
        terms = {"apple": []}
        file_path = os.path.join(self.test_dir, "quote.txt")
        with open(file_path, "w") as f:
            f.write("'apple'\n(apple)\nplain apple\n")

        ScanFiles(file_path, terms, case_sensitive=False)
        lines_found = [entry[1] for entry in terms["apple"]]
        self.assertEqual(sorted(lines_found), [1, 2, 3])

        terms = {"café": [], "naïve": [], "💡": []}
        file_path = os.path.join(self.test_dir, "unicode.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Try the café.\nDon't be naïve.\nHere's a lightbulb: 💡\n")

        ScanFiles(file_path, terms, case_sensitive=False)
        self.assertEqual(len(terms["café"]), 1)
        self.assertEqual(len(terms["naïve"]), 1)
        self.assertEqual(len(terms["💡"]), 1)

        # Test #: Overlapping search terms
        terms = {"apple": [], "apple1": [], "apple1_1": []}
        file_path = os.path.join(self.test_dir, "overlap.txt")
        with open(file_path, "w") as f:
            f.write("apple apple1 apple1_1\n")

        ScanFiles(file_path, terms, case_sensitive=False)
        self.assertEqual(len(terms["apple"]), 1)
        self.assertEqual(len(terms["apple1"]), 1)
        self.assertEqual(len(terms["apple1_1"]), 1)

    def test_GetAvailableFilename(self):
        base_name = os.path.join(self.test_dir, "output.csv")

        # Case 1: File doesn't exist — should return original
        result = GetAvailableFilename(base_name, overwrite_allowed=False)
        self.assertEqual(result, base_name)

        # Create the base file
        with open(base_name, "w") as f:
            f.write("original")

        # Case 2: File exists, overwrite allowed — should return original
        result_overwrite = GetAvailableFilename(base_name, overwrite_allowed=True)
        self.assertEqual(result_overwrite, base_name)

        # Case 3: File exists, overwrite not allowed — should return incremented name
        result_incremented = GetAvailableFilename(base_name, overwrite_allowed=False)
        expected_incremented = base_name.replace(".csv", "_1.csv")
        self.assertEqual(result_incremented, expected_incremented)

    def test_WriteOutput(self):
        terms = {"grape": [("file1.txt", 1)], "melon": []}
        output_file = os.path.join(self.test_dir, "result.csv")
        WriteOutput(output_file, terms, overwrite_allowed=True)
        self.assertTrue(os.path.isfile(output_file))

if __name__ == "__main__":
    unittest.main()