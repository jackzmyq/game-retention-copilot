-- Grain: one randomized player, with one pre-aggregated recorded-period outcome row.
-- The normalization below is a project data model, not original event logs.
CREATE VIEW v_arm_metrics AS
SELECT a.version, COUNT(*) AS players,
       SUM(o.retention_1) AS retained_d1, SUM(o.retention_7) AS retained_d7,
       AVG(o.retention_1) AS d1_rate, AVG(o.retention_7) AS d7_rate,
       AVG(o.sum_gamerounds) AS mean_observed_rounds,
       SUM(CASE WHEN o.sum_gamerounds = 0 THEN 1 ELSE 0 END) AS zero_round_players
FROM assignments a JOIN outcomes o ON a.userid=o.userid
GROUP BY a.version;

CREATE VIEW v_round_bands AS
SELECT a.version,
 CASE WHEN o.sum_gamerounds=0 THEN '0'
      WHEN o.sum_gamerounds<=10 THEN '1-10'
      WHEN o.sum_gamerounds<=30 THEN '11-30'
      WHEN o.sum_gamerounds<=100 THEN '31-100'
      WHEN o.sum_gamerounds<=300 THEN '101-300' ELSE '301+' END AS round_band,
 COUNT(*) AS players, SUM(o.retention_7) AS retained_d7,
 AVG(o.retention_7) AS d7_rate
FROM assignments a JOIN outcomes o ON a.userid=o.userid
GROUP BY a.version, round_band;

CREATE VIEW v_retention_transitions AS
SELECT a.version, o.retention_1 AS returned_d1, o.retention_7 AS returned_d7,
 COUNT(*) AS players
FROM assignments a JOIN outcomes o ON a.userid=o.userid
GROUP BY a.version, o.retention_1, o.retention_7;

CREATE VIEW v_quality AS SELECT check_name, observed, status, note FROM quality_checks;
CREATE VIEW v_capabilities AS SELECT metric, available, reason FROM capabilities;
CREATE VIEW v_test_results AS SELECT * FROM test_results;
CREATE VIEW v_definitions AS SELECT term, definition FROM metric_definitions;
