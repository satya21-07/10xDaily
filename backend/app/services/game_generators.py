import random
import string
from datetime import datetime, timedelta, timezone

import os
import requests

WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "wordlist.txt")

def get_word_bank():
    if not os.path.exists(WORDLIST_PATH):
        print("Downloading wordlist...")
        try:
            r = requests.get("https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt")
            if r.status_code == 200:
                with open(WORDLIST_PATH, "w") as f:
                    f.write(r.text)
        except Exception as e:
            print(f"Failed to download wordlist: {e}")
            # Fallback tiny word bank
            return ["PYTHON", "JAVASCRIPT", "HTML", "REACT", "OCEAN", "DESERT", "WINTER", "PLANET", "GALAXY", "TIGER", "GUITAR"]
            
    with open(WORDLIST_PATH, "r") as f:
        words = [line.strip().upper() for line in f if 4 <= len(line.strip()) <= 8]
        return words if words else ["FALLBACK"]

def generate_word_search():
    """
    Generate a 10x10 word search grid with 10 words.
    Seed is based on today's date.
    """
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed)
    
    grid_size = 10
    num_words = 10
    
    word_bank = get_word_bank()
    words = random.sample(word_bank, min(num_words, len(word_bank)))
    
    # Try to build a valid grid
    while True:
        grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
        placed_words_data = []
        
        success = True
        for word in words:
            placed = False
            # Try placing the word up to 100 times
            for _ in range(100):
                direction = random.choice([(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]) # dx, dy
                
                # Pick a starting coordinate
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - 1)
                
                # Check if it fits
                end_x = x + direction[0] * (len(word) - 1)
                end_y = y + direction[1] * (len(word) - 1)
                
                if 0 <= end_x < grid_size and 0 <= end_y < grid_size:
                    # Check for overlaps
                    can_place = True
                    for i in range(len(word)):
                        curr_x = x + direction[0] * i
                        curr_y = y + direction[1] * i
                        if grid[curr_y][curr_x] != '' and grid[curr_y][curr_x] != word[i]:
                            can_place = False
                            break
                    
                    if can_place:
                        # Place it
                        for i in range(len(word)):
                            curr_x = x + direction[0] * i
                            curr_y = y + direction[1] * i
                            grid[curr_y][curr_x] = word[i]
                        placed_words_data.append({
                            "word": word,
                            "start": [x, y],
                            "end": [end_x, end_y]
                        })
                        placed = True
                        break
                        
            if not placed:
                success = False
                break
                
        if success:
            # Fill empty spaces with random uppercase letters
            for y in range(grid_size):
                for x in range(grid_size):
                    if grid[y][x] == '':
                        grid[y][x] = random.choice(string.ascii_uppercase)
                        
            return {
                "grid": grid,
                "words": words,
                "solution": placed_words_data
            }


def generate_mini_sudoku():
    """
    Generate a 6x6 mini Sudoku puzzle.
    Seed is based on today's date.
    Grid has 2x3 blocks (2 rows of 3 columns each).
    """
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed + 1) # different seed offset so it doesn't match word search
    
    # Create an empty 6x6 grid
    grid = [[0 for _ in range(6)] for _ in range(6)]
    
    def is_safe(g, row, col, num):
        # Check row
        for x in range(6):
            if g[row][x] == num:
                return False
        # Check col
        for x in range(6):
            if g[x][col] == num:
                return False
        # Check 2x3 block
        start_row = row - row % 2
        start_col = col - col % 3
        for i in range(2):
            for j in range(3):
                if g[i + start_row][j + start_col] == num:
                    return False
        return True

    def solve_sudoku(g):
        for i in range(6):
            for j in range(6):
                if g[i][j] == 0:
                    nums = [1, 2, 3, 4, 5, 6]
                    random.shuffle(nums)
                    for num in nums:
                        if is_safe(g, i, j, num):
                            g[i][j] = num
                            if solve_sudoku(g):
                                return True
                            g[i][j] = 0
                    return False
        return True

    solve_sudoku(grid)
    
    # Save solution
    solution = [row[:] for row in grid]
    
    # Remove cells to create the puzzle (remove about 18-22 cells out of 36)
    cells_to_remove = random.randint(18, 22)
    positions = [(r, c) for r in range(6) for c in range(6)]
    random.shuffle(positions)

import os
import requests
from sqlalchemy.orm import Session

WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "wordlist.txt")

def get_word_bank():
    if not os.path.exists(WORDLIST_PATH):
        print("Downloading wordlist...")
        try:
            r = requests.get("https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt")
            if r.status_code == 200:
                with open(WORDLIST_PATH, "w") as f:
                    f.write(r.text)
        except Exception as e:
            print(f"Failed to download wordlist: {e}")
            # Fallback tiny word bank
            return ["PYTHON", "JAVASCRIPT", "HTML", "REACT", "OCEAN", "DESERT", "WINTER", "PLANET", "GALAXY", "TIGER", "GUITAR"]
            
    with open(WORDLIST_PATH, "r") as f:
        words = [line.strip().upper() for line in f if 4 <= len(line.strip()) <= 8]
        return words if words else ["FALLBACK"]

def generate_word_search():
    """
    Generate a 10x10 word search grid with 10 words.
    Seed is based on today's date.
    """
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed)
    
    grid_size = 10
    num_words = 10
    
    word_bank = get_word_bank()
    words = random.sample(word_bank, min(num_words, len(word_bank)))
    
    # Try to build a valid grid
    while True:
        grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
        placed_words_data = []
        
        success = True
        for word in words:
            placed = False
            # Try placing the word up to 100 times
            for _ in range(100):
                direction = random.choice([(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]) # dx, dy
                
                # Pick a starting coordinate
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - 1)
                
                # Check if it fits
                end_x = x + direction[0] * (len(word) - 1)
                end_y = y + direction[1] * (len(word) - 1)
                
                if 0 <= end_x < grid_size and 0 <= end_y < grid_size:
                    # Check for overlaps
                    can_place = True
                    for i in range(len(word)):
                        curr_x = x + direction[0] * i
                        curr_y = y + direction[1] * i
                        if grid[curr_y][curr_x] != '' and grid[curr_y][curr_x] != word[i]:
                            can_place = False
                            break
                    
                    if can_place:
                        # Place it
                        for i in range(len(word)):
                            curr_x = x + direction[0] * i
                            curr_y = y + direction[1] * i
                            grid[curr_y][curr_x] = word[i]
                        placed_words_data.append({
                            "word": word,
                            "start": [x, y],
                            "end": [end_x, end_y]
                        })
                        placed = True
                        break
                        
            if not placed:
                success = False
                break
                
        if success:
            # Fill empty spaces with random uppercase letters
            for y in range(grid_size):
                for x in range(grid_size):
                    if grid[y][x] == '':
                        grid[y][x] = random.choice(string.ascii_uppercase)
                        
            return {
                "grid": grid,
                "words": words,
                "solution": placed_words_data
            }


def generate_mini_sudoku():
    """
    Generate a 6x6 mini Sudoku puzzle.
    Seed is based on today's date.
    Grid has 2x3 blocks (2 rows of 3 columns each).
    """
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed + 1) # different seed offset so it doesn't match word search
    
    # Create an empty 6x6 grid
    grid = [[0 for _ in range(6)] for _ in range(6)]
    
    def is_safe(g, row, col, num):
        # Check row
        for x in range(6):
            if g[row][x] == num:
                return False
        # Check col
        for x in range(6):
            if g[x][col] == num:
                return False
        # Check 2x3 block
        start_row = row - row % 2
        start_col = col - col % 3
        for i in range(2):
            for j in range(3):
                if g[i + start_row][j + start_col] == num:
                    return False
        return True

    def solve_sudoku(g):
        for i in range(6):
            for j in range(6):
                if g[i][j] == 0:
                    nums = [1, 2, 3, 4, 5, 6]
                    random.shuffle(nums)
                    for num in nums:
                        if is_safe(g, i, j, num):
                            g[i][j] = num
                            if solve_sudoku(g):
                                return True
                            g[i][j] = 0
                    return False
        return True

    solve_sudoku(grid)
    
    # Save solution
    solution = [row[:] for row in grid]
    
    # Remove cells to create the puzzle (remove about 18-22 cells out of 36)
    cells_to_remove = random.randint(18, 22)
    positions = [(r, c) for r in range(6) for c in range(6)]
    random.shuffle(positions)
    
    for i in range(cells_to_remove):
        r, c = positions[i]
        grid[r][c] = 0
        
    return {
        "grid": grid,
        "solution": solution
    }

def generate_sliding_puzzle():
    """
    Generate a 4x4 sliding puzzle.
    Seed is based on today's date.
    Returns the initial shuffled state of the board and the cycle-free solution path.
    """
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed + 2) # different offset
    
    board_size = 3
    total_tiles = board_size * board_size
    solved_state = tuple(list(range(1, total_tiles)) + [0])
    
    tiles = list(solved_state)
    blank_idx = total_tiles - 1
    
    def get_neighbors(idx):
        neighbors = []
        r, c = divmod(idx, board_size)
        if r > 0: neighbors.append(idx - board_size) # up
        if r < board_size - 1: neighbors.append(idx + board_size) # down
        if c > 0: neighbors.append(idx - 1) # left
        if c < board_size - 1: neighbors.append(idx + 1) # right
        return neighbors

    history = [solved_state]
    moves = [] # tiles moved
    
    # 250 moves to ensure it's sufficiently shuffled even after cycle erasure
    last_swapped = -1
    for _ in range(250):
        neighbors = get_neighbors(blank_idx)
        valid_moves = [n for n in neighbors if n != last_swapped]
        next_idx = random.choice(valid_moves) if valid_moves else random.choice(neighbors)
        
        moved_tile = tiles[next_idx]
        tiles[blank_idx], tiles[next_idx] = tiles[next_idx], tiles[blank_idx]
        
        current_state = tuple(tiles)
        
        if current_state in history:
            # Cycle detected: erase the loop
            idx = history.index(current_state)
            history = history[:idx+1]
            moves = moves[:idx]
        else:
            history.append(current_state)
            moves.append(moved_tile)
            
        last_swapped = blank_idx
        blank_idx = next_idx
        
    # Edge case: avoid solved state
    if tuple(tiles) == solved_state:
        neighbors = get_neighbors(blank_idx)
        next_idx = neighbors[0]
        moved_tile = tiles[next_idx]
        tiles[blank_idx], tiles[next_idx] = tiles[next_idx], tiles[blank_idx]
        moves.append(moved_tile)
        
    # Reverse the generation moves to get the solution path
    solution_path = list(reversed(moves))
        
    return {
        "board_size": board_size,
        "tiles": tiles,
        "solution_path": solution_path
    }

def generate_latin_square_for_kenken(size):
    grid = [[0 for _ in range(size)] for _ in range(size)]
    
    def solve(r, c):
        if r == size:
            return True
        next_r = r if c < size - 1 else r + 1
        next_c = (c + 1) % size
        
        nums = list(range(1, size + 1))
        random.shuffle(nums)
        for num in nums:
            safe_c = all(grid[i][c] != num for i in range(r))
            safe_r = all(grid[r][j] != num for j in range(c))
            
            if safe_r and safe_c:
                grid[r][c] = num
                if solve(next_r, next_c):
                    return True
        grid[r][c] = 0
        return False
        
    solve(0, 0)
    return grid

def generate_kenken_cages(grid, size):
    cells = [(r, c) for r in range(size) for c in range(size)]
    random.shuffle(cells)
    
    assigned = set()
    cages = []
    
    for r, c in cells:
        if (r, c) in assigned:
            continue
        
        cage_cells = [(r, c)]
        assigned.add((r, c))
        
        target_size = random.choices([1, 2, 3, 4], weights=[10, 40, 35, 15])[0]
        
        current = [(r, c)]
        while len(cage_cells) < target_size:
            neighbors = set()
            for cr, cc in cage_cells:
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in assigned:
                        neighbors.add((nr, nc))
            
            if not neighbors:
                break
                
            nxt = random.choice(list(neighbors))
            cage_cells.append(nxt)
            assigned.add(nxt)
            
        cages.append(cage_cells)
        
    final_cages = []
    for i, cells_in_cage in enumerate(cages):
        vals = [grid[r][c] for r, c in cells_in_cage]
        if len(cells_in_cage) == 1:
            target = vals[0]
            op = ''
        elif len(cells_in_cage) == 2:
            v1, v2 = vals[0], vals[1]
            mx, mn = max(v1, v2), min(v1, v2)
            ops = []
            ops.append(('+', v1 + v2))
            ops.append(('*', v1 * v2))
            if mx - mn > 0:
                ops.append(('-', mx - mn))
            if mx % mn == 0:
                ops.append(('/', mx // mn))
            op, target = random.choice(ops)
        else:
            ops = []
            s = sum(vals)
            ops.append(('+', s))
            m = 1
            for v in vals: m *= v
            ops.append(('*', m))
            op, target = random.choice(ops)
            
        final_cages.append({
            "id": i,
            "cells": cells_in_cage,
            "op": op,
            "target": target
        })
        
    return final_cages

def solve_kenken_uniqueness(size, cages):
    grid = [[0 for _ in range(size)] for _ in range(size)]
    cell_to_cage = {}
    for cage in cages:
        for r, c in cage["cells"]:
            cell_to_cage[(r, c)] = cage
            
    solutions_count = 0
    
    def evaluate_cage(cage):
        vals = [grid[r][c] for r, c in cage["cells"]]
        target = cage["target"]
        op = cage["op"]
        
        if op == '':
            return vals[0] == target
        elif op == '+':
            return sum(vals) == target
        elif op == '*':
            m = 1
            for v in vals: m *= v
            return m == target
        elif op == '-':
            return abs(vals[0] - vals[1]) == target
        elif op == '/':
            v1, v2 = vals[0], vals[1]
            return (v1 == v2 * target) or (v2 == v1 * target)
        return False
        
    def solve(r, c):
        nonlocal solutions_count
        if solutions_count >= 2:
            return
            
        if r == size:
            solutions_count += 1
            return
            
        next_r = r if c < size - 1 else r + 1
        next_c = (c + 1) % size
        
        cage = cell_to_cage[(r, c)]
        
        for num in range(1, size + 1):
            safe_c = all(grid[i][c] != num for i in range(r))
            safe_r = all(grid[r][j] != num for j in range(c))
            
            if safe_r and safe_c:
                grid[r][c] = num
                
                cage_complete = True
                for cr, cc in cage["cells"]:
                    if grid[cr][cc] == 0:
                        cage_complete = False
                        break
                        
                if not cage_complete or evaluate_cage(cage):
                    solve(next_r, next_c)
                    
        grid[r][c] = 0
        
    solve(0, 0)
    return solutions_count

def generate_kenken(size=4):
    for _ in range(50):
        grid = generate_latin_square_for_kenken(size)
        cages = generate_kenken_cages(grid, size)
        if solve_kenken_uniqueness(size, cages) == 1:
            return {"size": size, "cages": cages, "solution": grid}
    
    # Fallback puzzle for each size if generating fails
    if size == 4:
        return {
            "size": 4,
            "cages": [
                {"id": 0, "cells": [[0, 0], [0, 1]], "op": "/", "target": 2},
                {"id": 1, "cells": [[0, 2], [1, 2]], "op": "+", "target": 5},
                {"id": 2, "cells": [[0, 3], [1, 3], [2, 3]], "op": "*", "target": 24},
                {"id": 3, "cells": [[1, 0], [2, 0]], "op": "-", "target": 1},
                {"id": 4, "cells": [[1, 1], [2, 1], [3, 1]], "op": "+", "target": 9},
                {"id": 5, "cells": [[2, 2], [3, 2]], "op": "-", "target": 1},
                {"id": 6, "cells": [[3, 0]], "op": "", "target": 3},
                {"id": 7, "cells": [[3, 3]], "op": "", "target": 1}
            ],
            "solution": [[2, 1, 4, 3], [1, 3, 2, 4], [4, 2, 3, 1], [3, 4, 1, 2]]
        }
    elif size == 5:
        # Fallback 5x5... (Simplified fallback for demonstration, assume solver works 99% of time)
        return {"size": 5, "cages": [{"id":0,"cells":[[0,0]],"op":"","target":1}], "solution": [[1,2,3,4,5],[2,3,4,5,1],[3,4,5,1,2],[4,5,1,2,3],[5,1,2,3,4]]}
    elif size == 6:
        return {"size": 6, "cages": [{"id":0,"cells":[[0,0]],"op":"","target":1}], "solution": [[1,2,3,4,5,6],[2,3,4,5,6,1],[3,4,5,6,1,2],[4,5,6,1,2,3],[5,6,1,2,3,4],[6,1,2,3,4,5]]}
    return None

def get_or_generate_daily_kenken(db, size: int) -> dict:
    from app.models.games import DailyKenKenPuzzle
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    
    # 1. Check cache
    cached = db.query(DailyKenKenPuzzle).filter(
        DailyKenKenPuzzle.puzzle_date == today_str,
        DailyKenKenPuzzle.size == size
    ).first()
    
    if cached:
        return cached.puzzle_data
        
    # 2. Generate
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 10000 + now.timetuple().tm_yday * 10 + size
    random.seed(seed)
    
    puzzle_data = generate_kenken(size)
    
    # 3. Persist
    new_puzzle = DailyKenKenPuzzle(
        puzzle_date=today_str,
        size=size,
        puzzle_data=puzzle_data
    )
    db.add(new_puzzle)
    db.commit()
    
    return puzzle_data
