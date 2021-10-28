#!/usr/bin/env python3

import logging, os, shutil, tempfile
import pandas as pd

from applications.bench import Benchmark

archs = {
    "x86_64": "amd64-linux.gcc",
    "aarch64": "aarch64-linux.gcc"
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

        # Fix number of threads (must be configured through environment variables)
        self.env["MR_NUMTHREADS"] = str(self.threads)
        self.env["MR_NUMPROCS"] = str(self.threads)


    def prepare(self, no_input=False, input_path=None):
        self.tmpdir = tempfile.mkdtemp(prefix=f"{self.app}.")

        if no_input is False:
            shutil.copy(input_path, f"{self.tmpdir}/")


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        stdout.seek(0)
        for l in fp:
            if "bench.py" in l:
                duration = float(l.split(' ')[2])
                retval = int(l.split(' ')[7])
                df = df.append({ 'bench': self.app,
                                 'dataset': self.dataset,
                                 'arch': self.arch,
                                 'threads': int(self.threads),
                                 'cmdline': ' '.join(self.cmdline),
                                 'unit': 'seconds',
                                 'retval': retval,
                                 'value': duration }, ignore_index=True)
        if len(df) == 0:
            return None
        return df

    def cleanup(self):
        shutil.rmtree(self.tmpdir)

    def __str__(self):
        ret = "<"
        ret += "name="+self.name
        ret += ", threads="+str(self.threads)
        ret += ", dataset="+self.dataset
        ret += ", arch="+self.arch
        ret += ", cmdline: " + str(self.cmdline)
        ret += ">"
        return ret


class Histogram(Phoenix):

    inputs = {
        'small': 'small.bmp',
        'med':     'med.bmp',
        'large': 'large.bmp'
    }

    def __init__(self, args, config):
        super().__init__(args, config)

        # Check dataset
        if args.dataset not in self.inputs:
            logging.error(f"Dataset not supported by {self.app}. Should be among {self.inputs.keys()}")
            exit(1)
        else:
            self.dataset = args.dataset


    def prepare(self):
        super().prepare(input_path=f"{self.phoenix_dir}/phoenix-2.0/tests/histogram/histogram_datafiles/{self.inputs[self.dataset]}")

        # Build cmdline
        self.cmdline = [ f"{self.phoenix_dir}/phoenix-2.0/tests/histogram/histogram",
                         f"{self.tmpdir}/{self.inputs[self.dataset]}" ]


class Kmeans(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)
        self.dataset = "large"


    def prepare(self):
        super().prepare(no_input=True)

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/kmeans/kmeans' ]


class LinearRegression(Phoenix):

    inputs = {
        'small': 'key_file_50MB.txt',
        'med':   'key_file_100MB.txt',
        'large': 'key_file_500MB.txt'
    }

    def __init__(self, args, config):
        super().__init__(args, config)

        # Check dataset
        if args.dataset not in self.inputs:
            logging.error(f"Dataset not supported by {self.app}. Should be among {self.inputs.keys()}")
            exit(1)
        else:
            self.dataset = args.dataset

    def prepare(self):
        super().prepare(input_path=f"{self.phoenix_dir}/phoenix-2.0/tests/linear_regression/linear_regression_datafiles/{self.inputs[self.dataset]}")

        # Build cmdline
        self.cmdline = [ f"{self.phoenix_dir}/phoenix-2.0/tests/linear_regression/linear_regression",
                         f"{self.tmpdir}/{self.inputs[self.dataset]}" ]


class MatrixMultiply(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)
        self.dataset = "large"

    def prepare(self):
        super().prepare(no_input=True)

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/matrix_multiply/matrix_multiply',
                         '5000', '5000', '1' ]


class Pca(Phoenix):

    def __init__(self, args, config):
        super().__init__(args, config)
        self.dataset = "large"

    def prepare(self):
        super().prepare(no_input=True)

        # Build cmdline
        self.cmdline = [ self.phoenix_dir + '/phoenix-2.0/tests/pca/pca',
                         '-r', '5000', '-c', '5000', '-s', '424242' ]


class StringMatch(Phoenix):

    inputs = {
        'small': 'key_file_50MB.txt',
        'med':   'key_file_100MB.txt',
        'large': 'key_file_500MB.txt'
    }   

    def __init__(self, args, config):
        super().__init__(args, config)

        # Check dataset
        if args.dataset not in self.inputs:
            logging.error(f"Dataset not supported by {self.app}. Should be among {self.inputs.keys()}")
            exit(1)
        else:
            self.dataset = args.dataset


    def prepare(self):
        super().prepare(input_path=f"{self.phoenix_dir}/phoenix-2.0/tests/linear_regression/linear_regression_datafiles/{self.inputs[self.dataset]}")

        # Build cmdline
        self.cmdline = [ f"{self.phoenix_dir}/phoenix-2.0/tests/string_match/string_match",
                         f"{self.tmpdir}/{self.inputs[self.dataset]}" ]


class WordCount(Phoenix):

    inputs = {
        'small': 'word_10MB.txt',
        'med':   'word_50MB.txt',
        'large': 'word_100MB.txt'
    }

    def __init__(self, args, config):
        super().__init__(args, config)

        # Check dataset
        if args.dataset not in self.inputs:
            logging.error(f"Dataset not supported by {self.app}. Should be among {self.inputs.keys()}")
            exit(1)
        else:
            self.dataset = args.dataset


    def prepare(self):
        super().prepare(input_path=f"{self.phoenix_dir}/phoenix-2.0/tests/word_count/word_count_datafiles/{self.inputs[self.dataset]}")

        # Build cmdline
        self.cmdline = [ f"{self.phoenix_dir}/phoenix-2.0/tests/word_count/word_count",
                         f"{self.tmpdir}/{self.inputs[self.dataset]}" ]


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
