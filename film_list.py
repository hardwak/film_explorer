from datetime import timedelta, datetime
import pandas as pd

from data_scraper import get_film_data


class FilmList:

    def __init__(self):
        self.film_data = get_film_data()

    def __len__(self):
        return len(self.film_data)

    def __iter__(self):
        return iter(self.film_data)

    def search_film(self, film_name: str):
        search_results = self.film_data[self.film_data['Title'].str.contains(film_name)]
        return search_results

    def sort_by(self, column: str, ascending=True):
        valid_columns = self.film_data.columns.tolist()
        if column not in valid_columns:
            raise ValueError(f'The column {column} does not exist')

        return self.film_data.sort_values(by=column, ascending=ascending)

    def filter_by(self,
                  date_from=datetime(2014, 1, 1),
                  date_to=None,
                  genre=None,
                  runtime_from=None,
                  runtime_to=None,
                  language=None,
                  film_type=None,
                  rating_from=0.0,
                  rating_to=10.0):
        films = self.film_data

        if date_from and date_to and date_from > date_to:
            raise ValueError('\'Date from\' cant be greater than \'Date to\'')
        if date_from:
            films = films[films['Release date'] >= date_from]
        if date_to:
            films = films[films['Release date'] <= date_to]

        if genre in films['Genre'].unique():
            films = films[films['Genre'].str.contains(genre, case=False, na=False)]
        elif genre is not None:
            raise ValueError(f'Genre {genre} does not exist in film list')

        if runtime_from and runtime_to and runtime_from > runtime_to:
            raise ValueError('\'Runtime from\' cant be greater than \'Runtime to\'')
        if runtime_from:
            films = films[films['Runtime'] >= runtime_from]
        if runtime_to:
            films = films[films['Runtime'] <= runtime_to]

        if language in films['Language'].unique():
            films = films[films['Language'].str.contains(language, case=False, na=False)]
        elif language is not None:
            raise ValueError(f'Language {language} does not exist in film list')

        if film_type in films['Type'].unique():
            films = films[films['Type'].str.contains(film_type, case=False, na=False)]
        elif film_type is not None:
            raise ValueError(f'Film type {film_type} does not exist in film list')

        if rating_from > rating_to:
            raise ValueError('\'Rating from\' cant be greater than \'Rating to\'')
        if rating_from >= 0.0:
            films = films[films['Rating'] >= rating_from]
        if rating_to <= 10.0:
            films = films[films['Rating'] <= rating_to]

        films['Runtime'] = films['Runtime'].apply(lambda td: f'{td.seconds // 3600} h {td.seconds // 60 % 60} min')

        return films


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    film_list = FilmList()
    print(film_list.filter_by(date_from=datetime(2020, 1, 1),
                              date_to=datetime(2022, 12, 31),
                              runtime_from=timedelta(hours=0, minutes=2),
                              runtime_to=timedelta(hours=1, minutes=2),
                              genre='Documentary',
                              language='English',
                              film_type='Documentaries',
                              rating_from=6.5,
                              rating_to=7.9
                              ))
    print(film_list.film_data.info())