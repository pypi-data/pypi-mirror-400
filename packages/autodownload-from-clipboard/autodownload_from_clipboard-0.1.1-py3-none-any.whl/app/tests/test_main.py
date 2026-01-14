from app.src.my_import import hello_world_string


def test_hello_world_string() -> None:
    assert hello_world_string == "Hello World"
