import unittest
import os
import json
from geezpy.translator import AmharicPythonTranslator

class TestAmharicPythonTranslator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dummy_keywords = {
            "False": "አሳሳቢ",
            "True": "እውነት",
            "None": "ምንም",
            "if": "ከሆነ",
            "else": "ካልሆነ",
            "for": "ለ",
            "while": "በሚኖርበት",
            "def": "ተግባር",
            "return": "ተመልሷል",
            "import": "አስመጣ",
            "from": "ከ",
            "as": "እንደ",
            "print": "አትም",
            "range": "ክልል",
            "in": "በ"
        }
        # Create a dummy keywords.json for testing
        cls.test_keywords_file = os.path.join(os.path.dirname(__file__), 'test_keywords.json')
        with open(cls.test_keywords_file, 'w', encoding='utf-8') as f:
            json.dump(cls.dummy_keywords, f, ensure_ascii=False, indent=4)
        
        # Instantiate translator, pointing to the actual keywords.json in geezpy package
        # and using the dummy keywords for testing purposes.
        # The translator expects keywords.json to be in the same directory as translator.py
        # For testing, we'll temporarily overwrite the keywords_map with our dummy ones.
        cls.translator = AmharicPythonTranslator()
        cls.translator.keywords_map = cls.dummy_keywords
        cls.translator.reverse_keywords_map = {v: k for k, v in cls.dummy_keywords.items()}
        cls.translator.amharic_keywords = sorted(cls.dummy_keywords.values(), key=len, reverse=True)
        cls.translator.amharic_to_english_patterns = cls.translator._create_translation_patterns()

    @classmethod
    def tearDownClass(cls):
        # Clean up the dummy keywords.json file
        os.remove(cls.test_keywords_file)

    def test_load_keywords(self):
        # Test that keywords are loaded correctly
        self.assertIn("if", self.translator.keywords_map)
        self.assertEqual(self.translator.keywords_map["if"], "ከሆነ")
        self.assertIn("ከሆነ", self.translator.reverse_keywords_map)
        self.assertEqual(self.translator.reverse_keywords_map["ከሆነ"], "if")

    def test_translate_simple_keywords(self):
        amharic_code = "ከሆነ እውነት:\n    አትም('ሰላም')"
        expected_english_code = "if True:\n    print('ሰላም')"
        self.assertEqual(self.translator.translate(amharic_code), expected_english_code)

    def test_translate_multiple_keywords(self):
        amharic_code = "ለ ቁጥር በ ክልል(5):\n    አትም(ቁጥር)"
        expected_english_code = "for ቁጥር in range(5):\n    print(ቁጥር)"
        self.assertEqual(self.translator.translate(amharic_code), expected_english_code)

    def test_translate_with_comments_and_strings(self):
        amharic_code = "# ይህ አስተያየት ነው\nአትም('ከሆነ')" # 'ከሆነ' inside string should not be translated
        expected_english_code = "# ይህ አስተያየት ነው\nprint('ከሆነ')"
        self.assertEqual(self.translator.translate(amharic_code), expected_english_code)

    def test_translate_error_message(self):
        english_error = "SyntaxError: invalid syntax in 'if True:'"
        # The current implementation only replaces exact word matches.
        # 'if' and 'True' are in the dummy keywords, but 'SyntaxError' is not.
        # So, we expect 'if', 'True', and 'in' to be translated.
        expected_amharic_error = "SyntaxError: invalid syntax በ 'ከሆነ እውነት:'"
        self.assertEqual(self.translator.translate_error_message(english_error), expected_amharic_error)

    def test_no_translation_for_non_keywords(self):
        amharic_code = "ተለዋዋጭ = 10" # 'ተለዋዋጭ' is not a keyword
        self.assertEqual(self.translator.translate(amharic_code), amharic_code)

    def test_complex_translation(self):
        # Update keywords for this specific test case
        additional_keywords = {
            "def": "ተግባር",
            "return": "ተመልሷል",
            "multiply": "ማባዛት",
            "result": "ውጤት",
            "second": "ሁለተኛ"
        }
        self.translator.keywords_map.update(additional_keywords)
        self.translator.reverse_keywords_map = {v: k for k, v in self.translator.keywords_map.items()}
        self.translator.amharic_keywords = sorted(self.translator.reverse_keywords_map.keys(), key=len, reverse=True)
        self.translator.amharic_to_english_patterns = self.translator._create_translation_patterns()

        amharic_code = """
ተግባር ማባዛት(ሀ, ሁለተኛ):
    ተመልሷል ሀ * ሁለተኛ

ከሆነ እውነት:
    ውጤት = ማባዛት(5, 3)
    አትም("ውጤት:", ውጤት)
"""
        expected_english_code = """
def multiply(ሀ, second):
    return ሀ * second

if True:
    result = multiply(5, 3)
    print("result:", result)
"""
        self.assertEqual(self.translator.translate(amharic_code), expected_english_code)

if __name__ == '__main__':
    unittest.main()
