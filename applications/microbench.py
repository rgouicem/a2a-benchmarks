#!/usr/bin/env python3

import logging, os
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


class Sqlite(Benchmark):

    app = None
    arch = None
    binary_path = None

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench[6:]
        self.binary_path = config.store['SQLITE_BENCH_BIN']
        self.binary_dir = os.path.dirname(self.binary_path)

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by micro.math. Should be among "+str(archs))
            exit(1)
        self.arch = args.arch


    def prepare(self):
        super().prepare()

        self.cmdline = [ self.binary_path ] + [ f"{self.binary_dir}/test{i}.sql" for i in range(1, 17) ]


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        stdout.seek(0)
        for l in stdout:
            if "bench.py" in l:
                retval = int(l.split(' ')[7])
            else:
                run, res = l.strip().split(';')
                test_id, hue = run.split('-')
                df = df.append({ 'bench': f"micro.{self.app}-{run}",
                                 'dataset': 'none',
                                 'arch': self.arch,
                                 'threads': 1,
                                 'cmdline': ' '.join(self.cmdline),
                                 'unit': 'ms',
                                 'value': float(res) }, ignore_index=True)

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

class Cas(Benchmark):

    app = None
    arch = None
    binary_path = None
    dataset = None
    configs = { "1-1": ["1", "1"],
                "4-1": ["4", "1"],
                "4-2": ["4", "2"],
                "4-4": ["4", "4"],
                "8-1": ["8", "1"],
                "8-4": ["8", "4"],
                "8-8": ["8", "8"],
                "16-1": ["16", "1"],
                "16-8": ["16", "8"],
                "16-16": ["16", "16"]
               }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench[6:]
        self.binary_path = config.store['CAS_BENCH_BIN']
        self.binary_dir = os.path.dirname(self.binary_path)
        self.dataset = args.dataset
        self.threads = self.dataset.split('-')[0]

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by micro.cas. Should be among "+str(archs))
            exit(1)
        self.arch = args.arch


    def prepare(self):
        super().prepare()

        try:
            self.cmdline = [ self.binary_path ] + self.configs[self.dataset]
        except KeyError:
            logging.error(f"Dataset not supported. Should be among {self.configs}")
            exit(1)


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        stdout.seek(0)
        for l in stdout:
            if "bench.py" in l:
                retval = int(l.split(' ')[7])
            else:
                res = l.strip()
                df = df.append({ 'bench': f"micro.{self.app}-{self.dataset}",
                                 'dataset': self.dataset,
                                 'arch': self.arch,
                                 'threads': self.threads,
                                 'cmdline': ' '.join(self.cmdline),
                                 'unit': 's',
                                 'value': float(res) }, ignore_index=True)

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
        ret += ", dataset="+self.dataset
        ret += ", arch="+self.arch
        ret += ", cmdline: " + str(self.cmdline)
        ret += ">"
        return ret



class MicrobenchFactory():

    apps = {
        'micro.math': Math,
        'micro.sqlite': Sqlite,
        'micro.cas': Cas
    }

    def create(args, config):
        try:
            bench = MicrobenchFactory.apps[args.bench]
        except:
            logging.error("This benchmark is not supported in microbenchmarks (yet?)")
            exit(1)
        return bench(args, config)
