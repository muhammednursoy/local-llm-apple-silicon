Yerel LLM (Büyük Dil Modeli) çalıştırmak isteyen bir mühendis için, sağlanan teknik belgeleri incelediğimde öne çıkan en kritik 5 bulgu şunlardır:

1.  **Apple Silicon Üzerinde En İyi Performans İçin MLX Önceliği:**
    Apple M4 Pro/Max çipleri ve unified memory mimarisi, yerel LLM çalıştırma için son derece güçlüdür. Ancak, farklı çalışma zamanları (MLX, Ollama, llama.cpp, PyTorch MPS) arasında yapılan karşılaştırmalı incelemeler, **MLX** framework'ünün Apple Silicon üzerinde en yüksek sürdürülebilir üretim hızını (throughput) sağladığını göstermektedir. MLC-LLM ise daha kısa ilk token süresi (TTFT) ve hazır özellikler açısından güçlüdürken, PyTorch MPS büyük modellerde bellek kısıtlamaları nedeniyle sınırlı kalabilmektedir.

2.  **4-Bit Quantization (Sıkıştırma) "Altın Standart" Haline Gelmektedir:**
    Model sıkıştırma teknikleri üzerine yapılan araştırmalar, özellikle kod üretimi ve genel görevler için **4-bit quantization**'ın performans kaybı olmadan bellek kullanımını yaklaşık %70 oranında azalttığını ortaya koymaktadır. 2-bit veya 3-bit gibi aşırı sıkıştırma yöntemleri ancak özel kalibrasyon veri setleriyle sınırlı kayıpla çalışabilmekte, ancak 4-bit genellikle doğruluk ve verimlilik arasındaki en iyi dengeyi sunmaktadır.

3.  **Uzun Bağlam (Long-Context) Görevlerinde Quantization Riski:**
    Modelin eğitim seviyesi ve quantization yöntemi seçimi kritik öneme sahiptir. Özellikle **64K token'd