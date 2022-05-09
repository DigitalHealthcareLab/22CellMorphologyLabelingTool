import src.center_label_page as center_label_page
import src.labelled_page as labelled_page
import src.labeller_page as labeller_page
from src.gdrive import GDriveCredential, GDriveDownloader
from src.multipage import MultiPage


def main():
    downloader = GDriveDownloader(GDriveCredential().credentials)

    app = MultiPage()
    app.add_page("Quality Labeller page", labeller_page.app)
    app.add_page("Center Labeller page", center_label_page.app)
    app.add_page("Labelled_overview_page", labelled_page.app)

    app.run()


if __name__ == "__main__":
    main()
