from py_mdr.helper import flatten_dict


def test_flatten_dict():
    # No changes
    simple = {
        "a": "value_a",
        "b": "value_b"
    }

    assert flatten_dict(simple) == simple

    # Simple nested
    flatten_simple = {
        "a": "value_a",
        "b": {
            "c": "value_c",
            "d": "value_d"
        },
        "e": {
            "f": "value_f",
            "g": "value_g"
        }
    }

    expected_flatten_simple = {
        "a": "value_a",
        "b.c": "value_c",
        "b.d": "value_d",
        "e.f": "value_f",
        "e.g": "value_g",
    }

    assert flatten_dict(flatten_simple) == expected_flatten_simple

    # Complex nested
    flatten_complex = {
        "a": "value_a",
        "b": {
            "c": {
                "d": "value_d",
                "e": "value_e"
            },
            "f": {
                "g": {
                    "h": "value_h",
                    "i": "value_i"
                },
                "j": "value_j"
            }
        }
    }

    expected_flatten_complex = {
        "a": "value_a",
        "b_c_d": "value_d",
        "b_c_e": "value_e",
        "b_f_g_h": "value_h",
        "b_f_g_i": "value_i",
        "b_f_j": "value_j"
    }

    assert flatten_dict(flatten_complex, separator="_") == expected_flatten_complex
