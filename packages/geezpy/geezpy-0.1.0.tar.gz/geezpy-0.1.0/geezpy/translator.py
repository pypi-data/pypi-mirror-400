import json
import os
import re

class AmharicPythonTranslator:
    def __init__(self, keywords_file='keywords.json'):
        self.keywords_map = self._load_keywords(keywords_file)
        self.reverse_keywords_map = {v: k for k, v in self.keywords_map.items()}
        self.amharic_keywords = sorted(self.keywords_map.values(), key=len, reverse=True)
        self.amharic_to_english_patterns = self._create_translation_patterns()

        # Regex for masking strings and comments
        self.string_pattern = re.compile(r"'(?:[^'\\]|\\.)*'") # Only single quotes for now
        self.comment_pattern = re.compile(r'#[^\n]*')

    def _create_translation_patterns(self):
        patterns = []
        # Sort by length in reverse order to ensure longer keywords are matched first
        sorted_amharic_keywords = sorted(self.keywords_map.values(), key=len, reverse=True)
        
        for am_keyword in sorted_amharic_keywords:
            en_keyword = self.reverse_keywords_map[am_keyword]
            # Use standard word boundary \b which handles Unicode correctly in Python 3
            pattern = re.compile(r'\b' + re.escape(am_keyword) + r'\b')
            patterns.append((pattern, en_keyword))
        return patterns

    def _load_keywords(self, keywords_file):
        # If keywords_file is an absolute path, use it directly
        if os.path.isabs(keywords_file):
            file_path = keywords_file
        else:
            # Otherwise, look for it relative to this file's directory
            file_path = os.path.join(os.path.dirname(__file__), keywords_file)
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Keyword mapping file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _mask_content(self, code, pattern, prefix):
        masked_content = {}
        def replacer(match):
            placeholder = f"__{prefix}_{len(masked_content)}__"
            masked_content[placeholder] = match.group(0)
            return placeholder
        processed_code = pattern.sub(replacer, code)
        return processed_code, masked_content

    def _unmask_content(self, code, masked_content):
        for placeholder, original_content in masked_content.items():
            code = code.replace(placeholder, original_content)
        return code

    def translate(self, amharic_code):
        # 1. Mask strings
        code_without_strings, masked_strings = self._mask_content(amharic_code, self.string_pattern, "STRING_MASK")
        
        # 2. Mask comments
        code_without_comments_and_strings, masked_comments = self._mask_content(code_without_strings, self.comment_pattern, "COMMENT_MASK")

        translated_code = code_without_comments_and_strings
        for pattern, en_keyword in self.amharic_to_english_patterns:
            translated_code = pattern.sub(en_keyword, translated_code)
        
        # 3. Unmask comments
        translated_code = self._unmask_content(translated_code, masked_comments)

        # 4. Unmask strings
        translated_code = self._unmask_content(translated_code, masked_strings)

        return translated_code

    def translate_error_message(self, english_message):
        translated_message = english_message
        for en_keyword, am_keyword in self.keywords_map.items():
            # Only replace if it's a standalone word
            translated_message = re.sub(r'\b' + re.escape(en_keyword) + r'\b', am_keyword, translated_message)
        return translated_message

if __name__ == '__main__':
    translator = AmharicPythonTranslator()
    
    # Example usage
    amharic_code_example = """
# ይህ የአማርኛ ኮድ ምሳሌ ነው።
ተግባር ሰላም_በል(ስም):
    አትም("ሰላም " + ስም + "!")

ከሆነ እውነት:
    ለ ቁጥር በ ክልል(5):
        አትም("ቁጥር:", ቁጥር)
    ሰላም_በል("አለም")
    ካልሆነ:
        አትም("ውሸት")
"""
    print("Original Amharic Code:")
    print(amharic_code_example)
    
    english_code = translator.translate(amharic_code_example)
    print("\nTranslated English Code:")
    print(english_code)

    # Example of error message translation (very basic)
    english_error = "SyntaxError: invalid syntax in 'if True:'"
    amharic_error = translator.translate_error_message(english_error)
    print("\nTranslated Error Message (basic):")
    print(amharic_error)

    english_error_2 = "NameError: name 'my_variable' is not defined"
    amharic_error_2 = translator.translate_error_message(english_error_2)
    print("\nTranslated Error Message 2 (basic):")
    print(amharic_error_2)
