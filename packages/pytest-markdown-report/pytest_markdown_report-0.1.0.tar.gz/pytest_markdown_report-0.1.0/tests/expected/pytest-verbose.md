# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/examples.py::test_edge_case FAILED

```python
examples.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
examples.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
examples.py:55: in test_known_bug
    raise ValueError(msg)
E   ValueError: Known issue
```

## Skipped

### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet

## Passes

- tests/examples.py::test_invalid_input[-False]
- tests/examples.py::test_invalid_input[x-True]
- tests/examples.py::test_simple
- tests/examples.py::test_validation_pass
- tests/examples.py::test_critical_path
