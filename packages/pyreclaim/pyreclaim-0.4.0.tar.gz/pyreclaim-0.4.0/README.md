<div align="center">
  <img src="https://github.com/UW-SASWE/RECLAIM/raw/main/docs/_static/Reclaim_logo_clearBG.png" alt="Reservoir Estimation of Capacity Loss using AI-based Methods" width="500"/>
</div>


# Reservoir Estimation of Capacity Loss using AI-based Methods (RECLAIM)

---

**First-of-its-kind globally scalable tool to predict reservoir sedimentation, screen vulnerable reservoirs, and pinpoint those struggling the most.**

**RECLAIM** (*Reservoir Estimation of Capacity Loss using AI-based Methods*) is a globally scalable machine learning framework to predict **absolute sedimentation rates** in reservoirs using observed records and multi-decadal satellite-based Earth observations.

It is the **first-of-its-kind tool** to:

- Rapidly assess sedimentation risk
- Provide scalable predictions across diverse climates and geographies
- Enable cost-effective screening to prioritize reservoirs for detailed surveys
- Support decision-making for mitigation interventions where they are most needed

> **Note:** RECLAIM is designed as a screening tool, not a replacement for field surveys. It helps guide **where and when to act first**.

---

## Installation

Install the package via pip:

```bash
pip install pyreclaim
```

---
## Download Data

To generate features for reservoirs using the **RECLAIM** framework and the [`pyreclaim`](https://pypi.org/project/pyreclaim/) Python package, you will need the global datasets.  

You can download all required global datasets from the Zenodo Repository:  

[Download Global Datasets](https://doi.org/10.5281/zenodo.17230533)  

These datasets include land cover, soil, terrain/DEM derivatives, and vegetation gain/loss data, which are essential for computing reservoir and catchment features for RECLAIM.

---
## Documentation

The documentation is available [here](https://reclaimio.readthedocs.io/en/latest/).


---

## Quick Start / Example Workflow

This example shows generating features, loading the pretrained model, predicting sedimentation rates, and evaluating results.

```python
from reclaim.generate_features import create_features_per_row
from reclaim.reclaim import Reclaim

# Step 1: Generate features for a reservoir
reservoir_static = {
    "obc": 150.0,
    "hgt": 45.0,
    "mrb": 4030033640,
    "lat": 25.6,
    "lon": 81.9,
    "reservoir_polygon": reservoir_polygon,
    "aec_df": aec_df
}

catchment_static = {
    "ca": 1200,
    "dca": 50,
    "catchment_geometry": catchment_geom,
    "glc_share_path": "data/glc.nc",
    "hwsd2_path": "data/soil.nc",
    "hilda_veg_freq_path": "data/veg.nc",
    "terrain_path": "data/terrain.nc"
}

features = create_features_per_row(
    reservoir_static_params=reservoir_static,
    catchment_static_params=catchment_static,
    observation_period=[2000, 2020]
)

# Step 2: Load pretrained RECLAIM model
model = Reclaim()
model.load_model()  # loads XGBoost, LightGBM, CatBoost, and metadata

# Step 3: Predict sedimentation rates using ensemble
pred_sr, weights = model.predict(features, return_weights=True)

# Step 4: Inspect predictions
print(pred_sr)
print(weights)

# Step 5: Evaluate (if ground truth available)
y_true = [...]  # replace with true sedimentation rates
metrics = model.evaluate(features, y_true)
print(metrics)  # {'RMSE': ..., 'MAE': ..., 'R2': ...}
```

---

## Citation

If you use RECLAIM in your work, please cite:

> Minocha, S., Hossain, F., Zhao, J., & Istanbulluoglu, E.  
> *RECLAIM: A Globally Scalable Machine Learning Framework to Predict Reservoir Sedimentation and Capacity Loss from Satellite-based Earth Observations* (Submitted to *Environmental Modelling and Software (EMS)*).

---

## License

RECLAIM 3.0 is distributed under the **GPL v3 license**. You may copy, distribute, and modify the software as long as you track changes/dates in source files. Any modifications or software including GPL-licensed code must also be made available under GPL along with build & install instructions.  
For more information, see [LICENSE](./LICENSE).