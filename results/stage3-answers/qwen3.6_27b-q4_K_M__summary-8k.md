Paylaşılan teknik belgeler ışığında, yerel (local) Büyük Dil Modellerini (LLM) çalıştırmak isteyen bir mühendis için en kritik 5 bulgu şunlardır:

1.  **Apple Silicon’da Performans ve Çerçeve Seçimi İçin Kritik Karşılaştırma**
    Apple M4 ailesi (özellikle M4 Pro ve M4 Max), 2. nesil 3nm teknoloji, yüksek bant genişliğine sahip birleşik bellek (Unified Memory) ve hızlandırılmış Neural Engine sayesinde yerel LLM çıkarımı için güçlü bir altyapı sunar. Ancak, hangi yazılım çerçevesinin kullanılacağı performans hedefine göre değişir:
    *   **MLX:** En yüksek sürekli üretim (throughput) hızını sağlar.
    *   **MLC-LLM:** Orta boyutlu promptlarda ilk token süresini (TTFT) en düşük tutar ve hazır çıkarım özellikleri sunar.
    *   **llama.cpp:** Hafif, tek akışlı kullanımlar için verimlidir.
    *   **Ollama:** Geliştirici deneyimi (ergonomi) açısından iyidir ancak ham performansta diğerlerine göre geridedir.
    *   **PyTorch MPS:** Büyük modeller ve uzun bağlamlarda bellek kısıtlamaları nedeniyle sınırlıdır.
    *   *Not:* Bu çerçeveler, NVIDIA GPU sistemlerine (vLLM gibi) göre mutlak performans açısından hala geride olsa da, gizlilik odaklı, cihaz üzerinde çalışan üretim düzeyi çözümler olarak olgunlaşmaktadır.

2.  **Kuantizasyon (Quantization) Derinliği ve Model Eğitimi Dengelemesi**
    Model boyutunu küçültmek için kuant