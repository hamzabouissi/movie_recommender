from typing import Dict, List, NamedTuple, Optional
from click.types import DateTime
import typer
import sys
import requests
from collections import namedtuple
from datetime import date


class Recommender:
    moods = {
        "happy": "I'm happy to hear that",
        "sad": "I'm sorry to hear that, maybe I can let you feel better",
        "stable": "let's make you happy",
        "on love": "That's a great news,I will recommend you "
    }
    baseurl = "https://api.themoviedb.org/3"
    genres: List = []
    RDate = namedtuple('RDate', ['message', 'query'])
    GenreNamed = namedtuple("GenreNamed", ["title", "query"])

    def __init__(self, token: str):
        self.year = None
        self.token = token
        self.his_genres: List = []
        self.mood = ""
        self.adult = ""
        self.release_date: str = ""
        self.query: Dict = {"api_key": self.token}
        self.__generate_genres()

    def __generate_genres(self):
        r = requests.get(f"{self.baseurl}/genre/movie/list?api_key={self.token}")
        result = r.json()
        for genre in result['genres']:
            self.genres.append(self.GenreNamed(genre["name"], str(genre['id'])))

    def __generate_release_date_questions(self) -> List[RDate]:
        this_year = date.today().year
        questions = [
            self.RDate(f"{this_year}<year", {"release_date.lte": date.today().isoformat()}),
            self.RDate(f"{this_year}<year>2010 , You Taste is getting better",
                       {"release_date.lte": date.today().isoformat(),
                        "release_date.gte": "2010-01-01"
                        }
                       ),
            self.RDate("2010<year>1990 , old but gold",
                       {"release_date.lte": "2009-01-01", "release_date.gte": "1991-01-01"}),
            self.RDate("<1990 , too old but A Legend", {"release_date.lte": "1990-01-01"}),
            # self.RDate("Custom Year", {"release_date.lte": None})#, "release_date.gte": self.year}),
        ]
        return questions

    def mood_question(self):
        typer.echo("Tell me, what's your mood for today")
        typer.echo("1- Happy")
        typer.echo("2- Sad")
        typer.echo("2- stable")
        typer.echo("2- on Love")
        mood: str = typer.prompt("")
        mood_message: Optional[str] = self.moods.get(mood.lower(), None)
        if not mood_message:
            typer.echo("I think I didn't understand your mood, I wish you can provide one of the above")
            raise typer.Abort()
        else:
            self.mood = mood

    def genre_question(self):
        typer.echo("Our genre List:")
        for index, g in enumerate(self.genres):
            typer.echo(f"{index + 1}- {g.title}")
        choices = typer.prompt("Pick Your Choices friend seperated by ',' example: 1,6 :)")
        try:
            choices = list(map(int, choices.split(",")))
        except ValueError:
            raise typer.Abort("invalid choices")
        self.__verify_genre(choices)
        genres = []
        for index in choices:
            genres.append(self.genres[index].query)
        self.his_genres = {"with_genres": ",".join(genres)}
        self.query.update(self.his_genres)

    def __verify_genre(self, genres):
        max_g = max(genres)
        min_g = min(genres)
        if min_g < 0 or max_g > len(self.genres):
            typer.echo(f"One The Genres is not available sadly")
            raise typer.Abort()

    def release_date_question(self):
        typer.echo("What release date are you interested in ")
        questions = self.__generate_release_date_questions()
        for n, qs in enumerate(questions):
            typer.echo(f"-{n + 1}: {qs.message} ")
        choice_index = int(typer.prompt(""))
        # if choice_index == 5:
        #     self.year = int(typer.prompt("Year: ?"))
        #     date(self.year, 1, 1).isoformat()
        choice = questions[choice_index - 1]
        self.release_date = choice.query
        self.query.update(self.release_date)

    def adult_question(self):
        choice = typer.confirm("Do You like Some Aduly Stuff on There  ?!")
        self.adult = {"include_adult": choice}
        self.query.update(self.adult)
        typer.echo("Okey dokie Friend")

    def favorite_actors_question(self):
        # typer.secho(f"Welcome here Friend")
        pass
    def search(self):
        typer.secho(f"Welcome here Friend", fg=typer.colors.MAGENTA)
        typer.secho("let's find your movie type :)", fg=typer.colors.MAGENTA)
        self.mood_question()
        self.genre_question()
        self.release_date_question()
        self.adult_question()
        self.favorite_actors_question()
        self.request()

    def request(self):
        next_page = True

        while next_page:
            res = requests.get(f"{self.baseurl}/discover/movie", params=self.query)
            movies = res.json()
            page = movies['page']
            pages = movies['total_pages']
            for movie in movies['results']:
                print(movie['title'], movie['release_date'])
            typer.secho(f"=====> Result {page} of {pages}", fg=typer.colors.RED)
            if page == pages:
                typer.Abort()
            next_page = typer.confirm("Do u wanna Continue")
            self.query.update({"page": page + 1})
        typer.secho("See you on another tripe :)", fg=typer.colors.BLUE)


def main():
    r = Recommender("317f14dfb95162ff57d20a4e44bdcc24")
    r.search()


if __name__ == "__main__":
    typer.run(main)
