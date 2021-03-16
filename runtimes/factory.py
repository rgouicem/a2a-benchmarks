#!/usr/bin/env python3

import logging

from runtimes.native import Native
from runtimes.qemu import Qemu

class RuntimeFactory():

    def create(args, config):
        if args.runtime == "native":
            return Native(args, config)
        if args.runtime == "qemu":
            return Qemu(args, config)

        logging.error("Specified runtime is not supported")
        exit(1)
