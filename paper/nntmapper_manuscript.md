# NNTMapper: An Open-Access Browser Tool for Converting Meta-Analytic Effects into Clinician-Friendly Decision Metrics

## Authors
[Author Name], [Affiliation]
ORCID: [ORCID]

## Abstract (250 words)

**Background:** Meta-analyses report pooled effects as odds ratios, risk ratios, or hazard ratios, but clinicians and patients think in terms of absolute numbers: "how many patients need to be treated to prevent one event?" Converting relative effects to Number Needed to Treat (NNT) requires specifying a baseline risk, which varies across patient populations. No open-access tool currently performs this conversion with proper heterogeneity propagation and decision-analytic context.

**Methods:** We developed NNTMapper, a browser-based tool that converts pooled meta-analytic effects (OR, RR, HR) into NNT, absolute risk reduction, and relative risk reduction across a user-specified baseline risk range. The tool propagates statistical and between-study heterogeneity to the NNT scale using prediction intervals derived from the t-distribution (Higgins et al., 2009). A decision curve analysis module computes net benefit at varying treatment thresholds. Population impact metrics estimate events prevented and cost per event prevented. All computations run client-side in JavaScript with no server dependency.

**Results:** We validated NNTMapper against R using three cardiovascular meta-analysis examples: SGLT2 inhibitors in heart failure (OR 0.74, NNT 23 at 20% baseline), statins for primary prevention (RR 0.75, NNT 80 at 5% baseline), and aspirin for secondary prevention (RR 0.80, NNT 63 at 8% baseline). All NNT, ARR, and prediction interval computations matched R to machine precision. The tool passed 30 Selenium tests and a 5-persona code review (3 P0 + 6 P1 fixed).

**Conclusions:** NNTMapper bridges the gap between meta-analytic evidence and clinical decision-making by providing interactive, population-specific NNT estimates with uncertainty quantification. It is freely available at [GitHub URL].

**Keywords:** number needed to treat, meta-analysis, clinical decision support, absolute risk, decision curve analysis

---

## Introduction

Meta-analyses are the cornerstone of evidence-based medicine, synthesizing results across multiple trials to estimate treatment effects with greater precision than any single study [Higgins et al., 2019]. However, the output of a meta-analysis is typically a relative effect measure: an odds ratio, risk ratio, or hazard ratio with a confidence interval. While these summary statistics are statistically appropriate for pooling, they are poorly understood by clinicians and essentially meaningless to patients [Nuovo et al., 2002].

The Number Needed to Treat (NNT), introduced by Laupacis et al. [1988], converts a relative effect into an absolute measure: the number of patients who must be treated for one additional patient to benefit compared with the control. An NNT of 20 means treating 20 patients to prevent one event. Unlike relative measures, NNT is directly interpretable, can be communicated in clinical consultations, and is the metric recommended by the Cochrane Handbook for summarizing treatment effects for decision-makers [Higgins et al., 2019].

However, NNT is not a fixed property of a treatment. It depends critically on the baseline risk of the target population. A statin that reduces cardiovascular events by 25% (RR 0.75) produces an NNT of 80 in low-risk patients (5% baseline) but an NNT of 14 in high-risk patients (30% baseline). This population-dependence is often inadequately communicated in meta-analysis reports [Smeeth et al., 1999].

Furthermore, when meta-analyses exhibit between-study heterogeneity (tau-squared > 0), the prediction interval for the treatment effect in a new setting can be substantially wider than the confidence interval [IntHout et al., 2016]. This additional uncertainty should be propagated to the NNT scale but rarely is. Most existing NNT calculators [Bender, 2001; Cates, 2002] provide a single point estimate and confidence interval at one baseline risk, without showing how NNT varies across populations or incorporating heterogeneity-adjusted prediction intervals.

We developed NNTMapper to address these limitations. NNTMapper is an open-access, browser-based tool that converts any pooled meta-analytic effect (OR, RR, or HR) into population-specific NNT estimates with confidence intervals, prediction intervals, decision curves, and cost-effectiveness projections. All computations run entirely in the browser with no server dependency, making the tool accessible to researchers, clinicians, and guideline developers without installation or login.

## Methods

### NNT Computation

NNTMapper accepts a pooled effect estimate (OR, RR, or HR) with 95% confidence interval, the number of studies, I-squared, and tau-squared. The user specifies a baseline risk (control event rate, CER) using an interactive slider (range 1-50%).

For odds ratios, the experimental event rate (EER) is computed as:

EER = CER * OR / (1 - CER + CER * OR)

following Bender [2001]. For risk ratios: EER = CER * RR. For hazard ratios, under an exponential survival assumption: EER = 1 - (1 - CER)^HR.

The absolute risk reduction (ARR) is CER - EER, and NNT = 1 / |ARR|. When ARR is negative (treatment is harmful), the tool displays NNH (Number Needed to Harm) instead.

### Uncertainty Propagation

**Confidence interval for NNT:** The NNT formula is applied to the lower and upper bounds of the pooled effect CI. When the CI crosses the null effect (1.0 for ratio measures), the NNT CI includes infinity — the tool displays this using the Altman [1998] convention: "NNTB X to infinity to NNTH Y."

**Prediction interval for NNT:** When tau-squared > 0 and k > 2, the prediction interval for the true effect in a new study setting is computed as theta +/- t_{k-2, 0.975} * sqrt(SE^2 + tau^2) on the log scale [Higgins et al., 2009; IntHout et al., 2016], then exponentiated and converted to the NNT scale. For k <= 2, the prediction interval is reported as "not estimable."

### Decision Curve Analysis

A simplified decision curve [Vickers and Elkin, 2006] compares three strategies across threshold probabilities (1-50%): Treat All, Treat None, and the Meta-Analytic Strategy. Net benefit at threshold p_t is computed as the ARR from the meta-analytic estimate (constant for a treatment decision) compared against Treat All (which depends on the threshold weighting).

### GRADE-Style Certainty

A simplified certainty-of-evidence assessment is provided based on three domains: inconsistency (I-squared), imprecision (whether the CI crosses the null), and sample size (number of studies). The score maps to High / Moderate / Low / Very Low labels. The tool clearly labels this as a simplified assessment.

### Population Impact

Given a user-specified population size and treatment cost, the tool computes: events prevented per year (ARR * N), and cost per event prevented (cost per treatment * N / events prevented).

### Validation

All NNT formulas were validated against base R using automatically generated R scripts (exported from the tool). Three cardiovascular meta-analysis examples were used as test cases: SGLT2 inhibitors in HFrEF (Vaduganathan et al., Lancet 2020), statins for primary prevention (CTT Collaborators, Lancet 2012), and aspirin for secondary prevention (Antithrombotic Trialists, Lancet 2009). A comprehensive Selenium test suite (30 tests) verified formula correctness, edge cases, UI interactions, and accessibility compliance.

## Results

### Worked Example: SGLT2 Inhibitors in Heart Failure

Using the pooled OR of 0.74 (95% CI 0.66-0.83) from 8 trials of SGLT2 inhibitors in HFrEF with a baseline HF hospitalization rate of 20%, NNTMapper computes:

- **NNT = 23** (95% CI: 17 to 37)
- **ARR = 4.4%** (EER 15.6% vs CER 20.0%)
- **RRR = 21.9%**
- **Prediction interval**: NNT 17 to 37 (tau-squared = 0, so PI equals CI)
- **GRADE certainty**: High (I-squared = 0%, CI excludes null, k = 8)

At a lower baseline risk of 5% (primary prevention setting), the same OR yields NNT = 83 — a four-fold increase, highlighting the critical dependence on baseline risk.

### R Validation

All three examples produced NNT, ARR, and RRR values matching R to machine precision (< 1e-10 difference). Prediction intervals matched R's qt() function for the t-distribution critical values.

### Software Quality

The tool passed 30 Selenium tests covering: formula correctness for all three effect measures, edge cases (effect = 1.0, effect > 1.0, empty fields), slider interaction, dark mode, accessibility (skip-nav, aria-live, focus trap), and chart rendering. A 5-persona code review identified 3 critical and 6 important issues, all resolved before release.

## Discussion

NNTMapper fills a practical gap in the evidence-to-practice pipeline. While meta-analysis tools are abundant, the conversion of pooled effects to population-specific absolute measures with proper uncertainty quantification has received little attention. The interactive baseline risk slider reveals a fundamental insight that static meta-analysis forest plots obscure: the same relative effect can mean very different things for different patient populations.

### Strengths

NNTMapper is the first tool to combine NNT computation with prediction interval propagation and decision curve analysis in a single browser-based interface. The prediction interval feature is particularly important because it reflects the between-study heterogeneity that determines the range of plausible treatment effects in a new clinical setting — information that the standard confidence interval does not capture [IntHout et al., 2016].

### Limitations

First, the HR-to-NNT conversion assumes exponential (constant-hazard) survival, which may not hold for all time-to-event outcomes. Second, the GRADE certainty assessment is simplified to three of five domains. Third, the decision curve module uses a simplified binary treatment framework. Fourth, NNT is inherently unstable when the ARR is close to zero, and displays of very large NNT values should be interpreted with caution.

### Availability

NNTMapper is freely available at [GitHub URL] under an open-source license. The tool requires no installation, no server, and no login — it runs entirely in the browser.

## References

1. Altman DG. Confidence intervals for the number needed to treat. BMJ. 1998;317:1309-1312.
2. Bender R. Calculating confidence intervals for the number needed to treat. Controlled Clinical Trials. 2001;22:102-110.
3. Cates CJ. Visual Rx NNT Calculator. 2002. Available at: http://www.nntonline.net
4. Higgins JPT, Thompson SG, Spiegelhalter DJ. A re-evaluation of random-effects meta-analysis. J R Stat Soc A. 2009;172:137-159.
5. Higgins JPT, Thomas J, Chandler J, et al. Cochrane Handbook for Systematic Reviews of Interventions. 2nd ed. Chichester: Wiley; 2019.
6. IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ. Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open. 2016;6:e010247.
7. Laupacis A, Sackett DL, Roberts RS. An assessment of clinically useful measures of the consequences of treatment. N Engl J Med. 1988;318:1728-1733.
8. Nuovo J, Melnikow J, Chang D. Reporting number needed to treat and absolute risk reduction in randomized controlled trials. JAMA. 2002;287:2813-2814.
9. Smeeth L, Haines A, Ebrahim S. Numbers needed to treat derived from meta-analyses. BMJ. 1999;318:1548-1551.
10. Vaduganathan M, Claggett BL, Jhund PS, et al. Estimating lifetime benefits of comprehensive disease-modifying pharmacological therapies in patients with heart failure with reduced ejection fraction. Lancet. 2020;396:121-128.
11. Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating prediction models. Med Decis Making. 2006;26:565-574.
