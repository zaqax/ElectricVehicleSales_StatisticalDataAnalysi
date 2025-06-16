import pandas as pd
import numpy as np
import os

# ----------------------------------------
# 1. Veri Hazırlama ve Filtreleme
# ----------------------------------------

df = pd.read_csv("data/electric_car_sales.csv")

filt = (
    (df["parameter"] == "EV sales") &
    (df["mode"] == "Cars") &
    (df["powertrain"] == "BEV")
)
df_bev = df.loc[filt, ["region", "year", "value"]].copy()
df_bev["value"] = pd.to_numeric(df_bev["value"], errors="coerce")

if "World" in df_bev["region"].unique():
    df_global = df_bev[df_bev["region"] == "World"].copy()
else:
    df_global = df_bev.groupby("year", as_index=False)["value"].sum()

df_global = df_global.rename(columns={"value": "Annual_Sales"})
df_global["year"] = df_global["year"].astype(int)
df_global = df_global.sort_values("year").reset_index(drop=True)

if not os.path.isdir("output"):
    os.makedirs("output")

df_global.to_csv("output/global_ev_sales.csv", index=False)
print("✅ global_ev_sales.csv başarıyla oluşturuldu.\n")

# ----------------------------------------
# 2. Tanımlayıcı İstatistikler
# ----------------------------------------

x = df_global["Annual_Sales"]
n = len(x)
mean = np.mean(x)
median = np.median(x)
var = np.var(x, ddof=1)
std = np.std(x, ddof=1)
stderr = std / np.sqrt(n)

print("📊 Tanımlayıcı İstatistikler:")
print(f"n (gözlem sayısı): {n}")
print(f"Ortalama: {mean:,.2f}")
print(f"Medyan: {median:,.2f}")
print(f"Varyans: {var:,.2f}")
print(f"Standart Sapma: {std:,.2f}")
print(f"Standart Hata: {stderr:,.2f}\n")

# ----------------------------------------
# 3. Aykırı Değer Tespiti (IQR Yöntemi)
# ----------------------------------------

Q1 = x.quantile(0.25)
Q3 = x.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = x[(x < lower_bound) | (x > upper_bound)]

print("📌 Aykırı Değer Analizi (IQR yöntemi):")
print(f"Q1 (1. Çeyreklik): {Q1:,.0f}")
print(f"Q3 (3. Çeyreklik): {Q3:,.0f}")
print(f"IQR (Q3 - Q1): {IQR:,.0f}")
print(f"Aykırı Alt Sınır: {lower_bound:,.0f}")
print(f"Aykırı Üst Sınır: {upper_bound:,.0f}\n")

if outliers.empty:
    print("🔹 Aykırı değer bulunmadı.\n")
else:
    print("🔺 Aykırı Değerler:")
    outlier_rows = df_global[df_global["Annual_Sales"].isin(outliers)].loc[:, ["year", "Annual_Sales"]]
    for year, value in outlier_rows.values:
        print(f"  - Yıl: {year}, Satış: {value:,.0f}")
    print()

# ----------------------------------------
# 4. %95 Güven Aralığı Hesabı
# ----------------------------------------

z = 1.96  # 95% güven düzeyi için Z değeri
ci_lower = mean - z * stderr
ci_upper = mean + z * stderr

print("📏 %95 Güven Aralığı Hesabı:")
print(f"Ortalama Yıllık Satış: {mean:,.0f}")
print(f"Standart Sapma: {std:,.0f}")
print(f"Örneklem Sayısı: {n}")
print(f"Standart Hata: {stderr:,.0f}")
print(f"%95 Güven Aralığı: ({ci_lower:,.0f} , {ci_upper:,.0f})\n")

# ----------------------------------------
# 5. Örneklem Büyüklüğü Hesabı (%90 güven düzeyi, ±0.1 milyon hata)
# ----------------------------------------

z_90 = 1.645  # 90% güven düzeyi için Z değeri
E = 0.1  # Hata payı (milyon birim üzerinden düşünüyoruz)
std_millions = std / 1e6  # milyon cinsinden standart sapma

n_required = (z_90 * std_millions / E) ** 2
n_required = int(np.ceil(n_required))

print("🧮 Örneklem Büyüklüğü Hesabı (90% güven, ±0.1 hata):")
print(f"Gerekli minimum örneklem sayısı: {n_required} yıl\n")

# ----------------------------------------
# 6. Hipotez Testi (Ortalama = 6 milyon mu?)
# ----------------------------------------

mu_0 = 6e6  # Test edilecek ortalama (6 milyon)
t_stat = (mean - mu_0) / stderr
df = n - 1
from scipy.stats import t as t_dist
p_value = 2 * (1 - t_dist.cdf(abs(t_stat), df=df))

print("🧪 Hipotez Testi (Ortalama 6 milyon mu?):")
print("H0: Ortalama = 6 milyon")
print("H1: Ortalama ≠ 6 milyon")
print(f"t-istatistiği: {t_stat:.2f}")
print(f"p-değeri: {p_value:.5f}")

if p_value < 0.05:
    print("❌ H0 reddedildi: Ortalama satış 6 milyondan farklıdır.\n")
else:
    print("✔ H0 kabul edildi: Ortalama satış 6 milyona eşittir.\n")