# Tables of the article, recomputed

**Table 2. Official meanings, sources and human readings (type-2 centroid: Karnik–Mendel centroid interval)**

| Phrase | Official meaning | Source and range | Human mean (SD) | Type-2 centroid |
|---|---|---|---|---|
| almost certain | 0.93 | Kent, 87–99% | 0.93 (0.07) | [0.89, 0.92] |
| highly likely | 0.95 | IPCC “very likely”, 90–100% | 0.87 (0.10) | [0.83, 0.88] |
| very good chance | — | — | 0.81 (0.09) | [0.77, 0.83] |
| likely | 0.83 | IPCC, 66–100% | 0.71 (0.11) | [0.69, 0.73] |
| probably | 0.75 | Kent “probable”, 63–87% | 0.70 (0.13) | [0.66, 0.73] |
| probable | 0.75 | Kent, 63–87% | 0.69 (0.14) | [0.64, 0.73] |
| better than even | — | — | 0.58 (0.09) | [0.56, 0.61] |
| about even | 0.50 | Kent “chances about even”, 40–60% | 0.50 (0.03) | [0.50, 0.51] |
| probably not | 0.30 | Kent, 20–40% | 0.25 (0.13) | [0.23, 0.30] |
| unlikely | 0.17 | IPCC, 0–33% | 0.20 (0.11) | [0.19, 0.22] |
| improbable | — | — | 0.17 (0.15) | [0.16, 0.22] |
| chances are slight | — | — | 0.14 (0.09) | [0.13, 0.16] |
| little chance | — | — | 0.12 (0.07) | [0.12, 0.15] |
| highly unlikely | 0.05 | IPCC “very unlikely”, 0–10% | 0.09 (0.12) | [0.09, 0.13] |
| almost no chance | 0.07 | Kent “almost certainly not”, 2–12% | 0.05 (0.11) | [0.06, 0.09] |

**Table 3. Reader-side results over 25 reader splits, mean ± SD**

| Labels | Method | R-ECE | Worst 10% | Large misread | Excess Brier | AUROC |
|---|---|---|---|---|---|---|
| Strict | Official meanings | 0.071 ± 0.007 | 0.141 ± 0.034 | 10.2 ± 1.7% | 0.0115 ± 0.0048 | 0.785 ± 0.009 |
|  | Crisp lookup | 0.080 ± 0.008 | 0.156 ± 0.033 | 15.0 ± 2.4% | 0.0140 ± 0.0044 | 0.774 ± 0.008 |
|  | ReadCal, 10 phrases | 0.074 ± 0.010 | 0.153 ± 0.057 | 10.0 ± 2.1% | 0.0135 ± 0.0072 | 0.787 ± 0.011 |
|  | ReadCal, type-1 decoder | 0.067 ± 0.008 | 0.134 ± 0.033 | 8.3 ± 2.3% | 0.0102 ± 0.0043 | 0.777 ± 0.007 |
|  | ReadCal | 0.066 ± 0.009 | 0.133 ± 0.035 | 9.0 ± 2.7% | 0.0092 ± 0.0044 | 0.774 ± 0.006 |
| Lenient | Official meanings | 0.091 ± 0.005 | 0.152 ± 0.017 | 16.2 ± 2.4% | 0.0142 ± 0.0027 | 0.753 ± 0.007 |
|  | Crisp lookup | 0.070 ± 0.005 | 0.128 ± 0.016 | 12.4 ± 2.2% | 0.0127 ± 0.0025 | 0.757 ± 0.005 |
|  | ReadCal, 10 phrases | 0.070 ± 0.004 | 0.121 ± 0.011 | 10.7 ± 1.9% | 0.0130 ± 0.0014 | 0.754 ± 0.003 |
|  | ReadCal, type-1 decoder | 0.068 ± 0.004 | 0.114 ± 0.012 | 9.8 ± 1.4% | 0.0117 ± 0.0016 | 0.761 ± 0.004 |
|  | ReadCal | 0.066 ± 0.004 | 0.112 ± 0.011 | 9.5 ± 1.4% | 0.0119 ± 0.0017 | 0.760 ± 0.003 |

**Table 4. R-ECE for unseen reader groups (leave-one-group-out; p: paired Wilcoxon test)**

| Method | Online (S) | Students (S) | Graduates (S) | Online (L) | Students (L) | Graduates (L) |
|---|---|---|---|---|---|---|
| Official meanings | 0.059 | 0.076 | 0.075 | 0.084 | 0.092 | 0.097 |
| Crisp lookup | 0.076 | 0.090 | 0.073 | 0.063 | 0.070 | 0.074 |
| ReadCal, type-1 decoder | 0.066 | 0.071 | 0.066 | 0.067 | 0.067 | 0.069 |
| ReadCal | 0.065 | 0.070 | 0.061 | 0.067 | 0.064 | 0.069 |
| ReadCal vs official, p | 0.32 | 0.64 | 0.004 | < 0.001 | < 0.001 | < 0.001 |

**Table 5. Paired comparisons over 165 readers (negative differences favour ReadCal)**

| Labels | Comparison | Mean difference | 95% CI | Wilcoxon p | Readers better |
|---|---|---|---|---|---|
| Strict | ReadCal vs official meanings | −0.0043 | [−0.0103, +0.0017] | 0.24 | 91 |
|  | ReadCal vs crisp lookup | −0.0139 | [−0.0199, −0.0080] | < 0.001 | 101 |
|  | ReadCal vs type-1 decoder | −0.0006 | [−0.0037, +0.0018] | 0.41 | 84 |
|  | ReadCal vs 10 phrases | −0.0079 | [−0.0155, −0.0015] | 0.01 | 103 |
| Lenient | ReadCal vs official meanings | −0.0250 | [−0.0295, −0.0206] | < 0.001 | 134 |
|  | ReadCal vs crisp lookup | −0.0034 | [−0.0067, −0.0003] | 0.11 | 84 |
|  | ReadCal vs type-1 decoder | −0.0018 | [−0.0026, −0.0010] | < 0.001 | 113 |
|  | ReadCal vs 10 phrases | −0.0031 | [−0.0051, −0.0010] | < 0.001 | 108 |

**Table 6. Claim reliability estimators**

| Estimator | Inputs | AUROC (S) | ECE (S) | Brier (S) | AUROC (L) | ECE (L) | Brier (L) |
|---|---|---|---|---|---|---|---|
| Logistic, 4 basic features | 4 | 0.728 | 0.032 | 0.161 | 0.751 | 0.028 | 0.195 |
| Logistic, 11 features | 11 | 0.811 | 0.025 | 0.142 | 0.806 | 0.015 | 0.175 |
| ReadCal fuzzy engine (9 rules) | 2 | 0.806 | 0.020 | 0.145 | 0.780 | 0.024 | 0.185 |

**Table 7. R-ECE (excess Brier loss) for each reliability engine (*: p < 0.01 against official meanings)**

| Engine (AUROC S / L) | Labels | Official meanings | Crisp lookup | ReadCal decoder |
|---|---|---|---|---|
| Logistic, 4 basic features (0.73 / 0.75) | Strict | 0.090 (0.0136) | 0.095 (0.0139) | 0.081 (0.0106)* |
|  | Lenient | 0.086 (0.0143) | 0.074 (0.0118) | 0.065 (0.0108)* |
| Logistic, 11 features (0.81 / 0.81) | Strict | 0.068 (0.0124) | 0.076 (0.0135) | 0.060 (0.0085)* |
|  | Lenient | 0.076 (0.0159) | 0.078 (0.0102) | 0.059 (0.0096)* |
| ReadCal fuzzy engine (9 rules) (0.81 / 0.78) | Strict | 0.071 (0.0115) | 0.080 (0.0140) | 0.066 (0.0092) |
|  | Lenient | 0.091 (0.0142) | 0.070 (0.0127) | 0.066 (0.0119)* |

**Table 8. R-ECE of official meanings and ReadCal under alternative settings (p: paired Wilcoxon test)**

| Setting | Official (S) | ReadCal (S) | p (S) | Official (L) | ReadCal (L) | p (L) |
|---|---|---|---|---|---|---|
| Main analysis (official midpoints) | 0.071 | 0.066 | 0.24 | 0.091 | 0.066 | < 0.001 |
| Narrowest official range containing p | 0.069 | 0.066 | 0.81 | 0.086 | 0.066 | < 0.001 |
| Expected loss over official range | 0.073 | 0.066 | 0.04 | 0.091 | 0.066 | < 0.001 |
| No respondents excluded (169 readers) | 0.080 | 0.075 | 0.07 | 0.094 | 0.068 | < 0.001 |
| Readings 0.05 higher | 0.072 | 0.087 | < 0.001 | 0.078 | 0.077 | 0.57 |
| Readings 0.05 lower | 0.091 | 0.071 | < 0.001 | 0.118 | 0.086 | < 0.001 |
| Readings 15% closer to 0.5 | 0.066 | 0.074 | 0.005 | 0.090 | 0.052 | < 0.001 |
| Readings 30% closer to 0.5 | 0.098 | 0.103 | 0.03 | 0.099 | 0.064 | < 0.001 |

**Table 9. ReadCal output for one GPT-3 passage (strict labels)**

| Sentence (shortened) | Label | p | Official | ReadCal | Fired rule |
|---|---|---|---|---|---|
| Eleanor Arnason (born 1942) is an American science … | accurate | 0.85 | likely | almost certain | E high, S high → 0.81 |
| She is best known for her novel A Woman of the Iron … | accurate | 0.72 | probable | likely | E high, S high → 0.81 |
| Her other works include Ring of Swords (1993), The … | minor error | 0.17 | unlikely | little chance | E low, S high → 0.13 |
| She has also written several short stories, … | minor error | 0.25 | probably not | unlikely | E medium, S high → 0.28 |
| Arnason's work often focuses on themes of gender, … | minor error | 0.53 | about even | about even | E medium, S high → 0.28 |
| She has been praised for her ability to combine … | accurate | 0.53 | about even | about even | E high, S high → 0.81 |

**Numbers quoted in the text**

- Strict: official speaker-side error 0.014, reader-side 0.071 (ratio 5.0); personal oracle 0.036; reliabilities below 0.35 / 0.35–0.65 / above 0.65: 70% / 18% / 11%
- Lenient: official speaker-side error 0.034, reader-side 0.091 (ratio 2.7); personal oracle 0.035; reliabilities below 0.35 / 0.35–0.65 / above 0.65: 21% / 36% / 43%
- Group means of a phrase differ by 0.025 on average and at most 0.053; Kruskal–Wallis p < 0.05 for 1 of 15 phrases
- Respondents removed by screening: {'zonination': 1, 'fagen': 3}; thresholds: none: 169 readers, p (S) 0.07, p (L) < 0.001; 0.3: 166 readers, p (S) 0.02, p (L) < 0.001; 0.4: 166 readers, p (S) 0.02, p (L) < 0.001; 0.5: 165 readers, p (S) 0.24, p (L) < 0.001; 0.6: 164 readers, p (S) 0.42, p (L) < 0.001; 0.7: 159 readers, p (S) 0.82, p (L) < 0.001
- Vocabulary stability (strict, 25 splits): {'About Even': 25, 'Little Chance': 25, 'Very Good Chance': 25, 'Unlikely': 17, 'Better Than Even': 13, 'Probably Not': 10, 'Likely': 9, 'Almost No Chance': 1}
- Vocabulary stability (lenient, 25 splits): {'About Even': 25, 'Almost Certain': 25, 'Likely': 24, 'Little Chance': 21, 'Probably Not': 12, 'Unlikely': 8, 'Better Than Even': 4, 'Highly Likely': 4, 'Chances Are Slight': 2}
- Heterogeneous groups (shift 0.3): mean centroid-interval width 0.119; strict: worst group type-1 0.0957 vs type-2 0.0905, shifted group difference -0.0078 (p < 0.001, better for 37 of 45); lenient: worst group type-1 0.0755 vs type-2 0.0757, shifted group difference 0.0002 (p 0.59, better for 19 of 45)
- Heterogeneous groups (shift 0.5): mean centroid-interval width 0.202; strict: worst group type-1 0.1416 vs type-2 0.1292, shifted group difference -0.0133 (p < 0.001, better for 42 of 45); lenient: worst group type-1 0.0973 vs type-2 0.0946, shifted group difference -0.0031 (p < 0.001, better for 34 of 45)
- Fuzzy centroid minus mean reading: 0.0085 on average (max 0.0283)
- Non-fuzzy decoder (strict): R-ECE {'empirical_pooled': 0.06533348893079804, 'empirical_group_robust': 0.06604871201448446, 'type1_15': 0.06704502328502618, 'it2_15': 0.06644182679053885}, same phrase {'empirical_pooled_vs_type1': 0.9330398322851151, 'empirical_group_robust_vs_it2': 0.9547798742138365}
- Non-fuzzy decoder (lenient): R-ECE {'empirical_pooled': 0.06709726859792899, 'empirical_group_robust': 0.06589759068674161, 'type1_15': 0.06823756368718632, 'it2_15': 0.06642127048599199}, same phrase {'empirical_pooled_vs_type1': 0.9465828092243187, 'empirical_group_robust_vs_it2': 0.900691823899371}
- Kernel bandwidth: {'0.03': {'strict': {'type1_15': 0.06526821339685025, 'it2_15': 0.06572193123816784}, 'lenient': {'type1_15': 0.06694627787307034, 'it2_15': 0.06574140461215931}}, '0.05': {'strict': {'type1_15': 0.06704502328502618, 'it2_15': 0.06644182679053885}, 'lenient': {'type1_15': 0.06823756368718632, 'it2_15': 0.06642127048599199}}, '0.08': {'strict': {'type1_15': 0.06930882303465427, 'it2_15': 0.06786984956987104}, 'lenient': {'type1_15': 0.06953499998221205, 'it2_15': 0.0690022741706372}}, '0.12': {'strict': {'type1_15': 0.0726769072534367, 'it2_15': 0.06905683940838651}, 'lenient': {'type1_15': 0.07422162410583827, 'it2_15': 0.07324746152150435}}}
- Anchor-phrase R²: {'Almost Certain': -0.04939416589062984, 'Highly Likely': 0.12205657838536432, 'Likely': 0.01824934817442747, 'Probable': 0.013581506001099197, 'Probably': -0.018795804614630596, 'About Even': -0.0777285510936172, 'Probably Not': 0.09211842871426013, 'Unlikely': 0.13479907268852243, 'Highly Unlikely': -0.009911174414835022, 'Almost No Chance': -0.04459890746101158}
