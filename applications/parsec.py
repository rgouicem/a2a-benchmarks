#!/usr/bin/env python3

import logging, tempfile, tarfile, os, shutil, tarfile
import pandas as pd

from applications.bench import Benchmark

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
        self.app = args.bench[7:]
        self.parsec_dir = config.store["PARSEC_DIR"]

        # Check dataset
        if args.dataset not in datasets:
            logging.error("Dataset not supported by PARSEC. Should be among "+str(datasets))
            exit(1)
        else:
            self.dataset = args.dataset

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by PARSEC. Should be among "+str(archs))
            exit(1)
        self.arch = args.arch


    def prepare(self, no_input=False):
        self.tmpdir = tempfile.mkdtemp(prefix=f"parsec.{self.app}.")

        # Extract input from tar in temp dir
        if no_input is False:
            tarpath = f"{self.parsec_dir}/{self.bench_dir}/{self.app}/inputs/input_{self.dataset}.tar"
            logging.debug(f"Extracting input {tarpath} to {self.tmpdir}")
            tar = tarfile.open(tarpath)
            tar.extractall(path=self.tmpdir)
            tar.close()


    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        with open(stdout.name, "r") as fp:
            for l in fp:
                if "bench.py" in l:
                    duration = float(l.split(' ')[2])
                    retval = int(l.split(' ')[7])
                    df = df.append({ 'bench': f"parsec.{self.app}",
                                     'dataset': self.dataset,
                                     'arch': self.arch,
                                     'threads': int(self.threads),
                                     'cmdline': ' '.join(self.cmdline),
                                     'unit': 'seconds',
                                     'retval': retval,
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


class Dedup(Parsec):

    inputs = {
        'test': 'test.dat',
        'simdev': 'hamlet.dat',
        'simsmall': 'media.dat',
        'simmedium': 'media.dat',
        'simlarge':  'media.dat',
        'native':   'FC-6-x86_64-disc1.iso'
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/kernels/"

    def prepare(self):
        super().prepare()

        # Build cmdline
        binary_path = f"{self.parsec_dir}/pkgs/kernels/dedup/inst/{archs[self.arch]}/bin/dedup"
        self.cmdline = [ binary_path, '-c', '-p', '-v', '-t', str(self.threads),
                         '-i', f"{self.tmpdir}/{self.inputs[self.dataset]}",
                         '-o', f"{self.tmpdir}/output.dat.ddp" ]


class Facesim(Parsec):

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()

        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/apps/facesim/inst/"+archs[self.arch]+"/bin/facesim"
        self.cmdline = [ binary_path ]
        if self.dataset == "test":
            self.cmdline += [ '-h' ]
        elif self.dataset == "native":
            self.cmdline += [ '-timing', '-threads', str(self.threads), '-lastframe', '100' ]
        else:
            self.cmdline += [ '-timing', '-threads', str(self.threads) ]

        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)

    def cleanup(self):
        super().cleanup()
        os.chdir(self.olddir)


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


class Fluidanimate(Parsec):

    inputs = {
        'test': 'in_5K.fluid',
        'simdev': 'in_15K.fluid',
        'simsmall': 'in_35K.fluid',
        'simmedium': 'in_100K.fluid',
        'simlarge': 'in_300K.fluid',
        'native':  'in_500K.fluid' 
    }

    args = {
        'test': '1',
        'simdev': '3',
        'simsmall': '5',
        'simmedium': '5',
        'simlarge': '5',
        'native': '500'
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/apps/fluidanimate/inst/"+archs[self.arch]+"/bin/fluidanimate"
        self.cmdline = [ binary_path, str(self.threads), self.args[self.dataset],
                         self.tmpdir+'/'+self.inputs[self.dataset], self.tmpdir+'/out.fluid' ]


class Streamcluster(Parsec):

    args = {
        'test': [ '2', '5', '1', '10', '10', '5', 'none' ],
        'simdev': [ '3', '10', '3', '16', '16', '10', 'none' ],
        'simsmall': [ '10', '20', '32', '4096', '4096', '1000', 'none' ],
        'simmedium': [ '10', '20', '64', '8192', '8192', '1000', 'none' ],
        'simlarge': [ '10', '20', '128', '16384', '16384', '1000', 'none' ],
        'native': [ '10', '20', '128', '1000000', '200000', '5000', 'none' ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/kernels/"

    def prepare(self):
        super().prepare(no_input=True)

        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/kernels/streamcluster/inst/"+archs[self.arch]+"/bin/streamcluster"
        self.cmdline = [ binary_path ] + self.args[self.dataset] + [ self.tmpdir+'/output.txt',
                                                                     str(self.threads) ]


class Vips(Parsec):

    inputs = {
        'test': 'barbados_256x288.v',
        'simdev': 'barbados_256x288.v',
        'simsmall': 'pomegranate_1600x1200.v',
        'simmedium': 'vulture_2336x2336.v',
        'simlarge': 'bigben_2662x5500.v',
        'native': 'orion_18000x18000.v'
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()
        
        # Build cmdline
        binary_path = self.parsec_dir+"/pkgs/apps/vips/inst/"+archs[self.arch]+"/bin/vips"
        self.cmdline = [ binary_path, 'im_benchmark',
                         self.tmpdir+'/'+self.inputs[self.dataset],
                         self.tmpdir+'/output.v' ]


class Freqmine(Parsec):

    inputs = {
        'test': [ "T10I4D100K_3.dat",  "1" ],
        'simdev': [ "T10I4D100K_1k.dat", "3" ],
        'simsmall': [ "kosarak_250k.dat", "220" ],
        'simmedium': [ "kosarak_500k.dat", "410" ],
        'simlarge': [ "kosarak_990k.dat", "790" ],
        'native': [ "webdocs_250k.dat", "11000" ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare()

        # Build cmdline
        binary_path = self.parsec_dir+self.bench_dir+"/freqmine/inst/"+archs[self.arch]+"/bin/freqmine"
        self.cmdline = [ binary_path, self.tmpdir+'/'+self.inputs[self.dataset][0], self.inputs[self.dataset][1] ]


class Swaptions(Parsec):

    inputs = {
        'test': [ '128', '1000000' ],
        'simdev': [ '3', '50' ],
        'simsmall': [ '16', '10000' ],
        'simmedium': [ '32', '20000' ],
        'simlarge': [ '64', '40000' ],
        'native': [ '128', '1000000' ]
    }

    def __init__(self, args, config):
        super().__init__(args, config)
        self.bench_dir = "/pkgs/apps/"

    def prepare(self):
        super().prepare(no_input=True)

        # Build cmdline
        binary_path = self.parsec_dir+self.bench_dir+"swaptions/inst/"+archs[self.arch]+"/bin/swaptions"
        self.cmdline = [ binary_path,
                         "-ns", self.inputs[self.dataset][0],
                         '-sm', self.inputs[self.dataset][1],
                         '-nt', str(min(self.threads, int(self.inputs[self.dataset][0]))) ]

class ParsecFactory():

    apps = {
        "parsec.blackscholes": Blackscholes,
        "parsec.bodytrack": Bodytrack,
        "parsec.canneal": Canneal,
        "parsec.dedup": Dedup,
        "parsec.facesim": Facesim,
        "parsec.ferret": Ferret,
        "parsec.fluidanimate": Fluidanimate,
        "parsec.freqmine": Freqmine,
        # "parsec.raytrace": Raytrace,
        "parsec.streamcluster": Streamcluster,
        "parsec.swaptions": Swaptions,
        "parsec.vips": Vips,
        # "parsec.x264": X264
    }

    def create(args, config):
        try:
            bench = ParsecFactory.apps[args.bench]
        except:
            logging.error("This benchmark does not exist in the PARSEC suite (or is not supported yet...)")
            exit(1)
        return bench(args, config)
