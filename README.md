# A* Pathfinding Visualization for CS 5800

This project visualizes the A* pathfinding algorithm on street networks from OpenStreetMap

## Features

- Real-time visualization of A* algorithm exploration
- Multiple heuristic options:
  - Euclidean distance (straight-line)
  - Manhattan distance (grid-like street layouts)
  - Diagonal distance (faster approximation)
  - Haversine distance (accounts for Earth's curvature)
- Automatic GIF recording of the complete algorithm execution
- Street network data from OpenStreetMap for any city worldwide
- Visualization shows:
  - Explored/visited nodes with gradient coloring
  - Current frontier (open set)
  - Best path found so far
  - Final optimal path
- Automatic caching of downloaded map data for quick reuse
- Save final visualizations as a GIF and image
- Compare results with ideal routes from Google Maps

## Installation

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run the main script

## Usage

Basic usage with default settings:

```bash
python main.py
```

Customize with command line options:

```bash
# Use a preset city
python main.py --preset london

# Use a specific heuristic algorithm
python main.py --heuristic manhattan

# Save GIF animation of the algorithm progress
python main.py --preset tokyo --heuristic diagonal

# Don't save GIF animation
python main.py --no-gif
```

## Command Line Options

- `--preset [city]`: Use a preset city (baku, seattle, tokyo, london, seoul, nyc, rome)
- `--city [name]`: Use a custom city name
  > ⚠️ **Warning**: The Tokyo preset downloads a very large street network and may take significantly longer than other presets.
- `--heuristic [type]`: Choose heuristic type (euclidean, manhattan, diagonal, haversine)
- `--output-dir [dir]`: Directory to save output
- `--data-dir [dir]`: Directory to store cached data
- `--no-display`: Do not display the visualization
- `--no-save`: Do not save the final result image
- `--no-gif`: Do not save animation as GIF

## Heuristic Types

- **Euclidean**: Straight-line distance (simplest)
- **Manhattan**: Sum of absolute differences (good for grid-like street layouts)
- **Diagonal**: Allows diagonal movement (faster than Manhattan)
- **Haversine**: Great-circle distance accounting for Earth's curvature (most accurate for geographic routing)

## Output

The program generates several outputs:

1. Interactive visualization during execution
2. Final path image in the output directory
3. GIF animation showing the algorithm's progress
4. Text file with route coordinates and statistics

## Examples

Manhattan heuristic in New York City:
```bash
python main.py --preset nyc --heuristic manhattan
```

Haversine heuristic in Tokyo with GIF recording:
```bash
python main.py --preset tokyo --heuristic haversine
```

## Project Structure

- `data/`: Cached street network data
- `output/`: Saved visualization images and GIFs
- `src/`
  - `algorithms/`: Implementation of A* and potentially other pathfinding algorithms
  - `data/`: Data handling and graph processing functions
  - `visualization/`: Visualization components and recording functionality
  - `utils/`: Utility functions
- `main.py`: Entry point script
