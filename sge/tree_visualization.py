"""
Code from Francisco Miranda (Github @FMiranda97)
"""

import random
import numpy as np
import pandas as pd
import re

from sklearn.preprocessing import StandardScaler

colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', '#ffffff', '#000000']

colormap = {}


def process_prediction(string):
    final_index = string.index(')')
    if string[0] == '\'':
        final_index -= 1
    prediction = string[:final_index + 1]
    return final_index, {'id': str(random.randint(0, 999999999)), 'content': prediction, 'left_child': None, 'right_child': None}


def process_node(string):
    i = 0
    node = None
    while i < len(string):
        if string[i] == '(':
            increase, node = get_tree(string[i + 1:])
            i += increase + 1
        elif string[i] == ')':
            i += 1
            break
        else:
            i += 1
    return i, node


def process_condition(string):
    condition_start = string.index('(')
    condition_end = string.index('else')
    return condition_end + 4, string[condition_start + 1:condition_end - 2]


def get_tree(string):
    # check for recursion end
    if string.startswith('is_positive') or string.startswith('\'Has Hearing Loss') or string.startswith('\'No Hearing Loss'):
        return process_prediction(string)

    # search left side of if
    i, left_child = process_node(string)

    # process condition
    increase, content = process_condition(string[i:])
    i += increase

    # search right side of if
    increase, right_child = process_node(string[i:])
    i += increase
    # return tree
    return i, {'id': str(random.randint(0, 999999999)), 'content': content, 'left_child': left_child, 'right_child': right_child}


def print_tree(tree, depth=0):
    if tree is None:
        return
    print("\t" * depth + tree['content'])
    print_tree(tree['left_child'], depth=depth + 1)
    print_tree(tree['right_child'], depth=depth + 1)


def draw_tree(tree, file_name):
    import graphviz
    dot = graphviz.Digraph()
    add_nodes(tree, dot)
    add_edges(tree, dot)
    dot.render('tree_graphs/%s.gv' % file_name, view=False)


def add_edges(node, dot):
    if node is not None:
        if node['left_child'] is not None:
            dot.edge(node['id'], node['left_child']['id'])
        if node['right_child'] is not None:
            dot.edge(node['id'], node['right_child']['id'])
        add_edges(node['left_child'], dot)
        add_edges(node['right_child'], dot)


def add_nodes(node, dot):
    if node is not None:
        if node['left_child'] is None and node['right_child'] is None:
            if colormap.get(node['content']) is not None:
                dot.node(node['id'], node['content'], color=colormap[node['content']], style="filled")
            else:
                dot.node(node['id'], node['content'], fontcolor='white', color='black', style="filled")
        else:
            dot.node(node['id'], node['content'])
            add_nodes(node['left_child'], dot)
            add_nodes(node['right_child'], dot)


def embellish(node):
    if node is not None:
        embellish(node['left_child'])
        embellish(node['right_child'])
        if node['content'].startswith('is_positive'):
            node['content'] = 'Hearing Loss' if eval(node['content']) == 1 else 'No Hearing Loss'
        elif node['content'].startswith('\''):
            node['content'] = node['content'].replace('\'', '')
        else:
            condition = node['content'][node['content'].find('<') + 2:]
            expr_tree = get_expr_tree(node['content'][:node['content'].find('<')])
            if " " in get_expr_from_tree(expr_tree):
                node['content'] = '%s <= %.2f' % (get_expr_from_tree(expr_tree), float(condition))
            else:
                node['content'] = '%s <= %.2f' % (get_expr_from_tree(expr_tree), get_original_feature_values(get_expr_from_tree(expr_tree), condition))

        if node['left_child'] is not None and node['right_child'] is not None and node['left_child']['content'] == node['right_child']['content']:
            node['content'] = node['left_child']['content']
            node['left_child'] = None
            node['right_child'] = None


def get_original_feature_values(feature, value):
    df = pd.read_csv('resources/a4a_reduced_dataset.csv')
    X = df.drop('corrected_diagnosed_hl', axis=1).iloc[:, 1:]
    scaler = StandardScaler().fit(X[feature].to_numpy().reshape(-1, 1))
    return scaler.inverse_transform(np.array(value).reshape(-1, 1))[0][0]


def get_expr_tree(expression):
    left_child = None
    right_child = None

    op_end = expression.find('(')
    if op_end != -1:
        content = expression[:op_end]
        separator = find_argument_separator(expression[op_end + 1:-1]) + op_end + 1
        left_child = get_expr_tree(expression[op_end + 1:separator])
        right_child = get_expr_tree(expression[separator + 1:-1])
    else:
        content = expression
    return {'content': content, 'left_child': left_child, 'right_child': right_child}


def get_expr_from_tree(expr_tree) -> str:
    if 'add' in expr_tree['content']:
        return '(%s + %s)' % (get_expr_from_tree(expr_tree['left_child']), get_expr_from_tree(expr_tree['right_child']))
    elif 'sub' in expr_tree['content']:
        return '(%s - %s)' % (get_expr_from_tree(expr_tree['left_child']), get_expr_from_tree(expr_tree['right_child']))
    elif 'mul' in expr_tree['content']:
        return '(%s * %s)' % (get_expr_from_tree(expr_tree['left_child']), get_expr_from_tree(expr_tree['right_child']))
    elif 'div' in expr_tree['content']:
        return '(%s / %s)' % (get_expr_from_tree(expr_tree['left_child']), get_expr_from_tree(expr_tree['right_child']))
    else:
        return expr_tree['content']


def find_argument_separator(expression):
    open_par = closed_par = i = 0
    while not (expression[i] == ',' and open_par == closed_par):
        if expression[i] == '(':
            open_par += 1
        elif expression[i] == ')':
            closed_par += 1
        i += 1
    return i


def is_positive(x):
    return 1 if x > 0 else 0


def decision_tree_to_pdf(phenotype, filename, feature_names=None):
    if feature_names is None:
        df = pd.read_csv('resources/a4a_reduced_dataset.csv')
        feature_names = df.drop('corrected_diagnosed_hl', axis=1).iloc[:, 1:].columns.to_list()
    for i in range(60):
        phenotype = phenotype.replace('x[%d]' % i, feature_names[i])
    phenotype = rename_branches(phenotype)
    _, tree = get_tree(phenotype)
    build_colormap(tree)
    embellish(tree)
    draw_tree(tree, filename)


def build_colormap(tree):
    if tree['left_child'] is None and tree['right_child'] is None:
        for color in colors:
            if color not in colormap.values():
                colormap[tree['content'][1:-1]] = color
                break
    else:
        build_colormap(tree['left_child'])
        build_colormap(tree['right_child'])


def print_decision_tree(phenotype, feature_names=None):
    if feature_names is None:
        df = pd.read_csv('resources/a4a_reduced_dataset.csv')
        feature_names = df.drop('corrected_diagnosed_hl', axis=1).iloc[:, 1:].columns.to_list()
    for i in range(60):
        phenotype = phenotype.replace('x[%d]' % i, feature_names[i])
    _, tree = get_tree(phenotype)
    embellish(tree)
    print_tree(tree)
    print(tree)


def rename_branches(phenotype):
    matches = re.findall('is_positive\(-?\d.\d*\)', phenotype)
    negative = 0
    positive = 0
    for match in matches:
        if eval(match) > 0:
            phenotype = phenotype.replace(match, "'Has Hearing Loss - %d'" % positive)
            positive += 1
        else:
            phenotype = phenotype.replace(match, "'No Hearing Loss - %d'" % negative)
            negative += 1
    return phenotype


if __name__ == '__main__':
    phenotype = '(((is_positive(%f)) if (x[29]<=%f) else (is_positive(%f))) if (x[41]<=%f) else ((is_positive(%f)) if (x[18]<=%f) else (is_positive(%f)))) if (_add_(x[22],x[42])<=%f) else ((is_positive(%f)) if (x[22]<=%f) else ((is_positive(%f)) if (_add_(x[8],x[35])<=%f) else (is_positive(%f))))'
    weights = [-1.5643429491234837, 1.0763929716596317, 0.6365091050213127, 1.7404346465002463, -1.0993870061833073, -1.7000983283958695, -1.1839071047059837, -0.4120808030876395, 0.7050316179683684, -2.374523666089661, -0.432038803750338, -0.020403093216980306, 2.812322313332377]
    phenotype = phenotype % tuple(weights)

    # colormap = {'Has Hearing Loss - 0': '#636efa', 'Has Hearing Loss - 2': '#EF553B', 'No Hearing Loss - 0': '#00cc96', 'No Hearing Loss - 2': '#ab63fa', 'No Hearing Loss - 3': '#FFA15A'}
    analyseBranches = True

    if analyseBranches:
        phenotype = rename_branches(phenotype)

    decision_tree_to_pdf(phenotype, 'example')
    print_decision_tree(phenotype)
