#!/usr/bin/env python3

from runtimes.runtime import Runtime

class Qemu(Runtime):

    arch = None
    path = None

    def __init__(self, args, config):
        super().__init__(args, config)

        # Get config
        for cfg in [ "QEMU_LD_PREFIX", "QEMU_STLD_DIR" ]:
            try:
                self.env[cfg] = config.store[cfg]
            except:
                pass

        self.path = config.store["QEMU_PATH"]

        # Get arch
        self.arch = args.arch

        # Build command line
        self.cmdline = [ f"{self.path}/qemu-{self.arch}" ]

    def __str__(self):
        return super().__str__()
