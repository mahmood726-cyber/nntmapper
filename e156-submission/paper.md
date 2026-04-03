Mahmood Ahmad
Tahir Heart Institute
author@example.com

NNTMapper: Converting Meta-Analytic Effects into Population-Specific Number Needed to Treat with Heterogeneity Propagation

How does the Number Needed to Treat from a meta-analysis vary across patient populations with different baseline risks, and how should heterogeneity propagate to this metric? We validated NNTMapper against R using three cardiovascular examples: SGLT2 inhibitors in heart failure, statins for primary prevention, and aspirin for secondary prevention. The tool converts pooled effects into population-specific NNT, absolute risk reduction, and relative risk reduction across user-specified baseline risks, with prediction intervals incorporating between-study variance via the t-distribution. For SGLT2 inhibitors with pooled OR 0.74 (95% CI 0.66 to 0.83) at 20 percent baseline risk, NNTMapper computed NNT of 23 (CI 17 to 37), matching R to machine precision. Decision curve analysis identified net benefit thresholds where treatment decisions shifted across the baseline risk spectrum. Converting relative effects to absolute patient-relevant metrics makes meta-analytic evidence directly actionable for clinical decision-making. The tool is limited to single pooled estimates and cannot incorporate patient-level risk stratification or competing risks.

Outside Notes

Type: methods
Primary estimand: Number Needed to Treat across baseline risk range
App: NNTMapper v1.0
Data: 3 cardiovascular validation examples (SGLT2i, statins, aspirin)
Code: https://github.com/mahmood726-cyber/nntmapper
Version: 1.0
Certainty: high
Validation: DRAFT

References

1. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
2. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. BMJ. 2003;327(7414):557-560.
3. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
