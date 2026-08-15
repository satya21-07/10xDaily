import re

with open(r'd:\10xDaily\backend\app\api\v1\endpoints\games.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We know the content from lines 1 to 142 is intact.
# The `calculate_game_streak` starts getting broken around line 150.
# The string to search for is:
search_str = """    date_strs = [d[0] for d in dates]
    
    # Start checking from today or yesterday
    today = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    streak = 0
    
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
    }"""

replace_str = """    date_strs = [d[0] for d in dates]
    
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
    }"""

new_content = content.replace(search_str, replace_str)

if new_content == content:
    print("REPLACE FAILED: Could not find search string.")
else:
    with open(r'd:\10xDaily\backend\app\api\v1\endpoints\games.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: games.py has been restored and fixed.")
