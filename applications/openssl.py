#!/usr/bin/env python3

import logging
import pandas as pd

from applications.bench import Benchmark

archs = [ 'x86_64', 'aarch64' ]

class Openssl(Benchmark):

    app = None
    tmpdir = None
    arch = None
    binary_path = None

    def __init__(self, args, config):
        super().__init__(args, config)
        self.app = args.bench[8:]
        self.binary_path = config.store["OPENSSL_BIN"]

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by Openssl. Should be among "+str(archs))
            exit(1)
        self.arch = args.arch


    def prepare(self):
        super().prepare()

        self.cmdline = [ self.binary_path, "speed", "-mr" ]


    def format_output(self, stdout, stderr):
        return None


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

def format_output_throughput(self, stdout, stderr):
    df = pd.DataFrame()
    stdout.seek(0)
    for l in stdout:
        if l.startswith("+H:"):
            blksize_list = l.split(':')[1:]
        elif l.startswith("+F:"):
            throughput_list = l.split(':')[3:]
        elif "bench.py" in l:
            retval = int(l.split(' ')[7])
    if len(blksize_list) != len(throughput_list):
        logging.error(f"Inconsistent output ({len(blksize_list)} block sizes and {len(throughput_list)} throughput values)")
        return None
    else:
        for i, b in enumerate(blksize_list):
            df = df.append({ 'bench': f"{self.name}-{b.strip()}",
                             'dataset': 'none',
                             'arch': self.arch,
                             'threads': 1,
                             'cmdline': ' '.join(self.cmdline),
                             'unit': 'B/s',
                             'retval': retval,
                             'value': float(throughput_list[i]) }, ignore_index=True)
    return df

class MD5(Openssl):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()
        self.cmdline.append("md5")


    def format_output(self, stdout, stderr):
        return format_output_throughput(self, stdout, stderr)


class SHA1(Openssl):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()
        self.cmdline.append("sha1")


    def format_output(self, stdout, stderr):
        return format_output_throughput(self, stdout, stderr)


class SHA256(Openssl):

    def __init__(self, args, config):
        super().__init__(args, config)


    def prepare(self):
        super().prepare()
        self.cmdline.append("sha256")


    def format_output(self, stdout, stderr):
        return format_output_throughput(self, stdout, stderr)


class OpensslFactory():

    apps = {
        "openssl.md5": MD5,
        "openssl.sha1": SHA1,
        "openssl.sha256": SHA256,
    }
    
    def create(args, config):
        try:
            bench = OpensslFactory.apps[args.bench]
        except:
            logging.error("This benchmark is not supported in Openssl (yet?)")
            exit(1)
        return bench(args, config)
