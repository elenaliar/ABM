import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import seaborn as sns

def plot_index(Si, params, order, title=''):
    """
    Plot Sobol sensitivity indices.

    Args:
        Si (dict): Output from sobol.analyze (contains 'S1', 'S1_conf', 'S2', etc.).
        params (list): Parameter names.
        order (str): '1' for first-order, '2' for second-order, 'T' for total-order.
        title (str): Plot title.
    """
    plt.figure(figsize=(10, 6))
    
    if order == '2':
        # Second-order indices
        p = len(params)
        index_pairs = list(combinations(params, 2))
        indices = Si['S2'].reshape(p, p)[np.triu_indices(p, k=1)]
        errors = Si['S2_conf'].reshape(p, p)[np.triu_indices(p, k=1)]
        labels = [f"{a}, {b}" for a, b in index_pairs]
    elif order == '1':
        indices = Si['S1']
        errors = Si['S1_conf']
        labels = params
    elif order.upper() == 'T':
        indices = Si['ST']
        errors = Si['ST_conf']
        labels = params
    else:
        raise ValueError("Order must be '1', '2', or 'T'.")

    y_pos = np.arange(len(labels))
    plt.barh(y_pos, indices, xerr=errors, align='center', alpha=0.7, capsize=5, color = 'dodgerblue')
    plt.yticks(y_pos, labels)
    plt.xlabel('Sobol Index')
    plt.title(title)
    plt.axvline(0, color='black', linewidth=0.8)
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_second_order_heatmap(Si, params, title='Second-order Sobol Indices'):
    """
    Plot a heatmap of second-order Sobol sensitivity indices.

    Args:
        Si (dict): Sobol analysis output containing second-order indices.
        params (list): List of parameter names.
        title (str): Title for the heatmap.
    """
    p = len(params)
    S2 = np.array(Si['S2']).reshape((p, p))
    mask = np.tril(np.ones_like(S2, dtype=bool))  # mask lower triangle

    plt.figure(figsize=(8, 6))
    sns.heatmap(S2, 
                xticklabels=params, 
                yticklabels=params, 
                cmap='coolwarm', 
                mask=mask, 
                annot=True, 
                fmt=".2f", 
                cbar_kws={'label': 'Second-order Sobol Index'})
    plt.title(title)
    plt.tight_layout()
    plt.show()