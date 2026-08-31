# HydroFed-ICAF Phase 1 Formula Execution & Intermediate Results

This document compiles the intermediate results of the three major formula groups implemented in the HydroFed-ICAF framework. 
The computations are performed using real visual and clinical data from the dataset (`final_metadata_registry.csv`) and real client performance registries (`fl_results.json`).

---

## 1. Cross-Attention & Gated AICA Modules

### Formula Formulations
1. **Dynamic Gate score**:
   $$G = \sigma(W_g \cdot [F_s \| F_f \| (F_s \odot F_f)])$$
   Where $F_s$ represents spatial visual features and $F_f$ represents Fourier frequency features.
   
2. **Visual Cross-Attention**:
   $$\text{Att}_{s \to f} = \text{Softmax}\left( \frac{Q_s K_f^T}{\sqrt{d}} \right) V_f$$
   $$\text{Att}_{f \to s} = \text{Softmax}\left( \frac{Q_f K_s^T}{\sqrt{d}} \right) V_s$$
   $$F_{\text{cross}} = \text{Att}_{s \to f} \| \text{Att}_{f \to s}$$
   
3. **Adaptive Fusion & LayerNorm**:
   $$F_{\text{fused}} = G \cdot \text{Att}_{s \to f} + (1 - G) \cdot \text{Att}_{f \to s}$$
   $$F_{\text{final}} = \text{LayerNorm}(F_{\text{fused}} + \text{AICA}(F_s, F_f))$$

### Measured Intermediate Tensor Statistics
Below is the table of the exact statistics (Shape, Mean, Standard Deviation, Minimum, Maximum) calculated during the execution of a real patient sample:

| Variable Name | Tensor Shape | Mean | Std Dev | Minimum | Maximum |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **$Fs$** (Spatial features) | [1, 128, 7, 7] | -0.243632 | 1.928009 | -7.143419 | 5.581689 |
| **$Ff$** (Frequency features) | [1, 128, 7, 7] | -0.000184 | 0.112346 | -0.889582 | 1.095525 |
| **$Q_s$** (Spatial Query projection) | [1, 49, 128] | 0.115321 | 1.939919 | -8.024058 | 6.815871 |
| **$K_f$** (Frequency Key projection) | [1, 49, 128] | 0.002625 | 0.112316 | -1.118043 | 1.160142 |
| **$Att\_map\_sf$** (Attention weights) | [1, 49, 49] | 0.020408 | 0.003366 | 0.015494 | 0.055698 |
| **$Att\_sf$** (S-to-F attention output) | [1, 128, 7, 7] | -0.000535 | 0.101206 | -0.293298 | 0.251222 |
| **$Att\_fs$** (F-to-S attention output) | [1, 128, 7, 7] | 0.046275 | 1.751467 | -4.145853 | 4.380567 |
| **$F\_cross$** (Concat features) | [1, 256, 7, 7] | 0.022870 | 1.240711 | -4.145853 | 4.380567 |
| **$F\_aica$** (AICA projection) | [1, 128, 7, 7] | 0.111845 | 1.192184 | -3.022709 | 3.624777 |
| **$G$** (Gating factor values) | [1, 128, 7, 7] | 0.469499 | 0.258844 | 0.007107 | 0.993757 |
| **$F\_fused$** (Gated fused maps) | [1, 128, 7, 7] | 0.037708 | 1.064491 | -3.302500 | 3.475913 |
| **$F\_final$** (LayerNorm output) | [1, 128, 7, 7] | -0.000000 | 1.000078 | -3.202435 | 2.679453 |

### Intermediate Feature Activations Visualization
The channel-averaged activation maps of all intermediate layers are shown below:

![AICA Intermediate Feature Maps](file:///c:/Users/Soundarya/OneDrive/Desktop/HydroFed/experiments/phase_1_outputs/Fig_01_aica_intermediates.png)

---

## 2. HydroFed Pressure / Flow Federated Gating

### Formula Formulations
1. **Client Node Importance Score (Pressure)**:
   $$\text{Pressure}_i = \text{Pi} = \frac{\text{Accuracy}_i}{\text{CommCost}_i + \varepsilon}$$
   
2. **Consensus Aggregation Gated Weight**:
   $$W_{\text{global}} = \sum_{i=1}^N \left( \frac{\text{Pressure}_i}{\sum_{j=1}^N \text{Pressure}_j} \right) W_i$$

### Simulation Aggregation Weight Statistics
Using the real final model accuracies across the $N=60$ client clinics from `fl_results.json` and generated communication costs, we obtain:

- **Total Client Pressure Sum**: 21.734410
- **Average Node Pressure**: 0.362240 (Min: 0.188878, Max: 0.707058)
- **Average Aggregation Weight**: 1.667% (Min: 0.869%, Max: 3.253%)

### Clinic Pressures & Weights Distribution Plots
The client-by-client breakdown of the accuracies, communication costs, computed pressures, and global aggregation weights are shown in the distributions below:

![HydroFed Pressure & Aggregation Weight Distributions](file:///c:/Users/Soundarya/OneDrive/Desktop/HydroFed/experiments/phase_1_outputs/Fig_02_hydrofed_pressure.png)

### First 10 Client Nodes Breakdown
Here is the raw data calculated for the first 10 clinic nodes:

| Client ID | Accuracy | Communication Cost | Pressure | Global Agg Weight |
| :---: | :---: | :---: | :---: | :---: |
| **Client 00** | 87.92% | 2.5483 | 0.3450 | 1.587% |
| **Client 01** | 88.89% | 4.6226 | 0.1923 | 0.885% |
| **Client 02** | 85.01% | 3.8352 | 0.2217 | 1.020% |
| **Client 03** | 87.03% | 3.3552 | 0.2594 | 1.193% |
| **Client 04** | 88.75% | 1.7617 | 0.5038 | 2.318% |
| **Client 05** | 83.23% | 1.7616 | 0.4724 | 2.174% |
| **Client 06** | 89.67% | 1.4091 | 0.6363 | 2.928% |
| **Client 07** | 85.47% | 4.3182 | 0.1979 | 0.911% |
| **Client 08** | 90.36% | 3.3640 | 0.2686 | 1.236% |
| **Client 09** | 89.60% | 3.7491 | 0.2390 | 1.100% |

---
*Results computed and compiled by the HydroFed Phase 1 Evaluator on 2026-08-27.*
