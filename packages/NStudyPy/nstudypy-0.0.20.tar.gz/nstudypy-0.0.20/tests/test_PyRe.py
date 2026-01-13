import pytest
from NStudyPy.PyRe import format_id_card

@pytest.mark.parametrize("input_id, expected", [
    # Valid 15 digit - returns same
    ("350524800101001", "350524800101001"),
    # Valid 18 digit - returns same
    ("35052419800101001X", "35052419800101001X"),
    ("350524198001010014", "350524198001010014"),
    ("35052419800101001x", "35052419800101001x"),
    # Invalid lengths
    ("123", ""),
    ("35052480010100", ""), # 14 digits
    ("3505248001010012", ""), # 16 digits
    ("35052419800101001", ""), # 17 digits
    ("35052419800101001XX", ""), # 19 digits
    # Invalid characters
    ("abcdefghijklmno", ""),
    ("35052419800101001Y", ""), # Y is invalid check digit char
    # Edge cases
    ("", ""),
    (None, ""),  # Ideally the function should handle None or we expect it to fail, but let's see. 
                 # Looking at code: match = _id_card.search(id_card_string). 
                 # re.search throws TypeError on None. The code doesn't check for None.
                 # I will omit None if the function isn't typed to handle it, or expect raise.
                 # Let's stick to string inputs as per signature hint implies string.
])
def test_format_id_card(input_id, expected):
    if input_id is None:
        with pytest.raises(TypeError):
            format_id_card(input_id)
    else:
        assert format_id_card(input_id) == expected
