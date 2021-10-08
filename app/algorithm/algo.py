import pandas as pd
import numpy as np
import joblib
import os
wls = [685, 785, 830, 850, 915, 975]

ecm_path = 'app/algorithm/chromophore/chromophores_emulsion_extended.txt'

## 데이터로더
def data_loader(path, wls = wls):
    df = pd.read_csv(path,skiprows=0)
    df = df[df.columns[:19]]

    columns = ['time']
    col_names = []
    for wl in wls :
        for i in range(1,4):
            col_names.append(f'{wl}nm_d{i}')
    columns = columns + col_names
    df.columns = columns

    df = df.loc[~(df.drop(['time'], axis=1)==0).any(axis=1)]
    df.reset_index(drop=True, inplace=True)
    return df
## 노말라이져
def normalizer(df, wls=wls):
    temp = df[['time']]
    for i in range(6):
        wl = wls[i]
        d2d1 = df[f'{wl}nm_d2']/df[f'{wl}nm_d1']
        d2d1 = pd.DataFrame(d2d1, columns = [f'{wl}nm_20/10'])
        d3d1 = df[f'{wl}nm_d3']/df[f'{wl}nm_d1']
        d3d1 = pd.DataFrame(d3d1, columns = [f'{wl}nm_30/10'])
        temp = pd.concat([temp, d2d1, d3d1], axis=1)

    return temp

## 룩업 범위 체크
def lookup_check(df, wls=wls):
    min_val = np.array([7.228325755165096e-05, 9.293100436557776e-09]    )
    max_val = np.array([0.2539044458383133, 0.09758506545204636])

    warning = []
    for i in range(6):
        for j, d in enumerate([20,30]):
            _min = df.describe().loc['min', f'{wls[i]}nm_{d}/10']
            _min = min_val[j] < _min
            if not _min :
                wc = f'{wls[i]}nm_{d}/10 의 최소값이 lookup 범위 벗어남.'
                warning.append(wc)
            _max = df.describe().loc['max', f'{wls[i]}nm_{d}/10']
            _max = max_val[j] > _max
            if not _max :
                wc = f'{wls[i]}nm_{d}/10 의 최대값이 lookup 범위 벗어남.'
                warning.append(wc)
    
    if len(warning) != 0 :
        for w in warning :
            print(w)
        return warning
    else :
        print("전부 lookup 범위에 있음")

##  스케일러
def scaler(df):
    x_norm_std = [0.030929544517112276  # a20/a10
                       ,0.006655351538966291 # a30/a10
                       ]*6
    df.loc[:,df.columns[1:]] = df.loc[:,df.columns[1:]]/x_norm_std
    return df

def model_loader(path):
    return joblib.load(path)

def infer_optical_prop(model, df, wls=wls):
    df_mua = []
    df_mus = []
    for i in range(6):
        wl = wls[i]
        temp = df[[f'{wl}nm_20/10', f'{wl}nm_20/10']]
        uaus = model.predict(temp)

        df_mua.append(pd.DataFrame(uaus[:,0], columns=[f'mua{wl}nm'])  )
        df_mus.append(pd.DataFrame(uaus[:,1], columns=[f'mus{wl}nm'])  )
    df_mua = pd.concat(df_mua, axis=1)
    df_mua = pd.concat([df['time'], df_mua ], axis=1)
    df_mus = pd.concat(df_mus, axis=1)
    df_mus = pd.concat([df['time'], df_mus ], axis=1)

    return df_mua, df_mus

def infer_chrom_conc(mua, chroms, echo=1, ecm_path=ecm_path, wls=wls):
    ecm = pd.read_csv(ecm_path, sep='\t')
    ecm = ecm[ecm.columns[:5]]
    ecm.columns = ['lambda', 'hbo2', 'hb', 'water', 'fat']
    ecm.loc[len(ecm)] = ecm.loc[ecm['lambda'].isin([684,686]) ].mean()
    ecm.loc[len(ecm)] = ecm.loc[ecm['lambda'].isin([784,786]) ].mean()
    ecm.loc[len(ecm)] = ecm.loc[ecm['lambda'].isin([914,916]) ].mean()
    ecm.loc[len(ecm)] = ecm.loc[ecm['lambda'].isin([974,976]) ].mean()

    ecm = ecm.loc[ecm['lambda'].isin(wls)]
    ecm = ecm.sort_values(by='lambda').drop(['lambda'], axis=1)
    ecm = ecm.T
    ecm.columns = wls

    if chroms == 1:
        chroms_ = ['water', 'fat']
        wl_cons = wls
    elif chroms == 0:
        chroms_ = ['hbo2', 'hb']
        wl_cons = wls

    ecm_only = ecm.loc[chroms_, wl_cons]
    ecm_inv = np.linalg.pinv(ecm_only)
    mua_only = mua[[f'mua{wl}nm' for wl in wl_cons]]
    chrom_conc = np.matmul(mua_only.values, ecm_inv)

    if chroms == 1:
        chrom_conc = chrom_conc*100
        if echo ==1 :
            print('water, fat 추정.     단위 : %')
        npTodf1 = pd.DataFrame(chrom_conc,columns=['H2O','Lipid'])
        return npTodf1
    elif chroms == 0:
        chrom_conc = chrom_conc*1000
        if echo ==1 :
            print('HbO2, Hb 추정.     단위 : uM')
        npTodf2 = pd.DataFrame(chrom_conc,columns=['HbO2','HHb'])
        return npTodf2