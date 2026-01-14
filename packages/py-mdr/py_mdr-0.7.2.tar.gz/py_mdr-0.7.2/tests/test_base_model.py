from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


def test_base_model_cleanup():
    test_data = {
        "a": "b",
        "c": None,
        "d": [],
        "e": {},
        "f": [{"g": None, "h": []}, {}],
        "i": {
            "j": None,
            "k": [],
            "l": {
                "m": None,
                "n": "o"
            }
        },
        "p": ["q", "r"]
    }

    expected_data = {
        "a": "b",
        "i": {
            "l": {
                "n": "o"
            }
        },
        "p": ["q", "r"]
    }

    BaseModel._cleanup_dict_values(test_data)
    assert test_data == expected_data


@dataclass
class TestModel(BaseModel):
    __test__ = False
    x: str = None
    y: int = None


def test_base_model():
    model = TestModel()
    model.x = "Hello"

    assert model.as_dict() == {"x": "Hello"}
    assert model.as_dict(False) == {"x": "Hello", "y": None}
