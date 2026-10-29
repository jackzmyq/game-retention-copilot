# Game Retention Experiment Analytics & AI Operations Copilot

Independent portfolio project by Yanqing Ma, developed with AI coding assistance. A historical public experiment case, based on public historical data, not a live production feed.

## What decision does it support?
Should a game's progression gate move from level 30 to 40? The workflow connects data checks, retention evidence, uncertainty and an operational recommendation.

## What was found?

The release includes 90,189 players. D7 retention is 19.02% in gate_30 and 18.20% in gate_40. The difference is -0.820 percentage points, with pointwise 95% CI [-1.328, -0.312] pp.
Recommendation: pause a full rollout and verify assignment integrity first. The intended allocation is unknown; a 50:50 assumption triggers an allocation screen, not a proven randomization failure.

## Review in three minutes

1. Experiment decision: see the conclusion, group denominators and uncertainty.
2. Decision lab: change a hypothetical population or tolerance; scenario outputs are not observed business loss.
3. Behavior & quality: inspect outlier sensitivity and return combinations.
4. AI copilot: choose offline mode and click Evaluate rollout, then Check regional coverage; inspect each answer's evidence. No API key is required for this route.

## Scope

| Classification | Scenario | Current support |
|---|---|---|
| Current case | Cookie Cats gate_30 vs gate_40 experiment | Runs now: D1/D7, checks, scenarios, bilingual briefs |
| Transferable method | Onboarding, progression pacing and feature experiments | Requires new data, metric definitions and validation; not connected today |
| International extension | Regional experiments and multilingual reporting | Bilingual reporting works; regional measurement needs country, locale and timezone data |
| Outside current evidence | Daily DAU, acquisition ROI, payment effects and early churn prediction | Required events, costs or earlier observation windows are absent |
| AI connection | Natural-language evidence queries and draft reporting | Local rules work; live DeepSeek interface implemented, provider acceptance pending |

## What the work demonstrates

- SQL/Python metric construction and experimental effect assessment.
- Integrity checks, uncertainty interpretation and business decision boundaries.
- Interactive delivery and bilingual communication.
- Implemented, bounded LLM tool interface with inspectable evidence; live-provider verification pending.

## How to access

The supplied static introduction opens in a browser with no Python, account or key. Open the no-login browser edition at https://jackzmyq.github.io/game-retention-copilot/ for scenarios, downloads and offline rules. Its SQL evidence was executed during the Python build, not by an arbitrary browser SQL engine. The full Python app runs locally; localhost is not a public URL. Technical reviewers can run the separately supplied source package using README.md.

## Key limitations

This release has no country, payment, timestamp or gate-exposure events. Recorded rounds have a 7/14-day source-description conflict and cannot serve as a prospective D7 predictor. The application currently supports this fixed reviewed dataset; it does not accept arbitrary CSVs, monitor live games or automatically change game settings.

Source fingerprint: `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`.

Source: https://assets.datacamp.com/production/project_184/datasets/cookie_cats.csv
