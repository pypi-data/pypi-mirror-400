"""Test basic ANNS functionality."""

import pytest


def test_import():
    """Test that sage_anns can be imported."""
    import sage_anns
    
    assert hasattr(sage_anns, '__version__')
    assert hasattr(sage_anns, 'create_index')
    assert hasattr(sage_anns, 'list_algorithms')


def test_list_algorithms():
    """Test listing algorithms."""
    from sage_anns import list_algorithms
    
    algorithms = list_algorithms()
    assert isinstance(algorithms, list)
    # Initially empty until algorithms are registered
    # assert len(algorithms) >= 0


def test_factory_unknown_algorithm():
    """Test that unknown algorithm raises error."""
    from sage_anns import create_index
    
    with pytest.raises(ValueError, match="Unknown algorithm"):
        create_index("nonexistent_algorithm")
