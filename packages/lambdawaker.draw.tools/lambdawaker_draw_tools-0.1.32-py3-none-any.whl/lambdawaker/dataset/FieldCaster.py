import io
import json
import xml.etree.ElementTree as ET
from typing import Any

import yaml


class FieldCaster:
    """
    A utility class for casting and serializing data fields based on their type.
    """

    @staticmethod
    def cast(raw_data: bytes, field_type: str) -> Any:
        """
        Casts raw byte data into a specific Python type.

        Args:
            raw_data (bytes): The raw byte data to cast.
            field_type (str): The target data type (e.g., 'int', 'json', 'PilImage').

        Returns:
            Any: The casted data.
        """
        if not raw_data:
            return None

        # --- Scalar Types ---
        if field_type == 'int':
            return int(raw_data.decode('utf-8'))

        elif field_type == 'float':
            return float(raw_data.decode('utf-8'))

        # --- Structured Data ---
        elif field_type == 'str':
            return raw_data.decode('utf-8')

        elif field_type == 'json':
            return json.loads(raw_data)

        elif field_type == 'yaml':
            return yaml.safe_load(raw_data)

        # --- Document / XML Types ---
        elif field_type == 'xml':
            return ET.fromstring(raw_data.decode('utf-8'))

        elif field_type == 'svgDoc':
            # Returns an ElementTree object representing the SVG
            return ET.fromstring(raw_data.decode('utf-8'))

        # --- Scientific / Image Types ---
        elif field_type == 'numpy':
            import numpy as np
            return np.load(io.BytesIO(raw_data))

        elif field_type == 'PilImage':
            try:
                from PIL import Image
                return Image.open(io.BytesIO(raw_data))
            except ImportError:
                return raw_data

        elif field_type == 'npImage':
            try:
                from PIL import Image
                import numpy as np
                return np.array(Image.open(io.BytesIO(raw_data)))
            except ImportError:
                return raw_data

        return raw_data

    @staticmethod
    def serialize(data: Any, field_type: str) -> bytes:
        """
        Serializes Python data into bytes based on the specified field type.

        Args:
            data (Any): The Python data to serialize.
            field_type (str): The data type to serialize as.

        Returns:
            bytes: The serialized data.
        """
        if field_type in ['int', 'float', 'str']:
            return str(data).encode('utf-8')

        elif field_type == 'json':
            return json.dumps(data, indent=2).encode('utf-8')

        elif field_type == 'yaml':
            return yaml.dump(data, default_flow_style=False).encode('utf-8')

        elif field_type in ['xml', 'svgDoc']:
            # Handle if data is already an ElementTree or an Element
            if hasattr(data, 'getroot'):
                data = data.getroot()
            return ET.tostring(data, encoding='utf-8')

        elif field_type == 'numpy':
            import numpy as np
            buf = io.BytesIO()
            np.save(buf, data)
            return buf.getvalue()

        elif field_type == 'PilImage':
            buf = io.BytesIO()
            data.save(buf, format='PNG')
            return buf.getvalue()

        return data if isinstance(data, bytes) else str(data).encode('utf-8')
