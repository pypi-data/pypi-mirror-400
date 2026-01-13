from zeroproof.autodiff.policies import (
    GradientPolicy,
    apply_policy,
    get_policy,
    gradient_policy,
)


def test_policy_context_manager_switches_policy():
    assert get_policy() == GradientPolicy.CLAMP
    with gradient_policy(GradientPolicy.REJECT):
        assert get_policy() == GradientPolicy.REJECT
    assert get_policy() == GradientPolicy.CLAMP


def test_apply_policy_masks_bottoms_and_clamps():
    assert apply_policy(5.0, is_bottom=False, policy=GradientPolicy.CLAMP) == 1.0
    assert apply_policy(-5.0, is_bottom=False, policy=GradientPolicy.CLAMP) == -1.0
    assert apply_policy(2.0, is_bottom=True, policy=GradientPolicy.CLAMP) == 0.0


def test_passthrough_policy_allows_bottom_flow():
    assert apply_policy(2.5, is_bottom=True, policy=GradientPolicy.PASSTHROUGH) == 2.5
