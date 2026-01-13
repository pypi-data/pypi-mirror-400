#!/usr/bin/env python3
#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
# Copyright (c) 2023-2025 Yunqi Inc. All rights reserved.
#

import importlib.metadata

try:
    __version__ = importlib.metadata.version("clickzetta-zettapark-python")
except importlib.metadata.PackageNotFoundError:
    # Fallback if running from source without being installed
    __version__ = "0.0.0"
