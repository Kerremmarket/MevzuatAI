"""
Agent 3: Legal Analyst
Uses GPT-4o to read full law texts and provide comprehensive legal analysis
"""

import openai
from typing import List, Dict, Optional
import logging
from config.config import Config

class LegalAnalyst:
    def __init__(self, api_key: str = None):
        """Initialize the Legal Analyst Agent"""
        self.api_key = api_key or Config.AGENT3_API_KEY or Config.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = Config.AGENT3_MODEL
        self.max_tokens = Config.MAX_TOKENS_AGENT3
        self.system_prompt = Config.AGENT3_SYSTEM_PROMPT
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def analyze_legal_question(self, 
                             user_question: str, 
                             law_texts: str, 
                             law_summaries: List[Dict] = None) -> Optional[str]:
        """
        Analyze user's legal question using relevant law texts
        
        Args:
            user_question (str): Original user question
            law_texts (str): Combined text of relevant laws
            law_summaries (List[Dict]): Summary of laws for context
            
        Returns:
            str: Comprehensive legal analysis
        """
        try:
            self.logger.info(f"Analyzing legal question: {user_question[:100]}...")
            
            # Prepare the user message with context
            user_message = f"""Kullanıcı Sorusu: {user_question}

İlgili Kanun Metinleri:
{law_texts}"""
            
            # Add law summaries if provided
            if law_summaries:
                summaries_text = "\n".join([
                    f"- {law['law_name']} ({law['law_type']}) - {law['law_number']}"
                    for law in law_summaries
                ])
                user_message += f"\n\nAnaliz Edilen Kanunlar:\n{summaries_text}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,  # Low temperature for consistent legal analysis
                top_p=0.95
            )
            
            analysis = response.choices[0].message.content.strip()
            
            self.logger.info("Legal analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in legal analysis: {str(e)}")
            return self._generate_error_response(user_question)
    
    def _generate_error_response(self, user_question: str) -> str:
        """Generate a fallback response when analysis fails"""
        return f"""🏛️ **Hukuki Değerlendirme**

Üzgünüm, şu anda teknik bir sorun nedeniyle sorunuzu tam olarak analiz edemiyorum.

📋 **Genel Öneriler:**
- Sorunuzla ilgili güncel mevzuatı kontrol edin
- Spesifik durumunuz için mutlaka bir hukuk uzmanına danışın
- İlgili kurumlardan resmi bilgi alın

⚠️ **Not:** Bu değerlendirme genel bilgi amaçlıdır. Spesifik durumunuz için mutlaka hukuk uzmanına danışın.

Sorunuz: {user_question}"""
    
    def test_agent(self, sample_law_text: str = None):
        """Test the agent with sample questions and law text"""
        
        if not sample_law_text:
            sample_law_text = """
=== ÇEVRE KANUNU ===
Kanun No: 2872
Kabul Tarihi: 9/8/1983
Türü: Kanun

MADDE 1 – Bu Kanunun amacı, bütün canlıların ortak varlığı olan çevrenin, sürdürülebilir çevre ve sürdürülebilir kalkınma ilkeleri doğrultusunda korunmasıdır.

MADDE 8 – Çevreyi kirletecek faaliyetlerde bulunacaklar, kirlilikten dolayı doğabilecek zararlardan sorumludur.

MADDE 20 – Çevreyi kirletenler hakkında 5.000 Türk Lirası idarî para cezası uygulanır.
"""
        
        test_cases = [
            "Çevre kirliliği yaparsam ne olur?",
            "Fabrikam çevre kirliliği yaparsa ne ceza alırım?",
            "Çevreye zarar verenlerin sorumluluğu nedir?"
        ]
        
        print("🧪 Testing Agent 3 - Legal Analyst")
        print("=" * 50)
        
        for i, question in enumerate(test_cases, 1):
            print(f"\n{i}. User Question: {question}")
            print("-" * 30)
            
            analysis = self.analyze_legal_question(question, sample_law_text)
            print(analysis)
            print("\n" + "="*50)
    
    def analyze_with_context(self, 
                           user_question: str,
                           optimized_query: str,
                           rag_results: List[Dict],
                           law_texts: str) -> str:
        """
        Enhanced analysis with full context from the pipeline
        
        Args:
            user_question (str): Original user question
            optimized_query (str): Query optimized by Agent 1
            rag_results (List[Dict]): Results from RAG system
            law_texts (str): Full text of relevant laws
            
        Returns:
            str: Comprehensive legal analysis with context
        """
        try:
            # Create enriched context
            context_info = f"""
🔍 **Arama Bilgileri:**
- Kullanıcı Sorusu: {user_question}
- Optimize Edilmiş Sorgu: {optimized_query}
- Bulunan Kanun Sayısı: {len(rag_results)}

📋 **Analiz Edilen Kanunlar:**"""
            
            for i, result in enumerate(rag_results, 1):
                context_info += f"\n{i}. {result['law_name']} (Relevans: {result.get('similarity', 0):.3f})"
            
            context_info += f"\n\n📖 **Kanun Metinleri:**\n{law_texts}"
            
            user_message = f"{context_info}\n\n❓ **Analiz Edilecek Soru:** {user_question}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,
                top_p=0.95
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error in enhanced analysis: {str(e)}")
            return self._generate_error_response(user_question)

if __name__ == "__main__":
    # Test the agent
    analyst = LegalAnalyst()
    analyst.test_agent()