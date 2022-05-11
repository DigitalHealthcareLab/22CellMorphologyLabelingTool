import src.center_labeller_page as center_labeller_page
import src.labelled_page as labelled_page
import src.quality_labeller_page as quality_labeller_page
from src.multipage import MultiPage

# TODO: downloader inject to each page


def main():
    app = MultiPage()
    app.add_page("Quality Labeller page", quality_labeller_page.app)
    app.add_page("Center Labeller page", center_labeller_page.app)
    app.add_page("Labelled_overview_page", labelled_page.app)

    app.run()


if __name__ == "__main__":
    main()
