from dronebuddylib.atoms.navigation.waypointnavigation.i_navigation import INavigation


class NavigationWaypointImpl(INavigation):
    def map_location(self) -> list:
        pass

    def navigate(self) -> list:
        pass

    def navigate_to_waypoint(self, location, destination_waypoint) -> list:
        pass

    def get_required_params(self) -> list:
        pass

    def get_optional_params(self) -> list:
        pass

    def get_class_name(self) -> str:
        pass

    def get_algorithm_name(self) -> str:
        pass

    def __init__(self):
        pass
