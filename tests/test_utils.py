from app.utils import compute_age_group, compute_detailed_age_group

# ============================================================================
# Tests for legacy compute_age_group (backward compatibility)
# ============================================================================

def test_compute_age_group_child():
    assert compute_age_group(5) == "child"

def test_compute_age_group_adult():
    assert compute_age_group(30) == "adult"

def test_compute_age_group_senior():
    assert compute_age_group(80) == "senior"

def test_compute_age_group_none():
    assert compute_age_group(None) == "unknown"

def test_compute_age_group_invalid():
    assert compute_age_group("abc") == "unknown"


# ============================================================================
# Tests for compute_detailed_age_group (enhanced analytics)
# ============================================================================

def test_detailed_age_group_children():
    """Test age group for children under 13."""
    assert compute_detailed_age_group(5) == "<13"
    assert compute_detailed_age_group(10) == "<13"
    assert compute_detailed_age_group(12) == "<13"


def test_detailed_age_group_adolescents():
    """Test age group for adolescents 13-17."""
    assert compute_detailed_age_group(13) == "13-17"
    assert compute_detailed_age_group(15) == "13-17"
    assert compute_detailed_age_group(17) == "13-17"


def test_detailed_age_group_young_adults():
    """Test age group for young adults 18-24."""
    assert compute_detailed_age_group(18) == "18-24"
    assert compute_detailed_age_group(21) == "18-24"
    assert compute_detailed_age_group(24) == "18-24"


def test_detailed_age_group_adults():
    """Test age group for adults 25-34."""
    assert compute_detailed_age_group(25) == "25-34"
    assert compute_detailed_age_group(30) == "25-34"
    assert compute_detailed_age_group(34) == "25-34"


def test_detailed_age_group_middle_age():
    """Test age group for middle age 35-44."""
    assert compute_detailed_age_group(35) == "35-44"
    assert compute_detailed_age_group(40) == "35-44"
    assert compute_detailed_age_group(44) == "35-44"


def test_detailed_age_group_mature_adults():
    """Test age group for mature adults 45-54."""
    assert compute_detailed_age_group(45) == "45-54"
    assert compute_detailed_age_group(50) == "45-54"
    assert compute_detailed_age_group(54) == "45-54"


def test_detailed_age_group_pre_senior():
    """Test age group for pre-seniors 55-64."""
    assert compute_detailed_age_group(55) == "55-64"
    assert compute_detailed_age_group(60) == "55-64"
    assert compute_detailed_age_group(64) == "55-64"


def test_detailed_age_group_seniors():
    """Test age group for seniors 65+."""
    assert compute_detailed_age_group(65) == "65+"
    assert compute_detailed_age_group(70) == "65+"
    assert compute_detailed_age_group(85) == "65+"
    assert compute_detailed_age_group(100) == "65+"


def test_detailed_age_group_edge_cases():
    """Test edge cases and boundaries."""
    # Boundary testing
    assert compute_detailed_age_group(0) == "<13"
    assert compute_detailed_age_group(120) == "65+"
    
    # None value
    assert compute_detailed_age_group(None) == "unknown"
    
    # Invalid string
    assert compute_detailed_age_group("abc") == "unknown"
    assert compute_detailed_age_group("") == "unknown"
    
    # Out of range
    assert compute_detailed_age_group(-5) == "unknown"
    assert compute_detailed_age_group(150) == "unknown"


def test_detailed_age_group_type_handling():
    """Test type conversion and error handling."""
    # String numbers should convert
    assert compute_detailed_age_group("25") == "25-34"
    assert compute_detailed_age_group("45") == "45-54"
    
    # Float should convert
    assert compute_detailed_age_group(30.5) == "25-34"
    assert compute_detailed_age_group(30.9) == "25-34"


def test_backward_compatibility():
    """Ensure new function doesn't break existing age group logic."""
    # The detailed function should provide more granularity
    # but should map to legacy categories consistently
    
    test_ages = {
        10: ("<13", "child"),
        16: ("13-17", "child"),
        20: ("18-24", "adult"),
        30: ("25-34", "adult"),
        40: ("35-44", "adult"),
        50: ("45-54", "adult"),
        60: ("55-64", "adult"),
        70: ("65+", "senior"),
    }
    
    for age, (expected_detailed, expected_legacy) in test_ages.items():
        assert compute_detailed_age_group(age) == expected_detailed
        assert compute_age_group(age) == expected_legacy
