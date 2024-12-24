from typing import Any, TypedDict

Runner = TypedDict("Runner", {"x": int, "y": int, "orientation": str})
def create_runner(x: int = 0, y: int = 0, orientation: str = "N") -> Runner:
    """
        Creates the runner with the provided x and y coordinates and orientates itself in the provided orientation.
        :param x: The x-coordinate.
        :param y: The y-coordinate.
        :param orientation: The orientation.
        :return: The runner with specified x, y, and orientation parameters.
    """
    return {"x": x, "y": y, "orientation": orientation}


def get_x(runner: Runner) -> int:
    """
        Gets the x-coordinate of the provided runner.
        :param: runner: The runner.
        :return: The x-coordinate of the provided runner.
    """
    return int(runner["x"])


def get_y(runner: Runner) -> int:
    """
        Gets the y-coordinate of the provided runner.
        :param: runner: The runner.
        :return: The y-coordinate of the provided runner.
    """
    return int(runner["y"])


def get_orientation(runner: Runner) -> str:
    """
        Gets the orientation of the provided runner.
        :param: runner: The runner.
        :return: The orientation of the provided runner.
    """
    return str(runner["orientation"])


def turn(runner: Runner, direction: str) -> Runner:
    """
        Turns the runner in the specified direction ("Left" or "Right").
        :param runner: The runner.
        :param direction: The direction to turn the runner.
        :return: The runner with the updated orientation.
    """
    new_orientations = orientation_options(runner)
    if direction == "Left":
        runner["orientation"] = new_orientations[0]
    if direction == "Right":
        runner["orientation"] = new_orientations[2]
    return runner


def orientation_options(runner: Runner) -> tuple[str, str, str]:
    """
        Provides a tuple structured as (orientation to the left, current orientation, orientation to the right).
        :param runner: The runner.
        :return: The structured tuple with the relevant orientations.
    """
    orientations = ("N", "E", "S", "W")
    current_orientation = get_orientation(runner)
    current_orientation_index = orientations.index(current_orientation)
    new_orientations = (orientations[current_orientation_index - 1], current_orientation,
                        orientations[(current_orientation_index + 1) % len(orientations)])
    return new_orientations


def forward(runner: Runner) -> Runner:
    """
        Moves the runner ahead by one cell (in the direction its facing).
        :param runner: The runner.
        :return: The runner with the updated location (x and y coordinates).
    """
    orientation = get_orientation(runner)
    if orientation == "N":
        runner["y"] += 1
    elif orientation == "S":
        runner["y"] -= 1
    elif orientation == "E":
        runner["x"] += 1
    elif orientation == "W":
        runner["x"] -= 1
    return runner
