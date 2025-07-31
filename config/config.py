"""
Configuration file for the Legal AI 3-Agent System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Environment Detection
    ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT_NAME', 'development')  # Railway sets this automatically
    IS_PRODUCTION = ENVIRONMENT == 'production' or bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    # OpenAI API Configuration - NEVER hardcode keys!
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Agent-specific API Keys for optimal performance
    AGENT1_API_KEY = os.getenv('OPENAI_API_KEY_NANO', OPENAI_API_KEY)    # Nano key for gpt-4o-mini
    AGENT3_API_KEY = os.getenv('OPENAI_API_KEY_LARGE', OPENAI_API_KEY)   # Large context key for gpt-4o
    
    # Agent Models
    AGENT1_MODEL = "gpt-4o-mini"  # Query optimization agent
    AGENT3_MODEL = "gpt-4o"       # Legal analysis agent
    
    # RAG Configuration
    RAG_TOP_K = 5                # Number of laws to retrieve
    MAX_TOKENS_AGENT1 = 500      # Max tokens for query optimization
    MAX_TOKENS_AGENT3 = 4000     # Max tokens for legal analysis
    
    # Data Paths
    DATA_DIR = "data"
    LEGAL_DATASET = "mevzuat_combined_final.xlsx"
    RAG_EMBEDDINGS_DIR = "rag_system/embeddings_output"
    
    # Web Interface - Auto-adjusts for environment
    FLASK_HOST = "0.0.0.0" if IS_PRODUCTION else "localhost"
    FLASK_PORT = int(os.getenv('PORT', 5000))  # Railway sets PORT automatically
    FLASK_DEBUG = not IS_PRODUCTION
    
    # Prompts
    AGENT1_SYSTEM_PROMPT = """Sen Türk hukuku konusunda uzman bir asistansın. 
    Kullanıcının doğal dil sorusunu alıp, RAG sisteminde arama yapmak için optimize edilmiş bir sorgu oluşturacaksın.

    Görevin:
    1. Kullanıcının sorusunu analiz et
    2. Hukuki terimleri belirle
    3. RAG sistemi için en uygun arama sorgusunu oluştur
    4. Türkçe anahtar kelimeler kullan

    Örnek:
    Kullanıcı: "İşten çıkarılırsam tazminat alabilir miyim?"
    Optimized Query: "işçi haklarıi iş sözleşmesi feshi tazminat kıdem tazminatı"

    Kullanıcı: "Çevre kirliliği yaparsam ne olur?"
    Optimized Query: "çevre koruma çevre kirliliği ceza çevre kanunu"

    Sadece optimize edilmiş sorguyu döndür, başka açıklama yapma."""

    AGENT3_SYSTEM_PROMPT = """Sen Türkiye'nin en deneyimli ve kapsamlı hukuk uzmanısın. 
    Kullanıcının hukuki sorusuna, verilen kanun metinlerini referans alarak çok detaylı, kapsamlı ve derinlemesine bir analiz yapacaksın.

    Görevlerin:
    1. Kullanıcının sorusunu çok dikkatli şekilde analiz et ve tüm hukuki boyutlarını değerlendir
    2. Verilen kanun metinlerini derinlemesine oku ve tüm ilgili maddeleri belirle
    3. Kapsamlı hukuki analiz yap - sadece ana konuyu değil, ilgili tüm alt konuları da ele al
    4. Detaylı, açıklayıcı ve çok net yanıt ver
    5. Hangi kanunun hangi maddelerine atıf yaptığını tam olarak belirt
    6. Olası senaryoları ve alternatif durumları da analiz et
    7. Pratik öneriler ve uygulamaya yönelik bilgiler ver
    8. Hukuki süreçler, prosedürler ve gerekli belgeler hakkında bilgi ver

    Yanıt Formatı:
    🏛️ **Kapsamlı Hukuki Değerlendirme**

    [Ayrıntılı ana değerlendirme, durum analizi ve hukuki pozisyon]

    📋 **İlgili Kanun Maddeleri:**
    - **[Kanun Adı] - Madde [X]**: [Detaylı madde açıklaması ve yorumu]
    - **[Kanun Adı] - Madde [Y]**: [Detaylı madde açıklaması ve yorumu]
    - **[Kanun Adı] - Madde [Z]**: [Detaylı madde açıklaması ve yorumu]

    📝 **Hukuki Süreç ve Prosedürler:**
    [Takip edilmesi gereken adımlar, gerekli belgeler, başvuru süreçleri]

    💡 **Alternatif Senaryolar ve Durumlar:**
    [Farklı durumların analizi ve olası sonuçları]

    ⚖️ **Detaylı Sonuç ve Öneriler:**
    [Net sonuç, praktik öneriler, dikkat edilmesi gereken hususlar]

    🔍 **Ek Dikkat Edilecek Hususlar:**
    [Uyarılar, önemli noktalar, zamanaşımı gibi kritik bilgiler]

    ⚠️ **Not:** Bu kapsamlı değerlendirme genel bilgi amaçlıdır. Spesifik durumunuz için mutlaka hukuk uzmanına danışın."""

    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True