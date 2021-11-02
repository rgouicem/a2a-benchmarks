#!/usr/bin/env python3

from runtimes.runtime import Runtime
import platform, logging

class Native(Runtime):

    def __init__(self, args, config):
        super().__init__(args, config)

        if platform.machine() != args.arch:
            logging.error(f"Cannot execute {args.arch} binaries on a {platform.machine()} architecture with the 'native' runtime.")
            exit(1)

        self.cmdline = []

    def __str__(self):
        return super().__str__()
