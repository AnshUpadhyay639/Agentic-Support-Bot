import random
import logging
from typing import Dict, List, Tuple

class FeedbackSimulator:
    """
    Simulates user feedback for support bot responses.
    This provides a more sophisticated feedback mechanism than simple random selection.
    """
    
    # Feedback types
    FEEDBACK_TYPES = ["good", "too vague", "not helpful", "incorrect", "partially correct"]
    
    # Keywords that might indicate a good response
    POSITIVE_KEYWORDS = [
        "step", "guide", "instruction", "detail", "specific", 
        "exactly", "precisely", "clearly", "here's how", "follow"
    ]
    
    # Keywords that might indicate a vague response
    VAGUE_KEYWORDS = [
        "might", "maybe", "possibly", "could", "perhaps", 
        "sometimes", "generally", "typically", "often", "usually"
    ]
    
    def __init__(self, seed: int = None):
        """Initialize the feedback simulator with optional random seed."""
        if seed is not None:
            random.seed(seed)
        
        self.feedback_history = []
        logging.info("Initialized FeedbackSimulator")
    
    def generate_feedback(self, query: str, response: Dict, context: str = None) -> Tuple[str, float]:
        """
        Generate simulated feedback for a response.
        
        Args:
            query: The user's query
            response: The bot's response dictionary (containing answer, confidence, etc.)
            context: Optional context used to generate the response
            
        Returns:
            Tuple of (feedback_type, confidence_score)
        """
        answer = response.get("answer", "")
        confidence = response.get("confidence", 0.0)
        
        # Base probabilities for different feedback types
        probabilities = {
            "good": 0.4,
            "too vague": 0.2,
            "not helpful": 0.2,
            "incorrect": 0.1,
            "partially correct": 0.1
        }
        
        # Adjust probabilities based on confidence
        if confidence > 0.8:
            probabilities["good"] += 0.3
            probabilities["incorrect"] -= 0.05
        elif confidence < 0.4:
            probabilities["good"] -= 0.2
            probabilities["not helpful"] += 0.1
            probabilities["incorrect"] += 0.1
        
        # Adjust based on answer length
        if len(answer.split()) < 10:  # Very short answer
            probabilities["too vague"] += 0.2
            probabilities["good"] -= 0.1
        elif len(answer.split()) > 50:  # Very long answer
            probabilities["good"] -= 0.05  # Long answers can be good but might be too verbose
        
        # Check for vague language
        vague_count = sum(1 for word in self.VAGUE_KEYWORDS if word.lower() in answer.lower())
        if vague_count > 2:
            probabilities["too vague"] += 0.15
            probabilities["good"] -= 0.1
        
        # Check for specific, helpful language
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word.lower() in answer.lower())
        if positive_count > 2:
            probabilities["good"] += 0.15
            probabilities["too vague"] -= 0.05
        
        # Check if the answer contains parts of the query (might be repeating the question)
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(query_words.intersection(answer_words)) / len(query_words) if query_words else 0
        
        if overlap > 0.7:  # High overlap might mean just repeating the question
            probabilities["not helpful"] += 0.2
            probabilities["good"] -= 0.1
        
        # Normalize probabilities
        total = sum(probabilities.values())
        normalized_probs = {k: v/total for k, v in probabilities.items()}
        
        # Select feedback type based on probabilities
        feedback_type = random.choices(
            list(normalized_probs.keys()),
            weights=list(normalized_probs.values()),
            k=1
        )[0]
        
        # Calculate a confidence score for this feedback (how certain we are)
        feedback_confidence = normalized_probs[feedback_type]
        
        # Log the feedback
        logging.info(f"Generated feedback: {feedback_type} (confidence: {feedback_confidence:.2f})")
        
        # Store in history
        self.feedback_history.append({
            "query": query,
            "answer": answer,
            "feedback": feedback_type,
            "confidence": confidence,
            "feedback_confidence": feedback_confidence
        })
        
        return feedback_type, feedback_confidence
    
    def get_detailed_feedback(self, query: str, response: Dict) -> Dict:
        """
        Generate more detailed feedback with specific improvement suggestions.
        
        Args:
            query: The user's query
            response: The bot's response dictionary
            
        Returns:
            Dictionary with feedback type and improvement suggestions
        """
        feedback_type, confidence = self.generate_feedback(query, response)
        answer = response.get("answer", "")
        
        suggestions = []
        
        if feedback_type == "too vague":
            suggestions = [
                "Add more specific details",
                "Include step-by-step instructions",
                "Provide concrete examples",
                "Avoid tentative language like 'might' or 'could'",
                "Be more assertive in your response"
            ]
        elif feedback_type == "not helpful":
            suggestions = [
                "Address the question more directly",
                "Provide actionable information",
                "Include relevant context from the documentation",
                "Focus on solving the user's specific problem",
                "Offer alternative solutions if applicable"
            ]
        elif feedback_type == "incorrect":
            suggestions = [
                "Verify information against the documentation",
                "Check for factual errors",
                "Ensure the answer is up-to-date",
                "Make sure you're addressing the right question",
                "Double-check technical details"
            ]
        elif feedback_type == "partially correct":
            suggestions = [
                "Expand on the correct parts",
                "Fix inaccuracies in specific sections",
                "Provide more comprehensive information",
                "Clarify ambiguous statements",
                "Add missing important details"
            ]
        
        # Select 1-2 relevant suggestions
        if suggestions:
            selected_suggestions = random.sample(suggestions, min(2, len(suggestions)))
        else:
            selected_suggestions = []
        
        return {
            "feedback_type": feedback_type,
            "confidence": confidence,
            "suggestions": selected_suggestions
        }
    
    def get_feedback_stats(self) -> Dict:
        """Return statistics about the feedback history."""
        if not self.feedback_history:
            return {"total": 0}
        
        stats = {"total": len(self.feedback_history)}
        
        # Count by feedback type
        for feedback_type in self.FEEDBACK_TYPES:
            count = sum(1 for item in self.feedback_history if item["feedback"] == feedback_type)
            stats[feedback_type] = count
            stats[f"{feedback_type}_percent"] = count / len(self.feedback_history) * 100
        
        # Average confidence
        avg_confidence = sum(item["confidence"] for item in self.feedback_history) / len(self.feedback_history)
        stats["avg_confidence"] = avg_confidence
        
        return stats

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create simulator
    simulator = FeedbackSimulator(seed=42)  # Fixed seed for reproducibility
    
    # Test with some example responses
    test_queries = [
        "How do I reset my password?",
        "What's your refund policy?",
        "My device isn't working"
    ]
    
    test_responses = [
        {"answer": "You might be able to reset your password somewhere on the website.", "confidence": 0.3},
        {"answer": "Our refund policy allows returns within 30 days of purchase. The product must be in its original packaging and in resellable condition.", "confidence": 0.9},
        {"answer": "Have you tried turning it off and on again?", "confidence": 0.5}
    ]
    
    for query, response in zip(test_queries, test_responses):
        feedback, confidence = simulator.generate_feedback(query, response)
        print(f"Query: {query}")
        print(f"Response: {response['answer']}")
        print(f"Feedback: {feedback} (confidence: {confidence:.2f})")
        
        detailed = simulator.get_detailed_feedback(query, response)
        print(f"Suggestions: {detailed['suggestions']}")
        print("-" * 50)
    
    # Print stats
    print("\nFeedback Statistics:")
    stats = simulator.get_feedback_stats()
    for key, value in stats.items():
        print(f"{key}: {value}") 