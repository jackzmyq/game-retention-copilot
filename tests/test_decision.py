import pytest
from src.decision import impact_scenario,harm_lens,allocation_check,return_patterns,scenario_markdown
from src.statistics import srm
from src.reporting import load_analysis


def test_impact_preserves_sign_and_interval_and_scaling():
    effect=load_analysis()["tests"][1]
    r=impact_scenario(effect,10000)
    assert r["ci_low"] < r["retained_difference"] < r["ci_high"] < 0
    assert r["retained_difference"]==pytest.approx(-82.012983)
    assert impact_scenario(effect,100000)["retained_difference"]==pytest.approx(10*r["retained_difference"])
    with pytest.raises(ValueError):
        impact_scenario(effect,0)


def test_tolerance_changes_lens_not_evidence():
    effect=load_analysis()["tests"][1]
    delta=effect["delta"]
    assert harm_lens(effect,.1)["state"]=="beyond_tolerance"
    assert harm_lens(effect,.5)["state"]=="overlaps_tolerance"
    assert harm_lens(effect,1.5)["state"]=="within_tolerance"
    assert harm_lens(effect,1.5)["integrity_audit_required"]
    assert effect["delta"]==delta


def test_allocation_assumptions_are_not_silently_verified():
    r=allocation_check(44700,45489,.5)
    assert r["p_value"]==pytest.approx(srm(44700,45489)["p_value"])
    observed=44700/90189
    fitted=allocation_check(44700,45489,observed)
    assert fitted["p_value"]==pytest.approx(1)
    assert fitted["assumption_verified"] is False


def test_return_patterns_reconcile_without_funnel():
    a=load_analysis()
    patterns=return_patterns(a)
    assert sum(r["players"] for r in patterns)==90189
    for arm in a["arms"]:
        rows=[r for r in patterns if r["version"]==arm["version"]]
        assert sum(r["share"] for r in rows)==pytest.approx(1)
        assert sum(r["players"] for r in rows if r["returned_d7"])==arm["retained_d7"]
        assert next(r["players"] for r in rows if r["pattern"]=="01")>0
    exported=scenario_markdown(a["tests"][1],10000,.5)
    assert "10,000" in exported and "不是实测" in exported
