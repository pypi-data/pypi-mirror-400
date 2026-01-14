def test_import_performance_table():
    try:
        from mcda import PerformanceTable  # noqa: F401
    except ImportError:
        assert False
    finally:
        assert True


def test_import_transform():
    try:
        from mcda import transform  # noqa: F401
    except ImportError:
        assert False
    finally:
        assert True


def test_import_normalize():
    try:
        from mcda import normalize  # noqa: F401
    except ImportError:
        assert False
    finally:
        assert True
