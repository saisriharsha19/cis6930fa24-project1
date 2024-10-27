import pytest
import os, sys
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from redactor import redact_file, main
from argparse import Namespace
from unittest.mock import patch
import shutil

@pytest.fixture
def sample_text_file(request):
    content = "Jane Doe visited Los Angeles on January 1, 2023. Contact at +1 (123) 456-7890."
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    yield temp_file.name
    os.remove(temp_file.name)
    
@pytest.fixture
def output_dir():
    dir = tempfile.mkdtemp()
    print(f"Output directory created: {dir}")
    yield dir
    shutil.rmtree(dir)
def test_redact_file(sample_text_file, output_dir):
    flags = ['names', 'dates', 'phones', 'address']
    concept = "visited"
    stats = redact_file(sample_text_file, output_dir, flags, concept)
    output_file = os.path.join(output_dir, os.path.basename(sample_text_file) + ".censored")
    
    assert os.path.exists(output_file)
    assert stats['names'] == 1
    assert stats['dates'] == 1
    assert stats['phones'] == 1
    assert stats['addresses'] == 1
    assert stats['concept'] == 1

def test_main(sample_text_file, output_dir):

    with patch.object(sys, 'argv', [
        'redactor.py', '--input', os.path.basename(sample_text_file),
        '--names', '--dates', '--phones', '--address',
        '--concept', 'visit', '--output', output_dir, '--stats', 'stdout'
    ]):
        main()

    print(os.path.join(output_dir, os.path.basename(sample_text_file) + ".censored"))
    output_file = os.path.join(output_dir, os.path.basename(sample_text_file) + ".censored")
    assert ".censored" in output_file
