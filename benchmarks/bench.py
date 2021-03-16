#!/usr/bin/env python3

class Benchmark():

    name = None
    threads = None
    env = {}
    cmdline = None

    def __init__(self, args, config):
        self.name = args.bench
        self.threads = args.num_threads

    def prepare(self):
        pass

    def get_results(self):
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
