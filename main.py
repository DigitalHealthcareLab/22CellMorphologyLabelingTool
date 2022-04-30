import src.labelled_page as labelled_page
import src.labeller_page as labeller_page
from src.multipage import MultiPage


def main():
    app = MultiPage()
    app.add_page("Labeller_page", labeller_page.app)
    app.add_page("Labelled_overview_page", labelled_page.app)
    app.run()


if __name__ == "__main__":
    main()
