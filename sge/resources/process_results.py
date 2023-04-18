# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import json
import numpy as np

# %%
EXPERIMENT = '../dumps/RRSE/5.0/0.5/'
header_list = ['Generation', 'Best', 'PopAvg', 'PopStd']
results = [pd.read_csv(run_dir.path + '/progress_report.csv', sep='\t', names=header_list,index_col='Generation').assign(Run=int(re.findall(r'run_(\d+)',run_dir.path)[0])) for run_dir in os.scandir(EXPERIMENT) if run_dir.is_dir()]
# %%
df_concat = pd.concat(results,axis=0)
df_concat = df_concat[df_concat.index <= 100]
df_concat = df_concat[df_concat['Run'] <= 14]

# %%
df_mean = df_concat.groupby('Generation').mean()
sns.lineplot(data=df_mean, x='Generation', y='Best')
# %%
plt.figure()
df_min = df_concat.groupby('Run').min()
sns.boxplot(data=df_min, y='Best')


# %%
df_concat.groupby(['Generation', 'Best']).min().loc[300]
sns.histplot(data=df_concat[df_concat.index == 300].reset_index(), x='Best', discrete=True)
# %%
df_concat[df_concat['Best'] == 0].loc[300,'Run']

# %%
df_concat[df_concat['Best'] == 0].loc[300,'Run'].count() / df_concat['Run'].max()
# %%
columns_names = [run_dir.name for run_dir in os.scandir(EXPERIMENT) if run_dir.is_dir()]
rrse_by_generation = np.asarray([[json.load(open(f'{run_dir.path}/iteration_{gen}.json'))[0]['other_info']['rrse'] for gen in range(101)] for run_dir in os.scandir(EXPERIMENT) if run_dir.is_dir()])
df = pd.DataFrame(data=rrse_by_generation.T, columns=columns_names)

ax = sns.lineplot(data=df.mean(axis=1))
ax.set_xlabel('Generations')
ax.set_ylabel('RRSE')

# %%

