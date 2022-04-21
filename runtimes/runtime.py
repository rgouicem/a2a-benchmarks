#!/usr/bin/env python3

class Runtime():

    name = None
    env = {}
    cmdline = None
    opts = ""

    def __init__(self, args, config):
        self.name = args.runtime
        self.opts = args.run_opt if args.run_opt is not None else ""


    def __str__(self):
        ret = "<"
        ret += f"name={self.name}"
        ret += f", env={self.env}"
        ret += f", cmdline={self.cmdline}"
        ret += ">"
        return ret
