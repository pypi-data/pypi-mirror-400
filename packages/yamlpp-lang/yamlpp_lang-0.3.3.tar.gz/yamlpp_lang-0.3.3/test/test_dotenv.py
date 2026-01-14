"Higher level tests on dotenv"

from pathlib import Path
from yamlpp import Interpreter
from yamlpp.util import print_yaml


CONFIG_FILENAME = 'test.env'
CONFIG = """
# This is a comment
foo=5
bar="A string"
"""

INSTRUCTION = f"""
# This is a comment
root:
    .load: {CONFIG_FILENAME}
"""



def test_dotenv_read(tmp_path):
    "Read a dotenv file"
    full_filename = Path(tmp_path) / CONFIG_FILENAME
    full_filename.write_text(CONFIG)
    i = Interpreter(source_dir=tmp_path)
    tree = i.load_text(INSTRUCTION)
    print_yaml(i.yamlpp, "Original as loaded")
    print_yaml(i.yaml, "Target")
    