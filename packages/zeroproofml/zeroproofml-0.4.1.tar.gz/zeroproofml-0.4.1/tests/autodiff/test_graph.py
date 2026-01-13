from zeroproof.autodiff.graph import SCMNode, add, div, mul, stop_gradient, sub
from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.scm.value import scm_real


def test_addition_backward_respects_policy():
    x = SCMNode.constant(scm_real(2.0))
    y = SCMNode.constant(scm_real(3.0))
    z = add(x, y)
    z.backward(policy=GradientPolicy.PASSTHROUGH)
    assert x.grad == 1.0
    assert y.grad == 1.0


def test_bottom_masks_gradients_under_clamp_policy():
    finite = SCMNode.constant(scm_real(1.0))
    zero = SCMNode.constant(scm_real(0.0))
    result = div(finite, zero)  # division by zero → bottom
    result.backward(policy=GradientPolicy.CLAMP)
    assert result.value.is_bottom
    assert finite.grad == 0.0
    assert zero.grad == 0.0


def test_stop_gradient_blocks_backprop():
    base = SCMNode.constant(scm_real(2.0))
    blocked = stop_gradient(base)
    out = mul(blocked, 3.0)
    out.backward(policy=GradientPolicy.PASSTHROUGH)
    assert base.grad == 0.0


def test_trace_outputs_hierarchy():
    x = SCMNode.constant(scm_real(2.0))
    expr = div(x.add(1.0), sub(1.0, x))
    trace_lines = expr.trace()
    assert trace_lines[0].startswith("div:")
