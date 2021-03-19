#!/usr/bin/env python3

import argparse, logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sbs

#########################################

# Parse the command line arguments
parser = argparse.ArgumentParser(description="Plot facility")
parser.add_argument('-i', '--input', required=True,
                    help='Pickle/csv file where benchmark results are stored.')
parser.add_argument('-o', '--output', required=True,
                    help='Output PDF file.')
parser.add_argument('-b', '--baseline', required=True,
                    help='Baseline to use for comparison, in the format arch,runtime,tag.')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Set the verbosity level')
args = parser.parse_args()

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

# Read input file
if args.input.endswith(".csv"):
    df = pd.read_csv(args.input, sep=';')
else:
    df = pd.read_pickle(args.input)

# Parse baseline arg
try:
    b = args.baseline.split(',')
    base_arch, base_runtime, base_tag = b
except ValueError:
    logging.error('Wrong format for baseline argument. Expecting arch,runtime,tag.')
    exit(1)

# Extract baseline from dataframe
base_df = df.loc[(df['arch'] == base_arch) & (df['runtime'] == base_runtime) & (df['tag'] == base_tag)]

# Get the mean for each baseline benchmark
base_means = {}
for b in set(base_df['bench']):
    base_means[b] = np.array(base_df.loc[base_df['bench'] == b]['value'].values, dtype=np.float32).mean()

# Normalize all results from original df to these means
df_norm = pd.DataFrame(columns=['arch', 'bench', 'dataset', 'threads', 'unit', 'value', 'runtime',
                                'tag', 'norm', 'label'])
norm_vals = []
for row in df.itertuples():
    try:
        norm = float(row.value) / base_means[row.bench]
        dct = row._asdict()
        dct['norm'] = norm
        dct['label'] = f"{dct['runtime']}-{dct['tag']}"
        del dct['Index']
        del dct['cmdline']
        norm_vals.append(dct)
    except KeyError:
        pass
df_norm = df_norm.append(norm_vals, ignore_index=True)

# Plot
sbs.barplot(data=df_norm, x='bench', y='norm', hue='label', log=True)
plt.savefig(args.output, dpi=500, bbox_inches='tight')
plt.show()
