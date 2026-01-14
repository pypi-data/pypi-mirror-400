"""
Utility functions for RL module.

This module provides helper utilities for reinforcement learning operations.
"""

import base64
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# Configuration constants
_MAX_REQUESTS = 200  # Daily request limit for external service (increased from 150)
_CACHE_FILE = Path.home() / ".matplotlab" / ".request_cache"


def _load_cache():
    """Load cached request data."""
    if not _CACHE_FILE.exists():
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0}
    
    try:
        with open(_CACHE_FILE, 'r') as f:
            data = json.load(f)
        
        # Reset count if new day
        today = datetime.now().strftime("%Y-%m-%d")
        if data.get("date") != today:
            data = {"date": today, "count": 0}
        
        return data
    except Exception:
        return {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0}


def _save_cache(data):
    """Save cache data."""
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def _check_request_limit():
    """Check request limit."""
    data = _load_cache()
    
    if data["count"] >= _MAX_REQUESTS:
        remaining_time = datetime.now().replace(hour=23, minute=59, second=59) - datetime.now()
        hours = int(remaining_time.total_seconds() // 3600)
        minutes = int((remaining_time.total_seconds() % 3600) // 60)
        
        raise RuntimeError(
            f"WARNING: Daily request limit exceeded!\n"
            f"You've used {data['count']}/{_MAX_REQUESTS} requests today.\n"
            f"Limit resets in {hours}h {minutes}m.\n\n"
            f"Use .show() method for instant code (no limits)!"
        )
    
    return data


def _update_counter():
    """Update request counter."""
    data = _load_cache()
    data["count"] += 1
    _save_cache(data)
    
    remaining = _MAX_REQUESTS - data["count"]
    if remaining <= 10:
        print(f"WARNING: {remaining} requests remaining today")


def _get_config():
    """Load configuration token."""
    # Configuration token for external service
    # Encode your token: base64.b64encode(b"YOUR_TOKEN").decode()
    _token = "QUl6YVN5Q0ZrWUJzNmZ6Uy10bWRWTENRUF9ETi1qN2xOZHJidlJn"
    
    if _token == "REPLACE_WITH_BASE64_ENCODED_KEY":
        raise ValueError(
            "Configuration not set! Follow setup instructions in documentation."
        )
    
    try:
        return base64.b64decode(_token.encode()).decode()
    except Exception as e:
        raise ValueError(f"Configuration error: {e}")


def query(text: str, mode: int = 1, temp: float = 0.7, max_length: int = 2048) -> str:
    """
    Query external service for information with THREE modes.
    
    Parameters:
    -----------
    text : str
        Your question/query OR "code + error" for mode 3
    mode : int (1, 2, or 3)
        1 = CODE MODE: Get complete, beginner-friendly code without errors
        2 = EXPLANATION MODE: Get detailed concept explanation  
        3 = ERROR FIX MODE: Fix syntax/runtime errors in your code
    temp : float
        Temperature for response generation (default: 0.7)
    max_length : int
        Maximum response tokens (default: 2048 - approx 1500-2000 words)
    
    Returns:
    --------
    str
        AI-generated response (code, explanation, or fixed code based on mode)
    
    Examples:
    ---------
    >>> from matplotlab import ann
    
    >>> # MODE 1: Get complete working code
    >>> code = ann.query("How to train a simple neural network?", mode=1)
    >>> print(code)
    
    >>> # MODE 2: Get detailed explanation
    >>> explanation = ann.query("What is backpropagation?", mode=2)
    >>> print(explanation)
    
    >>> # MODE 3: Fix errors (provide code + error together)
    >>> broken_code = '''
    ... import torch
    ... model = nn.Linear(10, 1
    ... x = torch.rand(5, 10)
    ... y = model(x)
    ... 
    ... ERROR: SyntaxError: invalid syntax (missing closing parenthesis)
    ... '''
    >>> fixed = ann.query(broken_code, mode=3)
    >>> print(fixed)
    
    Notes:
    ------
    - Mode 1: Returns complete, error-free, beginner-friendly CODE
    - Mode 2: Returns detailed, humanized EXPLANATION of concepts
    - Mode 3: Analyzes error + fixes code with explanation
    - Daily limit: 200 requests (resets at midnight)
    - Max response: ~1500-2000 words (2048 tokens)
    - Use .show() method for instant code viewing (no limits)
    - Mode 3 accepts EITHER "just error message" OR "code + error together"
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "Required package not installed. Run: pip install -e .[rl]"
        )
    
    # Check request limit
    _check_request_limit()
    
    # Load configuration
    token = _get_config()
    genai.configure(api_key=token)
    
    # Initialize model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare request based on mode
    if mode == 1:
        # CODE MODE: Complete, error-free, beginner-friendly code
        request_text = f"""
You are an expert programming instructor creating educational code examples for undergraduate computer science students who are learning Python and Machine Learning/Reinforcement Learning for the first time.

Your PRIMARY OBJECTIVE is to provide COMPLETE, FULLY FUNCTIONAL, ERROR-FREE, PRODUCTION-READY CODE that a complete beginner can copy, paste, and run immediately without any modifications whatsoever.

═══════════════════════════════════════════════════════════════════════
ABSOLUTE REQUIREMENTS (MUST FOLLOW):
═══════════════════════════════════════════════════════════════════════

CODE COMPLETENESS:
1. Write EVERY LINE of code from start to finish - NO placeholders
2. NEVER use "# rest of code here", "...", "# similar for other cases", "# implement remaining methods", or ANY shortcuts
3. EVERY function must have FULL implementation with complete logic
4. EVERY class must have ALL methods fully written out
5. EVERY loop must be complete (no "# repeat for others")
6. EVERY conditional must handle all cases explicitly
7. If something is repeated, write it out EVERY TIME - no "etc."

CODE QUALITY:
8. Code must be 100% functional with ZERO errors or bugs
9. Must run successfully on first try without any debugging
10. Use ONLY beginner-friendly techniques - NO advanced features like:
    - lambda functions
    - list comprehensions
    - assert statements
    - decorators
    - context managers
    - f-strings with complex expressions
11. Use simple for loops, if-else statements, and basic operations
12. All variable names must be descriptive and self-explanatory
13. Follow PEP 8 style guidelines strictly
14. Handle edge cases properly with clear error messages

PYTORCH NEURAL NETWORK REQUIREMENTS (VERY IMPORTANT):
15. ALWAYS use nn.Sequential() for creating neural networks - NEVER use class-based approach
16. Example GOOD code:
    model = nn.Sequential(
        nn.Linear(input_size, 16),
        nn.ReLU(),
        nn.Linear(16, 8),
        nn.ReLU(),
        nn.Linear(8, 1),
        nn.Sigmoid()
    )
17. NEVER create custom nn.Module classes with __init__ and forward methods
18. Training loop should be simple:
    - One for loop for epochs
    - Forward pass: y_pred = model(X_train)
    - Compute loss: loss = loss_fn(y_pred, y_train)
    - Zero gradients: optimizer.zero_grad()
    - Backward pass: loss.backward()
    - Update weights: optimizer.step()
    - Print progress: print("Epoch:", i+1, "Loss:", round(loss.item(), 4))
19. Store losses in a simple list: all_loss = [] and all_loss.append(loss.item())
20. Use basic print statements - no fancy progress bars or logging
21. Variable names: X_train, y_train, X_test, y_test, model, loss_fn, optimizer
22. Keep it simple - students should understand every single line

DOCUMENTATION REQUIREMENTS:
23. NO EMOJIS anywhere in code or text
24. Add comments ONLY where logic is non-obvious
25. Every function must have a clear docstring explaining purpose, parameters, and returns
26. Keep comments brief, precise, and beginner-appropriate
27. Comments should explain WHY, not WHAT (code should be self-explanatory)

CODE STRUCTURE:
28. Always start with necessary import statements
29. Define any helper functions before main code
30. Main code should follow logical progression
31. End with simple, working usage example that demonstrates the code
32. Include print statements in example to show output

FORMATTING REQUIREMENTS:
33. Use consistent 4-space indentation
34. One blank line between functions
35. Two blank lines between classes (only if absolutely necessary - prefer simple functions)
36. Proper spacing around operators (a + b, not a+b)
37. Maximum line length: 79 characters

BEGINNER-FRIENDLY REQUIREMENTS:
38. Assume student has only basic Python knowledge (variables, loops, if-else)
39. Explain any ML/RL concepts used in a brief comment
40. Use descriptive variable names that make code self-documenting
41. Break complex operations into smaller steps with intermediate variables
42. Prefer clarity over cleverness - simple is better than complex

RESPONSE FORMAT:
43. Start with 1-2 sentences explaining what the code does
44. Then provide complete code block
45. After code, add 2-3 sentences explaining how it works at high level
46. Keep all text professional - no emojis, no exclamation marks, no informal language

═══════════════════════════════════════════════════════════════════════

Student's Request: {text}

Now provide COMPLETE, FULLY FUNCTIONAL, BEGINNER-FRIENDLY CODE following ALL 46 requirements above. Remember: NO SHORTCUTS, NO PLACEHOLDERS, COMPLETE IMPLEMENTATION ONLY, USE nn.Sequential FOR PYTORCH MODELS.
"""
    
    elif mode == 2:
        # EXPLANATION MODE: Detailed concept explanation
        request_text = f"""
You are a patient, experienced university professor teaching undergraduate students who are encountering Machine Learning and Reinforcement Learning concepts for the very first time. Your teaching style is warm, encouraging, and exceptionally clear.

Your PRIMARY OBJECTIVE is to provide COMPREHENSIVE, DETAILED, EASY-TO-UNDERSTAND EXPLANATIONS that help complete beginners develop deep, intuitive understanding of complex concepts.

═══════════════════════════════════════════════════════════════════════
ABSOLUTE REQUIREMENTS (MUST FOLLOW):
═══════════════════════════════════════════════════════════════════════

AUDIENCE UNDERSTANDING:
1. Assume student has ZERO prior knowledge of the topic
2. Assume student knows only basic programming (variables, loops, functions)
3. Assume student has high school level math (algebra, basic calculus)
4. Never assume familiarity with ML/RL terminology
5. Treat every technical term as if student is hearing it for the first time

CONTENT REQUIREMENTS:
6. Provide COMPLETE, THOROUGH explanations - not brief summaries
7. Explain the WHY before the HOW
8. Define every technical term when you first use it
9. Connect new concepts to things students already understand
10. Use at least TWO different analogies from everyday life
11. Explain common mistakes and misconceptions explicitly
12. Include concrete, relatable examples

EXPLANATION STRUCTURE (MANDATORY ORDER):
13. Start with simple one-sentence definition in plain English
14. Then explain what problem this concept solves
15. Use detailed real-world analogy (restaurant, library, sports, etc.)
16. Break down the concept into smallest possible steps
17. Explain each step with clear reasoning
18. Provide concrete numerical example if applicable
19. Explain when and why to use this concept
20. Address common confusions explicitly
21. Compare with similar concepts if relevant
22. End with key takeaways (3-5 bullet points)

LANGUAGE STYLE:
23. NO EMOJIS anywhere in the explanation
24. Use conversational but professional tone
25. Write in second person ("you") to be engaging
26. Use active voice, not passive voice
27. Keep sentences simple - one idea per sentence
28. Break into short paragraphs (3-4 sentences maximum)
29. Use transition words to connect ideas smoothly
30. Be encouraging without being condescending

FORMATTING:
31. Use clear section headings to organize content
32. Use bullet points for lists of items
33. Use numbered steps for sequential processes
34. Bold or emphasize key terms when first defined
35. Keep technical jargon to minimum - explain it when used

ANALOGY REQUIREMENTS:
36. Use everyday situations (cooking, driving, shopping, gaming, sports)
37. Make analogies detailed with specific examples
38. Ensure analogies are accurate to the concept
39. Use multiple analogies to reinforce understanding from different angles

DEPTH OF EXPLANATION:
40. Go into sufficient detail that student can explain it to others
41. Anticipate follow-up questions and answer them preemptively
42. Explain not just WHAT happens but WHY it happens
43. Provide intuition for why the concept works the way it does
44. Connect to broader context of ML/RL when relevant

EXAMPLES:
45. Include at least one concrete, worked-out example
46. Use real numbers and scenarios, not abstract variables
47. Walk through example step-by-step with explanations
48. Show both correct usage and common mistakes

MISCONCEPTIONS:
49. Explicitly address at least 2-3 common beginner mistakes
50. Explain why these misconceptions are incorrect
51. Provide correct understanding to replace misconception

═══════════════════════════════════════════════════════════════════════

Student's Question: {text}

Now provide COMPREHENSIVE, DETAILED, BEGINNER-FRIENDLY EXPLANATION following ALL 51 requirements above. Make it thorough enough that a complete beginner can develop deep understanding and explain the concept to others confidently.
"""
    
    elif mode == 3:
        # ERROR FIX MODE: Debug and fix code errors
        request_text = f"""
You are an expert debugging assistant helping undergraduate computer science students fix errors in their Python/PyTorch/TensorFlow code.

Your PRIMARY OBJECTIVE is to:
1. IDENTIFY the exact error in the code
2. EXPLAIN what caused the error in simple terms
3. PROVIDE the COMPLETE CORRECTED CODE that works perfectly
4. EXPLAIN what you changed and why

═══════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS:
═══════════════════════════════════════════════════════════════════════

ERROR ANALYSIS:
1. Carefully analyze the error message provided
2. Identify the root cause (syntax error, runtime error, logic error, etc.)
3. Explain in plain English what went wrong
4. Point out the exact line(s) where error occurred

CODE FIXING RULES:
5. Provide COMPLETE fixed code - not just snippets
6. Fix ALL errors, not just the first one
7. Ensure code follows beginner-friendly style:
   - Use nn.Sequential() for PyTorch models (NO custom classes)
   - Simple for loops (NO list comprehensions)
   - Clear variable names
   - NO lambda functions
   - NO assert statements
8. Test logic to ensure fix actually solves the problem
9. Handle edge cases properly

RESPONSE STRUCTURE (MANDATORY):
10. Start with: "ERROR FOUND: [brief description]"
11. Then: "CAUSE: [explain what caused it in simple terms]"
12. Then: "FIXED CODE:" followed by complete corrected code
13. After code: "CHANGES MADE:" with bullet points explaining fixes
14. End with: "HOW TO AVOID: [tips to prevent this error]"

INPUT HANDLING:
15. If input contains BOTH code AND error: analyze both together
16. If input contains ONLY error message: provide general fix strategy
17. If input contains ONLY code: scan for potential errors and fix them
18. Be flexible - understand the student's intent

OUTPUT REQUIREMENTS:
19. NO EMOJIS anywhere
20. Use clear section headers
21. Keep explanations concise but complete
22. Provide working code that can be copy-pasted immediately
23. Use professional, encouraging tone

═══════════════════════════════════════════════════════════════════════

Student's Code/Error:
{text}

Now analyze the error, fix the code completely, and provide detailed explanation following ALL requirements above.
"""
    
    else:
        # Invalid mode
        return f"ERROR: Invalid mode={mode}. Use mode=1 (code), mode=2 (explanation), or mode=3 (fix errors)."
    
    try:
        # Send request
        result = model.generate_content(
            request_text,
            generation_config={
                'temperature': temp,
                'max_output_tokens': max_length,
            }
        )
        
        # Update counter
        _update_counter()
        
        # Return response
        if hasattr(result, 'text'):
            return result.text
        else:
            return str(result)
            
    except Exception as e:
        return f"WARNING: Service error: {str(e)}"


def _test_query():
    """Test external query service."""
    try:
        response = query("Say hello in one sentence.")
        print("Service Test:")
        print(response)
        return True
    except Exception as e:
        print(f"Service Test Failed:")
        print(f"   {str(e)}")
        return False


# Create wrapper for .show() compatibility
class QueryWrapper:
    """Wrapper class for query function."""
    
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def show(self, include_imports=True, clean=True):
        """Display function usage information."""
        print("=" * 80)
        print("📋 FUNCTION: query()")
        print("=" * 80)
        print()
        print("Query external knowledge service for RL information.")
        print()
        print("USAGE:")
        print("------")
        print("from sohail_mlsuite import rl")
        print()
        print("# Ask questions")
        print('result = rl.query("How do I implement policy iteration?")')
        print("print(result)")
        print()
        print("# Get code examples")
        print('code = rl.query("write python code for epsilon-greedy")')
        print("print(code)")
        print()
        print("TIPS:")
        print("----")
        print("- Be specific in queries")
        print("- Ask for 'code only' for just code")
        print("- Limited to 80 requests per day")
        print("=" * 80)


# Wrap function
query = QueryWrapper(query)
