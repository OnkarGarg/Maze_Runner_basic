# Maze Runner (Basic)

This project is a maze runner and solver that reads a maze from a file, processes it, and finds a valid path from a starting point to a goal. It utilizes the Left-Hug algorithm along with a layer of post-processing to remove all loops from the path. It also generates exploration data and statistics about the maze run.

## Requirements

- Python 3.x
- `matplotlib`
- `alive-progress`

## Usage

To run the maze runner from the terminal, use the command format:

```
python maze_runner.py [options] <maze_file>
```
Here is a list of available options:

- `-h, --help`: Show the help message and exit.
- `--starting`: The starting point of the maze. Default is (0, 0).
- `--goal`: The goal point of the maze. Default is the top right corner.
- `--save_images`: Save the maze images to the working directory. Default is False.
- `--display_images`: Display the maze images. Default is False.
- `--display_time`: The amount of time each step is displayed for. Default is 1 second.

Here is a sample command to run the maze runner from terminal:

```sh
python maze_runner.py --starting "0, 0" --goal "9, 4" --save_images --display_images --display_time 1 medium_maze2.mz
```
The above command will run the maze runner on the `medium_maze2.mz` file with the starting point at (0, 0) and the goal at (9, 4). It will save the maze images to the working directory, display the maze images, and display each step for 1 second.  The exploration data about the maze run will be saved in a CSV file named `exploration.csv` while the final path and the score are stored in a Text fle called `statstics.txt`.