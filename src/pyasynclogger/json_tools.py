"""JSON Tools."""
import base64
import datetime
import decimal
import json
import uuid

import numpy as np
import pandas as pd


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder."""

    def default(self, o):
        """Default."""
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            return o.isoformat()
        elif isinstance(o, decimal.Decimal):
            return float(o)  # or str(obj) for precision
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, complex):
            return {"real": o.real, "imag": o.imag}
        elif isinstance(o, bytes):
            return base64.b64encode(o).decode()
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, pd.DataFrame):
            return o.to_dict(orient="records")
