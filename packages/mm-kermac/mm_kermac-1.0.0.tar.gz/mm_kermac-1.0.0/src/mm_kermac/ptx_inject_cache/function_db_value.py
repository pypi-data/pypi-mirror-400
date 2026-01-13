# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import json
import base64

class FunctionDBValue:
    """Represents the value structure for the function database."""
    def __init__(
        self,
        lowered_name: bytes,
        ptx_data: bytes
    ):
        self.lowered_name = lowered_name
        self.ptx_data = ptx_data

    def to_bytes(self) -> bytes:
        """Serialize the value to a bytes object for storage."""
        value_dict = {
            'lowered_name': base64.b64encode(self.lowered_name).decode('utf-8'),
            'ptx_data': base64.b64encode(self.ptx_data).decode('utf-8')
        }
        return json.dumps(value_dict, sort_keys=True).encode('utf-8')

    @classmethod
    def from_bytes(cls, data: bytes) -> 'FunctionDBValue':
        """Deserialize bytes to a FunctionDBValue object."""
        value_dict = json.loads(data.decode('utf-8'))
        return cls(
            lowered_name=base64.b64decode(value_dict['lowered_name']),
            ptx_data=base64.b64decode(value_dict['ptx_data'])
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionDBValue):
            return False
        return (
            self.lowered_name == other.lowered_name and
            self.ptx_data == other.ptx_data
        )

    def __repr__(self) -> str:
        return (f"FunctionDBValue(lowered_name={self.lowered_name!r}, "
                f"ptx_data={self.ptx_data!r})")