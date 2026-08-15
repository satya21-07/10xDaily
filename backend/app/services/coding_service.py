import os
import json
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fallback mock data in case API key is missing or API fails
FALLBACK_DATA = {
    "topic": "Sliding Window",
    "learning_objective": "Understand how the sliding window technique can reduce repeated traversal of contiguous elements.",
    "concepts": [
        {
            "title": "What is a Sliding Window?",
            "explanation": "A sliding window is a sublist that runs over an underlying collection. That is, if you have an array like [a b c d e f], a window of size 3 would be [a b c], then [b c d], then [c d e], and so on.",
            "key_points": [
                "It avoids redundant work in nested loops.",
                "Typically used for contiguous subarrays or substrings.",
                "Can be fixed size or dynamically resizing."
            ],
            "example": "Finding the maximum sum of any contiguous subarray of size k."
        },
        {
            "title": "Fixed vs Dynamic Window",
            "explanation": "Windows can be fixed in size, moving one element at a time, or dynamic, where the window grows and shrinks based on certain conditions.",
            "key_points": [
                "Fixed windows are useful for 'subarray of size k' problems.",
                "Dynamic windows are useful for 'smallest/largest subarray meeting a condition' problems.",
                "Both maintain a running state (sum, count, etc.)."
            ],
            "example": "Dynamic window: Find the smallest subarray with a sum >= S."
        },
        {
            "title": "When to use it?",
            "explanation": "The technique is best applied to problems involving contiguous sequences (arrays or strings) where you need to find an optimal subarray or calculate a running metric.",
            "key_points": [
                "Look for keywords like 'contiguous', 'subarray', 'substring'.",
                "Often optimizes an O(N^2) brute force solution to O(N).",
                "Requires processing elements in order."
            ],
            "example": "Longest substring without repeating characters."
        },
        {
            "title": "Common Mistakes & Optimization",
            "explanation": "A common mistake is off-by-one errors when adjusting window boundaries or updating the running state before/after moving pointers.",
            "key_points": [
                "Ensure the element leaving the window is removed from the state.",
                "Ensure the element entering the window is added to the state.",
                "Be careful with loop conditions (e.g., right < n)."
            ],
            "example": "Forgetting to subtract nums[left] before left++."
        }
    ],
    "questions": [
        {
            "id": "q1-sw",
            "title": "Maximum Subarray Average",
            "description": "Given an array of integers nums and an integer k, find the contiguous subarray of length k that has the maximum average value and return this value.",
            "difficulty": "Easy",
            "pattern": "Sliding Window",
            "tags": ["Array", "Sliding Window"],
            "hint": "Calculate the sum of the first k elements. Then, slide the window by subtracting the element going out and adding the element coming in.",
            "approach": "We can maintain a running sum of the current window of size k. As the window slides to the right, we update the sum in O(1) time.",
            "explanation": "This approach avoids recalculating the sum from scratch for every window, reducing the time complexity from O(N*K) to O(N).",
            "time_complexity": "O(N)",
            "space_complexity": "O(1)",
            "solution_java": "class Solution {\n    public double findMaxAverage(int[] nums, int k) {\n        long sum = 0;\n        for (int i = 0; i < k; i++) sum += nums[i];\n        long maxSum = sum;\n        for (int i = k; i < nums.length; i++) {\n            sum += nums[i] - nums[i - k];\n            maxSum = Math.max(maxSum, sum);\n        }\n        return (double) maxSum / k;\n    }\n}",
            "solution_python": "class Solution:\n    def findMaxAverage(self, nums: List[int], k: int) -> float:\n        curr_sum = sum(nums[:k])\n        max_sum = curr_sum\n        for i in range(k, len(nums)):\n            curr_sum += nums[i] - nums[i - k]\n            max_sum = max(max_sum, curr_sum)\n        return max_sum / k",
            "solution_javascript": "var findMaxAverage = function(nums, k) {\n    let sum = 0;\n    for(let i=0; i<k; i++) sum += nums[i];\n    let maxSum = sum;\n    for(let i=k; i<nums.length; i++) {\n        sum += nums[i] - nums[i-k];\n        maxSum = Math.max(maxSum, sum);\n    }\n    return maxSum / k;\n};",
            "solution_cpp": "class Solution {\npublic:\n    double findMaxAverage(vector<int>& nums, int k) {\n        long long sum = 0;\n        for(int i = 0; i < k; i++) sum += nums[i];\n        long long maxSum = sum;\n        for(int i = k; i < nums.size(); i++) {\n            sum += nums[i] - nums[i-k];\n            maxSum = max(maxSum, sum);\n        }\n        return (double)maxSum / k;\n    }\n};"
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
        "Greedy Algorithms", "Backtracking", "Linked Lists", "Bit Manipulation",
        "Two Pointers", "Stacks & Queues", "Heaps", "Intervals"
    ]
    topic_seed = topics[day_of_year % len(topics)]

    prompt = f"""
    You are an expert Data Structures and Algorithms instructor.
    Generate an original, daily coding lesson focused on the topic: {topic_seed}.
    
    CRITICAL REQUIREMENTS:
    1. Do NOT reproduce or closely paraphrase existing LeetCode problem statements. Generate original interview-style problems.
    2. Generate exactly 4 concepts that progressively teach the topic.
    3. Generate exactly 5 coding questions with this difficulty distribution:
       - Q1: Easy
       - Q2: Easy
       - Q3: Medium
       - Q4: Medium
       - Q5: Hard
    4. Do not generate five questions that test exactly the same technique. Questions should cover meaningful variations of the day's topic/pattern.
    5. Provide valid solutions in Java, Python, JavaScript, and C++ as raw strings without markdown code fences.

    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "topic": "{topic_seed}",
      "learning_objective": "Clear statement of what the user should understand...",
      "concepts": [
        {{
          "title": "Concept 1",
          "explanation": "Detailed but easy-to-understand explanation...",
          "key_points": ["Point 1", "Point 2", "Point 3"],
          "example": "A small practical example..."
        }},
        ... 3 more concepts
      ],
      "questions": [
        {{
          "id": "unique-question-id",
          "title": "Original Problem Title",
          "description": "Full original problem description...",
          "difficulty": "Easy",
          "pattern": "{topic_seed}",
          "tags": ["{topic_seed}", "Array"],
          "hint": "A helpful hint without giving away the full code.",
          "approach": "Explanation of the algorithm before showing code...",
          "explanation": "Explanation teaching WHY the solution works...",
          "time_complexity": "O(N)",
          "space_complexity": "O(1)",
          "solution_java": "class Solution {{ ... }}",
          "solution_python": "class Solution: ...",
          "solution_javascript": "var solve = function(...) {{ ... }};",
          "solution_cpp": "class Solution {{ ... }};"
        }},
        ... 4 more questions
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

