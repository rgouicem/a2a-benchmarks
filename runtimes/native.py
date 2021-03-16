#!/usr/bin/env python3

from runtimes.runtime import Runtime

class Native(Runtime):

    def __init__(self, args, config):
        super().__init__(args, config)

        self.cmdline = []

    def __str__(self):
        return super().__str__()
