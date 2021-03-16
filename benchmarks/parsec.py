#!/usr/bin/env python3

import logging, tempfile, tarfile, os, shutil, tarfile
import pandas as pd

from benchmarks.bench import Benchmark

datasets = [ 'test', 'simdev', 'simsmall', 'simmedium', 'simlarge', 'native' ]
archs = {
    "x86_64": "amd64-linux.gcc",
    "aarch64": "aarch64-linux.gcc"
}

class Parsec(Benchmark):

    app = None
    dataset = None
    tmpdir = None
    arch = None
    parsec_dir = None
    bench_dir = None

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench.split('.')[1]
        self.parsec_dir = config.store["PARSEC_DIR"]

        # Check dataset
        if args.dataset not in datasets:
            logging.error("Dataset not supported by PARSEC. Should be among "+datasets)
            exit(1)
        else:
            self.dataset = args.dataset

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by PARSEC. Should be among "+archs)
            exit(1)
        self.arch = args.arch


    def prepare(self):
        self.tmpdir = tempfile.mkdtemp(prefix=f"parsec.{self.app}.")

        # Extract input from tar in temp dir
        tar = tarfile.open(self.parsec_dir+f"{self.bench_dir}/{self.app}/inputs/input_"+self.dataset+".tar")
        tar.extractall(path=self.tmpdir)
        tar.close()


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        with open(stdout.name, "r") as fp:
            for l in fp:
                if "bench.py" in l:
                    duration = l.split(' ')[2]
                    df = df.append({ 'bench': self.app,
                                     'dataset': self.dataset,
                                     'arch': self.arch,
                                     'threads': int(self.threads),
                                     'cmdline': ' '.join(self.cmdline),
                                     'unit': 'seconds',
                                     'value': duration }, ignore_index=True)
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

class Blackscholes(Parsec):

    inputs = {
        'test': 'in_4.txt',
        'simdev': 'in_16.txt',
        'simsmall': 'in_4K.txt',
        'simmedium': 'in_16K.txt',
        'simlarge': 'in_64K.txt',
        'native': 'in_10M.txt'
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"


    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+self.bench_dir+"blackscholes/inst/"+archs[self.arch]+"/bin/blackscholes"
        self.cmdline = [ binary_path,
                         str(self.threads),
                         self.tmpdir+"/"+self.inputs[self.dataset],
                         self.tmpdir+"/prices.txt" ]


class Bodytrack(Parsec):

    inputs = {
        'test': 'sequenceB_1', 
        'simdev': 'sequenceB_1',
        'simsmall': 'sequenceB_1',
        'simmedium': 'sequenceB_2',
        'simlarge': 'sequenceB_4',
        'native': 'sequenceB_261'
    }

    args = {
        'test': [ '4', '1', '5', '1', '0' ],
        'simdev': [ '4', '1', '100', '3', '0' ],
        'simsmall': [ '4', '1', '1000', '5', '0' ],
        'simmedium': [ '4', '2', '2000', '5', '0' ],
        'simlarge': [ '4', '4', '4000', '5', '0' ],
        'native': [ '4', '261', '4000', '5', '0' ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/apps/bodytrack/inst/"+archs[self.arch]+"/bin/bodytrack"
        self.cmdline = [ binary_path,
                         self.tmpdir+"/"+self.inputs[self.dataset] ] + self.args[self.dataset] + [ str(self.threads) ]


class Canneal(Parsec):

    inputs = {
        'test': '10.nets', 
        'simdev': '100.nets',
        'simsmall': '100000.nets',
        'simmedium': '200000.nets',
        'simlarge':  '400000.nets',
        'native':   '2500000.nets'
    }

    args = {
        'test': [ [ '5', '100' ], [ '1' ] ],
        'simdev': [ [ '100', '300' ], [ '2' ] ],
        'simsmall': [ [ '10000', '2000' ], [ '32' ] ],
        'simmedium': [ [ '15000', '2000' ], [ '64' ] ],
        'simlarge': [ [ '15000', '2000' ], [ '128' ] ],
        'native': [ [ '15000', '2000' ], [ '6000' ] ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/kernels/"

    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/kernels/canneal/inst/"+archs[self.arch]+"/bin/canneal"
        self.cmdline = [ binary_path, str(self.threads) ] + self.args[self.dataset][0] + [ self.tmpdir+"/"+self.inputs[self.dataset] ] + self.args[self.dataset][1]


# class Facesim(Parsec):

#     inputs = {
#     }


class Ferret(Parsec):

    args = {
        'test': [ '5', '5' ],
        'simdev': [ '5', '5' ],
        'simsmall': [ '10', '20' ],
        'simmedium': [  '10', '20'],
        'simlarge': [ '10', '20' ],
        'native': [ '50', '20' ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/apps/ferret/inst/"+archs[self.arch]+"/bin/ferret"
        self.cmdline = [ binary_path,
                         self.tmpdir+'/corel',
                         'lsh',
                         self.tmpdir+'/queries' ] + self.args[self.dataset] + [ str(self.threads),
                                                                                   self.tmpdir+'/output.txt' ]


class ParsecFactory():

    apps = {
        "parsec.blackscholes": Blackscholes,
        "parsec.bodytrack": Bodytrack,
        "parsec.canneal": Canneal,
        "parsec.ferret": Ferret
    }

    def create(args, config):
        try:
            bench = ParsecFactory.apps[args.bench]
        except:
            logging.error("This benchmark does not exist in the PARSEC suite (or is not supported yet...)")
            exit(1)
        return bench(args, config)
