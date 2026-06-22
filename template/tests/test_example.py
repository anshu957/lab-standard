"""EXAMPLE test — replace with your project's real science tests, then delete this file.

Lab Standard testing convention:
  - Pin every load-bearing scientific transform with a known-input -> known-output test.
  - In particular, EVERY ADR that encodes a computational rule should have a test that enforces it
    (name the ADR in the test, so a future edit that violates the decision fails loudly).
  - Keep tests fast and dependency-light; put slow/data-heavy ones behind a pytest marker.

Pattern:

    from {{PKG}} import features

    def test_extract_matches_adr_0002():
        # ADR 0002 says extract() reflects the input; pin it on a known case.
        assert features.extract([1, 2]) == [2, 1]
"""


def test_placeholder():
    # Replace this whole file with real tests. `just test` runs them.
    assert True
