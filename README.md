# 🏛️ Legal AI System - 3-Agent Pipeline

Türk hukuku için geliştirilmiş 3-aşamalı AI sistemi. Doğal dil sorularını alır, RAG (Retrieval-Augmented Generation) ile ilgili kanunları bulur ve kapsamlı hukuki analiz sağlar.

## 🎯 Sistem Mimarisi

### 3-Agent Pipeline:

1. **🤖 Agent 1 - Query Optimizer (GPT-4o-mini)**
   - Kullanıcının doğal dil sorusunu alır
   - RAG sistemi için optimize edilmiş sorgu oluşturur
   - Hızlı ve verimli sorgu dönüşümü

2. **🔍 RAG System - Semantic Search**
   - Vector embeddings ile semantik arama
   - 1,708 Türk kanunu üzerinde arama
   - En ilgili 10 kanunu bulur

3. **⚖️ Agent 3 - Legal Analyst (GPT-4o)**
   - Bulunan kanunların tam metnini okur
   - Kapsamlı hukuki analiz yapar
   - Madde referansları ile detaylı yanıt verir

## 📁 Proje Yapısı

```
the_project/
├── agents/                 # AI Agent sınıfları
│   ├── agent1_query_optimizer.py
│   └── agent3_legal_analyst.py
├── rag_system/            # RAG sistemi bileşenleri
│   └── rag_integration.py
├── utils/                 # Yardımcı araçlar
│   └── law_matcher.py
├── frontend/              # Web arayüzü
│   ├── app.py
│   └── templates/chat.html
├── config/                # Yapılandırma
│   └── config.py
├── data/                  # Veri dosyaları
│   └── mevzuat_combined_final.xlsx
├── main.py               # Ana uygulama
├── requirements.txt      # Gereksinimler
└── setup.py             # Kurulum scripti
```

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.8+
- OpenAI API Key
- 8GB+ RAM (vector embeddings için)

### 2. Hızlı Kurulum

```bash
# 1. Gereksinimleri yükle
pip install -r requirements.txt

# 2. Setup scriptini çalıştır
python setup.py

# 3. OpenAI API Key'ini gir
```

### 3. Manuel Kurulum

```bash
# Gerekli paketleri yükle
pip install flask flask-cors openai pandas numpy openpyxl scikit-learn sentence-transformers tiktoken python-dotenv tqdm

# Environment variable ayarla
export OPENAI_API_KEY="your_api_key_here"  # Linux/Mac
set OPENAI_API_KEY=your_api_key_here       # Windows
```

## 🎮 Kullanım

### 1. Web Arayüzü (Önerilen)

```bash
# Web sunucusunu başlat
python frontend/app.py

# Tarayıcıda aç
http://localhost:5000
```

**Özellikler:**
- ChatGPT benzeri arayüz
- Real-time soru-cevap
- Bulunan kanunları görüntüleme
- Mobil uyumlu tasarım

### 2. Komut Satırı Arayüzü

```bash
# Terminal arayüzü
python main.py
```

**Özellikler:**
- Interaktif soru-cevap
- Sistem testi
- Detaylı pipeline görünümü

## 💡 Örnek Kullanım

### Web Arayüzü Örnekleri:

```
Kullanıcı: "İşten çıkarılırsam tazminat alabilir miyim?"

System Response:
📋 Analiz Edilen Kanunlar (3):
• İŞ KANUNU (Kanun)
• SENDİKALAR VE TOPLU İŞ SÖZLEŞMESİ KANUNU (Kanun)

🏛️ Hukuki Değerlendirme

Evet, İş Kanunu'na göre belirli şartlarda tazminat alma hakkınız bulunmaktadır...

📋 İlgili Kanun Maddeleri:
- İş Kanunu - Madde 17: İş sözleşmesinin feshi...
- İş Kanunu - Madde 32: Kıdem tazminatı...

⚖️ Sonuç:
İşten çıkarılma şeklinize göre kıdem ve/veya ihbar tazminatı alma hakkınız vardır...
```

## 🔧 Yapılandırma

### `config/config.py` dosyasında özelleştirilebilir:

```python
# AI Model ayarları
AGENT1_MODEL = "gpt-4o-mini"    # Sorgu optimizasyonu
AGENT3_MODEL = "gpt-4o"         # Hukuki analiz

# RAG ayarları
RAG_TOP_K = 10                  # Getirilecek kanun sayısı
MAX_TOKENS_AGENT1 = 500         # Agent 1 token limiti
MAX_TOKENS_AGENT3 = 4000        # Agent 3 token limiti

# Web sunucu ayarları
FLASK_HOST = "localhost"
FLASK_PORT = 5000
```

## 📊 Veri

Sistem şu veri türlerini içerir:

- **1,708 Türk Kanunu**
- **6 Hukuk Türü:** Kanun, Yönetmelik, Genelge, Tüzük, KHK, Cumhurbaşkanlığı Kararnamesi
- **Vector Embeddings:** 1536-boyutlu semantik temsilciler
- **Metadata:** Kabul tarihi, resmi gazete bilgileri, detay URL'ler

## 🧪 Test

### Sistem Testi:

```bash
# Tam sistem testi
python main.py
# Seçenek 2: Sistem testini çalıştır

# Bireysel agent testleri
python agents/agent1_query_optimizer.py
python agents/agent3_legal_analyst.py
python utils/law_matcher.py
```

### Web API Testi:

```bash
# Health check
curl http://localhost:5000/api/health

# Soru sorma
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Çevre kirliliği yaparsam ne olur?"}'
```

## 🔍 API Referansı

### Web Endpoints:

- `GET /` - Ana chat arayüzü
- `POST /api/ask` - Hukuki soru API'si
- `GET /api/health` - Sistem durumu

### Request Format:

```json
{
  "question": "Hukuki sorunuz..."
}
```

### Response Format:

```json
{
  "status": "success",
  "response": {
    "user_question": "...",
    "optimized_query": "...",
    "found_laws": [...],
    "legal_analysis": "...",
    "pipeline_steps": {...}
  }
}
```

## 🚨 Önemli Notlar

1. **API Limitleri:** OpenAI API kullanım limitlerini kontrol edin
2. **Maliyet:** GPT-4o kullanımı GPT-3.5'ten daha pahalıdır
3. **Hukuki Sorumluluk:** Bu sistem genel bilgi amaçlıdır, resmi hukuki danışmanlık değildir
4. **Veri Güncelliği:** Kanun metinleri periyodik olarak güncellenmelidir

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Sorun Giderme

### Yaygın Hatalar:

1. **"OPENAI_API_KEY not found"**
   - API key'i environment variable olarak ayarlayın
   - setup.py scriptini çalıştırın

2. **"No embedding files found"**
   - RAG embeddings dosyalarını kopyalayın
   - Embeddings'leri yeniden oluşturun

3. **"Dataset not found"**
   - Excel dosyasını data/ klasörüne kopyalayın
   - Dosya adının doğru olduğunu kontrol edin

4. **Memory errors**
   - RAM'inizi kontrol edin (min 8GB)
   - Batch size'ı azaltın

### Destek:

Sorun yaşıyorsanız:
1. Logları kontrol edin
2. API key'inizin geçerli olduğunu doğrulayın
3. Gereksinimlerin yüklü olduğunu kontrol edin
4. Issue açın ve log'ları paylaşın

---

**🏛️ Legal AI System - Türk Hukuku'nda AI Destekli Araştırma**