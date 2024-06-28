from collections import deque

def parse_grid(grid_str):
    grid = [s for s in grid_str.splitlines() if len(s) > 0]
    start_position = None
    pill_positions = []
    grid_map = []
    
    for row_index, row in enumerate(grid):
        grid_row = []
        for col_index, cell in enumerate(row):
            if cell == 'L':
                start_position = (row_index, col_index)
            elif cell == '.':
                pill_positions.append((row_index, col_index))
            grid_row.append(cell)
        grid_map.append(grid_row)
    
    return grid_map, start_position, pill_positions

directions = {'U': (-1, 0), 'R': (0, 1), 'D': (1, 0), 'L': (0, -1)}
def bfs(grid, start_position, target_position):
    queue = deque([(start_position, "")])
    visited = set()
    visited.add(start_position)
    
    while queue:
        current_position, path = queue.popleft()
        if current_position == target_position:
            return path
        
        for move, (dx, dy) in directions.items():
            new_position = (current_position[0] + dx, current_position[1] + dy)
            try:
                if grid[new_position[0]][new_position[1]] != '#' and new_position not in visited:
                    visited.add(new_position)
                    queue.append((new_position, path + move))
            except IndexError:
                pass
    
    return None

def find_nearest_pill(grid, current_position, pill_positions):
    shortest_path = None
    nearest_pill = None
    
    for pill in pill_positions:
        path = bfs(grid, current_position, pill)
        if path is not None and (shortest_path is None or len(path) < len(shortest_path)):
            shortest_path = path
            nearest_pill = pill
            
    return nearest_pill, shortest_path

def find_greedy_path(grid_str):
    grid_map, start_position, pill_positions = parse_grid(grid_str)
    full_path = ""
    current_position = start_position
    
    while pill_positions:
        nearest_pill, path_to_pill = find_nearest_pill(grid_map, current_position, pill_positions)
        if not path_to_pill:
            raise ValueError("No path to reach remaining pills.")
        
        for move in path_to_pill:
            dx, dy = directions[move]
            current_position = (current_position[0] + dx, current_position[1] + dy)
        
        full_path += path_to_pill
        pill_positions.remove(nearest_pill)
    
    return full_path

# Example usage:
problem2 = '''
L...#.
#.#.#.
##....
...###
.##..#
....##
'''

print('Problem:')
print(problem2)
path = find_greedy_path(problem2)
print("Path:", path)
print("Length:", len(path))

while True:
    print('Input problem:')
    problem = []
    while True:
        line = input().strip()
        if len(line) == 0:
            break
        problem.append(line)
    path = find_greedy_path('\n'.join(problem))
    print("Path:", path)
    print("Length:", len(path))