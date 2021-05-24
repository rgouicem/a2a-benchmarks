#!/usr/bin/env python3

import logging, os
import pandas as pd

from applications.bench import Benchmark

archs = {
    "x86_64": "amd64-linux.gcc",
    "aarch64": "aarch64-linux.gcc"
}

class SQLite(Benchmark):

    sqlite_dir = None
    app = 'sqlite-speedtest1'

    def __init__(self, args, config):
        super().__init__(args, config)
        self.sqlite_dir = config.store["SQLITE_DIR"]

        # Get binary ISA
        if args.arch not in archs:
            logging.error("Architecture not supported by PARSEC. Should be among "+archs)
            exit(1)
        self.arch = args.arch

    def prepare(self):
        super().prepare()

        self.cmdline = [ self.sqlite_dir + '/speedtest1', '--multithread', '--threads', str(self.threads) ]

    def format_output(self, stdout, stderr):
        df = pd.DataFrame()
        with open(stdout.name, "r") as fp:
            for l in fp:
                if "TOTAL..." in l:
                    duration = float(l.split()[1][:-1])
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


class DbFactory():

    apps = {
        "db.sqlite": SQLite,
    }

    def create(args, config):
        try:
            bench = DbFactory.apps[args.bench]
        except:
            logging.error("This benchmark does not exist")
            exit(1)
        return bench(args, config)
