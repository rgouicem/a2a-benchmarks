#!/usr/bin/env python3

class Benchmark():

    name = None
    threads = None
    env = {}
    cmdline = None

    def __init__(self, args, config):
        self.name = args.bench
        self.threads = int(args.num_threads)

    def prepare(self):
        pass

    def format_results(self, stdout, stderr):
        pass

    def cleanup(self):
        pass

    def __str__(self):
        ret = "<"
        ret += f"name={self.name}"
        ret += f", threads={self.threads}"
        ret += f", env={self.env}"
        ret += ">"
        return ret
