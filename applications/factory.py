#!/usr/bin/env python3

from applications.parsec import ParsecFactory
from applications.phoenix import PhoenixFactory
from applications.db import DbFactory

class BenchmarkFactory():

    def create(args, config):
        if args.bench.startswith('parsec.'):
            return ParsecFactory.create(args, config)
        if args.bench.startswith('phoenix.'):
            return PhoenixFactory.create(args, config)
        if args.bench.startswith('db.'):
            return DbFactory.create(args, config)
        return None
