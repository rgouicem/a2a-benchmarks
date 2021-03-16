#!/usr/bin/env python3

from benchmarks.parsec import ParsecFactory

class BenchmarkFactory():

    def create(args, config):
        if args.bench.startswith('parsec.'):
            return ParsecFactory.create(args, config)
        return None
