# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

# PTX Inject now returns data type tokens as strings (e.g., "F32").
# Keep these constants for callers that want named access.
class DataTypeInfo:
    F16 = "F16"
    F16X2 = "F16X2"
    S32 = "S32"
    U32 = "U32"
    F32 = "F32"
    B32 = "B32"
