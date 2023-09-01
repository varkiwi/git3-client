import pytest
import unittest

from git3Client.gitCommands.catFile import cat_file

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('blob', b'1234567890'))
def test_cat_file_wrong_mode(mocked_read_object):
    with pytest.raises(ValueError):
        cat_file('wrong mode', '1234567890')

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('tree', b'1234567890'))
def test_cat_file_wrong_mode_in_file(mocked_read_object):
    with pytest.raises(ValueError):
        cat_file('blob', '1234567890')

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('blob', b'1234567890'))
def test_cat_file_correct_blob_mode(mocked_read_object, capsys):
    cat_file('blob', '1234567890')
    captured = capsys.readouterr()
    assert captured.out == '1234567890'

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('blob', b'1234567890'))
def test_cat_file_correct_size_mode(mocked_read_object, capsys):
    cat_file('size', '1234567890')
    captured = capsys.readouterr()
    assert captured.out == '10\n'

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('blob', b'1234567890'))
def test_cat_file_correct_type_mode(mocked_read_object, capsys):
    cat_file('type', '1234567890')
    captured = capsys.readouterr()
    assert captured.out == 'blob\n'


@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('blob', b'1234567890'))
def test_cat_file_correct_pretty_mode_blob(mocked_read_object, capsys):
    cat_file('pretty', '1234567890')
    captured = capsys.readouterr()
    assert captured.out == '1234567890'

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('tree', b'1234567890'))
def test_cat_file_correct_pretty_mode_tree(mocked_read_object, capsys):
    cat_file('pretty', '1234567890')
    captured = capsys.readouterr()
    assert captured.out == ''

@unittest.mock.patch('git3Client.gitCommands.catFile.read_object', return_value=('wrong', b'1234567890'))
def test_cat_file_error_pretty_mode_wrong_type(mocked_read_object):
    with pytest.raises(ValueError) as excinfo:
        cat_file('pretty', '1234567890')
    assert excinfo.value.args[0] == 'unhandled object type \'wrong\''