#!/usr/bin/env python3

import logging
import pandas as pd

from applications.bench import Benchmark

archs = [ 'x86_64', 'aarch64' ]

class Math(Benchmark):

    app = None
    arch = None
    binary_path = None

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench[6:]
        self.binary_path = config.store['MATH_BIN']

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by micro.math. Should be among "+str(archs))
            exit(1)
        self.arch = args.arch


    def prepare(self):
        super().prepare()

        self.cmdline = [ self.binary_path ]


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        stdout.seek(0)
        for l in stdout:
            if "bench.py" in l:
                retval = int(l.split(' ')[7])
            else:
                test, value = l.strip().split(',')
                df = df.append({ 'bench': f"micro.{self.app}-{test}",
                                 'dataset': 'none',
                                 'arch': self.arch,
                                 'threads': 1,
                                 'cmdline': ' '.join(self.cmdline),
                                 'unit': 'ops/ms',
                                 'value': float(value) }, ignore_index=True)

        df['retval'] = retval
        if len(df) == 0:
            return None
        return df


    def cleanup(self):
        pass


    def __str__(self):
        ret = "<"
        ret += "name="+self.name
        ret += ", threads="+str(self.threads)
        ret += ", dataset=none"
        ret += ", arch="+self.arch
        ret += ", cmdline: " + str(self.cmdline)
        ret += ">"
        return ret


class MicrobenchFactory():

    apps = {
        'micro.math': Math,
    }

    def create(args, config):
        try:
            bench = MicrobenchFactory.apps[args.bench]
        except:
            logging.error("This benchmark is not supported in microbenchmarks (yet?)")
            exit(1)
        return bench(args, config)
