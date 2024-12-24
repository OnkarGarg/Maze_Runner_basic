import csv
import os
import uuid
from pstats import Stats

from maze import Maze
import argparse
import cProfile as cp


def maze_reader(maze_file: str) -> Maze:
    """
    Reads the .mz maze file and generates a Maze object.

    :param maze_file: File name.
    :return: The generated Maze object.
    """
    input_lines = []

    # Tries to read the .mz file.
    try:
        with open(maze_file, 'r') as file:
            for line in file:
                line = line.strip()
                input_lines.append(line)
    except FileNotFoundError:
        raise IOError

    # Checks if the shape of the maze is correct
    line_lengths = set(len(line) for line in input_lines)
    if len(line_lengths) != 1:
        raise ValueError("The maze file may be missing a column.")
    if len(input_lines) % 2 != 1:
        raise ValueError("The maze file may be missing a row.")

    # Checks if the outer horizontal walls are valid.
    if not all(c == "#" for c in input_lines[0]) or not all(c == "#" for c in input_lines[-1]):
        raise ValueError("There is an incorrect character in at least one or more of the horizontal outer walls.")

    height = len(input_lines) // 2
    width = len(input_lines[0]) // 2

    # Checks if the outer vertical walls are valid and if the characters in the file are valid ('#' or '.').
    for i, line in enumerate(input_lines):
        if len(line) != 2 * width + 1 or not line.startswith('#') or not line.endswith('#'):
            raise ValueError(f"Line {i + 1} is not a valid line as it's missing the outer wall.")
        for j, c in enumerate(line):
            if c not in "#.":
                raise ValueError(f"Invalid character at position {j + 1} in line {i + 1}.")

    maze = Maze(width=width, height=height)  # Creates the Maze object.

    try:
        # Tries to add the horizontal walls to the Maze object
        # and makes sure that the intersections are correct (i.e. are '#').
        for y in range(height + 1):
            horizontal_line = input_lines[2 * y]
            for x in range(width):
                if horizontal_line[2 * x] != '#':
                    raise ValueError(f"The wall intersections in the file are incorrect."
                                     f" The character at {y * 2 + 1}:{x * 2 + 1} seems wrong. It should be a '#'.")
                if horizontal_line[2 * x + 1] == '#':
                    maze.add_horizontal_wall(x, height - y)

        # Tries to add the horizontal walls to the Maze object
        for y in range(height):
            vertical_line = input_lines[2 * y + 1]
            for x in range(width + 1):
                if vertical_line[2 * x] == '#':
                    maze.add_vertical_wall(height - y - 1, x)
    except IndexError:
        raise ValueError("There is something wrong with the maze file.")

    return maze


def build_files(file_name: str, exploration_data: list[tuple[str, str, str, str]], final_path: list[tuple[int, int]], run_id: str) -> None:
    """
    Builds the exploration.csv and statistics.txt files with the maze run data.

    :param file_name: The name of the maze file.
    :param exploration_data: The exploration data collected by the runner.
    :param final_path: The final/shortest path discovered by the runner.
    """

    try:
        os.mkdir(run_id)
    except FileExistsError:
        pass

    # Creates the exploration.csv and writes the required data into it.
    with open(f"{run_id}\exploration.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(exploration_data)

    # Creates the statistics.txt and writes the required data into it.
    with open(f"{run_id}\statistics.txt", "w") as file:
        file.write(file_name + "\n")
        file.write(str((len(exploration_data) - 1) / 4 + (len(final_path))) + "\n")
        file.write(str(len(exploration_data) - 1) + "\n")
        file.write(str(final_path).replace("[", "").replace("]", "") + "\n")
        file.write(str(len(final_path)))


# Allows this to be run from the terminal.
if __name__ == "__main__":

    # Creates a parser enabling arguments from terminal.
    parser = argparse.ArgumentParser(description="ECS Maze Runner")

    parser.add_argument("--starting", help='The starting position, e.g., "2, 1"', default=None)
    parser.add_argument("--goal", help='The goal position, e.g., "4, 5"', default=None)
    parser.add_argument("--save_images", help='Saves an image of the mind maze at each step (negatively influences '
                                              'speed).', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--display_images", help='Displays an image of the mind maze at each step'
                                                 ' (negatively influences speed).',
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--display_time", help='The amount of time the image is displayed.', default=1.)
    parser.add_argument("maze", help='The name of the maze file, e.g., maze1.mz')

    args = parser.parse_args()

    run_id = args.maze + "_" + str(uuid.uuid4())

    maze = maze_reader(args.maze)
    maze.run_id = run_id

    # Ensures that the starting coordinates from the terminal are in a valid format.
    try:
        if args.starting is not None:
            starting: tuple[int, int] = (tuple(int(x) for x in args.starting.split(", "))[0], tuple(int(x) for x in args.starting.split(", "))[1])
            if starting[0] > maze.width - 1 or starting[0] < 0 or starting[1] > maze.height - 1 or starting[1] < 0:
                print("The starting coordinates are out of bounds. Using default starting coordinates of '0, 0'.")
        else:
            starting = (0, 0)

    except ValueError:
        print("One or more of the elements provided in the starting coordinates can not be converted into integers. "
              "Using default starting coordinates of '0, 0'.")
        starting = (0, 0)
    except TypeError:
        print("The starting coordinates provided are not in the correct format, i.e., '2, 1'. Using default starting "
              "coordinates of '0, 0'.")
        starting = (0, 0)

    # Ensures that the goal coordinates from the terminal are in a valid format.
    try:
        if args.goal is not None:
            goal: tuple[int, int] = (tuple(int(x) for x in args.goal.split(", "))[0], tuple(int(x) for x in args.goal.split(", "))[1])
            if goal[0] > maze.width - 1 or goal[0] < 0 or goal[1] > maze.height - 1 or goal[1] < 0:
                print("The goal coordinates are out of bounds. Using default goal coordinates of '0, 0'.")
                goal = (maze.width - 1, maze.height - 1)
        else:
            goal = (maze.width - 1, maze.height - 1)

    except ValueError:
        print("One or more of the elements provided in the goal coordinates can not be converted into integers. Using "
              "default goal coordinates of 'width - 1, height - 1'.")
        goal = (maze.width - 1, maze.height - 1)

    except TypeError:
        print("The goal coordinates provided are not in the correct format, i.e., '2, 1'. Using default goal "
              "coordinates of 'width - 1, height - 1'.")
        goal = (maze.width - 1, maze.height - 1)

    # Sets the inputted arguments about rendering.
    maze.render_settings = args.save_images, args.display_images, float(args.display_time)

    # Starts the profiler.
    pr = cp.Profile()
    pr.enable()

    final_path = maze.shortest_path(starting=starting, goal=goal)
    build_files(args.maze, maze.exploration_data, final_path, run_id)

    pr.disable()
    stats = Stats(pr)
    stats.sort_stats('tottime').print_stats(10)  # Prints the 15 most time-consuming functions.
