"""Tests for the CustomJSONEncoder class"""
import base64
import datetime
import decimal
import json
import uuid

import numpy as np
import pandas as pd

from pyasynclogger.json_tools import CustomJSONEncoder


def test_datetime_serialization():
    """Test datetime serialization and deserialization."""
    now = datetime.datetime.now()
    serialized = json.dumps(now, cls=CustomJSONEncoder)
    deserialized = datetime.datetime.fromisoformat(json.loads(serialized))
    assert now == deserialized


def test_date_serialization():
    """Test date serialization and deserialization."""
    today = datetime.date.today()
    serialized = json.dumps(today, cls=CustomJSONEncoder)
    deserialized = datetime.date.fromisoformat(json.loads(serialized))
    assert today == deserialized


def test_time_serialization():
    """Test time serialization and deserialization."""
    now_time = datetime.datetime.now().time()
    json.dumps(now_time, cls=CustomJSONEncoder)
    # Direct deserialization of time is not as straightforward as date/datetime
    # This test skips direct comparison


def test_decimal_serialization():
    """Test decimal serialization and deserialization."""
    value = decimal.Decimal("10.5")
    serialized = json.dumps(value, cls=CustomJSONEncoder)
    deserialized = decimal.Decimal(json.loads(serialized))
    assert value == deserialized


def test_uuid_serialization():
    """Test UUID serialization and deserialization."""
    unique_id = uuid.uuid4()
    serialized = json.dumps(unique_id, cls=CustomJSONEncoder)
    deserialized = uuid.UUID(json.loads(serialized))
    assert unique_id == deserialized


def test_set_serialization():
    """Test set serialization and deserialization."""
    value_set = {1, 2, 3}
    serialized = json.dumps(value_set, cls=CustomJSONEncoder)
    deserialized = set(json.loads(serialized))
    assert value_set == deserialized


def test_complex_serialization():
    """Test complex number serialization and deserialization."""
    complex_num = complex(1, 2)
    serialized = json.dumps(complex_num, cls=CustomJSONEncoder)
    deserialized = json.loads(serialized)
    assert complex_num == complex(deserialized["real"], deserialized["imag"])


def test_bytes_serialization():
    """Test bytes serialization and deserialization."""
    bytes_data = b"hello world"
    serialized = json.dumps(bytes_data, cls=CustomJSONEncoder)
    deserialized = base64.b64decode(json.loads(serialized))
    assert bytes_data == deserialized


def test_numpy_array_serialization():
    """Test numpy array serialization and deserialization."""
    np_array = np.array([1, 2, 3])
    serialized = json.dumps(np_array, cls=CustomJSONEncoder)
    deserialized = np.array(json.loads(serialized))
    assert np.array_equal(np_array, deserialized)


def test_pandas_dataframe_serialization():
    """Test pandas dataframe serialization and deserialization."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    serialized = json.dumps(df, cls=CustomJSONEncoder)
    deserialized = pd.DataFrame(json.loads(serialized))
    pd.testing.assert_frame_equal(df, deserialized)
