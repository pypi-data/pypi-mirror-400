# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************


class AddinBase:
    def __init__(self, name, *args, **kwargs):
        self.name = name

    def decorator_impl(
        self,
        signature,
        wrapper,
        func_name,
        description,
        help,
        volatile,
        streaming,
    ):
        pass


class Queue:
    def __init__(self, name, _id):
        self.name = name
        self.id = _id

    def push(self, value):
        print(f"Queue {self.name} ({self.id}): {value}")

    def error(self, message):
        print(f"Queue {self.name} ({self.id}) Error: {message}")
