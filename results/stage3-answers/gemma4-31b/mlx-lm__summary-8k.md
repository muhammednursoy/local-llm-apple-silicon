Yerel LLM çalıştırmak isteyen bir mühendis için sağlanan teknik belgelerdeki en kritik 5 bulgu şunlardır:

**1. Donanım Seçimi ve Bellek Bant Genişliği (Apple Silicon):**
Yerel LLM performansı için bellek bant genişliği kritik bir darboğazdır. Apple'ın M4 serisi bu konuda önemli artışlar sunmaktadır. Özellikle **M4 Max**, 546 GB/s bant genişliği ve 128 GB'a kadar birleşik bellek (unified memory) desteği ile yaklaşık 200 milyar parametreli büyük modellerle etkileşime girmeyi mümkün kılmaktadır.

**2. Çalışma Zamanı (Runtime) Karşılaştırmaları:**
Apple Silicon üzerinde farklı framework'lerin farklı avantajları vardır:
*   **MLX:** En yüksek sürdürülebilir üretim (throughput) hızını sağlar.
*   **MLC-LLM:** Orta ölçekli istemler (prompts) için en düşük "ilk token süresini" (TTFT) sunar.
*   **llama.cpp:** Hafif, tek akışlı kullanımlar için oldukça verimlidir.
*   **Ollama:** Geliştirici deneyimi ve kurulum kolaylığı ön plandadır ancak performans (throughput/TTFT) açısından diğerlerinin gerisindedir.

**3. Kuantizasyon (Sıkıştırma) Riskleri ve Sınırları:**
Kuantizasyon bellek ayak izini azaltsa da dikkat edilmesi gereken kritik noktalar vardır:
*   **Hassasiyet Kaybı:** 8-bit kuantizasyon genellikle doğruluğu korurken, 4-bit ve altı yöntemler özellikle uzun bağlamlı (long-context) görevlerde ve İngilizce dışı dillerde ciddi performans düşüşlerine (bazı duruml