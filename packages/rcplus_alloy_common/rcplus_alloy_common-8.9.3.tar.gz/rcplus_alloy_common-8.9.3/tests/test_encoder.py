"""
BaseNN encoder tests
"""
import uuid
import string
from rcplus_alloy_common import encode

BASE_36_ALPHABET = string.ascii_lowercase + string.digits
ENCODER_LENGTH = 8


def test_encoder():
    assert encode(1, BASE_36_ALPHABET, ENCODER_LENGTH) == "baaaaaaa"
    assert encode(1_000_000, BASE_36_ALPHABET, ENCODER_LENGTH) == "2vpvaaaa"

    uuid1 = "ad058dca-4722-11ee-b1e8-acde48001122"
    uuid1_time = uuid.UUID(uuid1).time
    assert encode(uuid1_time, BASE_36_ALPHABET, ENCODER_LENGTH) == "wb74h3zm"

    uuid4 = "dd0d8eb6-ab74-4a6f-bf65-32886173511b"
    uuid4_time = uuid.UUID(uuid4).time
    assert encode(uuid4_time, BASE_36_ALPHABET, ENCODER_LENGTH) == "40pathrx"
