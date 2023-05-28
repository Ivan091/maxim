from datetime import datetime
from typing import List, Dict

import psycopg2
import psycopg2.extras

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
        return f'PathPiece({self.origin} -> {self.origin + 1})'

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
        return f'{str(self.path_piece)} <=> {self.intensity}'

    def __repr__(self):
        return str(self)


class HourIntensity:
    def __init__(self, hour: int, intensity: int):
        self.hour = hour
        self.intensity = intensity

    def __str__(self):
        return f'Hour({str(self.hour)}) <=> {self.intensity}'

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


def analyze_path_intensity(samples: List[Sample]) -> List[PathPieceIntensity]:
    paths = list(map(lambda x: x.path, samples))
    path_pieces_intensity_dict: Dict[PathPiece, int] = {}
    for path in paths:
        path_piece = PathPiece(path.origin)
        if path_piece in path_pieces_intensity_dict:
            current_val = path_pieces_intensity_dict[path_piece]
            path_pieces_intensity_dict[path_piece] = current_val + 1
        else:
            path_pieces_intensity_dict[path_piece] = 1

    path_piece_intensity: List[PathPieceIntensity] = []
    for (k) in path_pieces_intensity_dict.keys():
        path_piece_intensity.append(PathPieceIntensity(k, path_pieces_intensity_dict[k]))
    return list(sorted(path_piece_intensity, key=lambda x: x.intensity, reverse=True))


def analyze_hour_intensity(samples: List[Sample]) -> List[HourIntensity]:
    hours = list(map(lambda x: x.time_request.hour, samples))
    hour_intensity_dict: Dict[int, int] = {}
    for hour in hours:
        if hour in hour_intensity_dict:
            current_val = hour_intensity_dict[hour]
            hour_intensity_dict[hour] = current_val + 1
        else:
            hour_intensity_dict[hour] = 1

    hour_intensity: List[HourIntensity] = []
    for (k) in hour_intensity_dict.keys():
        hour_intensity.append(HourIntensity(k, hour_intensity_dict[k]))
    return list(sorted(hour_intensity, key=lambda x: x.intensity, reverse=True))


def analyze_weekday_intensity(samples: List[Sample]) -> List[WeekdayIntensity]:
    days = list(map(lambda x: x.time_request.weekday(), samples))
    weekday_intensity_dict: Dict[int, int] = {}
    for day in days:
        if day in weekday_intensity_dict:
            current_val = weekday_intensity_dict[day]
            weekday_intensity_dict[day] = current_val + 1
        else:
            weekday_intensity_dict[day] = 1

    hour_intensity: List[WeekdayIntensity] = []
    for (k) in weekday_intensity_dict.keys():
        hour_intensity.append(WeekdayIntensity(k, weekday_intensity_dict[k]))
    return list(sorted(hour_intensity, key=lambda x: x.intensity, reverse=True))


def main() -> None:
    samples: List[Sample] = read_samples()
    path_piece_intensity: List[PathPieceIntensity] = analyze_path_intensity(samples)
    print(path_piece_intensity)
    hour_intensity: List[HourIntensity] = analyze_hour_intensity(samples)
    print(hour_intensity)
    weekday_intensity: List[WeekdayIntensity] = analyze_weekday_intensity(samples)
    print(weekday_intensity)


if __name__ == "__main__":
    main()
