import os
from typing import Optional

import matplotlib.pyplot as plt
from alive_progress import alive_bar
from matplotlib import patches

from runner import create_runner, get_x, get_y, get_orientation, turn, forward, orientation_options, Runner


class Maze:
    """
    A class representing a maze. It contains methods for adding walls, getting walls, sensing walls, moving the runner,
    exploring the maze, finding the shortest path, rendering the maze and getting the maze dimensions.
        :ivar _width: The width of the maze.
        :ivar _height: The height of the maze.
        :ivar _h_walls: The set that stores all the horizontal walls (x-coordinate, horizontal line).
        :ivar _v_walls: The set that stores all the vertical walls (vertical line, y-coordinate).
        :ivar _path: The path of the runner's exploration through the maze.
        :ivar _exploration_data: The data of the runner's exploration through the maze.
        :ivar render_settings: The settings for rendering the maze (save the maze, show the maze, display duration).
        :ivar prev_runner: The previous runner coordinates.
        :ivar run_id: The unique run ID.
    """

    def __init__(self, width: int = 5, height: int = 5):
        """
        Initializes a Maze object of specified size.
        :param width: The width of the maze (default = 5).
        :param height: The height of the maze (default = 5).
        """
        # Initializing the class variables
        self._width = width
        self._height = height
        self._h_walls = set()
        self._v_walls = set()
        self._path: list[tuple[int, int]] = []
        self._exploration_data = [("Step", "x-coordinate", "y-coordinate", "Actions")]
        self.render_settings = (False, False, 1.)
        self.prev_runner: tuple[int, int]
        self.run_id = ""

        # Adds the outer vertical walls to the v_walls set
        for i in range(height):
            self._v_walls.add((0, i))
            self._v_walls.add((width, i))

        # Adds the outer horizontal walls to the h_walls set
        for i in range(width):
            self._h_walls.add((i, 0))
            self._h_walls.add((i, height))

    @property
    def width(self) -> int:
        """
        :return: width.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        :return: height.
        """
        return self._height

    @property
    def h_walls(self) -> set[tuple[int, int]]:
        """
        :return: Horizontal walls.
        """
        return self._h_walls

    @property
    def v_walls(self) -> set[tuple[int, int]]:
        """
        :return: Vertical walls.
        """
        return self._v_walls

    @property
    def path(self) -> list[tuple[int, int]]:
        """
        :return: Path.
        """
        return self._path

    # @path.setter
    # def path(self, value: tuple[int, int]) -> None:
    #     """
    #     :param value: The value is added to path.
    #     """
    #     (self._path.append(value)

    @path.setter
    def path(self, path: list[tuple[int, int]]) -> None:
        """
        :param path: The path is set to the provided path.
        """
        self._path = path

    @property
    def exploration_data(self) -> list[tuple[str, str, str, str]]:
        """
        :return: Exploration data.
        """
        return self._exploration_data

    # @exploration_data.setter
    # def exploration_data(self, value: tuple[int, int, int, str]) -> None:
    #     """
    #     :param value: The value is added to the exploration data.
    #     """
    #     self._exploration_data.append(value)

    @exploration_data.setter
    def exploration_data(self, exploration_data: list[tuple[str, str, str, str]]) -> None:
        """
        :param exploration_data: The exploration data is set to the provided exploration data.
        """
        self._exploration_data = exploration_data

    def add_horizontal_wall(self, x_coordinate: int, horizontal_line: int) -> None:
        """
        Adds a wall at the provided x-coordinate and horizontal line.
        :param x_coordinate: The x-coordinate.
        :param horizontal_line: The horizontal line.
        """
        if 0 <= x_coordinate < self._width and 1 <= horizontal_line < self._height:
            self._h_walls.add((x_coordinate, horizontal_line))

    def add_vertical_wall(self, y_coordinate: int, vertical_line: int) -> None:
        """
        Adds a wall at the provided x-coordinate and horizontal line.
        :param y_coordinate: The y-coordinate.
        :param vertical_line: The vertical line.
        """
        if 0 <= y_coordinate < self._height and 1 <= vertical_line < self._width:
            self._v_walls.add((vertical_line, y_coordinate))

    def get_walls(self, x_coordinate: int, y_coordinate: int) -> tuple[bool, bool, bool, bool]:
        """
        Provides a tuple of four boolean values representing the presence of walls
         in the four directions at specified coordinates.
        :param x_coordinate: The x-coordinate.
        :param y_coordinate: The Y-coordinate.
        :return: The wall presence tuple.
        """
        h_walls = self.h_walls
        v_walls = self.v_walls
        north = (x_coordinate, y_coordinate + 1) in h_walls
        east = (x_coordinate + 1, y_coordinate) in v_walls
        south = (x_coordinate, y_coordinate) in h_walls
        west = (x_coordinate, y_coordinate) in v_walls
        return north, east, south, west

    def sense_walls(self, runner: Runner) -> tuple[bool, bool, bool]:
        """
        Senses the walls that are on the left, right and in front of the runner.
        :param runner: The runner.
        :return: Sensed walls (Left wall, wall in front, right wall).
        """
        walls = self.get_walls(get_x(runner), get_y(runner))
        sensed_walls = []
        wall_num = 0
        for orientation in orientation_options(runner):
            if orientation == "N":
                wall_num = 0
            elif orientation == "S":
                wall_num = 2
            elif orientation == "E":
                wall_num = 1
            elif orientation == "W":
                wall_num = 3
            sensed_walls.append(bool(walls[wall_num]))
        return sensed_walls[0], sensed_walls[1], sensed_walls[2]

    def go_straight(self, runner: Runner) -> Runner:
        """
        Moves the runner one cell forward.
        :param runner: The runner.
        :return: The updated runner
        """
        if not self.sense_walls(runner)[1]:  # Checks if there is a wall in front.
            runner = forward(runner)
        else:
            raise ValueError()  # Raises an error when there is a wall ahead and the runner is told to go straight.
        return runner

    def move(self, runner: Runner) -> tuple[Runner, str]:
        """
        Moves the runner according to left-hug algorithm.
        :param runner: The runner.
        :return:The updated runner.
        """
        self.prev_runner = (get_x(runner), get_y(runner))
        sensed_walls = self.sense_walls(runner)  # Gets the walls that the runner can see.
        if not sensed_walls[0]:  # Checks if there is a left wall
            turn(runner, "Left")  # Turns left as there is no left wall
            self.go_straight(runner)  # Moves to the cell ahead
            action = "LF"
        elif not sensed_walls[1]:
            self.go_straight(runner)
            action = "F"
        elif not sensed_walls[2]:
            turn(runner, "Right")
            self.go_straight(runner)
            action = "RF"
        else:
            turn(runner, "Left")
            turn(runner, "Left")
            self.go_straight(runner)
            action = "LLF"
        return runner, action

    def explore(self, runner: Runner, goal: tuple[int, int]) -> str:
        """
        Controls the movement of the runner. It keeps "moving" (with the move method) the runner until it reaches the
        goal.
        :param runner: The runner.
        :param goal: The goal (end coordinates).
        :return: The sequence of actions for the exploration.
        """
        num = 0
        actions = ""
        with alive_bar() as bar:
            while (get_x(runner), get_y(runner)) != goal:
                if self.render_settings[0] or self.render_settings[1]:
                    self.render(runner, goal, num)
                self.path.append((get_x(runner), get_y(runner)))
                runner, action = self.move(runner)
                self.exploration_data.append((str(num + 1), str(self.prev_runner[0]), str(self.prev_runner[1]), action))
                num += 1
                actions += action
                bar()
        self.path.append((get_x(runner), get_y(runner)))
        if self.render_settings[0] or self.render_settings[1]:
            self.render(runner, goal, num)
        print("reached")
        print("Actions:", actions)
        return actions

    def shortest_path(self, starting: Optional[tuple[int, int]] = None, goal: Optional[tuple[int, int]] = None) -> list[
            tuple[int, int]]:
        """
        Calculates the shortest path using the exploration path (done with loop removal).
        :param starting: The starting coordinates.
        :param goal: The goal (end coordinates).
        :return: A list of coordinates that make up the shortest path based on the exploration path.
        """
        if starting is None:
            starting = (0, 0)
        if goal is None:
            goal = (self.width - 1, self.height - 1)
        runner = create_runner(starting[0], starting[1])
        self.explore(runner, goal)  # Explores the maze and get the exploration path that most likely contains
        # backtracing and loops

        visited: dict[tuple[int, int], int] = {}  # Stores the first occurrence of each position
        direct_path: list[tuple[int, int]] = []
        with alive_bar() as bar:
            for index, position in enumerate(self.path):
                if position in visited:
                    # Removes the loop by truncating intermediate positions
                    loop_start = visited[position]
                    direct_path = direct_path[:loop_start + 1]
                else:
                    # Adds the position to the simplified path
                    direct_path.append((position[0], position[1]))
                    visited[position] = len(direct_path) - 1
                bar()
        print("Final path:", direct_path)
        if self.render_settings[0] or self.render_settings[1]:
            self.render(runner, goal, "final", direct_path)
        print("Exploration steps:", len(self.exploration_data) - 1, "    Final path length:", len(direct_path),
              "    score:", (len(self.exploration_data) - 1) / 4 + len(direct_path),
              "    Final data file path:", self.run_id)
        return direct_path

    def render(self, runner: Runner, goal: tuple[int, int], name: int | str,
               final_path: list[tuple[int, int]] = []) -> None:
        """
        Renders the maze as a plot with the runner, goal, exploration path and final path being displayed.
        The horizontal walls are rendered in red and the vertical walls are rendered in green.
        It also facilitates the saving the plots to the working directory.
        :param runner: The runner that is being rendered - Rendered in blue.
        :param goal: The goal (end coordinates) - Rendered in yellow.
        :param name: The file name
        (this is an integer solely for allow the compilation of a video/gif using the generated image sequence)
        :param final_path: The final/shortest path that the mouse comes up with - Rendered in pink.
        """
        if final_path is None:
            final_path = []
        plt.figure(figsize=(10, 10))
        ax = plt.gca()
        colored_boxes = []

        for step in self.path:
            colored_boxes.append(
                (step[0], step[1], "grey"))  # Appends the exploration path coordinates to the rendering box queue

        for step in final_path:  # Appends the final path coordinates to the rendering box queue
            colored_boxes.append((step[0], step[1], "pink"))

        # Draw horizontal walls
        for x, y in self._h_walls:
            plt.plot([x, x + 1], [y, y], color="red", linewidth=2)

        # Draw vertical walls
        for x, y in self._v_walls:
            plt.plot([x, x], [y, y + 1], color="green", linewidth=2)

        # Appends the goal coordinates and the start coordinates
        colored_boxes.append((goal[0], goal[1], "yellow"))
        colored_boxes.append((get_x(runner), get_y(runner), "blue"))

        for x, y, color in colored_boxes:  # Renders/colors the coordinates that are in colored_boxes
            print(type(x), type(y), type(color), type(colored_boxes))
            rect = patches.Rectangle((x, y), 1, 1, linewidth=0, facecolor=color)
            ax.add_patch(rect)

        # Draws an arrow to mark the runner's orientation
        direction = get_orientation(runner)
        dx, dy = 0., 0.
        if direction == "N":
            dy = 0.3
        elif direction == "S":
            dy = -0.3
        elif direction == "E":
            dx = 0.3
        elif direction == "W":
            dx = -0.3
        ax.arrow(get_x(runner) + 0.5, get_y(runner) + 0.5, dx, dy, head_width=0.2, head_length=0.2, fc='yellow',
                 ec='blue')

        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Add custom axes showing x and y values
        for x in range(self._width):
            plt.text(x + 0.5, -0.5, str(x), ha='center', va='center', fontsize=10, color='black')  # x-axis values
        for y in range(self._height):
            plt.text(-0.5, y + 0.5, str(y), ha='center', va='center', fontsize=10, color='black')  # y-axis values

        # Set grid and labels
        plt.xlim(0, self._width)
        plt.ylim(0, self._height)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(visible=True, which='both', color='lightgray', linestyle='--', linewidth=0.5)
        if self.render_settings[0]:
            try:
                os.mkdir(self.run_id)
            except FileExistsError:
                pass
            plt.savefig(f'./{self.run_id}/{name}.png')

        # This code block can be used to display the maze as the runner is moving through it
        if self.render_settings[1]:
            plt.show(block=False)
            plt.pause(self.render_settings[2])
            plt.close()
