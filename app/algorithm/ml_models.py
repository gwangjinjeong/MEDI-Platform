import glob
from app.algorithm import algo
import os
import pandas as pd
def knn(fname):
    cwd = os.getcwd() 
    model_path = '/app/algorithm/model/knn_6.ml'
    data_path = '/app/algorithm/data/'

    print(cwd+data_path+'raw'+fname+'.csv')
    temp = algo.data_loader(cwd+data_path+'raw_'+fname+'.csv')    # 데이터 불러오기
    temp = algo.normalizer(temp)    # 노말라이제이션  A20/A10, A30/A10
    algo.lookup_check(temp)    # 룩업 범위 벗어나면 경고해줌.
    temp = algo.scaler(temp)    # 스케일링. 학습데이터의 표준편차로 나누어줌

    model = algo.model_loader(cwd+model_path) # 모델 불러오기. 학습된 sklearn의 knn모델을 불러옴.

    mua, mus = algo.infer_optical_prop(model, temp) # mua, mu's 추론

    # echo가 1이면 추정할 chromophores의 이름과 출력 단위를 보여줌.
    hbo2_hb = algo.infer_chrom_conc(mua, chroms=0, echo=1) # chroms=0,  HbO2, Hb
    water_fat = algo.infer_chrom_conc(mua, chroms=1, echo=1) # chroms=1, H2O, Fat
    water_fat['Water'] = water_fat['H2O'] / (water_fat['H2O'] + water_fat['Lipid'])*100
    water_fat['Fat'] = water_fat['Lipid'] / (water_fat['H2O'] + water_fat['Lipid'])*100
    # 추정된 값 분석.
    hemo_mean = hbo2_hb.mean(axis=0)
    hemo_std = hbo2_hb.std(axis=0)

    wf_mean = water_fat.mean(axis=0)
    wf_std = water_fat.std(axis=0)
    wf_sum = wf_mean.sum()
    w_frac = (wf_mean[0] / wf_sum)*100
    f_frac = (wf_mean[1] / wf_sum)*100
    df_summary = pd.concat([mua, mus.iloc[:,1:],hbo2_hb,water_fat.loc[:,['Water','Fat']]], axis=1) # column bind
    print(df_summary)
    return df_summary