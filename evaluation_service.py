from typing import Dict, Any, List
import re

class EvaluationService:
    """Service for evaluating AI responses"""
    
    def __init__(self):
        """Initialize evaluation service"""
        pass
    
    def evaluate_response(self, user_query: str, response: str, query_type: str) -> Dict[str, Any]:
        """Evaluate the quality of an AI response"""
        try:
            evaluation = {
                "accuracy": self._evaluate_accuracy(user_query, response, query_type),
                "relevance": self._evaluate_relevance(user_query, response, query_type),
                "completeness": self._evaluate_completeness(user_query, response, query_type),
                "clarity": self._evaluate_clarity(response),
                "overall_score": 0,
                "feedback": []
            }
            
            # Calculate overall score
            scores = [evaluation["accuracy"], evaluation["relevance"], 
                     evaluation["completeness"], evaluation["clarity"]]
            evaluation["overall_score"] = sum(scores) / len(scores)
            
            # Generate feedback
            evaluation["feedback"] = self._generate_feedback(evaluation)
            
            return evaluation
            
        except Exception as e:
            return {
                "accuracy": 3,
                "relevance": 3,
                "completeness": 3,
                "clarity": 3,
                "overall_score": 3,
                "feedback": ["Evaluation service temporarily unavailable"],
                "error": str(e)
            }
    
    def _evaluate_accuracy(self, query: str, response: str, query_type: str) -> int:
        """Evaluate response accuracy (1-5 scale)"""
        if not response or response.strip() == "":
            return 1
        
        # Check for error messages
        if any(word in response.lower() for word in ['error', 'failed', 'unavailable', 'limitation']):
            return 2
        
        # Check for weather responses
        if query_type == "weather":
            weather_indicators = ['temperature', 'humidity', 'wind', 'pressure', '°c', '°f']
            if any(indicator in response.lower() for indicator in weather_indicators):
                return 4
            return 3
        
        # Check for RAG responses
        if query_type == "rag":
            if 'document' in response.lower() or 'chunk' in response.lower():
                return 4
            return 3
        
        return 3
    
    def _evaluate_relevance(self, query: str, response: str, query_type: str) -> int:
        """Evaluate response relevance (1-5 scale)"""
        if not response:
            return 1
        
        # Check if response addresses the query
        query_words = set(re.findall(r'\w+', query.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        
        # Calculate word overlap
        overlap = len(query_words.intersection(response_words))
        if overlap > 0:
            return min(5, 3 + overlap)
        
        return 3
    
    def _evaluate_completeness(self, query: str, response: str, query_type: str) -> int:
        """Evaluate response completeness (1-5 scale)"""
        if not response:
            return 1
        
        # Check response length
        word_count = len(response.split())
        if word_count < 10:
            return 2
        elif word_count < 50:
            return 3
        elif word_count < 200:
            return 4
        else:
            return 5
    
    def _evaluate_clarity(self, response: str) -> int:
        """Evaluate response clarity (1-5 scale)"""
        if not response:
            return 1
        
        # Check for proper formatting
        has_headers = '#' in response or '**' in response
        has_structure = any(char in response for char in ['•', '-', '*', '1.', '2.'])
        has_paragraphs = '\n\n' in response
        
        score = 3
        if has_headers:
            score += 1
        if has_structure:
            score += 1
        if has_paragraphs:
            score += 1
        
        return min(5, score)
    
    def _generate_feedback(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate feedback based on evaluation scores"""
        feedback = []
        
        if evaluation["accuracy"] < 3:
            feedback.append("⚠️ Response accuracy could be improved")
        
        if evaluation["relevance"] < 3:
            feedback.append("⚠️ Response could be more relevant to the query")
        
        if evaluation["completeness"] < 3:
            feedback.append("⚠️ Response could be more comprehensive")
        
        if evaluation["clarity"] < 3:
            feedback.append("⚠️ Response could be clearer and better formatted")
        
        if evaluation["overall_score"] >= 4:
            feedback.append("✅ Excellent response quality")
        elif evaluation["overall_score"] >= 3:
            feedback.append("✅ Good response quality")
        else:
            feedback.append("⚠️ Response quality needs improvement")
        
        return feedback
    
    def get_evaluation_summary(self, evaluation: Dict[str, Any]) -> str:
        """Get a formatted evaluation summary"""
        summary = f"""
## 📊 Response Evaluation Summary

### 📈 Quality Scores (1-5 Scale)
- **Accuracy**: {evaluation.get('accuracy', 'N/A')}/5
- **Relevance**: {evaluation.get('relevance', 'N/A')}/5  
- **Completeness**: {evaluation.get('completeness', 'N/A')}/5
- **Clarity**: {evaluation.get('clarity', 'N/A')}/5

### 🎯 Overall Score: {evaluation.get('overall_score', 'N/A'):.1f}/5

### 💡 Feedback
"""
        
        for feedback in evaluation.get('feedback', []):
            summary += f"- {feedback}\n"
        
        return summary.strip() 