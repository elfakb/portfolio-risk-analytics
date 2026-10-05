# Yatırım Portföyü ve Piyasa Risk Analitiği (Borsa İstanbul)

Borsa İstanbul (BIST) üzerinde oluşturulan bir yatırım portföyünün getiri, risk, volatilite ve
drawdown performansını analiz eden; Modern Portföy Teorisi ile Efficient Frontier oluşturan ve
tüm sonuçları interaktif bir Streamlit dashboard'unda sunan uçtan uca bir Python projesidir.

> 🇬🇧 English documentation: [README.md](README.md)

![Dashboard Genel Görünüm](images/dashboard_overview.png)

## Özellikler

- Günlük, aylık ve yıllıklandırılmış getiri
- Volatilite, kovaryans ve korelasyon analizi
- BIST 100 benchmark'ına göre Beta ve Alpha
- Sharpe ve Sortino oranları
- Maksimum Drawdown, tarihsel VaR ve CVaR (%95)
- Modern Portföy Teorisi: Efficient Frontier, Maksimum Sharpe ve Minimum Volatilite portföyleri
- Ağırlıkların ve risksiz faiz oranının canlı değiştirilebildiği interaktif dashboard
- Temel metrikler için birim testler

## Portföy (varsayılan, `config.yaml` içinden değiştirilebilir)

| Varlık | Ticker | Ağırlık |
|---|---|---|
| Hisse A - Türk Hava Yolları | THYAO.IS | %25 |
| Hisse B - Aselsan | ASELS.IS | %20 |
| Hisse C - BİM | BIMAS.IS | %20 |
| Endeks - BIST 30 (ETF proxy) | XU030.IS | %20 |
| TL cinsinden gram altın (defansif) | GOLD_TRY | %15 |

Benchmark: BIST 100 (`XU100.IS`). Veri kaynağı: `yfinance` üzerinden Yahoo Finance.
Analiz dönemi: 7 Ekim 2021 - 2 Ekim 2026 (1.300 işlem günü). Risksiz faiz oranı: %37.

## Temel Sonuçlar

### Portföy (mevcut dağılım)

| Metrik | Değer |
|---|---|
| Yıllık Getiri (CAGR) | %83,31 |
| Yıllık Volatilite | %27,44 |
| Sharpe Oranı | 1,00 |
| Sortino Oranı | 1,50 |
| Maksimum Drawdown | -%23,10 |
| BIST 100'e göre Beta | 0,87 |
| Alpha (yıllık) | %19,10 |
| VaR %95 (1 günlük) | %2,21 |
| CVaR %95 (1 günlük) | %3,55 |

### Tekil varlıklar

| Varlık | Getiri | Volatilite | Sharpe | Max Drawdown | Beta |
|---|---|---|---|---|---|
| THYAO | %81,75 | %41,07 | 0,76 | -%25,61 | 1,08 |
| ASELS | %113,36 | %47,35 | 1,06 | -%43,53 | 1,06 |
| BIMAS | %70,16 | %37,80 | 0,62 | -%33,47 | 0,85 |
| BIST 30 | %57,34 | %29,98 | 0,43 | -%21,96 | 1,05 |
| Gram Altın (TL) | %64,64 | %24,80 | 0,65 | -%34,42 | 0,08 |

### Optimizasyon

| Varlık | Mevcut | Maks. Sharpe | Min. Volatilite |
|---|---|---|---|
| THYAO | %25,0 | %13,1 | %1,4 |
| ASELS | %20,0 | %34,0 | %0,0 |
| BIMAS | %20,0 | %9,4 | %9,4 |
| BIST 30 | %20,0 | %0,0 | %29,7 |
| Gram Altın | %15,0 | %43,5 | %59,5 |
| **Beklenen getiri** | - | %67,23 | %52,98 |
| **Volatilite** | %27,44 | %24,39 | %19,81 |
| **Sharpe** | 1,00 | 1,24 | 0,81 |

![Efficient Frontier](images/efficient_frontier.png)

![Korelasyon Matrisi](images/correlation_matrix.png)

### Bulgular

- **Çeşitlendirme işe yarıyor.** Portföy volatilitesi (%27,4), üç hissenin (%38-47) ve BIST 30
  endeksinin (%30,0) volatilitesinden düşüktür. Sharpe oranı (1,00) ASELS hariç tüm varlıklardan
  yüksektir.
- **Asıl çeşitlendirici altındır.** Altın, hisselerle neredeyse sıfır korelasyona (0,04-0,10) ve
  yalnızca 0,08 betaya sahiptir. Bu yüzden optimize edilmiş her iki portföy de %43-60 oranında
  altına yönelir.
- **BIST 30 endeksi çok katkı sağlamıyor.** Üç hisseyle yüksek korelasyonlu (0,63-0,75) ve en
  düşük Sharpe oranına (0,43) sahip. Maks. Sharpe portföyü onu tamamen çıkarıyor.
- **Defansif ama drawdown'a karşı bağışık değil.** Portföyün maksimum drawdown'ı -%23,1 ile üç
  hisseden ve altından daha iyi, BIST 30 endeksine (-%22,0) yakın.
- **Optimizasyon dengeleri.** Mevcut dağılımdan Maks. Sharpe'a geçmek Sharpe'ı 1,00'dan 1,24'e
  çıkarır ve volatiliteyi %24,4'e düşürür. Min. Volatilite portföyü %19,8 volatiliteye ulaşır,
  fakat getiriden vazgeçer ve altında yoğunlaşır.

## Proje Yapısı

```
portfolio-risk-analytics/
├── config.yaml            # ticker, ağırlık, risksiz faiz, parametreler
├── main.py                # tüm pipeline (terminal çıktısı + CSV)
├── src/
│   ├── data_loader.py     # veri indirme, önbellek, temizleme
│   ├── returns.py         # günlük / aylık / yıllık getiri
│   ├── risk_metrics.py    # volatilite, kovaryans, drawdown, VaR
│   ├── performance.py     # Sharpe, Sortino, Beta, Alpha
│   ├── portfolio.py       # portföy seviyesinde hesaplamalar
│   ├── optimization.py    # Markowitz optimizasyonu, efficient frontier
│   └── visualization.py   # Plotly grafikleri
├── dashboard/app.py       # Streamlit dashboard
├── notebooks/             # keşifsel analiz
├── tests/                 # birim testler
└── images/                # ekran görüntüleri
```

## Kurulum

```bash
git clone https://github.com/elfakb/portfolio-risk-analytics.git
cd portfolio-risk-analytics
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py              # pipeline'ı çalıştırır ve sonuçları yazdırır
python main.py --refresh    # veriyi yeniden indirir
streamlit run dashboard/app.py
pytest -v                   # testleri çalıştırır
```

## Metodoloji

| Metrik | Tanım |
|---|---|
| Yıllık getiri | Geometrik (CAGR): `(∏(1+r))^(252/n) − 1` |
| Volatilite | `std(günlük) × √252` |
| Sharpe | `(ort(günlük) × 252 − rf) / (std(günlük) × √252)` |
| Sortino | Pay aynı, payda sadece aşağı yönlü sapma |
| Beta | `Cov(varlık, benchmark) / Var(benchmark)` |
| Alpha | Yıllık Jensen alfa |
| Max Drawdown | Servet endeksinde zirveden dibe en büyük düşüş |
| VaR / CVaR | Tarihsel, 1 günlük, %95 güven |
| Optimizasyon | Long-only, tam yatırım, SciPy SLSQP ile çözülür |

Portföy getirisi, hedef ağırlıklara günlük yeniden dengeleme varsayımıyla hesaplanır.

## Sınırlamalar ve Notlar

- **Tüm değerler nominal Türk Lirası cinsindendir.** Yüksek enflasyon nedeniyle nominal getiriler
  yüksek görünür, reel getiriler çok daha düşüktür.
- **İki farklı getiri yöntemi kullanılır.** Raporlanan yıllık getiri geometriktir (CAGR);
  Sharpe, Alpha ve optimizasyon ise aritmetik ortalama × 252 kullanır. TL varlıklarında günlük
  getiriler yüksek olduğu için ikisi arasındaki fark belirgindir (mevcut portföyde %83 CAGR
  ve yaklaşık %64 aritmetik). Bu yüzden optimizasyondaki beklenen getiriler CAGR ile doğrudan
  karşılaştırılmamalıdır.
- Varsayılan risksiz faiz oranı **%37**'dir (TCMB politika faizine yakın). Faiz değiştikçe
  `config.yaml` içindeki `risk_free_rate` değerini güncelleyin; Sharpe oranı buna çok duyarlıdır.
- **Örneklem içi sonuçlar.** Optimal ağırlıklar, değerlendirildikleri aynı dönemin geçmiş
  ortalamalarıyla hesaplanır. Bu yüzden geçmişe bakar ve **yatırım tavsiyesi değildir**.
- **Seçim yanlılığı.** Hisseler tanınmış BIST şirketlerinden seçilmiştir; geçmişte güçlü
  performans gösteren hisseler (örn. ASELS) tarihsel sonuçları şişirir.
- Yahoo Finance'teki BIST ETF'lerinin geçmişi yaklaşık bir yıl olduğu için ETF yerine BIST 30
  endeksi (`XU030.IS`) proxy olarak kullanılmıştır. TL cinsinden gram altın,
  `GC=F (USD/ons) × TRY=X ÷ 31,1035` formülüyle sentetik olarak üretilir; vadeli işlem ve BIST
  farklı saatlerde kapandığı için günlük korelasyonlar hafifçe düşük çıkabilir.

## Kullanılan Teknolojiler

Python, pandas, NumPy, SciPy, yfinance, Plotly, Streamlit, pytest

