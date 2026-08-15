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
    
    for i in range(cells_to_remove):
        r, c = positions[i]
        grid[r][c] = 0
        
    return {
        "grid": grid,
        "solution": solution
    }

