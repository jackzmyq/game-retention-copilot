# Game retention experiment: decision brief

**Recommendation: pause a full rollout of gate_40; verify allocation and data integrity first.**

## Evidence
- Population: 90,189 players; gate_30 44,700, gate_40 45,489.
- D7 retention: 8,502/44,700 = 19.02% vs 8,279/45,489 = 18.20%.
- Treatment minus control: **-0.820 percentage points**; pointwise 95% Newcombe CI [-1.328, -0.312] pp; two-sided p=0.00155; Holm-adjusted p=0.00311 across D1/D7. Relative difference -4.31%.
- D1 difference: -0.591 pp; CI [-1.239, +0.058] pp; Holm-adjusted p=0.07441. No significant difference does not demonstrate equivalence.

## Integrity gate
Under an **assumed, unverified 50:50 allocation**, the sample-ratio-mismatch screening p-value is 0.00861; screening threshold 0.01; flag=YES. This does not prove a randomization failure. Obtain the intended ratio, assignment logs, eligibility rules and full outcome coverage before treating the estimate as causal.

## Decision and follow-up
The public sample supports a negative D7 difference. It does not identify whether pacing, difficulty or another mechanism explains it. Keep gate_30 as the provisional reference; audit assignment, deduplication, observation maturity, platform balance, and exposure. If integrity is confirmed, consider a new fixed-horizon experiment with prespecified D7 and guardrails. For illustration, a 1 pp absolute decline at baseline 19.02%, 80% power, two-sided alpha 0.05 requires approximately **23,688 players per arm** under an equal-allocation normal approximation. This is a planning scenario, not achieved power or observed lift.

## Scope
Historical Cookie Cats educational A/B release, not miHoYo telemetry. No raw timestamps, country, channel, payments or gate-exposure events. D7 is a source flag for return seven days after installation; it is not cumulative seven-day retention. The selected primary outcome and tests are retrospective, not verified preregistration. Teaching materials conflict on the rounds horizon (7 vs 14 days); the recorded aggregate is post-treatment, overlaps the outcome, and must not be used as a prospective churn predictor or a causal segment. The 49,854-round record is retained; the exclusion is sensitivity-only. Regional expansion requires new data and market-specific validation.
