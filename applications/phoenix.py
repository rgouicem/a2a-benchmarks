#!/usr/bin/env python3

import logging, os
import pandas as pd

from applications.bench import Benchmark

archs = {
    "x86_64": "amd64-linux.gcc"
}

class Phoenix(Benchmark):

    app = None
    arch = None
    phoenix_dir = None

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench
        self.phoenix_dir = config.store["PHOENIX_DIR"]

         # Get binary ISA
        if args.arch not in archs:
            logging.error(f"Architecture not supported by Phoenix. Should be among {archs}")
            exit(1)
        self.arch = args.arch

        # Fix number of threads (cannot be configured in Phoenix, defaults to number of cores)
        self.threads = os.cpu_count()


    def prepare(self, no_input=False):
        pass

    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        with open(stdout.name, "r") as fp:
            for l in fp:
                if "bench.py" in l:
                    duration = float(l.split(' ')[2])
                    retval = int(l.split(' ')[7])
                    df = df.append({ 'bench': self.app,
                                     'dataset': 'none',
                                     'arch': self.arch,
                                     'threads': int(self.threads),
                                     'cmdline': ' '.join(self.cmdline),
                                     'unit': 'seconds',
                                     'retval': retval,
                                     'value': duration }, ignore_index=True)
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


class Histogram(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/histogram/histogram',
                         self.phoenix_dir + '/phoenix-2.0/tests/histogram/histogram_datafiles/large.bmp' ]


class Kmeans(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/kmeans/kmeans' ]


class LinearRegression(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/linear_regression/linear_regression',
                         self.phoenix_dir + '/phoenix-2.0/tests/linear_regression/linear_regression_datafiles/key_file_500MB.txt' ]


class MatrixMultiply(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/matrix_multiply/matrix_multiply',
                         '5000', '5000', '1' ]


class Pca(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/pca/pca',
                         '-r', '5000', '-c', '5000', '-s', '424242' ]


class StringMatch(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/string_match/string_match',
                         self.phoenix_dir + '/phoenix-2.0/tests/string_match/string_match_datafiles/key_file_500MB.txt' ]


class WordCount(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/word_count/word_count',
                         self.phoenix_dir + '/phoenix-2.0/tests/word_count/word_count_datafiles/word_100MB.txt' ]


class PhoenixFactory():

    apps = {
        "phoenix.histogram": Histogram,
        "phoenix.kmeans": Kmeans,
        "phoenix.linearregression": LinearRegression,
        "phoenix.matrixmultiply": MatrixMultiply,
        "phoenix.pca": Pca,
        "phoenix.stringmatch": StringMatch,
        "phoenix.wordcount": WordCount
    }

    def create(args, config):
        try:
            bench = PhoenixFactory.apps[args.bench]
        except:
            logging.error("This benchmark does not exist in the Phoenix suite (or is not supported yet...)")
            exit(1)
        return bench(args, config)
