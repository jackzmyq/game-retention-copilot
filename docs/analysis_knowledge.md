# Reusable analysis knowledge

This is a small curated Markdown knowledge base read through a function tool. It is not a vector database, not an embedding RAG implementation and not MCP.

1. Unit is a randomized player, not a session. Source contains one recorded-period aggregate per player.
2. D1 and D7 are supplied day-specific return flags; not cumulative return, and not a nested funnel.
3. All assigned players remain in the main comparison (ITT-style), including zero-round and extreme-round records. Raw assignment/exposure cannot be re-audited from this release.
4. The tutorial says players were randomly assigned to gate_30 or gate_40. Allocation probability, exposure dates, collection period and completeness are not supplied. Any 50:50 SRM is conditional on an unverified assumption. A flagged check requests investigation, not automatic deletion or proof of broken randomization.
5. D7 is the portfolio's retrospectively selected main metric; no preregistration is claimed. Report pointwise Newcombe 95% intervals and Holm-adjusted p-values over D1 and D7. No sequential monitoring or optional-stopping validity is claimed.
6. sum_gamerounds is recorded-period play, after assignment and overlapping the D7 label. Segment differences may be outcomes of treatment. Never call them causal retention drivers. Rounds do not equal levels or gate exposure.
7. No country, language, channel, calendar events, revenue, cost or SDK event ingestion is present. International extension is a measurement proposal, not measured regional results.
8. If estimating business impact, name the hypothetical population, baseline and assumptions. No realized retention uplift, revenue gain or operational efficiency gain has been measured.
9. The extreme maximum is retained in the main sample; sensitivity exclusion is descriptive. Do not silently trim data to improve a result.
10. Answer structure: conclusion / executed evidence / uncertainty / next investigation. If a metric is unsupported, explain the missing fields before proposing queries.
11. The mirrored teaching notebook defines sum_gamerounds as the first 14 days in its field list but calls it first-week rounds elsewhere. The CSV has no timestamps to settle the conflict. Use 'recorded-period rounds', not a verified 7-day feature, and disclose the ambiguity. This further rules out using this aggregate to predict D7 prospectively.
