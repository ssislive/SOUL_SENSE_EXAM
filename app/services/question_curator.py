
import random
from typing import List, Dict, Any, Optional
from app.models import UserProfile

class QuestionCurator:
    """
    Curates questions for specific Deep Dive assessments.
    Supports: 'career_clarity', 'work_satisfaction', 'strengths'.
    """
    
    # Hardcoded Question Banks for MVP
    # In a real app, these would come from the database with category_id links.
    QUESTION_BANKS = {
        "career_clarity": [
            "I have a clear 5-year career plan.",
            "I feel my current role utilizes my best skills.",
            "I know exactly what skills I need to learn for my next promotion.",
            "I have a mentor who guides my professional growth.",
            "I am confident in my industry knowledge.",
            "I regularly network with people in my field.",
            "I can clearly articulate my professional value proposition.",
            "I feel secure in my current employment.",
            "I am excited about the future of my career path.",
            "My personal values align with my career choice.",
            "I have unexplored career interests I want to pursue.",
            "I feel stuck in my current role.",
            "I regularly receive constructive feedback.",
            "I have updated my resume/portfolio in the last 6 months.",
            "I know my market value (salary expectation).",
            "I have a clear definition of 'success' for myself.",
            "I prioritize work-life balance in my career planning.",
            "I am open to changing industries if needed.",
            "I have a 'Plan B' if my current job disappears.",
            "I feel my career is progressing at the right pace."
        ],
        "work_satisfaction": [
            "I look forward to starting my work day.",
            "I feel appreciated by my manager/supervisor.",
            "I have good relationships with my colleagues.",
            "My workload is manageable.",
            "I have the tools and resources to do my job well.",
            "I feel my compensation is fair.",
            "The company culture aligns with my personality.",
            "I have autonomy in how I do my work.",
            "I feel my opinions are valued at work.",
            "I rarely think about quitting.",
            "I leave work feeling energized, not drained.",
            "I have a clear understanding of my responsibilities.",
            "I receive recognition for my achievements.",
            "My physical/remote work environment is comfortable.",
            "I have opportunities for professional development.",
            "Communication within my team is effective.",
            "I feel a sense of purpose in my work.",
            "I can disconnect from work when off the clock.",
            "I trust the leadership of my organization.",
            "I would recommend my workplace to a friend."
        ],
        "strengths_deep_dive": [
            "I am aware of my top 3 personal strengths.",
            "I use my strengths every day.",
            "When faced with a challenge, I rely on my natural talents.",
            "I actively seek opportunities to use my strengths.",
            "I can easily describe what I'm best at to others.",
            "I focus more on building strengths than fixing weaknesses.",
            "My strengths have helped me overcome past failures.",
            "Others often compliment me on the same specific traits.",
            "I feel 'in flow' when using my core strengths.",
            "I seek feedback to refine my talents.",
            "I admire the strengths of others without envy.",
            "I know which tasks drain me versus energize me.",
            "I have a plan to further develop my talents.",
            "I help others discover their strengths.",
            "I feel authentic when I am performing well.",
            "I can distinguish between a learned skill and a natural talent.",
            "I consider my strengths when making big decisions.",
            "I have taken a formal strengths assessment before.",
            "I believe my strengths are valuable to my community.",
            "I am confident in what I bring to the table."
        ]
    }

    @staticmethod
    def get_questions(assessment_type: str, count: int = 10) -> List[str]:
        """
        Returns a list of questions for the given type.
        
        Args:
            assessment_type (str): 'career_clarity', 'work_satisfaction', 'strengths_deep_dive'
            count (int): Number of questions to return (5, 10, or 20).
        """
        if assessment_type not in QuestionCurator.QUESTION_BANKS:
            return []
            
        bank = QuestionCurator.QUESTION_BANKS[assessment_type]
        
        # Ensure we don't ask for more than we have
        actual_count = min(count, len(bank))
        
        # For consistency, return the first N questions (not random) so re-takes are stable-ish
        # Or random if we want variety. Let's do first N for now for predictable 'Short'/'Long' versions.
        return bank[:actual_count]

    @staticmethod
    def recommend_tests(user_profile: Any, score_data: Dict[str, Any]) -> List[str]:
        """
        Analyzes user data to recommend specific Deep Dives.
        
        Args:
            user_profile: dict/object with age, occupation, etc.
            score_data: dict with 'total_score', 'stress', 'energy' (if available)
            
        Returns:
            list of recommended assessment_types
        """
        recommendations = []
        
        # Safe extraction
        age = getattr(user_profile, 'age', 0) or 0
        stress = score_data.get('stress', 0)
        energy = score_data.get('energy', 0)
        total_eq = score_data.get('total_score', 0)
        
        # logic
        # 1. Career Clarity
        if 20 <= age <= 35: # Quarter-life crisis / Early career
            recommendations.append("career_clarity")
        elif total_eq > 80 and age > 40: # High EQ mid-career -> Focus on optimization
            recommendations.append("career_clarity")

        # 2. Work Satisfaction
        if stress > 6 or energy < 4: # Signs of burnout
            recommendations.append("work_satisfaction")
            
        # 3. Strengths
        if total_eq < 50: # Low confidence? Build on strengths.
            recommendations.append("strengths_deep_dive")
        elif len(recommendations) == 0: # Default if nothing else triggers
            recommendations.append("strengths_deep_dive")
            
        return list(set(recommendations)) # Unique list
