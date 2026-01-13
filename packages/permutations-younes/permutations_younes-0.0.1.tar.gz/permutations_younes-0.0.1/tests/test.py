import pytest
from permutations_younes.permutations import permutations


class TestPermutationsBasic:
    """Test basic functionality of the permutations function."""

    def test_single_element(self):
        """Test permutations of a single element."""
        result = permutations([1], 1)
        expected = [[1]]
        assert result == expected

    def test_two_elements(self):
        """Test permutations of two elements."""
        result = permutations([1, 2], 2)
        assert len(result) == 2
        assert [1, 2] in result
        assert [2, 1] in result

    def test_three_elements(self):
        """Test permutations of three elements."""
        result = permutations([1, 2, 3], 3)
        assert len(result) == 6  # 3! = 6
        
        expected_perms = [
            [1, 2, 3],
            [1, 3, 2],
            [2, 1, 3],
            [2, 3, 1],
            [3, 1, 2],
            [3, 2, 1],
        ]
        
        for perm in expected_perms:
            assert perm in result

    def test_four_elements(self):
        """Test permutations of four elements."""
        result = permutations([1, 2, 3, 4], 4)
        assert len(result) == 24  # 4! = 24


class TestPermutationsTypes:
    """Test permutations with different data types."""

    def test_string_elements(self):
        """Test permutations with string elements."""
        result = permutations(['a', 'b'], 2)
        assert len(result) == 2
        assert ['a', 'b'] in result
        assert ['b', 'a'] in result

    def test_mixed_elements(self):
        """Test permutations with mixed data types."""
        result = permutations(['1', '2', '3'], 3)
        assert len(result) == 6


class TestPermutationsUniqueness:
    """Test uniqueness properties of generated permutations."""

    def test_all_permutations_unique(self):
        """Test that all generated permutations are unique."""
        result = permutations([1, 2, 3], 3)
        unique_result = [tuple(perm) for perm in result]
        assert len(unique_result) == len(set(unique_result))

    def test_no_duplicates_in_result(self):
        """Test that no permutation appears twice."""
        result = permutations([1, 2, 3, 4], 4)
        result_tuples = [tuple(perm) for perm in result]
        assert len(result_tuples) == len(set(result_tuples))


class TestPermutationsIntegrity:
    """Test data integrity of generated permutations."""

    def test_each_permutation_has_correct_length(self):
        """Test that each permutation has the correct length."""
        k = 3
        result = permutations([1, 2, 3], k)
        for perm in result:
            assert len(perm) == k

    def test_permutations_contain_all_original_elements(self):
        """Test that each permutation contains all original elements."""
        lst = [1, 2, 3]
        result = permutations(lst.copy(), 3)
        for perm in result:
            assert sorted(perm) == sorted(lst)

    def test_permutation_elements_match_input(self):
        """Test that permutation elements match the input list."""
        lst = ['x', 'y', 'z']
        result = permutations(lst.copy(), 3)
        for perm in result:
            assert sorted(perm) == sorted(lst)


@pytest.mark.parametrize("n,expected_count", [
    (1, 1),
    (2, 2),
    (3, 6),
    (4, 24),
    (5, 120),
])
def test_permutation_count(n, expected_count):
    """Test that the correct number of permutations are generated."""
    lst = list(range(1, n + 1))
    result = permutations(lst, n)
    assert len(result) == expected_count