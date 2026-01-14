import pytest
from phenixio.reader import PhenixReader
import numpy

test_file_path_legacy = '..\\_testdata\\legacy_data'
test_file_path_new = '..\\_testdata\\new_data'

@pytest.fixture
def reader_legacy():
    return PhenixReader(test_file_path_legacy)

def test_create_reader(reader_legacy):
    assert isinstance(reader_legacy, PhenixReader)

def test_reader_format_detect_legacy(reader_legacy):
    assert reader_legacy.format == 'legacy'

def test_reader_format_detect_new():
    reader = PhenixReader(test_file_path_new)
    print(reader.format)
    assert reader.format == 'new'

def test_create_reader_error():
    with pytest.raises(TypeError):
        reader = PhenixReader('../')

def test_num_wells(reader_legacy):
    assert reader_legacy.num_wells == 18

def test_get_image_metadata(reader_legacy):

    img_metadata = reader_legacy.get_image_metadata(2, 2, 1, 1, 1, 1)
    assert isinstance(img_metadata, dict)

def test_read_image(reader_legacy):

    image = reader_legacy.read_image(2, 2, 1)

    assert isinstance(image, numpy.ndarray)
    assert image.dtype == numpy.uint16