#!/usr/bin/env python3

import argparse, logging, subprocess, os, time, tempfile
import pandas as pd

from config import Config
from benchmarks.factory import BenchmarkFactory
from runtimes.factory import RuntimeFactory


######################################

# Parse the command line arguments and options
parser = argparse.ArgumentParser(description="Benchmark facility")
parser.add_argument('-b', '--bench', required=True,
                    help='Benchmark to run')
parser.add_argument('-d', '--dataset', required=True,
                    help='Dataset to use, benchmark specific (for PARSEC: test, simlarge, native)')
parser.add_argument('-r', '--runtime', required=True, choices=['native','qemu','llvm'],
                    help='Type of runtime')
parser.add_argument('-o', '--output', required=True,
                    help='Pickle file where results should be outputed. If file already exists, results will be appended.')
parser.add_argument('-a', '--arch', default='x86_64', choices=['x86_64', 'aarch64'],
                    help='ISA to use when selecting the binary')
parser.add_argument('-n', '--num-threads', type=int, required=True,
                    help='Number of threads')
parser.add_argument('-i', '--num-runs', type=int, default=1,
                    help='Number of runs to perform')
parser.add_argument('-t', '--tag', type=str, default='none',
                    help='Tag used for results (default: none)')
parser.add_argument('-c', '--config-file', default='./config',
                    help='Path to a config file (default: ./config)')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Set the verbosity level')
args = parser.parse_args()
args.output = os.path.abspath(args.output)

# Setup logging
try:
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level={ 0: logging.ERROR,
                                1: logging.WARNING,
                                2: logging.INFO,
                                3: logging.DEBUG }[args.verbose])
except:
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.DEBUG)

# Read configuration file
config = Config(args.config_file)
logging.info("Configuration: "+str(config))

# Get the benchmark object
logging.info("Creating benchmark...")
bench = BenchmarkFactory.create(args, config)
logging.info("Benchmark created: "+str(bench))

# Prepare the benchmark
logging.info("Preparing benchmark...")
bench.prepare()
logging.info(f"Benchmark is ready: {bench}")

# Get the runtime object
logging.info("Preparing runtime...")
runtime = RuntimeFactory.create(args, config)
logging.info("Runtime is ready: "+str(runtime))

# Build the complete command line
# env = os.environ | runtime.env | bench.env
env = {**runtime.env, **bench.env}
logging.info(f"Environment: {env}")
cmdline = runtime.cmdline + bench.cmdline
logging.info(f"Command line: {cmdline}")

# Execute the command line
logging.info(f"Executing command {args.num_runs} times...")
stdout = tempfile.NamedTemporaryFile(mode="w")
stderr = tempfile.NamedTemporaryFile(mode="w")
for i in range(1, args.num_runs + 1):
    logging.info(f"Run {i}...")
    start = time.time()
    subprocess.run(cmdline, env=env, stdout=stdout, stderr=stderr)
    end = time.time()
    print(f"bench.py: duration: {end - start} seconds, run: {i}", file=stdout, flush=True)
    logging.info(f"Run {i}... done")
logging.info(f"Executing command {args.num_runs} times... done")

# Format the output
logging.info("Formatting output...")
result = bench.format_output(stdout, stderr)
result['runtime'] = args.runtime
result['tag'] = args.tag
try:
    df = pd.read_pickle(args.output)
    df = df.append(result, ignore_index=False)
    df.to_pickle(args.output)
except FileNotFoundError:
    result.to_pickle(args.output)
logging.info(f"Results available at: {args.output}")

print('\nStandard output:')
with open(stdout.name, "r") as fp:
    print(fp.read())
print('\nStandard error:')
with open(stderr.name, "r") as fp:
    print(fp.read())

# Cleanup
logging.info("Cleaning up benchmark data...")
bench.cleanup()
logging.info("Cleaning up benchmark data... done")
