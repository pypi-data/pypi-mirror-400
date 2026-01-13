from opensemantic import OswBaseModel
from opensemantic.v1 import OswBaseModel as OswBaseModel_v1


def test_opensemantic():

    # Create an instance of OswBaseModel
    model = OswBaseModel()

    # Check if the instance is created successfully
    assert isinstance(
        model, OswBaseModel
    ), "Failed to create an instance of OswBaseModel"

    model_v1 = OswBaseModel_v1()

    assert isinstance(
        model_v1, OswBaseModel_v1
    ), "Failed to create an instance of OswBaseModel_v1"


if __name__ == "__main__":
    test_opensemantic()
    print("All tests passed!")
