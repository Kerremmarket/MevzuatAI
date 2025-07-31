"""
Agent 1: Query Optimizer
Takes user's natural language question and creates optimal RAG query
Uses GPT-4o-mini for efficiency
"""

import openai
from typing import Optional
import logging
from config.config import Config

class QueryOptimizer:
    def __init__(self, api_key: str = None):
        """Initialize the Query Optimizer Agent"""
        self.api_key = api_key or Config.AGENT1_API_KEY or Config.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = Config.AGENT1_MODEL
        self.max_tokens = Config.MAX_TOKENS_AGENT1
        self.system_prompt = Config.AGENT1_SYSTEM_PROMPT
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def optimize_query(self, user_question: str) -> Optional[str]:
        """
        Take user's natural language question and create optimized RAG query
        
        Args:
            user_question (str): User's legal question in natural language
            
        Returns:
            str: Optimized query for RAG system
        """
        try:
            self.logger.info(f"Optimizing query for: {user_question[:100]}...")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_question}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more focused results
                top_p=0.9
            )
            
            optimized_query = response.choices[0].message.content.strip()
            
            self.logger.info(f"Optimized query created: {optimized_query}")
            return optimized_query
            
        except Exception as e:
            self.logger.error(f"Error in query optimization: {str(e)}")
            # Fallback: return original question if optimization fails
            return user_question
    
    def test_agent(self):
        """Test the agent with sample queries"""
        test_cases = [
            "İşten çıkarılırsam tazminat alabilir miyim?",
            "Çevre kirliliği yaparsam ne olur?", 
            "Vergi ödememezsem hapse girer miyim?",
            "Trafik cezası almamak için ne yapmalıyım?"
        ]
        
        print("🧪 Testing Agent 1 - Query Optimizer")
        print("=" * 50)
        
        for i, question in enumerate(test_cases, 1):
            print(f"\n{i}. User Question: {question}")
            optimized = self.optimize_query(question)
            print(f"   Optimized Query: {optimized}")

if __name__ == "__main__":
    # Test the agent
    optimizer = QueryOptimizer()
    optimizer.test_agent()