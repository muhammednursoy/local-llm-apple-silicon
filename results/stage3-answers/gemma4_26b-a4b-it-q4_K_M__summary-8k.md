Yerel LLM (Large Language Model) çalıştırmak isteyen bir mühendis için teknik belgelerden çıkarılan en önemli 5 bulgu şunlardır:

1.  **Donanım Seçimi ve Bellek Bant Genişliği Kritik Önemdedir:**
    LLM çıkarımı (inference) genellikle bellek bant genişliğine (memory-bound) takılır. Apple M4 serisi çiplerde, M4 Max'in **546 GB/s** gibi çok yüksek bir bellek bant genişliği sunması, 200 milyar parametreye kadar olan büyük modellerle etkileşime girmeyi mümkün kılmaktadır. Model boyutu büyüdükçe, yüksek bant genişliği ve geniş bir birleşik bellek (unified memory) kapasitesi (M4 Max ile 128GB'a kadar) performansı belirleyen ana unsurdur.

2.  **Runtime (Çalışma Zamanı) Seçimi Performansı Doğrudan Etkiler:**
    Apple Silicon üzerinde yerel çalıştırma yaparken kullanılacak framework, kullanım amacına göre değişmelidir. Yapılan karşılaştırmalı çalışma; **MLX**'in en yüksek sürdürülebilir üretim (throughput) kapasitesine sahip olduğunu, **MLC-LLM**'in ise düşük gecikme süreli (TTFT) başlangıçlar için daha iyi olduğunu göstermektedir. **Ollama** ise kullanım kolaylığı (ergonomi) sunsa da yüksek throughput gerektiren işlerde geride kalabilmektedir.

3.  **Kuantizasyon (Quantization) ve Doğruluk Dengesi:**
    Modelleri küçültmek için kullanılan kuantizasyon teknikleri bellek kullanımını azaltsa da ciddi riskler taşır. 4-bit kuantizasyon bellek ayak izini %70 oranında azaltabilirken, özellikle **uzun bağlam