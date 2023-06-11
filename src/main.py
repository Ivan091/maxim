from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import psycopg2
import psycopg2.extras
import colorsys

dbname = "maxim"
user = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
table_name = "Metrix"


class Path:
    def __init__(self, origin: int, destination: int):
        self.origin = origin
        self.destination = destination

    def __str__(self):
        return f'Path({self.origin} -> {self.destination})'

    def __repr__(self):
        str(self)


class PathPiece:
    def __init__(self, origin: int):
        self.origin = origin

    def __str__(self):
        return f'{self.origin} -> {self.origin + 1}'

    def __repr__(self):
        str(self)

    def __eq__(self, other):
        if isinstance(other, PathPiece):
            return self.origin == other.origin
        return False

    def __hash__(self):
        return self.origin


class PathPieceIntensity:
    def __init__(self, path: PathPiece, intensity: int):
        self.path_piece = path
        self.intensity = intensity

    def __str__(self):
        return f'PathPieceIntensity({str(self.path_piece)} <=> {self.intensity})'

    def __repr__(self):
        return str(self)


class HourIntensity:
    def __init__(self, hour: int, intensity: int):
        self.hour = hour
        self.intensity = intensity

    def __str__(self):
        return f'HourIntensity({str(self.hour)} <=> {self.intensity})'

    def __repr__(self):
        return str(self)


class PathProbability:
    def __init__(self, path: PathPiece, probability: float):
        self.path_piece = path
        self.probability = probability

    def __str__(self):
        return f'PathProbability({str(self.path_piece)} <=> {self.probability})'

    def __repr__(self):
        return str(self)


class WeekdayIntensity:
    def __init__(self, day: int, intensity: int):
        self.day = day
        self.intensity = intensity

    def __str__(self):
        return f'Day({str(self.day)}) <=> {self.intensity}'

    def __repr__(self):
        return str(self)


class Sample:
    def __init__(
            self,
            id_: int,
            path: Path,
            seats_number: int,
            time_request):
        self.time_request: datetime = time_request
        self.seats_number = seats_number
        self.path = path
        self.id = id_

    def __str__(self):
        return f"Sample({self.id} {self.path.origin} -> {self.path.destination} {self.time_request})"

    def __repr__(self):
        return str(self)


def read_samples() -> [Sample]:
    cursor = None

    try:
        # Подключение к базе данных
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

        # Создание курсора
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Выполнение SQL-запроса
        cursor.execute(f"SELECT * FROM \"{table_name}\"")

        samples: List[Sample] = []
        rows = cursor.fetchall()
        for row in rows:
            next_sample = map_sample(row)
            samples.append(next_sample)
        return samples

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при подключении к PostgreSQL:", error)

    finally:
        # Закрытие курсора и соединения в блоке finally
        if cursor is not None:
            cursor.close()


def map_sample(row) -> Sample:
    next_sample = Sample(
        row["ID"],
        Path(
            row["Origin"],
            row["Destination"]
        ),
        row["SeatsNumber"],
        row["TimeRequest"],
    )
    return next_sample


def plot(x, y, path: str) -> None:
    fig, ax = plt.subplots()
    plt.xticks(np.arange(min(x), max(x) + 1, 1.0))
    ax.plot(x, y, marker='o', linestyle='-')
    plt.savefig(path)
    plt.close(fig)

def plot_many(x: [], y: [], labeles: [], path: str) -> None:
    colors = np.linspace(0, 0.65, len(x))

    fig, ax = plt.subplots()
    plt.xticks(np.arange(np.min(x), np.max(x) + 1, 1.0))
    for x0, y0, l, c in zip(x, y, labeles, colors):
        ax.plot(x0, y0, marker='o', linestyle='-', label=l, color=colorsys.hsv_to_rgb(c, 1, 0.7))
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", borderaxespad=0)
    plt.savefig(path, bbox_inches="tight")
    plt.close(fig)


def analyze_path_intensity(samples: List[Sample]) -> None:
    origins = np.array([s.path.origin for s in samples])
    x, y = np.unique(origins, return_counts=True)
    plot(x, y, "../analyze_path_intensity")


def analyze_hour_intensity(samples: List[Sample]) -> None:
    hours = np.array([s.time_request.hour for s in samples])
    x, y = np.unique(hours, return_counts=True)
    plot(x, y, "../analyze_hour_intensity")


def analyze_weekday_intensity(samples: List[Sample]) -> None:
    days = np.array([s.time_request.weekday() for s in samples])
    x, y = np.unique(days, return_counts=True)
    plot(x, y, "../analyze_weekday_intensity")


def analyze_math_expectation(samples: List[Sample]) -> None:
    hours = np.array([s.time_request.hour for s in samples])
    hours, hours_count = np.unique(hours, return_counts=True)
    print(hours)

    xs = []
    ys = []
    ls = []
    for i in range(len(hours)):
        h = hours[i]

        filtered = list(filter(lambda x: x.time_request.hour == h, samples))

        origins = np.array([s.path.origin for s in filtered])
        origins, origins_count = np.unique(origins, return_counts=True)
        xs.append(origins)
        ys.append(origins_count)
        ls.append(f"hour {h}")

    plot_many(xs, ys, ls, "../test")


def main():
    samples: List[Sample] = read_samples()
    analyze_path_intensity(samples)
    analyze_hour_intensity(samples)
    analyze_weekday_intensity(samples)
    analyze_math_expectation(samples)


if __name__ == "__main__":
    main()
