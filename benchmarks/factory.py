#!/usr/bin/env python3

from benchmarks.parsec import ParsecFactory
from benchmarks.phoenix import PhoenixFactory

class BenchmarkFactory():

    def create(args, config):
        if args.bench.startswith('parsec.'):
            return ParsecFactory.create(args, config)
        if args.bench.startswith('phoenix.'):
            return PhoenixFactory.create(args, config)
        return None
