# This project was created by Yusuf on 09/06/2025.
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------
# Grafik Çizme: Türkçe Etiketli Histogram ve Boxplot
# ---------------------------------------------

# 1) Veriyi oku ve filtrele
df = pd.read_csv("data/electric_car_sales.csv")

filt = (
    (df["parameter"] == "EV sales") &
    (df["mode"] == "Cars") &
    (df["powertrain"] == "BEV")
)
df_bev = df.loc[filt, ["region", "year", "value"]].copy()
df_bev["value"] = pd.to_numeric(df_bev["value"], errors="coerce")

# 2) "World" bölgesi varsa al, yoksa yıllara göre topla
if "World" in df_bev["region"].unique():
    df_global = df_bev[df_bev["region"] == "World"].copy()
else:
    df_global = df_bev.groupby("year", as_index=False)["value"].sum()

df_global = df_global.rename(columns={"value": "Annual_Sales"})

# 3) Satışları milyon birime çevir
sales_millions = df_global["Annual_Sales"] / 1e6

# 4) Histogram çiz
plt.figure(figsize=(8, 4))
plt.hist(sales_millions, bins=8, edgecolor="black")
plt.title("Yıllık Elektrikli Araç Satışları Histogramı (Milyon Adet)")
plt.xlabel("Yıllık Satış (Milyon Adet)")
plt.ylabel("Frekans")
plt.xticks([i for i in range(0, 11)])
plt.tight_layout()
plt.savefig("output/histogram.png")
plt.show()

# 5) Boxplot çiz
plt.figure(figsize=(6, 2))
plt.boxplot(sales_millions, vert=False)
plt.title("Yıllık Elektrikli Araç Satışları Boxplot (Milyon Adet)")
plt.xlabel("Yıllık Satış (Milyon Adet)")
plt.xticks([i for i in range(0, 11)])
plt.tight_layout()
plt.savefig("output/boxplot.png")
plt.show()
