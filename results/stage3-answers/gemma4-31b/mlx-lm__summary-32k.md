Yerel LLM çalıştırmak isteyen bir mühendis için belgelerdeki en önemli 5 bulgu şunlardır:

1.  **Donanım ve Model Kapasitesi İlişkisi:**
    *   **Tüketici GPU'ları:** NVIDIA RTX 5090 gibi üst segment bir kart ile yaklaşık 40B parametreye kadar modeller çalıştırılabilir. Güncel tüketici donanımları, yaklaşık 6-12 ay öncesinin "frontier" (en ileri seviye) model performansına ulaşabilmektedir.
    *   **Apple Silicon:** M4 Max, 128 GB'a kadar birleşik bellek (unified memory) ve 546 GB/s bant genişliği sunarak 200 milyar parametreli büyük modellerle etkileşime olanak tanır.

2.  **Kuantizasyonun Kritik Rolü ve Sınırları:**
    *   **Verimlilik:** 4-bit kuantizasyon, performans kaybı yaşatmadan bellek ayak izini ortalama %70 oranında azaltan "yeni sınır" olarak görülmektedir.
    *   **Riskler:** 4-bit altındaki (2-bit veya 3-bit) ekstrem kuantizasyonlar, özellikle uzun bağlamlı (long-context) görevlerde ve İngilizce dışı dillerde ciddi performans düşüşlerine (bazı durumlarda %59'a varan kayıplar) neden olabilmektedir.

3.  **Çalışma Zamanı (Runtime) Seçimi (Apple Silicon için):**
    *   **MLX:** En yüksek sürdürülebilir üretim çıktı hızını (throughput) sağlar.
    *   **MLC-LLM:** Orta ölçekli istemler için en düşük "ilk token süresini" (TTFT) sunar.
