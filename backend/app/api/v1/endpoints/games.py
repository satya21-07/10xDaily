from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.api import deps
from app.models.core_models import User
from app.models.games import GameProgress
from app.schemas.user import UserUpdate # Assuming we might need something like this, or we can just update directly
from app.services.game_generators import generate_word_search, generate_mini_sudoku

router = APIRouter()

# Simple pool of flow levels
import random
import time

def get_daily_flow_level() -> Dict[str, Any]:
    # Use the current day of the year + year as seed to be deterministic per day
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    seed = now.year * 1000 + now.timetuple().tm_yday
    random.seed(seed)
    
    grid_sizes = [5, 6, 7, 8]
    grid_size = random.choice(grid_sizes)
    
    color_palette = [
        {"id": "red", "color": "#ef4444"},
        {"id": "blue", "color": "#3b82f6"},
        {"id": "green", "color": "#22c55e"},
        {"id": "yellow", "color": "#eab308"},
        {"id": "orange", "color": "#f97316"},
        {"id": "purple", "color": "#a855f7"},
        {"id": "cyan", "color": "#06b6d4"},
        {"id": "pink", "color": "#ec4899"},
        {"id": "lime", "color": "#84cc16"},
        {"id": "teal", "color": "#14b8a6"},
        {"id": "indigo", "color": "#4f46e5"},
        {"id": "rose", "color": "#f43f5e"}
    ]
    
    while True:
        grid = [[-1 for _ in range(grid_size)] for _ in range(grid_size)]
        paths = []
        empty_cells = [(x, y) for x in range(grid_size) for y in range(grid_size)]
        
        while empty_cells:
            start = random.choice(empty_cells)
            path_idx = len(paths)
            grid[start[1]][start[0]] = path_idx
            paths.append([start])
            empty_cells.remove(start)
            
            target_len = random.randint(3, grid_size * 3)
            curr = start
            
            while len(paths[path_idx]) < target_len:
                neighbors = [
                    (curr[0] + 1, curr[1]), (curr[0] - 1, curr[1]),
                    (curr[0], curr[1] + 1), (curr[0], curr[1] - 1)
                ]
                valid_neighbors = [(nx, ny) for nx, ny in neighbors 
                                   if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == -1]
                
                if valid_neighbors:
                    nxt = random.choice(valid_neighbors)
                    grid[nxt[1]][nxt[0]] = path_idx
                    paths[path_idx].append(nxt)
                    empty_cells.remove(nxt)
                    curr = nxt
                else:
                    break
                    
        # Ensure all paths have at least 2 cells
        if any(len(p) < 2 for p in paths):
            continue
            
        # Ensure we don't exceed available colors
        if len(paths) > len(color_palette):
            continue
            
        # Valid level!
        level = {
            "grid_size": grid_size,
            "colors": []
        }
        for i, path in enumerate(paths):
            level["colors"].append({
                "id": color_palette[i]["id"],
                "color": color_palette[i]["color"],
                "start": list(path[0]),
                "end": list(path[-1]),
                "solution_path": [list(p) for p in path]
            })
        return level

from pydantic import BaseModel
from datetime import timedelta

def update_daily_streak_and_xp(db: Session, current_user: User) -> int:
    """
    Awards XP if this is their first game today.
    Returns the points awarded (100).
    """
    points_awarded = 100 # 100 XP for every game completed
            
    current_user.xp += points_awarded
    return points_awarded


def calculate_game_streak(db: Session, user_id: int, game_name: str) -> int:
    """Calculate the current daily streak for a specific game."""
    # Get all completion dates in descending order
    dates = db.query(GameProgress.completion_date)\
              .filter(GameProgress.user_id == user_id, GameProgress.game_name == game_name)\
              .order_by(GameProgress.completion_date.desc())\
              .all()
              
    if not dates:
        return 0
        
    date_strs = [d[0] for d in dates]
    
    # Start checking from today or yesterday
    today = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    streak = 0
    
    # If they haven't played today or yesterday, streak is 0
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if today_str not in date_strs and yesterday_str not in date_strs:
        return 0
        
    current_check_date = today
    if today_str not in date_strs:
        current_check_date = today - timedelta(days=1)
        
    while True:
        check_str = current_check_date.strftime("%Y-%m-%d")
        if check_str in date_strs:
            streak += 1
            current_check_date -= timedelta(days=1)
        else:
            break
            
    return streak

class FlowCompleteRequest(BaseModel):
    paths: Optional[Dict[str, Any]] = None
    time_taken: Optional[int] = 0

@router.get("/flow/today")
def get_today_flow_puzzle(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "flow",
        GameProgress.completion_date == today_str
    ).first()
    
    level_data = get_daily_flow_level()
    game_streak = calculate_game_streak(db, current_user.id, "flow")
    
    return {
        "completed": progress is not None,
        "date": today_str,
        "level": level_data,
        "game_streak": game_streak,
        "saved_paths": progress.game_data.get("paths") if progress and progress.game_data else None,
        "time_taken": progress.game_data.get("time_taken", 0) if progress and progress.game_data else 0
    }

@router.post("/flow/complete")
def complete_flow_puzzle(
    request: FlowCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "flow",
        GameProgress.completion_date == today_str
    ).first()
    
    if progress:
        if request.paths is not None:
            progress.game_data = {"paths": request.paths, "time_taken": request.time_taken}
            db.commit()
        game_streak = calculate_game_streak(db, current_user.id, "flow")
        return {"message": "Puzzle paths saved!", "points_awarded": 0, "new_xp": current_user.xp, "current_streak": current_user.current_streak, "game_streak": game_streak}
        
    points_awarded = update_daily_streak_and_xp(db, current_user)
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="flow",
        completion_date=today_str,
        score=100,
        game_data={"paths": request.paths, "time_taken": request.time_taken} if request.paths is not None else None
    )
    db.add(new_progress)
    db.commit()
    
    game_streak = calculate_game_streak(db, current_user.id, "flow")
    
    return {
        "message": "Puzzle completed successfully!",
        "points_awarded": points_awarded,
        "new_xp": current_user.xp,
        "current_streak": current_user.current_streak,
        "game_streak": game_streak
    }

class WordSearchCompleteRequest(BaseModel):
    time_taken: int
    found_words: list[str]

@router.get("/word-search/today")
def get_today_word_search(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "word-search",
        GameProgress.completion_date == today_str
    ).first()
    
    level_data = generate_word_search()
    game_streak = calculate_game_streak(db, current_user.id, "word-search")
    
    return {
        "completed": progress is not None,
        "date": today_str,
        "level": level_data,
        "game_streak": game_streak,
        "saved_state": progress.game_data if progress and progress.game_data else None
    }

@router.post("/word-search/complete")
def complete_word_search(
    request: WordSearchCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "word-search",
        GameProgress.completion_date == today_str
    ).first()
    
    if progress:
        progress.game_data = {"found_words": request.found_words, "time_taken": request.time_taken}
        db.commit()
        game_streak = calculate_game_streak(db, current_user.id, "word-search")
        return {"message": "Word search progress saved!", "points_awarded": 0, "game_streak": game_streak}
        
    points_awarded = update_daily_streak_and_xp(db, current_user)
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="word-search",
        completion_date=today_str,
        score=100,
        game_data={"found_words": request.found_words, "time_taken": request.time_taken}
    )
    db.add(new_progress)
    db.commit()
    
    game_streak = calculate_game_streak(db, current_user.id, "word-search")
    
    return {
        "message": "Word Search completed!",
        "points_awarded": points_awarded,
        "new_xp": current_user.xp,
        "current_streak": current_user.current_streak,
        "game_streak": game_streak
    }

class MiniSudokuCompleteRequest(BaseModel):
    time_taken: int
    grid: list[list[int]]

@router.get("/mini-sudoku/today")
def get_today_mini_sudoku(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "mini-sudoku",
        GameProgress.completion_date == today_str
    ).first()
    
    level_data = generate_mini_sudoku()
    game_streak = calculate_game_streak(db, current_user.id, "mini-sudoku")
    
    return {
        "completed": progress is not None,
        "date": today_str,
        "level": level_data,
        "game_streak": game_streak,
        "saved_state": progress.game_data if progress and progress.game_data else None
    }

@router.post("/mini-sudoku/complete")
def complete_mini_sudoku(
    request: MiniSudokuCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "mini-sudoku",
        GameProgress.completion_date == today_str
    ).first()
    
    if progress:
        progress.game_data = {"grid": request.grid, "time_taken": request.time_taken}
        db.commit()
        game_streak = calculate_game_streak(db, current_user.id, "mini-sudoku")
        return {"message": "Mini Sudoku progress saved!", "points_awarded": 0, "new_xp": current_user.xp, "current_streak": current_user.current_streak, "game_streak": game_streak}
        
    points_awarded = update_daily_streak_and_xp(db, current_user)
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="mini-sudoku",
        completion_date=today_str,
        score=100,
        game_data={"grid": request.grid, "time_taken": request.time_taken}
    )
    db.add(new_progress)
    db.commit()
    
    game_streak = calculate_game_streak(db, current_user.id, "mini-sudoku")
    
    return {
        "message": "Mini Sudoku completed!",
        "points_awarded": points_awarded,
        "new_xp": current_user.xp,
        "current_streak": current_user.current_streak,
        "game_streak": game_streak
    }

