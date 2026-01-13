import io
import json
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image


def process_data_payload(data):
    """
    Standardizes casted Python objects back into (mime_type, bytes/str)
    for transmission or storage.
    """

    if isinstance(data, str):
        return "text/plain", data

    if isinstance(data, (int, float, list, tuple, dict)):
        return "application/json", json.dumps(data)

    if isinstance(data, (ET.Element, ET.ElementTree)):

        if isinstance(data, ET.ElementTree):
            root = data.getroot()
        else:
            root = data

        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')

        mime = "image/svg+xml" if "svg" in root.tag.lower() else "application/xml"
        return mime, xml_str

    if isinstance(data, (Image.Image, np.ndarray)):
        if isinstance(data, np.ndarray):

            if data.ndim >= 2:
                data = Image.fromarray(data)
            else:

                buffer = io.BytesIO()
                np.save(buffer, data)
                return "application/octet-stream", buffer.getvalue()

        buffer = io.BytesIO()
        if data.mode == 'RGBA':
            data.save(buffer, format="PNG")
            return "image/png", buffer.getvalue()
        else:
            data.save(buffer, format="JPEG")
            return "image/jpeg", buffer.getvalue()

    if isinstance(data, (bytes, bytearray, io.BytesIO)):
        content = data.getvalue() if isinstance(data, io.BytesIO) else data
        return "application/octet-stream", content

    return "application/octet-stream", str(data).encode('utf-8')
