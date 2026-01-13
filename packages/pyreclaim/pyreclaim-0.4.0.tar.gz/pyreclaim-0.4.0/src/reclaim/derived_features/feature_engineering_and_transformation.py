import pandas as pd
import numpy as np

def engineer_and_transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer and transform features in reservoir/catchment dataset.

    Features are first engineered in raw space (linear), then log-transformations
    are applied in a single pass to avoid double-logging.

    Log-transformed columns are prefixed with ``log_`` to clearly indicate their state.

    Required input columns (abbreviations):
        - CA, DCA, OBC, HGT, RA, RP, FL
        - SA_mean, SA_mean_clip, SA_std, SA_kurt
        - PAI, MAI, MAO, I_std, O_std, MAR
        - OEY, BY, VGF, VLF
        - Land cover: LCAS, LCC, LCG, LCT, LCS, LCHV, LCM, LCSV, LCBS, LCSG, LCWB
        - COAR, SAND, NSSC2_mean
    """
    
    # Ensure required columns exist
    required_cols = ['CA', 'DCA', 'OBC', 'HGT', 'RA', 'RP', 'FL',
                     'SA_mean', 'SA_mean_clip', 'SA_std', 'SA_kurt',
                     'PAI', 'MAI', 'MAO', 'I_std', 'O_std', 'MAR',
                     'OEY', 'BY', 'VGF', 'VLF',
                     'LCAS','LCC','LCG','LCT','LCS','LCHV','LCM','LCSV','LCBS','LCSG','LCWB',
                     'COAR','SAND','NSSC2_mean']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # -------------------------
    # ENGINEER RAW FEATURES
    # -------------------------
    inflow_cap_ratio = (df['MAI'] * 3600 * 24 * 365.25 / 1e6) / df['OBC']
    
    feature_dict = {
        "AGE": df["OEY"] - df["BY"],
        "ROBC": df["OBC"] / df["CA"],
        "NVGF": df["VGF"] - df["VLF"],
        "GC": df["RA"] / (df["RP"]**2),
        "rain_per_area": np.where(df["CA"]!=0, df["MAR"]/df["CA"], df["MAR"]),
        "R_tree_bare": np.where(df["LCBS"]!=0, df["LCT"]/df["LCBS"], df["LCT"]),
        "R_shrub_bare": np.where(df["LCBS"]!=0, df["LCS"]/df["LCBS"], df["LCS"]),
        "R_coarse_sand": df["COAR"]/df["SAND"],
        "RT": df["OBC"] * 1e6 / (df["MAI"] * 3600 * 24 * 365.25),
        "TE": np.exp(-0.0079 * inflow_cap_ratio) * 100,
        "ECLR": np.exp(-0.0079 * inflow_cap_ratio) * 100 * df["NSSC2_mean"] * inflow_cap_ratio,
        "ESR": np.exp(-0.0079 * inflow_cap_ratio) * 100 * df["NSSC2_mean"] * inflow_cap_ratio * df["OBC"] / 100,
        "rel_SA_mean_clip": df["SA_mean_clip"] / df["RA"],
        "R_SA_cap": df["SA_mean_clip"] / df["OBC"],
        "SIN": df["MAI"] * df["NSSC2_mean"],
        "SOUT": df["MAO"] * df["NSSC2_mean"],
    }
    
    df = pd.concat([df, pd.DataFrame(feature_dict)], axis=1)

    # Land cover log-area features
    lc_cols = ['LCAS','LCC','LCG','LCT','LCS','LCHV','LCM','LCSV','LCBS','LCSG','LCWB']
    for col in lc_cols:
        df[col] = df["CA"] * df[col] / 100
        
    # -------------------------
    # APPLY LOG TRANSFORMATIONS
    # -------------------------
    log_candidates = ['CA','DCA','OBC','HGT','RA','RP','FL',
                      'SA_mean','SA_mean_clip','SA_std','SA_kurt','PAI','MAI','MAO','I_std','O_std','MAR',
                      'ROBC','rain_per_area','GC','TE','RT','ECLR','ESR','SIN','SOUT'] + lc_cols

    for col in log_candidates:
        log_col = f'log_{col}'  # add prefix to avoid double log
        try:
            df[log_col] = np.log(df[col].clip(lower=1e-15))
        except Exception as e:
            raise ValueError(f"Error applying log transform to column '{col}': {e}")
    
    # Process DLc as categorical column
    df['DLC'] = df['DLC'].astype(int).fillna(0)
    
    return df