from persistency.model import weibull_survival, retained_starters_mass


def test_weibull_survival_basic_properties():
    # S(0) must be 1
    assert weibull_survival(0, alpha=10.0, beta=1.2) == 1.0

    # Monotone decreasing (for positive alpha,beta)
    s1 = weibull_survival(1, alpha=10.0, beta=1.2)
    s2 = weibull_survival(2, alpha=10.0, beta=1.2)
    assert 0 < s2 < s1 < 1


def test_retained_starters_mass_simple_case_alpha_large():
    # If alpha is huge and beta=1, then S(age) ~ exp(-age/huge) ~ near 1 for small ages
    nbrx = [10.0, 10.0, 10.0]
    A = retained_starters_mass(nbrx, alpha=1e9, beta=1.0)
    # Should be approximately cumulative sum
    assert A[0] == 10.0
    assert abs(A[1] - 20.0) < 1e-6
    assert abs(A[2] - 30.0) < 1e-6


def test_retained_starters_mass_with_max_lag():
    nbrx = [10.0, 10.0, 10.0, 10.0]
    A_full = retained_starters_mass(nbrx, alpha=10.0, beta=1.0, max_lag=None)
    A_lag1 = retained_starters_mass(nbrx, alpha=10.0, beta=1.0, max_lag=1)

    # With lag=1, A_t excludes cohorts older than 1 month, so it must be <= full A_t
    assert all(a1 <= af for a1, af in zip(A_lag1, A_full))
