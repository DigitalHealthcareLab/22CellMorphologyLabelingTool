import src.labeller as labeller
from src.multipage import MultiPage


def main():
    app = MultiPage()
    app.add_page('Labeller', labeller.app)
    app.run()


if __name__ == "__main__":
    main()
