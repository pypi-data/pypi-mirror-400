from app.src.my_import import hello_world_string
import webbrowser


def main() -> None:
    print(hello_world_string)
    webbrowser.open("https://www.google.com")
