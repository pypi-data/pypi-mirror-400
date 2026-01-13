"""
TODO: This module must be moved. I have the
'yta-positioning' module in which I work with
position calculations, and maybe this could be
implemented there as this is very similar to the
Map class we have there.

These classes are to store the trajectory that
will be managed by the timeline (or other 
instance related to this) and pass the values
to render to the node that is capable of it. The
trajectory will not be stored by the node.
"""
from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass

import numpy as np

        
@dataclass
class TrajectoryCoordinate:
    """
    Dataclass to store a trajectory coordinate, that is
    a position (x, y), the rotation of the object and some
    aditional parameters.
    """

    def __init__(
        self,
        position: tuple[int, int],
        rotation: int = 0,
        additional_params: dict = {}
    ):
        """
        - The `position` parameter must be an (x, y) position
        in pixels.
        - The `rotation` must be an int in the range [0, 360].
        """
        self.position: tuple[int, int] = position
        """
        The position (x, y) of the center of the item that
        will be moving doing this trajectory.
        """
        self.rotation: int = rotation
        """
        The rotation of the element whose center will be
        positioned in the given `position`.
        """
        self._additional_params: dict = additional_params
        """
        Some additional parameters to include more information
        of the movement.
        """

@dataclass
class TrajectoryCoordinateWithT(TrajectoryCoordinate):
    """
    Dataclass to store a trajectory coordinate, that is
    a position (x, y), the rotation of the object, a time
    moment and some aditional parameters.
    """

    def __init__(
        self,
        position: tuple[int, int],
        t: float,
        rotation: int = 0,
        additional_params: dict = {}
    ):
        super().__init__(
            position = position,
            rotation = rotation,
            additional_params = additional_params
        )

        self.t: float = t
        """
        The time moment in which the center of the object
        must be placed in this position.
        """

@dataclass
class Trajectory:
    """
    Dataclass to store a set of consecutive coordinates
    that build a trajectory for some object. It includes
    the rotation and also can have some aditional
    parameters.
    """

    @property
    def coordinates(
        self
    ) -> list[TrajectoryCoordinate]:
        """
        The coordinates of the trajectory, ordered as they
        were added.
        """
        return self._coordinates

    def __init__(
        self,
        coordinates: list[TrajectoryCoordinate]
    ):
        ParameterValidator.validate_mandatory_list_of_these_instances('coordinates', coordinates, TrajectoryCoordinate)

        self._coordinates: list[TrajectoryCoordinate] = coordinates
        """
        The coordinates in which the center of the object
        that follows the trajectory will be placed.
        """

    def add_coordinate(
        self,
        coordinate: TrajectoryCoordinate
    ) -> 'Trajectory':
        """
        Add a new coordinate to the list.
        """
        ParameterValidator.validate_mandatory_instance_of('coordinate', coordinate, TrajectoryCoordinate)

        self._coordinates.append(coordinate)

        return self
    
@dataclass
class TrajectoryWithT(Trajectory):
    """
    Dataclass to store a set of consecutive coordinates
    that build a trajectory for some object. It includes
    the rotation, the time moment and also can have some
    aditional parameters.
    """
    
    @property
    def min_t(
        self
    ) -> float:
        """
        Get the min `t` of the coordinates of this trajectory.
        """
        return self.coordinates[0].t
    
    @property
    def max_t(
        self
    ) -> float:
        """
        Get the max `t` of the coordinates of this trajectory.
        """
        return self.coordinates[-1].t
    
    @property
    def coordinates(
        self
    ) -> list[TrajectoryCoordinateWithT]:
        """
        The coordinates but ordered by the `t` time moment.
        """
        if not hasattr(self, '_coordinates_ordered_by_t'):
            self._coordinates_ordered_by_t = sorted(self._coordinates, key = lambda coordinate: coordinate.t)

        return self._coordinates_ordered_by_t

    def __init__(
        self,
        coordinates: list[TrajectoryCoordinateWithT]
    ):
        ParameterValidator.validate_mandatory_list_of_these_instances('coordinates', coordinates, TrajectoryCoordinateWithT)

        self._coordinates: list[TrajectoryCoordinateWithT] = coordinates
        """
        The coordinates in which the center of the object
        that follows the trajectory will be placed.
        """

    def add_coordinate(
        self,
        coordinate: TrajectoryCoordinateWithT
    ) -> 'TrajectoryWithT':
        """
        Add a new coordinate to the list.
        """
        ParameterValidator.validate_mandatory_instance_of('coordinate', coordinate, TrajectoryCoordinateWithT)

        self._coordinates.append(coordinate)
        self._coordinates_ordered_by_t = None

        return self

    def get_position_at(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get a coordinate for the `t` time moment provided
        that includes the position (interpolated from the
        ones we actually have in the trajectory) and maybe
        some additional parameters if existing.
        """
        if t <= self.min_t:
            return self._coordinates[0]
        if t >= self.max_t:
            return self._coordinates[-1]

        # Extract the times to be able to search
        times = [
            coordinate.t
            for coordinate in self.coordinates
        ]

        i = np.searchsorted(times, t) - 1

        # This is the factor to interpolate
        interpolation_factor = (t - self.coordinates[i].t) / (self.coordinates[i + 1].t - self.coordinates[i].t)

        return TrajectoryCoordinateWithT(
            # Interpolated position
            position = (1 - interpolation_factor) * self.coordinates[i].position + interpolation_factor * self.coordinates[i + 1].position,
            t = t,
            # Interpolated rotation
            rotation = (1 - interpolation_factor) * self.coordinates[i].rotation + interpolation_factor * self.coordinates[i + 1].rotation,
            # TODO: By now we are providing the additional
            # parameters of the previous coordinate
            additional_params = self.coordinates[i]._additional_params
        )