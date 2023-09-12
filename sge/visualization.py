import re
import os
import json
from plotnine import *
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

plt.rcParams["figure.figsize"] = (20,15)
plt.rcParams['axes.grid'] = True
# plt.style.use('fivethirtyeight')
plt.rcParams['figure.facecolor'] = 'FFFFFF'
plt.rcParams['axes.facecolor'] = 'FFFFFF'
plt.rcParams['lines.linewidth'] = 3
plt.rcParams.update({'font.size': 26})

NT = "NT"
T = "T"
NT_PATTERN = "(<.+?>)"
RULE_SEPARATOR = "::="
PRODUCTION_SEPARATOR = "|"

GENERATIONS = 50
RUNS = 30

# TODO: automaticamente guardar grafico numa pasta ou apenas mostrar ?

def read_grammar(path):
    """
    Reads a Grammar in the BNF format and converts it to a python dictionary
    This method was adapted from PonyGE version 0.1.3 by Erik Hemberg and James McDermott
    """
    grammar = {}
    with open(path, "r") as f:
        for line in f:
            if not line.startswith("#") and line.strip() != "":
                if line.find(PRODUCTION_SEPARATOR):
                    left_side, productions = line.split(RULE_SEPARATOR)
                    left_side = left_side.strip()
                    if not re.search(NT_PATTERN, left_side):
                        raise ValueError("Left side not a non-terminal!")

                    temp_productions = []
                    for production in [production.strip() for production in productions.split(PRODUCTION_SEPARATOR)]:
                        temp_production = []
                        if not re.search(NT_PATTERN, production):
                            if production == "None":
                                production = ""
                            temp_production.append((production, T))
                        else:
                            for value in re.findall("<.+?>|[^<>]*", production):
                                if value != "":
                                    if re.search(NT_PATTERN, value) is None:
                                        sym = (value, T)
                                    else:
                                        sym = (value, NT)
                                    temp_production.append(sym)
                        temp_productions.append(temp_production)                          
                    if left_side not in grammar:
                        grammar[left_side] = temp_productions
    return grammar

def plot_probabilities(path, grammar_path):
    fig = 1
    grammar = read_grammar(grammar_path)
    prob_gram = {}
    for run in os.listdir(path):
        if 'last' not in run:
            continue
        # filter number of runs
        s = run.split("_")
        if int(s[1]) > RUNS:
            continue
        foldername = path + run + "/"   
        
        for nt in grammar.keys():
            if nt not in prob_gram:
                prob_gram[nt] = [[ [] for _ in range(GENERATIONS) ] for _ in range(len(grammar[nt]))]
        for i in range(0,GENERATIONS):
            filename = foldername + "generation_" + str(i) + ".json"
            with open(filename) as f:
                data = json.load(f)
                for rule, nt in enumerate(grammar):
                    number_rules = len(grammar[nt])
                    # list position for each production rule of nt
                    for j in range(number_rules):
                        prob_gram[nt][j][i].append(data[0]['grammar'][rule][j])


    lines = [':','-.','--','-','^']
    colors = [(0,0,0), (0.5,0.5,0.5), (0.25,0.25,0.25), (0.375,0.375,0.375), (0.625,0.625,0.625)]
    colors_rgb = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
    # if "bostonhousing" in path:
        # names = ["CRIM","ZN","INDUS","CHAS","NOX","RM","AGE","DIS","RAD","TAX","PTRATIO","B","LSTAT","MEDV"]            
    c = 0
    for i, (nt, prods) in enumerate(prob_gram.items()):
        print(nt)
        plt.figure(fig)
        plt.title(nt)
        plt.ylabel("PROBABILITIES")
        plt.xlabel("GENERATIONS")
        plt.axis([0,GENERATIONS,-0.1,1.1])
        valores_x = list(range(0,GENERATIONS))
        line = 0
        c = 0
        for j, prod in enumerate(prods):
            if len(colors) == c:
                c = 0
            if len(lines) == line:
                line = 0
            valores_y = []
            for gen in prod:
                valores_y.append(sum(gen)/len(gen))
            
            nome_da_linha = grammar[nt][j]
            nome_da_linha = ""
            for sym, type in grammar[nt][j]:
                if "pre_op" in nt:
                    nome_da_linha = sym[1:]
                elif "<op>" == nt:
                    nome_da_linha += sym
                    if nome_da_linha == "\eb_div\eb":
                        nome_da_linha = "/"  
                else:
                    nome_da_linha += sym

            if line > 3:
                plt.plot(valores_x,valores_y, label=nome_da_linha, marker=lines[line], color=colors_rgb[c])
            else:
                plt.plot(valores_x,valores_y, label=nome_da_linha, linestyle=lines[line], color=colors_rgb[c])
            line += 1
            c += 1
        plt.legend()
        nnt = nt.replace("<","")
        nnt = nnt.replace(">","")
        plt.savefig(path + "pagie_" + nnt + '.png')
        fig += 1
        plt.close('all')

def preprocess_data(path):
    data_dic = {}
    test_data_dic = {}
    for folder_name in os.listdir(path):
        if 'run' not in folder_name:
            continue
        # filter number of runs
        if int(folder_name.split("_")[1]) > RUNS:
            continue
        fp = open(path + folder_name + "/progress_report.csv","r") 
        while True:
            line = fp.readline()
            if not line:
                break
            l = line.split("\t")
            if len(l) == 4:
                gen, best, _ , _  = l
                test = "-1"
            else:
                gen, best, _ , _ , test = l

            # gen, best, _ , _ , test = line.split("\t")
            if int(gen) > GENERATIONS-1:
                continue
            gen = int(gen)
            gen = str(gen)
            if gen in data_dic:
                data_dic[gen].append(float(best.rstrip('\n')))
                test_data_dic[gen].append(float(test.rstrip('\n')))
            else:
                data_dic[gen] = [float(best.rstrip('\n'))]
                test_data_dic[gen] = [float(test.rstrip('\n'))]
        fp.close()

    return data_dic, test_data_dic

def process_data(path, dic):
    fp = open(path + "aggregated_data.txt", "w")
    g = []  # list of generations
    m = []  # list of maximum fitness
    a = []  # list of average of fitnesses
    d = []  # median
    s = []  # list of stf standard deviation

    for gen, fit in dic.items():
        g.append(gen)
        m.append(min(fit))
        a.append(np.mean(fit))
        s.append(np.std(fit))
        d.append(np.median(fit))
        string = gen + "," + str(min(fit)) + "," + str(np.mean(fit))  + "," + str(np.std(fit)) + "," + str(np.median(fit)) + "\n"
        fp.write(string)
    fp.close()

    df = pd.DataFrame([g,a,s,d]).transpose()

    df.columns=['gen','mean','std','median']
    df['gen'] = df['gen'].astype(int)
    df['mean'] = df['mean'].astype(float)
    df['std'] = df['std'].astype(float)
    df['median'] = df['median'].astype(float)
    df['mean-std'] = df['mean'] - df['std']
    df['mean+std'] = df['mean'] + df['std']

    # df_max = pd.DataFrame([g,m]).transpose()
    # df_max.columns=['gen','max']
    # df_max['gen'] = df_max['gen'].astype(int)
    # df_max['max'] = df_max['max'].astype(float)
    return df

def read_processed_data(file):
    fp = open(file, "r")

    g = []  # list of generations
    m = []  # list of best fitness
    a = []  # list of average of fitnesses
    s = []  # list of stf standard deviation
    d = []  # median
    for line in fp.readlines():
        l = line.split(",")
        if line == "":
            continue
        if int(l[0]) >= GENERATIONS:
            continue 
        g.append(l[0])
        m.append(l[1]) 
        a.append(l[2]) 
        s.append(l[3]) 
        d.append(l[4])   

    df = pd.DataFrame([g,a,s,d]).transpose()

    df.columns=['gen','mean','std','median']
    df['gen'] = df['gen'].astype(int)
    df['mean'] = df['mean'].astype(float)
    df['std'] = df['std'].astype(float)
    df['median'] = df['median'].astype(float)
    df['mean-std'] = df['mean'] - df['std']
    df['mean+std'] = df['mean'] + df['std']

    return df

def generate_plots(problem, methods_df):

    x = [i for i in range(0,GENERATIONS)]
    fig = plt.figure()

    lines = [':','-.','--','-','^']
    colors = [(0,0,0), (0.5,0.5,0.5), (0.25,0.25,0.25), (0.375,0.375,0.375), (0.625,0.625,0.625)]
    colors_rgb = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]

    line = 0
    c = 0
    for df, path in methods_df:
        if len(colors_rgb) == c:
            c = 0
        if len(lines) == line:
            line = 0

        if line > 3:
            plt.plot(x, df['mean'], color=colors_rgb[c], marker = lines[line], label = path)
        else:
            plt.plot(x, df['mean'], color=colors_rgb[c], linestyle = lines[line], label = path)

        c += 1
        line += 1

    plt.legend()
    plt.xlabel('GENERATIONS')
    # if not ARTICLE:
    #     plt.title(title)
    plt.grid(color='lightgray')
    plt.box(False)
    if problem == "pagie":
        plt.ylim(0.5,1.2)
        plt.ylabel('RRSE')
    elif "quad" in problem:
        plt.ylim(0, 1.5)
        plt.ylabel('RRSE')
    elif problem == "bostonhousing":
        plt.ylim(0.6,1.2)
        plt.ylabel('RRSE')
    elif problem == "5parity":
        plt.ylim(6,17)
        plt.ylabel('ERROR')
    elif problem == "11mult":
        plt.ylim(400,900)
        plt.ylabel('ERROR')
    elif problem == "ant":
        plt.ylim(0,70)
        plt.ylabel('ERROR')
    elif problem == "bio":
        plt.ylabel('RRSE')
        plt.ylim(0,50)
    elif problem == "ppb":
        plt.ylabel('RRSE')
        plt.ylim(0,50)

    # plt.show()
    plt.savefig("plots.png", bbox_inches='tight')
    plt.close()



def plot_performance(problem, *paths):
    methods_df = []
    for path in paths:
        data_dic, test_data_dic = preprocess_data(path)
        data_df = process_data(path, data_dic)
        # data_df_test = process_data(path, data_dic)
        methods_df.append([data_df, path])
    p = "/home/jessica/co-psge/sge/mut_level_compare/"
    for path in os.listdir(p):
        df = read_processed_data(p + path)
        methods_df.append([df, p + path])
    generate_plots(problem, methods_df)
    



if __name__ == "__main__":
    # plot_probabilities("/home/jessicamegane/Documents/hyb_rule_them_all/pagie/2.0/0.01/", "/home/jessicamegane/Documents/ge/grammars/regression.bnf")
    plot_performance("pagie","/home/jessica/co-psge/sge/mutation_level/prob_mut_0.5_gauss_sd_0.005/5.0/0.5/","/home/jessica/co-psge/sge/mutation_level/prob_mut_0.75_gauss_sd_0.01/5.0/0.5/", "/home/jessica/co-psge/sge/mutation_level/prob_mut_0.75_gauss_sd_0.005/5.0/0.5/", "/home/jessica/co-psge/sge/mutation_level/prob_mut_1.0_gauss_sd_0.01/5.0/0.5/", "/home/jessica/co-psge/sge/mutation_level/prob_mut_1.0_gauss_sd_0.005/5.0/0.5/")
    # plot_probabilities("/home/jessica/co-psge/sge/mutation_level/prob_mut_0.5_gauss_sd_0.005/5.0/0.5/","/home/jessica/co-psge/sge/grammars/regression.pybnf")