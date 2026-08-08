import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fallback mock data in case API key is missing or API fails
FALLBACK_DATA = {
    "topic": "Arrays & Two Pointers",
    "concepts": [
        {
            "title": "Arrays",
            "explanation": "An array is a collection of items stored at contiguous memory locations. The idea is to store multiple items of the same type together."
        },
        {
            "title": "Two Pointers Technique",
            "explanation": "Two pointers is really an easy and effective technique that is typically used for searching pairs in a sorted array."
        },
        {
            "title": "Time Complexity",
            "explanation": "Accessing an element is O(1). Searching an element is O(N). Using two pointers can often reduce nested loops from O(N^2) to O(N)."
        },
        {
            "title": "Space Complexity",
            "explanation": "Arrays take O(N) space. The two pointer technique itself only uses O(1) auxiliary space."
        }
    ],
    "questions": [
        {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "difficulty": "Easy",
            "hint": "Can you use a Hash Map to store the elements you have seen so far to do this in O(N) time?",
            "solution_java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        Map<Integer, Integer> map = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int complement = target - nums[i];\n            if (map.containsKey(complement)) {\n                return new int[] { map.get(complement), i };\n            }\n            map.put(nums[i], i);\n        }\n        return new int[] {};\n    }\n}",
            "solution_python": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        seen = {}\n        for i, num in enumerate(nums):\n            complement = target - num\n            if complement in seen:\n                return [seen[complement], i]\n            seen[num] = i\n        return []"
        },
        {
            "title": "Container With Most Water",
            "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water.",
            "difficulty": "Medium",
            "hint": "Start with the maximum width container and go to a shorter width container if there is a vertical line longer than the current containers shorter line.",
            "solution_java": "class Solution {\n    public int maxArea(int[] height) {\n        int maxarea = 0;\n        int left = 0; \n        int right = height.length - 1;\n        while (left < right) {\n            int width = right - left;\n            maxarea = Math.max(maxarea, Math.min(height[left], height[right]) * width);\n            if (height[left] <= height[right]) {\n                left++;\n            } else {\n                right--;\n            }\n        }\n        return maxarea;\n    }\n}",
            "solution_python": "class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        max_area = 0\n        left, right = 0, len(height) - 1\n        while left < right:\n            width = right - left\n            max_area = max(max_area, min(height[left], height[right]) * width)\n            if height[left] <= height[right]:\n                left += 1\n            else:\n                right -= 1\n        return max_area"
        }
    ]
}

def generate_daily_coding_lesson() -> dict:
    """Uses Groq API to generate a daily coding lesson."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY not found in environment. Using fallback data.")
        return FALLBACK_DATA

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        logger.error("groq package not installed. Using fallback data.")
        return FALLBACK_DATA
    
    # We use day of year as a seed concept for variety
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    topics = [
        "Dynamic Programming", "Graph Theory", "Hash Maps & Sets", 
        "Binary Search Trees", "Sliding Window", "Tries", 
        "Greedy Algorithms", "Backtracking", "Linked Lists", "Bit Manipulation"
    ]
    topic_seed = topics[day_of_year % len(topics)]

    prompt = f"""
    You are an expert Data Structures and Algorithms instructor.
    Generate a daily coding lesson focused on the topic: {topic_seed}.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "topic": "{topic_seed}",
      "concepts": [
        {{ "title": "Concept 1", "explanation": "Detailed explanation..." }},
        {{ "title": "Concept 2", "explanation": "Detailed explanation..." }},
        {{ "title": "Concept 3", "explanation": "Detailed explanation..." }},
        {{ "title": "Concept 4", "explanation": "Detailed explanation..." }}
      ],
      "questions": [
        {{
          "title": "Famous Leetcode Style Question 1",
          "description": "Full problem description...",
          "difficulty": "Easy/Medium/Hard",
          "hint": "A helpful hint without giving away the full code.",
          "solution_java": "The optimal solution in Java as a raw string without markdown blocks",
          "solution_python": "The optimal solution in Python as a raw string without markdown blocks"
        }},
        {{
          "title": "Famous Leetcode Style Question 2",
          "description": "Full problem description...",
          "difficulty": "Medium/Hard",
          "hint": "A helpful hint without giving away the full code.",
          "solution_java": "The optimal solution in Java as a raw string without markdown blocks",
          "solution_python": "The optimal solution in Python as a raw string without markdown blocks"
        }}
      ]
    }}
    
    Ensure the JSON is perfectly formatted and contains no markdown code blocks outside of the raw JSON itself. Ensure code strings properly escape newlines and quotes.
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that strictly outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        text_response = response.choices[0].message.content
        
        # Clean up any potential markdown formatting
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response.rsplit("```", 1)[0]
            
        data = json.loads(text_response.strip())
        return data
    except Exception as e:
        logger.error(f"Error generating Groq content: {e}")
        return FALLBACK_DATA
