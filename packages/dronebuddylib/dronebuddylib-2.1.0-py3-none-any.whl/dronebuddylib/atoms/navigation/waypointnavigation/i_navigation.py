from abc import abstractmethod

from dronebuddylib.models.i_dbl_function import IDBLFunction


class INavigation(IDBLFunction):

    def __init__(self):
        pass

    @abstractmethod
    def map_location(self) -> list:
        pass

    @abstractmethod
    def navigate(self) -> list:
        pass

    @abstractmethod
    def navigate_to_waypoint(self, location, destination_waypoint) -> list:
        pass
