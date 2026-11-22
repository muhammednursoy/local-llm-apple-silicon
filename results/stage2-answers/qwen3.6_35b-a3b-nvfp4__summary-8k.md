Yerel LLM (Büyük Dil Modeli) çalıştırmak isteyen bir mühendis için paylaşılan teknik belgelerin ışığında, en önemli 5 bulgu aşağıdadır:

1.  **Apple Silicon Üzerinde Framework Seçimi Kritik Önem Taşıyor:**
    `Production-Grade Local LLM Inference on Apple Silicon` başlıklı çalışma, yerel LLM çalıştırma ekosisteminde tek bir "en iyi" çözüm olmadığını göstermektedir. MLX, yüksek sürdürülebilir üretim hızı (throughput) sunarken; MLC-LLM, özellikle orta boyutlu istemler için daha düşük ilk token süresi (TTFT) ve hazır özellikler sunar. Ollama geliştirici deneyimi açısından iyiyken performans açısından geride kalabilir. Mühendisler, uygulama ihtiyaçlarına göre (örneğin; uzun bağlam işleme vs. interaktif yanıt hızı) bu framework'ler arasında seçim yapmalı ve Apple Silicon'un birleşik bellek mimarisini en iyi kullananı seçmelidir.

2.  **Düşük Bit Genişlikli Quantization (Sıkıştırma) "Eğitilmemiş" Modellerde Daha İyi Çalışır:**
    `Low-Bit Quantization Favors Undertrained LLMs` makalesi, düşük bit genişliğine sahip quantization tekniklerinin (örneğin 4-bit veya 8-bit), tam olarak eğitilmiş büyük modellerden ziyade, daha az eğitim token'ına sahip ("undertrained") veya daha küçük modellerde daha az performans kaybına yol açtığını ortaya koymaktadır. Bu, mühendislerin model sıkıştırma stratejisi belirlerken modelin eğitim seviyesini ve büyüklüğünü dikkate alması gerektiğini gösterir; aksi takdirde beklenmedik kalite düşüşleri yaşanabilir.

3.  **U