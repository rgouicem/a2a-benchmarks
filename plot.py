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
    base_arch, base_runtime, base_tag = args.baseline.split(',')
except ValueError:
    logging.error('Wrong format for baseline argument. Expecting arch,runtime,tag.')
    exit(1)

# Extract baseline from dataframe
base_df = df.loc[(df['arch'] == base_arch) & (df['runtime'] == base_runtime) & (df['tag'] == base_tag)]

# Get the mean for each baseline benchmark
base_means = {}
for b in set(base_df['bench']):
    base_means[b] = np.array(base_df.loc[base_df['bench'] == b]['value'].values, dtype=np.float32).mean()
    # print(f"{b};{base_means[b]:.2f}")

# Print the mean of every benchmark for each runtime
mean_df = pd.DataFrame(columns=['bench',
                                # 'none',
                                'master',
                                'no-fences',
                                # 'new-mappings'
                                ])
for b in sorted(set(df['bench'])):
    df_b = df.loc[df['bench'] == b]
    tmp_dict = { 'bench': b }
    for t in set(df_b['tag']):
        df_b_t = df_b.loc[df_b['tag'] == t]
        tmp_dict[t] = np.mean(df_b_t['value'])
    mean_df = mean_df.append(tmp_dict, ignore_index=True)
print(mean_df)

# Normalize all results from original df to these means
df_norm = pd.DataFrame(columns=['arch', 'bench', 'dataset', 'threads', 'unit', 'value', 'runtime',
                                'tag', 'norm', 'label'])
norm_vals = []
for row in df.itertuples():
    try:
        if row.arch == base_arch and row.runtime == base_runtime and row.tag == base_tag:
            continue
        # norm = base_means[row.bench] / float(row.value)      # speedup
        norm = float(row.value) / base_means[row.bench]    # relative perf
        
        # norm = 100 * (base_means[row.bench] - float(row.value)) / base_means[row.bench]
        dct = row._asdict()
        dct['norm'] = norm
        dct['label'] = f"{dct['tag']}"
        # dct['label'] = f"{dct['runtime']}-{dct['tag']}"
        del dct['Index']
        del dct['cmdline']
        norm_vals.append(dct)
    except KeyError:
        pass
df_norm = df_norm.append(norm_vals, ignore_index=True)

# Plot
fig = plt.figure(figsize=(10, 3))
palette = sbs.color_palette("muted")
# palette ={"native-none": "C0", "qemu-master": "C4", "qemu-no-fences": "C1", "qemu-new-mappings": "C2"}
# df_norm = df_norm.loc[df_norm['label'] != 'qemu-master']
ax = sbs.barplot(data=df_norm, ci='sd',
                 x='bench', y='norm',
                 # x='norm', y='bench',
                 hue='label', palette=palette,
                 order=sorted(set(df_norm['bench'])))

plt.grid(b=True, axis='y')
# plt.grid(b=True, axis='x')

plt.xticks(# ticks=list(range(0, len(set(base_df['bench'])))),
           # labels=
           rotation=45, ha="right", fontsize='x-small')

# plt.ylim(0, 1.1)
# plt.ylim(0, 22)

# plt.yticks(ticks=np.arange(0, 25, step=5))
# plt.yticks(ticks=np.arange(0, 1.1, step=.1))

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),borderaxespad=0, ncol=4)
# ax.get_legend().remove()

ax.set_axisbelow(True)

plt.xlabel("")
# plt.xlabel("Speedup compared to vanilla QEMU")

# plt.ylabel("Speedup w.r.t. QEMU")
plt.ylabel("Runtime relative to qemu-master")

plt.axhline(y=1, xmin=0, xmax=1, color='red')
# Annotate the raw value of the baseline
for idx, value in enumerate(sorted(set(base_means))):
    plt.text(idx - .2, 1.02, f"{base_means[value]:.1f}", fontsize='xx-small')

plt.savefig(args.output, dpi=500, bbox_inches='tight')
# plt.show()
