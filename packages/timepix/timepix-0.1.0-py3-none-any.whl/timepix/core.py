import time
from typing import Optional

from .exceptions import IncorrectPointTypeError, IncorrectPointValueError, \
    LastPointNotSetError, PointNotFoundError


class TimePix:

    __slots__ = ['__last_point', '__points']
    __last_point: Optional[tuple[str | int, float]]
    __points: dict[str | int, float]

    def __init__(self):
        self.__last_point: Optional[tuple[str | int, float]] = None
        self.__points = {}

    def set_point(self, name: str = None):
        if name is not None:
            name = self.__check_name(name)
        else:
            name = 0
        current_time = time.perf_counter()
        self.__points[name] = current_time
        self.__set_last_point((name, current_time))

    def from_point(self, name: str, round_nums: int = 7, verbose: bool = True) -> float:
        name = self.__check_name(name)
        diff = self.__get_diff(time.perf_counter(), self.__get_point(name), round_nums)
        if verbose:
            self.__print_time(name, diff)
        return diff

    def from_last_point(self, round_nums: int = 7, verbose: bool = True) -> float:
        if self.__last_point is None:
            raise LastPointNotSetError('The last point is not set')

        name, lp_time = self.__last_point
        diff = self.__get_diff(lp_time, time.perf_counter(), round_nums)
        if verbose:
            self.__print_time(name, diff)
        return diff

    def between_points(
        self,
        first_point_name: str,
        second_point_name: str,
        round_nums: int = 7,
        verbose: bool = True
    ) -> float:
        first_point_name = self.__check_name(first_point_name)
        second_point_name = self.__check_name(second_point_name)
        diff = self.__get_diff(
            self.__get_point(first_point_name),
            self.__get_point(second_point_name),
            round_nums
        )
        if verbose:
            self.__print_between(first_point_name, second_point_name, diff)
        return diff

    def __set_last_point(self, point: tuple[str | int, float]):
        self.__last_point = point

    def __get_diff(self, diff_from: float, diff_to: float, round_nums: int) -> float:
        if not isinstance(round_nums, int) or round_nums < 0:
            raise ValueError('round_nums must be a non-negative integer')
        return round(abs(diff_to - diff_from), round_nums)

    def __print_time(self, name: str | int, diff: float):
        if name == 0:
            print(f'Time from point: {diff}s.')
            return
        print(f'Time from point "{name}": {diff}s.')

    def __print_between(self, first_point_name: str, second_point_name: str,  diff: float):
        print(f'Time between "{first_point_name}" and "{second_point_name}" is {diff}s.')

    def __get_point(self, name: str) -> float:
        if name not in self.__points:
            raise PointNotFoundError(f'TimePix point "{name}" does not exist in saved points')
        return self.__points[name]

    def __check_name(self, name: str) -> str:
        if not isinstance(name, str):
            raise IncorrectPointTypeError('TimePix point name must be a string')
        if len(name) < 1:
            raise IncorrectPointValueError('TimePix point name length must be >= 1')
        return name
