import logging
import os
import random
import time
from typing import List, Dict, Tuple, Optional
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import PyPDF2
import colorama
from colorama import Fore, Style

# Import our custom modules
from feedback_simulator import FeedbackSimulator

# Initialize colorama for colored console output
colorama.init()

# Set up logging
logging.basicConfig(
    filename='support_bot_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DocumentProcessor:
    """Handles document loading and processing from various formats."""
    
    @staticmethod
    def load_document(path: str) -> str:
        """Load document content from file path."""
        logging.info(f"Loading document from {path}")
        
        if path.lower().endswith('.pdf'):
            return DocumentProcessor._load_pdf(path)
        elif path.lower().endswith('.txt'):
            return DocumentProcessor._load_text(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")
    
    @staticmethod
    def _load_pdf(path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            logging.error(f"Error loading PDF: {e}")
            raise
    
    @staticmethod
    def _load_text(path: str) -> str:
        """Load text from a plain text file."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error loading text file: {e}")
            raise

class SupportBotAgent:
    """Agentic support bot that learns from documents and improves through feedback."""
    
    def __init__(self, document_path: str):
        """Initialize the support bot with document and models."""
        logging.info("Initializing SupportBotAgent")
        print(f"{Fore.CYAN}Initializing support bot...{Style.RESET_ALL}")
        
        self.document_path = document_path
        self.document_text = DocumentProcessor.load_document(document_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qa_pipeline = pipeline('question-answering', model='distilbert-base-uncased')
        self.corpus_embeddings = self.embedding_model.encode(self._split_into_sections(self.document_text), convert_to_tensor=True)
        
        # Initialize feedback simulator
        self.feedback_simulator = FeedbackSimulator()
        
        # Performance tracking
        self.performance_history = []
        self.feedback_stats = {"good": 0, "not helpful": 0, "too vague": 0, "incorrect": 0, "partially correct": 0}
        
        # Decision-making parameters
        self.confidence_threshold = 0.7
        self.max_iterations = 3
        
        # Learning parameters
        self.learning_rate = 0.05
        self.improvement_strategies = {
            "too vague": self._improve_vague_response,
            "not helpful": self._improve_unhelpful_response,
            "incorrect": self._improve_incorrect_response,
            "partially correct": self._improve_partial_response
        }
        
        logging.info(f"Loaded document with {len(self.corpus_embeddings)} sections")
        print(f"{Fore.GREEN}Support bot initialized successfully with {len(self.corpus_embeddings)} document sections{Style.RESET_ALL}")
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split document into meaningful sections for retrieval."""
        # First try to split by double newlines (paragraphs)
        sections = [s.strip() for s in text.split('\n\n') if s.strip()]
        
        # If sections are too long, split them further
        processed_sections = []
        for section in sections:
            if len(section.split()) > 100:  # If section has more than 100 words
                # Split by single newlines
                subsections = [s.strip() for s in section.split('\n') if s.strip()]
                processed_sections.extend(subsections)
            else:
                processed_sections.append(section)
        
        return processed_sections
    
    def find_relevant_sections(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Find the most relevant sections for a given query."""
        query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.corpus_embeddings, top_k=top_k)
        return [(self._split_into_sections(self.document_text)[hit['corpus_id']], hit['score']) for hit in hits[0]]
    
    def answer_query(self, query: str) -> Dict:
        """Generate an answer for the given query."""
        relevant_sections = self.find_relevant_sections(query)
        best_section = relevant_sections[0][0] if relevant_sections else ""
        result = self.qa_pipeline(question=query, context=best_section)
        
        # Ensure 'reasoning' is included in the response
        response = {
            "answer": result.get("answer", "No answer found."),
            "confidence": result.get("score", 0.0),
            "context": best_section,
            "reasoning": "Generated using the most relevant section."
        }
        
        return response
    
    def get_feedback(self, query: str, response: Dict) -> Dict:
        """
        Get simulated feedback on the response.
        Uses the FeedbackSimulator for more realistic feedback.
        """
        detailed_feedback = self.feedback_simulator.get_detailed_feedback(query, response)
        feedback_type = detailed_feedback["feedback_type"]
        
        # Update feedback stats
        self.feedback_stats[feedback_type] += 1
        
        logging.info(f"Feedback received: {feedback_type}")
        logging.info(f"Suggestions: {detailed_feedback['suggestions']}")
        
        return detailed_feedback
    
    def _improve_vague_response(self, query: str, response: Dict, feedback: Dict) -> Dict:
        """Strategy to improve vague responses."""
        # Get more specific information from the document
        relevant_sections = self.find_relevant_sections(query, top_k=2)
        additional_context = relevant_sections[0][0] if relevant_sections else ""
        
        # Extract specific details
        specific_details = additional_context.split('.')[:2]  # First two sentences
        specific_text = '. '.join(specific_details) + '.'
        
        new_response = response.copy()
        new_response["answer"] = f"{response['answer']} To be more specific: {specific_text}"
        new_response["reasoning"] = f"Added specific details to address 'too vague' feedback."
        
        return new_response
    
    def _improve_unhelpful_response(self, query: str, response: Dict, feedback: Dict) -> Dict:
        """Strategy to improve unhelpful responses."""
        # Try a different approach - rephrase the query to be more specific
        rephrased_query = f"{query} Please provide specific steps and details."
        
        # Get a completely new answer
        new_response = self.answer_query(rephrased_query)
        new_response["reasoning"] = f"Generated new answer with rephrased query to address 'not helpful' feedback."
        
        return new_response
    
    def _improve_incorrect_response(self, query: str, response: Dict, feedback: Dict) -> Dict:
        """Strategy to improve incorrect responses."""
        # Get more relevant sections with higher similarity threshold
        relevant_sections = self.find_relevant_sections(query, top_k=5)
        
        # Filter for high-confidence sections
        high_confidence_sections = [(section, score) for section, score in relevant_sections if score > 0.6]
        
        if high_confidence_sections:
            # Use the highest confidence section
            best_section = high_confidence_sections[0][0]
            
            # Generate a new answer with this specific context
            try:
                result = self.qa_pipeline(question=query, context=best_section)
                
                new_response = {
                    "answer": result["answer"],
                    "confidence": result["score"],
                    "context": best_section,
                    "reasoning": "Generated new answer using highest-confidence document section to address 'incorrect' feedback."
                }
                
                return new_response
            except Exception:
                pass
        
        # Fallback: try a more conservative approach
        return self._improve_unhelpful_response(query, response, feedback)
    
    def _improve_partial_response(self, query: str, response: Dict, feedback: Dict) -> Dict:
        """Strategy to improve partially correct responses."""
        # Keep the good parts but add more information
        original_answer = response["answer"]
        
        # Get additional context
        relevant_sections = self.find_relevant_sections(query, top_k=3)
        additional_contexts = [section for section, _ in relevant_sections if section not in response["context"]]
        
        if additional_contexts:
            additional_info = additional_contexts[0]
            
            # Generate a supplementary answer
            try:
                supplementary_result = self.qa_pipeline(question=query, context=additional_info)
                supplementary_answer = supplementary_result["answer"]
                
                # Combine the original and supplementary answers
                new_answer = f"{original_answer} Additionally: {supplementary_answer}"
                
                new_response = response.copy()
                new_response["answer"] = new_answer
                new_response["reasoning"] = "Enhanced partially correct answer with additional information."
                
                return new_response
            except Exception:
                pass
        
        # Fallback
        return self._improve_vague_response(query, response, feedback)
    
    def adjust_response(self, query: str, response: Dict, feedback: Dict) -> Dict:
        """Adjust the response based on detailed feedback."""
        logging.info(f"Adjusting response based on feedback: {feedback['feedback_type']}")
        
        feedback_type = feedback["feedback_type"]
        
        # Use the appropriate improvement strategy
        if feedback_type in self.improvement_strategies:
            return self.improvement_strategies[feedback_type](query, response, feedback)
        
        # If feedback is "good" or unrecognized, return the original response
        return response
    
    def learn_from_feedback(self, feedback_history: List[Dict]) -> None:
        """Update internal parameters based on feedback history."""
        if not feedback_history:
            return
        
        # Calculate success rate
        success_count = sum(1 for item in feedback_history if item["final_feedback"]["feedback_type"] == "good")
        success_rate = success_count / len(feedback_history)
        
        # Adjust confidence threshold based on performance
        if success_rate < 0.5 and self.confidence_threshold > 0.5:
            self.confidence_threshold -= self.learning_rate
            logging.info(f"Decreased confidence threshold to {self.confidence_threshold:.2f}")
        elif success_rate > 0.8 and self.confidence_threshold < 0.9:
            self.confidence_threshold += self.learning_rate
            logging.info(f"Increased confidence threshold to {self.confidence_threshold:.2f}")
        
        # Analyze which types of feedback are most common
        feedback_counts = {}
        for item in feedback_history:
            feedback_type = item["final_feedback"]["feedback_type"]
            feedback_counts[feedback_type] = feedback_counts.get(feedback_type, 0) + 1
        
        # Log the most common feedback type
        if feedback_counts:
            most_common = max(feedback_counts.items(), key=lambda x: x[1])
            logging.info(f"Most common feedback: {most_common[0]} ({most_common[1]} times)")
            
            # Adjust learning parameters based on most common feedback
            if most_common[0] == "too vague" and self.learning_rate < 0.1:
                self.learning_rate += 0.01
                logging.info(f"Increased learning rate to {self.learning_rate:.2f} to address vague responses")
        
        # Log learning progress
        logging.info(f"Learning from feedback: success rate {success_rate:.2f}, adjusted threshold to {self.confidence_threshold:.2f}")
    
    def run(self, queries: List[str]) -> None:
        """Process a list of queries with feedback loop."""
        feedback_history = []
        
        print(f"\n{Fore.YELLOW}Starting support bot session with {len(queries)} queries{Style.RESET_ALL}\n")
        
        for i, query in enumerate(queries):
            print(f"\n{Fore.BLUE}Query {i+1}/{len(queries)}: {query}{Style.RESET_ALL}")
            logging.info(f"Processing query: {query}")
            
            # Initial response
            response = self.answer_query(query)
            print(f"{Fore.WHITE}Initial Response: {response['answer']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Reasoning: {response['reasoning']}{Style.RESET_ALL}")
            
            # Track iterations for this query
            query_feedback_history = []
            final_response = response
            final_feedback = None
            
            # Feedback loop (max iterations)
            for iteration in range(self.max_iterations):
                # Get feedback
                feedback = self.get_feedback(query, response)
                query_feedback_history.append(feedback)
                final_feedback = feedback
                
                print(f"{Fore.MAGENTA}Feedback: {feedback['feedback_type']}{Style.RESET_ALL}")
                if feedback['suggestions']:
                    print(f"{Fore.MAGENTA}Suggestions: {', '.join(feedback['suggestions'])}{Style.RESET_ALL}")
                
                # If feedback is good, we're done with this query
                if feedback['feedback_type'] == "good":
                    break
                
                # Adjust response based on feedback
                response = self.adjust_response(query, response, feedback)
                final_response = response
                
                print(f"{Fore.GREEN}Updated Response: {response['answer']}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Reasoning: {response['reasoning']}{Style.RESET_ALL}")
                
                # Simulate a short delay for the agent to "think"
                time.sleep(0.5)
            
            # Record the outcome of this query
            feedback_history.append({
                "query": query,
                "iterations": len(query_feedback_history),
                "feedback_sequence": query_feedback_history,
                "final_feedback": final_feedback
            })
            
            # Log the final outcome
            logging.info(f"Query completed after {len(query_feedback_history)} iterations with final feedback: {final_feedback['feedback_type'] if final_feedback else 'none'}")
        
        # Learn from this session's feedback
        self.learn_from_feedback(feedback_history)
        
        # Print session summary
        print(f"\n{Fore.YELLOW}Session Summary:{Style.RESET_ALL}")
        print(f"Processed {len(queries)} queries")
        print(f"Feedback stats: {self.feedback_stats}")
        print(f"Current confidence threshold: {self.confidence_threshold:.2f}")
        print(f"Current learning rate: {self.learning_rate:.2f}")
        
        logging.info(f"Session completed. Feedback stats: {self.feedback_stats}")

def main():
    """Main function to run the support bot."""
    # Sample document path
    document_path = "faq.txt"
    
    # Check if document exists
    if not os.path.exists(document_path):
        print(f"{Fore.RED}Error: Document '{document_path}' not found.{Style.RESET_ALL}")
        return
    
    # Initialize and run the support bot
    bot = SupportBotAgent(document_path)
    
    # Sample queries
    sample_queries = [
        "How do I reset my password?",
        "What's the refund policy?",
        "How do I track my order?",
        "Do you offer international shipping?",  # Not explicitly covered in FAQ
        "How do I update my device software?",
        "What happens if my device breaks after warranty?",  # Partially covered
    ]
    
    # Run the bot
    bot.run(sample_queries)

if __name__ == "__main__":
    main() 