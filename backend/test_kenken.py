import random

def generate_latin_square(size):
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

def generate_cages(grid, size):
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

def solve_kenken(size, cages):
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

if __name__ == "__main__":
    for size in [4, 5, 6]:
        for attempt in range(50):
            grid = generate_latin_square(size)
            cages = generate_cages(grid, size)
            sol_count = solve_kenken(size, cages)
            if sol_count == 1:
                print(f"Size {size} generated successfully on attempt {attempt+1}")
                break
        else:
            print(f"Size {size} failed to generate a unique solution.")
