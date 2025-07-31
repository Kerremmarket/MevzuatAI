"""
Main Application - 3-Agent Legal AI System
Orchestrates the complete pipeline: Query Optimization -> RAG Search -> Legal Analysis
"""

import logging
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agent1_query_optimizer import QueryOptimizer
from rag_system.rag_integration import RAGSystem
from utils.law_matcher import LawMatcher
from agents.agent3_legal_analyst import LegalAnalyst
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalAISystem:
    """Main class that orchestrates the 3-agent system"""
    
    def __init__(self):
        """Initialize all agents and systems"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize all components
            logger.info("Initializing Legal AI System...")
            
            self.agent1 = QueryOptimizer()
            logger.info("✅ Agent 1 (Query Optimizer) initialized")
            
            self.rag_system = RAGSystem()
            logger.info("✅ RAG System initialized")
            
            self.law_matcher = LawMatcher()
            logger.info("✅ Law Matcher initialized")
            
            self.agent3 = LegalAnalyst()
            logger.info("✅ Agent 3 (Legal Analyst) initialized")
            
            logger.info("🎉 Legal AI System ready!")
            
        except Exception as e:
            logger.error(f"Error initializing system: {str(e)}")
            raise
    
    def process_legal_question(self, user_question: str) -> Dict[str, Any]:
        """
        Process a legal question through the complete 3-agent pipeline
        
        Args:
            user_question (str): User's legal question in natural language
            
        Returns:
            Dict: Complete response with all pipeline steps
        """
        try:
            logger.info(f"Processing question: {user_question}")
            
            # Step 1: Query Optimization (Agent 1)
            logger.info("🤖 Step 1: Query optimization...")
            optimized_query = self.agent1.optimize_query(user_question)
            
            if not optimized_query:
                return self._create_error_response("Query optimization failed")
            
            # Step 2: RAG Search
            logger.info("🔍 Step 2: RAG search...")
            rag_results = self.rag_system.search_laws(optimized_query, top_k=Config.RAG_TOP_K)
            
            if not rag_results:
                return self._create_error_response("No relevant laws found")
            
            # Step 3: Law Matching
            logger.info("📋 Step 3: Finding full law texts...")
            law_names = [result['law_name'] for result in rag_results]
            law_summaries = self.law_matcher.get_laws_summary(law_names)
            combined_law_text = self.law_matcher.get_combined_law_text(law_names)
            
            if not combined_law_text:
                return self._create_error_response("Could not retrieve law texts")
            
            # Step 4: Legal Analysis (Agent 3)
            logger.info("⚖️ Step 4: Legal analysis...")
            legal_analysis = self.agent3.analyze_with_context(
                user_question=user_question,
                optimized_query=optimized_query,
                rag_results=rag_results,
                law_texts=combined_law_text
            )
            
            # Compile complete response
            response = {
                'status': 'success',
                'user_question': user_question,
                'optimized_query': optimized_query,
                'found_laws': law_summaries,
                'legal_analysis': legal_analysis,
                'pipeline_steps': {
                    'step1_query_optimization': optimized_query,
                    'step2_rag_results': len(rag_results),
                    'step3_laws_found': len(law_summaries),
                    'step4_analysis_complete': True
                }
            }
            
            logger.info("✅ Legal question processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return self._create_error_response(str(e))
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            'status': 'error',
            'error_message': error_message,
            'legal_analysis': f"""🏛️ **Hukuki Değerlendirme**

Üzgünüm, şu anda teknik bir sorun nedeniyle sorunuzu analiz edemiyorum.

📋 **Genel Öneriler:**
- Sorunuzu daha spesifik hale getirmeyi deneyin
- İlgili mevzuatı manuel olarak kontrol edin
- Bir hukuk uzmanına danışın

⚠️ **Hata:** {error_message}"""
        }
    
    def test_system(self):
        """Test the complete system with sample questions"""
        test_questions = [
            "İşten çıkarılırsam tazminat alabilir miyim?",
            "Çevre kirliliği yaparsam ne olur?",
            "Vergi ödememezsem hapse girer miyim?",
            "Trafik kazası yaparsam sorumluluğum nedir?"
        ]
        
        print("🧪 Testing Complete Legal AI System")
        print("=" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Test Case {i}: {question}")
            print("-" * 60)
            
            response = self.process_legal_question(question)
            
            if response['status'] == 'success':
                print(f"✅ Status: Success")
                print(f"🤖 Optimized Query: {response['optimized_query']}")
                print(f"📋 Found Laws: {len(response['found_laws'])}")
                print(f"\n⚖️ Legal Analysis:")
                print(response['legal_analysis'])
            else:
                print(f"❌ Status: Error")
                print(f"🚫 Error: {response['error_message']}")
            
            print("\n" + "="*60)

def main():
    """Main function for command line interface"""
    try:
        # Initialize system
        legal_ai = LegalAISystem()
        
        print("🏛️ Legal AI System - 3-Agent Pipeline")
        print("=" * 50)
        print("Bu sistem 3 aşamalı AI pipeline kullanır:")
        print("1. 🤖 GPT-4o-mini: Sorgu optimizasyonu") 
        print("2. 🔍 RAG Sistemi: İlgili kanunları bulma")
        print("3. ⚖️ GPT-4o: Hukuki analiz")
        print("=" * 50)
        
        while True:
            print("\nSeçenekler:")
            print("1. Hukuki soru sor")
            print("2. Sistem testini çalıştır")  
            print("3. Çıkış")
            
            choice = input("\nSeçiminiz (1-3): ").strip()
            
            if choice == "1":
                question = input("\n❓ Hukuki sorunuzu yazın: ").strip()
                if question:
                    print("\n🔄 İşleniyor...")
                    response = legal_ai.process_legal_question(question)
                    
                    print(f"\n📋 Bulunan Kanunlar ({len(response.get('found_laws', []))}):")
                    for law in response.get('found_laws', []):
                        print(f"  - {law['law_name']} ({law['law_type']})")
                    
                    print(f"\n{response['legal_analysis']}")
                
            elif choice == "2":
                legal_ai.test_system()
                
            elif choice == "3":
                print("👋 Güle güle!")
                break
                
            else:
                print("❌ Geçersiz seçim")
    
    except KeyboardInterrupt:
        print("\n👋 Güle güle!")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    main()