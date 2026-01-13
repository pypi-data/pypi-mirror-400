import time, os, copy, datetime, math, random, warnings
import subprocess, sys
import numpy as np
import pandas as pd
from scipy import stats, signal

import matplotlib.pyplot as plt
from matplotlib import cm, colormaps
import matplotlib as mpl
from matplotlib.pyplot import figure
from matplotlib.patches import Rectangle
from sklearn import cluster, mixture
import sklearn.linear_model as lm
import sklearn.metrics as met

from importlib_resources import files

SCANVPY = True
try:
    import scanpy as sc
    import anndata
except ImportError:
    print('WARNING: scanpy not installed.')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scanpy"])
        import scanpy as sc
        import anndata
        print('INFO: scanpy was sucessfully installed.')
    except:
        print('WARNING: Cannot install scanpy.')
        SCANVPY = False

STATANNOT = True
try:
    # from statannot import add_stat_annotation
    from statannotations.Annotator import Annotator
except ImportError:
    print('WARNING: statannot not installed or not available. ')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "statannotations"])
        from statannotations.Annotator import Annotator
        print('INFO: statannotations was sucessfully installed.')
    except:
        print('WARNING: Cannot install statannotations.')
        STATANNOT = False

SEABORN = True
try:
    import seaborn as sns
except ImportError:
    print('WARNING: seaborn not installed or not available. ')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "seaborn"])
        import seaborn as sns
        print('INFO: seaborn was sucessfully installed.')
    except:
        print('WARNING: Cannot install seaborn.')
        SEABORN = False

try:
    import plotly.graph_objects as go
except ImportError:
    print('WARNING: plotly not installed.')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
        import plotly.graph_objects as go
        print('INFO: plotly was sucessfully installed.')
    except:
        print('WARNING: Cannot install plotly.')
    

def get_sample_to_group_dict( samples, conditions ):
    
    samples = np.array(samples)
    conditions = np.array(conditions)
    
    slst = list(set(list(samples)))
    slst.sort()
    glst = []
    for s in slst:
        b = samples == s
        g = conditions[b][0]
        glst.append(g)
        
    dct = dict(zip(slst, glst))
    return dct


def get_sample_to_group_map( samples, conditions ):
    return get_sample_to_group_dict( samples, conditions )


# df_cnt, df_pct= get_population( adata_s.obs['sid'], 
#                                 adata_s.obs['minor'], sort_by = [] )
def get_population( pids, cts, sort_by = [] ):
    
    pid_lst = list(set(list(pids)))
    pid_lst.sort()
    celltype_lst = list(set(list(cts)))
    celltype_lst.sort()

    df_celltype_cnt = pd.DataFrame(index = pid_lst, columns = celltype_lst)
    df_celltype_cnt.loc[:,:] = 0

    for pid in pid_lst:
        b = np.array(pids) == pid
        ct_sel = np.array(cts)[b]

        for ct in celltype_lst:
            bx = ct_sel == ct
            df_celltype_cnt.loc[pid, ct] = np.sum(bx)

    df_celltype_pct = (df_celltype_cnt.div(df_celltype_cnt.sum(axis = 1), axis = 0)*100).astype(float)
    
    if len(sort_by) > 0:
        df_celltype_pct.sort_values(by = sort_by, inplace = True)

    return df_celltype_cnt, df_celltype_pct


def get_gene_expression( adata, items_to_plot = [], 
                         group_col = 'sample' ): 

    sample_col = group_col
    slst = adata.obs[sample_col].unique().tolist()
    slst.sort()

    if items_to_plot is None:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    elif len(items_to_plot) == 0:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    else:
        Xs = adata[:, items_to_plot].to_df()
        df = pd.DataFrame(index = slst, columns = items_to_plot)
        
    for s in slst:
        b = adata.obs[sample_col] == s
        mns = (Xs.loc[b,:] > 0).mean(axis = 0)
        df.loc[s,:] = list(mns)
    
    df = df.astype(float)
    return df


def cci_get_means( cci_df_dct, cci_idx_lst = None, 
                   cells = [], genes = [], pval_cutoff = 0.05 ):

    if cci_idx_lst is None:
        ## get coomon cci index
        for j, key in enumerate(cci_df_dct.keys()):
            b = cci_df_dct[key]['pval'] <= pval_cutoff
            if len(cells) > 0:
                b = b & (cci_df_dct[key]['cell_A'].isin(cells) | cci_df_dct[key]['cell_B'].isin(cells))
            if len(genes) > 0:
                b = b & (cci_df_dct[key]['gene_A'].isin(genes) | cci_df_dct[key]['gene_B'].isin(genes))
                         
            if j == 0:
                idx_union = list(cci_df_dct[key].index.values[b])
            else:
                idx_union = list(set(idx_union).union(list(cci_df_dct[key].index.values[b])))
        cci_idx_lst = idx_union
    
    tlst = cci_idx_lst
    slst = list(cci_df_dct.keys())
    
    df = pd.DataFrame(index = slst, columns = tlst)
    df.loc[:,:] = None
    
    for s in slst:
        dfv = cci_df_dct[s]
        idx = list(dfv.index.values)
        clst = list(set(tlst).intersection(idx))
        df.loc[s, clst] = dfv.loc[clst, 'mean'].astype(float)   
                
    df = df.astype(float)
    return df
    

def get_cci_means( cci_df_dct, cci_idx_lst = None, 
                   cells = [], genes = [], pval_cutoff = 0.05 ):

    return cci_get_means( cci_df_dct, cci_idx_lst, 
                          cells, genes, pval_cutoff)


def cci_get_diff_interactions( df_cci_sample, sample_group_map, 
                               ref_group = None, pval_cutoff = 0.05 ):
    df = df_cci_sample
    group = []
    for k in list(df.index.values):
        group.append( sample_group_map[k] )
    glst = list(set(group))
    glst.sort()
    group = pd.Series(group, index = df.index)
    
    df_res = pd.DataFrame(index = list(df.columns.values))
    
    if ref_group is None:
        for i, g1 in enumerate(glst):
            
            b_r = (group == g1) # & (~df[item].isnull())
            n_r = np.sum(b_r)
            if n_r > 0:
                for j, g2 in enumerate(glst):
                    if i > j:
                        b_o = (group == g2) # & (~df[item].isnull())
                        n_o = np.sum(b_o)
                        if n_o > 0:
                            res = stats.ttest_ind(df.loc[b_r,:], 
                                                  df.loc[b_o,:], axis=0, 
                                                  equal_var=False, # (n_r == n_o), 
                                                  nan_policy='omit', # 'propagate', 
                                                  permutations=None, 
                                                  random_state=None, 
                                                  alternative='two-sided', 
                                                  trim=0)
                            df_res.loc[:, '%s_vs_%s' % (g1, g2)] = res.pvalue
            
    elif ref_group in glst:
    
        b_ref = group == ref_group
        for g in glst:
            if g != ref_group:
                b_r = (group == g) # & (~df[item].isnull()) 
                n_r = np.sum(b_r)
    
                b_o = b_ref # & (~df[item].isnull())
                n_o = np.sum(b_o)
    
                res = stats.ttest_ind(df.loc[b_r,:], 
                                      df.loc[b_o,:], axis=0, 
                                      equal_var=False, # (n_r == n_o), 
                                      nan_policy='omit', # 'propagate', 
                                      permutations=None, 
                                      random_state=None, 
                                      alternative='two-sided', 
                                      trim=0)
                df_res.loc[:, '%s_vs_%s' % (g, ref_group)] = res.pvalue
    
    b = df_res.isnull()
    df_res[b] = 1
    
    pv_min = df_res.min(axis = 1)
    df_res = df_res.loc[pv_min <= pval_cutoff,:]

    df_res['ss'] = (df_res <= pval_cutoff).sum(axis = 1)
    df_res['pp'] = -np.log10(df_res.prod(axis = 1))
    df_res.sort_values(by = ['ss', 'pp'], ascending = False, inplace = True)
       
    return df_res.iloc[:,:-2]


def test_group_diff( df_sample_by_items, sample_group_map, 
                     ref_group = None, pval_cutoff = 0.05 ):
    
    return cci_get_diff_interactions( df_sample_by_items, sample_group_map, 
                               ref_group, pval_cutoff )


### Remove common CCI
def cci_remove_common( df_dct ):
    
    idx_dct = {}
    idxo_dct = {}
    celltype_lst = []

    for j, g in enumerate(df_dct.keys()):
        idx_dct[g] = list(df_dct[g].index.values)
        if j == 0:
            idx_c = idx_dct[g]
        else:
            idx_c = list(set(idx_c).intersection(idx_dct[g]))

        ctA = list(df_dct[g]['cell_A'].unique())
        ctB = list(df_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    for g in df_dct.keys():
        idxo_dct[g] = list(set(idx_dct[g]) - set(idx_c))

    dfs_dct = {}
    for g in df_dct.keys():
        dfs_dct[g] = df_dct[g].loc[idxo_dct[g],:]

    celltype_lst.sort()
    # len(idx_c), celltype_lst
    
    return dfs_dct


## Get matrices summarizing the num CCIs for each condition
def cci_get_ni_mat( df_dct, remove_common = True ):
    
    if remove_common: 
        dfs_dct = cci_remove_common( df_dct )
    else:
        dfs_dct = df_dct
        
    celltype_lst = []
    for j, g in enumerate(dfs_dct.keys()):
        ctA = list(dfs_dct[g]['cell_A'].unique())
        ctB = list(dfs_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    celltype_lst.sort()
    
    df_lst = {} 
    for g in dfs_dct.keys():
        b = dfs_dct[g]['cell_A'].isin(celltype_lst) & (dfs_dct[g]['cell_B'].isin(celltype_lst))
        dfs = dfs_dct[g].loc[b,:]
        df = pd.DataFrame(index = celltype_lst, columns = celltype_lst)
        df.loc[:] = 0
        for a, b in zip(dfs['cell_A'], dfs['cell_B']):
            df.loc[a,b] += 1

        df_lst[g] = df
                
    return df_lst

def get_cci_ni_mat( df_dct, remove_common = True ):
    return cci_get_ni_mat( df_dct, remove_common )


def cci_get_df_to_plot( df_dct, pval_cutoff = 0.01, mean_cutoff = 1, target_cells = None ):

    idx_lst_all = []
    for k in df_dct.keys():
        b = df_dct[k]['pval'] <= pval_cutoff
        b = b & df_dct[k]['mean'] >= mean_cutoff
        if target_cells is not None:
            if isinstance(target_cells, list):
                b1 = df_dct[k]['cell_A'].isin(target_cells)
                b2 = df_dct[k]['cell_B'].isin(target_cells)
                b = b & (b1 | b2)
                
        idx_lst_all = idx_lst_all + list(df_dct[k].index.values[b])

    idx_lst_all = list(set(idx_lst_all))
    display('Union of Interactions: %i' % len(idx_lst_all))    

    df_dct_to_plot = {}
    for k in df_dct.keys():
        df = df_dct[k]
        dfv = pd.DataFrame(index = idx_lst_all, columns = df.columns)
        dfv['mean'] = 0
        dfv['pval'] = 1

        idxt = list(set(idx_lst_all).intersection(list(df.index.values)))
        cols = list(df.columns.values)
        cols.remove('mean')
        cols.remove('pval')
        dfv.loc[idxt, cols] = df.loc[idxt, cols]
        dfv.loc[idxt, 'mean'] = df.loc[idxt, 'mean']
        dfv.loc[idxt, 'pval'] = df.loc[idxt, 'pval']

        gp, cp, ga, gb, ca, cb = [], [], [], [], [], []
        for s in list(dfv.index.values):
            gpt, cpt, gat, gbt, cat, cbt = cpdb_get_gp_n_cp(s)

            gp = gp + [gpt]
            cp = cp + [cpt]
            ga = ga + [gat]
            gb = gb + [gbt]
            ca = ca + [cat]
            cb = cb + [cbt]

        dfv['gene_pair'] = gp
        dfv['cell_pair'] = cp
        dfv['gene_A'] = ga
        dfv['gene_B'] = gb
        dfv['cell_A'] = ca
        dfv['cell_B'] = cb
        
        df_dct_to_plot[k] = dfv
        # print(dfv.shape)
        
    return df_dct_to_plot


def get_markers_from_deg( df_dct, ref_col = 'score',  N_mkrs = 30, 
                          nz_pct_test_min = 0.5, nz_pct_ref_max = 0.1,
                          rem_common = True ):
## Get markers from DEG results

    df_deg = df_dct
    mkr_dict = {}
    b = True
    for key in df_deg.keys():
        if ref_col not in list(df_deg[key].columns.values):
            b = False
            break
    
    if not b:
        print('ERROR: %s not found in column name of DEG results.' % ref_col)
        return None

    for key in df_deg.keys():

        g = key.split('_')[0]
        df = df_deg[key].copy(deep = True)
        b1 = df['nz_pct_test'] >= nz_pct_test_min
        b2 = df['nz_pct_ref'] <= nz_pct_ref_max
        df = df.loc[b1&b2, : ]
        df = df.sort_values([ref_col], ascending = False)

        mkr_dict[g] = list(df.iloc[:N_mkrs].index.values)

    ## Remove common markers
    if rem_common:
        lst = list(mkr_dict.keys())
        cmm = []
        for j, k1 in enumerate(lst):
            for i, k2 in enumerate(lst):
                if (k1 != k2) & (j < i):
                    lc = list(set(mkr_dict[k1]).intersection(mkr_dict[k2]))
                    cmm = cmm + lc
        cmm = list(set(cmm))

        for j, k in enumerate(lst):
            mkr_dict[k] = list(set(mkr_dict[k]) - set(cmm))

    return mkr_dict


def filter_gsa_result( dct, neg_log_p_cutoff ):
    
    dct_t = {}
    for kk in dct.keys():
        dft = dct[kk]
        b = dft['-log(p-val)'] >= neg_log_p_cutoff
        dct_t[kk] = dft.loc[b,:]
    return dct_t


def get_abbreviations( ):

    ### celltype 이름을 짧은 이름으로 대치
    rename_dict = {}
    
    lst = ['Epithelial cell', 'T cell', 'Smooth muscle cell',
           'Fibroblast', 'Myeloid cell', 'Endothelial cell', 'B cell']
    lst2 = ['Epi', 'T cell', 'SMC', 'Fib', 'Myeloid', 'Endo', 'B cell']
    ## 이름 변경을 위한 dictionalry 생성
    rename_dict['celltype_major'] = dict(zip(lst, lst2))
    
    ## minor type에 대해 동일한 과정으로 이름 변경
    lst = ['Epithelial cell', 'T cell CD4+', 'T cell CD8+', 'Smooth muscle cell',
           'Fibroblast', 'ILC', 'Dendritic cell', 'Monocyte', 'Endothelial cell',
           'Macrophage', 'B cell', 'Plasma cell', 'NK cell',
           'Aneuploid Epithelial cell', 'Diploid Epithelial cell']
    lst2 = ['Epi', 'T CD4+', 'T CD8+', 'SMC', 'Fib', 'ILC', 'DC', 'Mono',
            'Endo', 'Mac', 'B cell', 'Plasma', 'NK', 'Epi (Aneup)', 'Epi (Dip)']
    rename_dict['celltype_minor'] = dict(zip(lst, lst2))
    
    ## subset에 대해 동일한 과정으로 이름 변경
    lst = ['B cell (Breg)', 'B cell (Follicular)', 'B cell (MZ)', 'B cell(Memory)',
           'DC (Classical)', 'DC (Inflammatory)', 'DC (Plasmacytoid)', 'Monocyte',
           'Endothelial cell', 'Epithelial cell', 'Fibroblast',
           'ILC1', 'ILC2', 'ILC3 (NCR+)', 'ILC3 (NCR-)', 'ILCreg', 'LTI',
           'Macrophage (M1)', 'Macrophage (M2A)', 'Macrophage (M2B)', 'Macrophage (M2C)', 'Macrophage (M2D)',
           'NK cell', 'Plasma cell', 'Smooth muscle cell',
           'T cell (Cytotoxic)', 'T cell (Naive)', 'T cell (Tfh)', 'T cell (Th1)',
           'T cell (Th17)', 'T cell (Th2)', 'T cell (Th22)', 'T cell (Th9)',
           'T cell (Treg)', 'MDSC (Granulocytic)', 'MDSC (Monocytic)',
           'Endothelial tip cell', 'Lymphatic Endothelial cell', 'Luminal epithelial cell', 'Mammary epithelial cell' ]
    lst2 = ['Breg', 'Bf', 'BMZ', 'Bmem', 'cDC', 'iDC', 'pDC', 'Mono', 'Endo',
            'Epi', 'Fib', 'ILC1', 'ILC2', 'ILC3(+)', 'ILC3(-)', 'ILCreg', 'LTI',
            'Mac_M1', 'Mac_M2a', 'Mac_M2b', 'Mac_M2c', 'Mac_M2d', 'NK', 'Plasma',
            'SMC', 'T_Cyto', 'T_Naive', 'Tfh', 'Th1', 'Th17', 'Th2', 'Th22', 'Th9',
            'Treg', 'MDSC_G', 'MDSC_M', 'Endo tip', 'Endo Lymp', 'Epi lum', 'Epi mam']
    rename_dict['celltype_subset'] = dict(zip(lst, lst2))
    
    return rename_dict


def split_text( s, N_max = 20 ):
    
    if len(s) > N_max:
        positions = [i for i, c in enumerate(s) if c == ' ']
        positions.append(len(s) - 1)
        pcnt = 0
        ps = []
        pc = 0
        for j, p in enumerate(positions):
            if (j > 0) & ((p - pc) > N_max):
                ps.append(positions[j-1]+1)
                pc = positions[j-1]+1

        if len(ps) > 0:
            s2 = s
            for p in reversed(ps):
                s2 = s2[:p] + '\n' + s2[p:]
            return s2
        else:
            return s
    else:
        return s


def evaluate_performance(y, y_pred, labels = ['Tumor', 'Normal'] ):

    acc = np.sum(y == y_pred)/len(y)
    # print('Acc: %4.2f ' % acc)
    perf = {}
    perf['Accuracy'] = np.round(acc,3)
    perf['F1'] = 0
    f1_all = []
    nc = []
    for t in labels:
        b1 = y == t
        b2 = y_pred == t
        bc = b1 & b2
        prec = np.sum(bc)/np.sum(b2)
        recall = np.sum(bc)/np.sum(b1)
        bd = (~b1) & b2
        fpr = np.sum(bd)/np.sum(~b1)
        f1 = 2*prec*recall/(prec + recall)
        perf['F1 (%s)' %t] = np.round(f1,3)
        perf['Precision (%s)' %t] = np.round(prec,3)
        perf['Recall (%s)' %t] = np.round(recall,3)
        perf['FPR (%s)' %t] = np.round(fpr,3)
        f1_all.append(f1)
        nc.append(np.sum(b1))
    perf['F1'] = np.round(np.sum(np.array(f1_all)*np.array(nc))/np.sum(nc), 3)
    
    return perf


def compute_sample_div_index( adata, sample_col = 'sample',
                              cluster_col = 'cnv_cluster',
                              tumor_dec = 'ploidy_dec',
                              ref_ind_col = 'cnv_ref_ind',
                              sdi_col = 'sample_diversity_index',
                              tumor_name = 'Aneuploid'):

    slst = adata.obs[sample_col].unique().tolist()
    clust_lst = adata.obs[cluster_col].unique().tolist()
    clust_lst.sort()
    
    df = pd.DataFrame( columns = ['Tumor_pct', 'N_samples', 'sample_diversity_index'], 
                       index = clust_lst )
    for c in clust_lst:
        b = adata.obs[cluster_col] == str(c)
        pcnt = adata.obs.loc[b, sample_col].value_counts()
        pcnt = pcnt/np.sum(pcnt)
        pcnt = pcnt[pcnt > 0]
        H = np.sum( -pcnt*np.log2(pcnt) )    
        pt = int( 100*(adata.obs.loc[b, tumor_dec] == tumor_name).sum()/np.sum(b) )
        pt_ref = int( 100*(adata.obs.loc[b, ref_ind_col]).sum()/np.sum(b) )
        Ns = np.sum(pcnt > 0)
        # print('%2i: p_t: %i, n_s: %i -> H = %4.2f' % (c, pt, np.sum(pcnt > 0), 2**H) )
    
        df.loc[c, 'Tumor_pct'] = pt
        df.loc[c, 'Ref_pct'] = pt_ref
        df.loc[c, 'N_samples'] = Ns
        df.loc[c, 'sample_diversity_index'] = H
    
    df['Tumor'] = df['Tumor_pct'] >= 50

    adata.obs[sdi_col] = 0
    for c in df.index.values.tolist():
        b = adata.obs[cluster_col] == str(c)
        adata.obs.loc[b, sdi_col] = df.loc[c, 'sample_diversity_index'].round()
    adata.obs[sdi_col] = adata.obs[sdi_col].astype(str)
    
    return df


def get_axes( axes, nr, nc, j ):
    if nr > 1:
        jr = int(np.floor(j/nc))
        jc = j%nc
        ax = axes[jr][jc]
    else:
        ax = axes[j]
    return ax


def _get_value_info(value, key_name=None, is_top_level_anndata_component=False, 
                    level_of_value=None, max_depth = 3, n_to_show = 3, limited_keys=None):
    """Helper to format the value's type/shape/info for printing."""
    info_str = f"({type(value).__name__})"

    if key_name and key_name in limited_keys:
        return "(dict) --"

    if isinstance(value, pd.DataFrame):
        # For top-level AnnData components like obs/var, show full columns
        if True: # is_top_level_anndata_component:
            if len(value.columns.tolist()) > n_to_show:
                lst = value.columns.tolist()[:n_to_show]
                lst.append('...')
                info_str = f"DataFrame {value.shape}, cols=[{', '.join(lst)} ])"
            else:
                info_str = f"DataFrame {value.shape}, cols={value.columns.tolist()})"
        else:
            info_str = f"DataFrame (shape={value.shape}, {len(value.columns)} cols)"
    elif hasattr(value, 'shape') and hasattr(value, 'dtype'):
        if len(value.shape) == 0:
            info_str = f"{value}"
        elif (len(value.shape) == 1) and (value.shape[0] < 5):
            info_str = f"{value}"
        else:
            info_str = f"array (shape={value.shape}, dtype={value.dtype})"
    elif isinstance(value, dict):
        info_str = "(dict)"
        # Check if recursion for this dict will be stopped at the next level
        if level_of_value is not None and level_of_value >= max_depth:
            keys_to_show = list(value.keys())
            if keys_to_show:
                if len(keys_to_show) > n_to_show: # Limit display for very long key lists
                    info_str += f" Keys=[{', '.join(map(str, keys_to_show[:n_to_show]))}, ... ]" # (Max depth reached)"
                    # info_str += f" Keys: [{', '.join(map(str, keys_to_show))}]" # (Max depth reached)"
                else:
                    info_str += f" Keys=[{', '.join(map(str, keys_to_show))}]" # (Max depth reached)"
            else:
                info_str += " (empty dictionary at max depth)"
    elif isinstance(value, str):
        if len(value) < 80: # Display short strings directly
            info_str = f"'{value}'"
        else:
            info_str = "(str)"
    elif isinstance(value, (int, float, bool)):
        info_str = str(value)
    elif value is None:
        info_str = "None"
    
    return info_str

def _display_dict_or_dataframe_recursive(current_obj, current_depth, parent_prefix, 
                                         max_depth = 3, n_to_show = 3, limited_keys = None ):
    # The max_depth check here is now primarily for stopping further recursion
    # The 'Max depth reached' message is handled by _get_value_info for dicts.
    if current_depth >= max_depth:
        return # Stop further recursion
    
    if isinstance(current_obj, dict) or hasattr(current_obj, 'keys'):
        if not current_obj:
            print(f"{parent_prefix}└── (empty)")
            return
        
        keys = list(current_obj.keys())
        max_key_len = max(len(str(k)) for k in keys) if keys else 0

        for i, key in enumerate(keys):
            is_last_item = (i == len(keys) - 1)
            line_connector = "└── " if is_last_item else "├── "
            child_sub_prefix = "     " if is_last_item else "│    "

            value = current_obj[key]
            # Pass the level for this value (which is current_depth + 1) to _get_value_info
            value_info = _get_value_info(value, key_name=key, level_of_value=current_depth + 1, 
                                         max_depth = max_depth, n_to_show = n_to_show, limited_keys = limited_keys)
            
            key_display = str(key).ljust(max_key_len) if max_key_len > 0 else str(key)
            print(f"{parent_prefix}{line_connector}{key_display}: {value_info}")

            # Only recurse if the current_depth + 1 is less than max_depth AND not in limited_keys
            if current_depth + 1 < max_depth and key not in limited_keys:
                if isinstance(value, dict) or isinstance(value, pd.DataFrame):
                    show_anndata_tree(value, max_depth=max_depth, limited_keys=limited_keys,
                                     _current_depth=current_depth + 1, _parent_prefix=parent_prefix + child_sub_prefix,
                                     n_to_show = n_to_show )
            # If it's a DataFrame, even if limited, display its columns if not already in info
            elif isinstance(value, pd.DataFrame):
                if "columns=" not in value_info and hasattr(value, 'columns'):
                    # print(f"{parent_prefix}{child_sub_prefix}└─ Columns: {', '.join(value.columns.tolist())}")
                    pass

    # No need for explicit DataFrame handling here, _get_value_info covers it.
        
def show_anndata_tree(obj, max_depth = 3, n_to_show = 3, limited_keys = None, _current_depth = 0, _parent_prefix = ""):
    """
    Prints a tree-like structure of an AnnData object or its components (dict, DataFrame),
    detailing their main components, with recursive exploration of nested
    dictionaries up to a specified depth. Recursion is limited for keys
    specified in `limited_keys`.

    Args:
        obj: The AnnData object, dictionary, or pandas DataFrame to print.
        max_depth (int): The maximum depth to recurse into nested dictionaries.
        limited_keys (list): A list of keys whose dictionary values should not be recursed into.
        _current_depth (int): Internal parameter for tracking current recursion depth.
        _parent_prefix (str): Internal parameter for tracking indentation in tree structure.
    """

    if limited_keys is None:
        # Default keys to limit recursion for very large nested dicts/dataframes
        limited_keys = [
            'gene_to_band_map', 'Celltype_marker_DB', 'Pathways_DB', 'cnv',
            'DEG_grouping_vars', 'DEG_stat', 'DEG_vs_ref_stat', 'run summary',
            # 'CCI', 'CCI_sample', 'DEG', 'DEG_vs_ref', 'GSA_down', 'GSA_up',
            # 'GSA_vs_ref_down', 'GSA_vs_ref_up', 'GSEA', 'GSEA_vs_ref',
            'log', 'inferploidy_summary', 'cnv_neighbors_info', 'HiCAT_summary', 
            'lut_sample_to_cond', 'analysis_parameters'
        ]

    # --- Main function logic ---

    # If the initial object is an AnnData object
    if _current_depth == 0 and isinstance(obj, anndata.AnnData):
        print(f"AnnData object with n_obs × n_vars = {obj.n_obs} × {obj.n_vars}")

        # List of main AnnData attributes to display
        anndata_components = {
            "X": obj.X,
            "obs": obj.obs,
            "var": obj.var,
            "obsm": obj.obsm,
            "obsp": obj.obsp,
            "varm": obj.varm,
            "varp": obj.varp,
            "uns": obj.uns
        }

        component_keys = list(anndata_components.keys())
        for i, comp_key in enumerate(component_keys):
            is_last_comp = (i == len(component_keys) - 1)
            comp_connector = "└── " if is_last_comp else "├── "
            comp_sub_prefix = "     " if is_last_comp else "│    "

            comp_value = anndata_components[comp_key]
            # Pass level_of_value=1 to _get_value_info for top-level AnnData components
            comp_info = _get_value_info(comp_value, key_name=comp_key, is_top_level_anndata_component=True, 
                                        level_of_value=1, max_depth = max_depth, n_to_show = n_to_show, limited_keys = limited_keys)
            
            print(f"{_parent_prefix}{comp_connector}{comp_key}: {comp_info}")

            # Recurse into complex components (dicts, DataFrames from obsm/obsp) if not at max_depth
            if comp_key in ["uns", "obsm", "obsp", "varm", "varp"]:
                # Only recurse if current_depth + 1 is less than max_depth
                if _current_depth + 1 < max_depth:
                    _display_dict_or_dataframe_recursive(comp_value, _current_depth + 1, _parent_prefix + comp_sub_prefix, 
                                                         max_depth = max_depth, n_to_show = n_to_show, limited_keys = limited_keys)
            # For obs/var (DataFrames), columns are already in comp_info, so no further action needed.

    # Handle dictionary (top-level or recursive)
    elif isinstance(obj, dict):
        if _current_depth == 0: # If called directly with a dict
            print("Dictionary Structure (top-level):")
        _display_dict_or_dataframe_recursive(obj, _current_depth, _parent_prefix, 
                                             max_depth = max_depth, n_to_show = n_to_show, limited_keys = limited_keys)

    # Handle DataFrame (top-level or recursive)
    elif isinstance(obj, pd.DataFrame):
        if _current_depth == 0: # If called directly with a DataFrame
            if len(obj.columns.tolist()) > 3:
                lst = obj.columns.tolist()[:3]
                lst.append('...')
                print(f"DataFrame Structure (top-level): shape={obj.shape}, columns={lst}")
            else:
                print(f"DataFrame Structure (top-level): shape={obj.shape}, columns={obj.columns.tolist()}")
            pass
        # Otherwise, its info is handled by the parent's _get_value_info.

    # Handle other types if called directly (e.g., array, string, int)
    elif _current_depth == 0:
        print(f"Object Type: {type(obj).__name__}")
        print(f"Value Info: {_get_value_info(obj, max_depth = max_depth, n_to_show = n_to_show, limited_keys = limited_keys)}")

    return
    
show_tree = show_anndata_tree    