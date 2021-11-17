#!/usr/bin/env python3

from applications.parsec import ParsecFactory
from applications.phoenix import PhoenixFactory
from applications.db import DbFactory
from applications.openssl import OpensslFactory
from applications.microbench import MicrobenchFactory

class BenchmarkFactory():

    def create(args, config):
        if args.bench.startswith('parsec.'):
            return ParsecFactory.create(args, config)
        if args.bench.startswith('phoenix.'):
            return PhoenixFactory.create(args, config)
        if args.bench.startswith('db.'):
            return DbFactory.create(args, config)
        if args.bench.startswith("openssl."):
            return OpensslFactory.create(args, config)
        if args.bench.startswith("micro."):
            return MicrobenchFactory.create(args, config)
        return None
