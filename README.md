# A* Pathfinding Visualization for CS 5800

This project visualizes the A* pathfinding algorithm on street networks from OpenStreetMap.

## Features

- Download street network data from OpenStreetMap for any city worldwide
- Implementation of A* pathfinding algorithm with customizable heuristics
- Real-time visualization of the search process showing:
  - Explored/visited nodes
  - Current frontier (open set)
  - Best path found so far
  - Final optimal path
- Automatic caching of downloaded map data for quick reuse
- Adaptive animation speed that scales based on graph complexity
- Save final visualizations as image files
- Compare results with ideal straight-line distance

## Installation

1. Clone this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the main script with desired options:
```
python main.py [options]
```


### Command-line Options

- `--preset CITY`: Use a predefined city preset (options: "baku", "seattle", "tokyo", etc.)
  > ⚠️ **Warning**: The Tokyo preset downloads a very large street network and may take significantly longer than other presets.
- `--city CITY_NAME`: Specify a custom city (e.g., "Paris, France")
- `--output-dir DIR`: Directory to save visualization results (default: "output")
- `--data-dir DIR`: Directory for cached map data (default: "data")
- `--no-display`: Run without showing the visualization window
- `--no-save`: Don't save the final visualization image
- `--delay SECONDS`: Delay between processing nodes (default: 0.05)
- `--batch-size SIZE`: Number of nodes processed in each batch (default: 20)
- `--runtime SECONDS`: Target runtime for visualization (default: 12.0)

### Examples

Basic usage with a preset city:
```
python main.py --preset seattle
```

Using a custom city with visualization settings:
```
python main.py --city "Barcelona, Spain" --delay 0.02 --batch-size 30
```

## Project Structure

- `data/`: Cached street network data
- `output/`: Saved visualization images
- `src/`
  - `algorithms/`: Implementation of A* and potentially other pathfinding algorithms
  - `data/`: Data handling and graph processing functions
  - `visualization/`: Visualization components and rendering
  - `utils/`: Utility functions
- `main.py`: Entry point script
