from app.ingestion.adapters.anilist import AniListProvider
from app.ingestion.adapters.tvmaze import TVmazeProvider
from app.ingestion.adapters.wikidata import WikidataProvider
from app.ingestion.adapters.kaggle import KaggleDatasetImporter
from app.ingestion.adapters.reddit import RedditProvider
from app.ingestion.adapters.x_twitter import XTwitterProvider
from app.ingestion.adapters.tmdb import TMDBProvider

class ProviderRegistry:
    def __init__(self):
        self.anilist = AniListProvider()
        self.tvmaze = TVmazeProvider()
        self.wikidata = WikidataProvider()
        self.kaggle = KaggleDatasetImporter()
        self.reddit = RedditProvider()
        self.x = XTwitterProvider()
        self.tmdb = TMDBProvider()

    def get_all_providers(self):
        return [
            self.anilist,
            self.tvmaze,
            self.wikidata,
            self.kaggle,
            self.reddit,
            self.x,
            self.tmdb
        ]

registry = ProviderRegistry()
