import sys
import os
import runpy
from .translator import AmharicPythonTranslator

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m geezpy <amharic_python_script.gp>")
        sys.exit(1)

    script_path = sys.argv[1]
    
    if not os.path.exists(script_path):
        print(f"Error: Script file not found: {script_path}")
        sys.exit(1)

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            amharic_code = f.read()
    except Exception as e:
        print(f"Error reading script file: {e}")
        sys.exit(1)

    translator = AmharicPythonTranslator()
    translated_code = translator.translate(amharic_code)

    # Prepare the environment for executing the translated code
    # This mimics how runpy executes a script
    sys.argv = [script_path] + sys.argv[2:] # Set sys.argv for the executed script
    
    # Execute the translated code
    # We use a dictionary for globals and locals to isolate the execution environment
    # and to allow the script to behave as if it were run directly.
    exec_globals = {
        '__name__': '__main__',
        '__file__': os.path.abspath(script_path),
        '__cached__': None,
        '__doc__': None,
        '__loader__': None,
        '__package__': None,
        '__spec__': None,
        '__builtins__': __builtins__,
    }
    exec_locals = exec_globals

    try:
        exec(translated_code, exec_globals, exec_locals)
    except Exception as e:
        # Attempt to translate the error message
        error_type = type(e).__name__
        translated_error_type = translator.translate_error_message(error_type)
        translated_error_message = translator.translate_error_message(str(e))
        print(f"ስህተት ተከስቷል ({translated_error_type}): {translated_error_message}")
        sys.exit(1)

if __name__ == '__main__':
    main()
