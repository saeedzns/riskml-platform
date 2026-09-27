from risk_ml.data.fixture import generate_fixture
from risk_ml.monitoring.drift import drift_report, reference_profile


def test_similar_fixture_does_not_raise_obvious_false_alarm() -> None:
    reference = generate_fixture(3000, 10)
    current = generate_fixture(3000, 11)
    report = drift_report(reference, current)
    assert report["status"] == "ok"
    assert report["drifted_features"] == []


def test_controlled_shift_is_detected() -> None:
    reference = generate_fixture(1000, 10)
    shifted = generate_fixture(1000, 11)
    shifted["credit_amount"] *= 4
    shifted["checking_status"] = "negative"
    report = drift_report(reference, shifted)
    assert report["status"] == "alert"
    assert {"credit_amount", "checking_status"}.issubset(report["drifted_features"])


def test_reference_profile_is_json_safe() -> None:
    profile = reference_profile(generate_fixture(20, 10))
    assert profile["rows"] == 20
    assert profile["numeric"]["age"]["mean"] > 18
    assert profile["categorical"]["housing"]
