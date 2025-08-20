#!/usr/bin/env python3
"""
Latency & Bandwidth Simulation — Holo‑Artisan vs. Conventional Cloud
────────────────────────────────────────────────────────────────────
‧ 延遲模型：  總延遲 = 網路 RTT + 固定處理時間（本研究假設 20 ms，來源[Baumeister 2017]）。
‧ 頻寬模型： • 雲端串流：720 Mbps (=90 MB/s)，來源[Irlitti 2023]；
              • Edge FL : 1.05 M params × 4 B = 4.2 MB，每 15 s 傳送一次。
"""
import matplotlib.pyplot as plt
import numpy as np

# ───── 1. 參數（全部有據可查） ─────
CLOUD_RTT_MS = 150        # 典型公有雲 RTT [Orlosky 2016, Bartolomeo 2023]
EDGE_RTT_MS  =  15        # 5G/區域 Wi‑Fi 至 edge server RTT [Sereno 2022]
PROCESSING_TIME_MS = 20   # 影像/語音前處理固定成本 [Baumeister 2017]

CLOUD_TOTAL_LATENCY  = CLOUD_RTT_MS + PROCESSING_TIME_MS  # 170 ms
EDGE_TOTAL_LATENCY   = EDGE_RTT_MS  + PROCESSING_TIME_MS  # 35 ms

RAW_VOLUMETRIC_BW_MBps      = 90      # 720 Mbps [Orlosky 2016, Irlitti 2023]
METADATA_UPDATE_SIZE_MB      = 4.2     # 1.05 M × 4 B [McMahan 2017]
UPDATE_INTERVAL_S            = 15
HOLO_ARTISAN_EFFECTIVE_BW_MBps = METADATA_UPDATE_SIZE_MB / UPDATE_INTERVAL_S  # ≈0.28 MB/s

# ───── 2. 繪圖資料 ─────
architectures_latency = ["Conventional Cloud", "Holo-Artisan (Edge)"]
latencies            = [CLOUD_TOTAL_LATENCY, EDGE_TOTAL_LATENCY]

architectures_bw = architectures_latency.copy()
bandwidths       = [RAW_VOLUMETRIC_BW_MBps, HOLO_ARTISAN_EFFECTIVE_BW_MBps]

# # ───── 3. 視覺化 ─────
# plt.style.use("seaborn-v0_8-whitegrid")
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
# fig.suptitle("Holo‑Artisan vs. Conventional Cloud Performance", fontsize=16, y=1.04)
#
# # (a) 延遲
# bars1 = ax1.bar(architectures_latency, latencies, color=["#d9534f", "#5cb85c"])
# ax1.set_ylabel("End‑to‑End Latency (ms)")
# ax1.set_title("Latency Comparison")
# ax1.set_ylim(0, max(latencies)*1.25)
# for bar in bars1:
#     ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5, f"{bar.get_height():.0f} ms", ha="center", va="bottom")
#
# # (b) 頻寬（對數軸）
# bars2 = ax2.bar(architectures_bw, bandwidths, color=["#d9534f", "#5cb85c"])
# ax2.set_ylabel("Average Bandwidth (MB/s)")
# ax2.set_title("Bandwidth Consumption Comparison")
# ax2.set_yscale("log")
# ax2.set_ylim(0.1, 1000)
# for bar, bw in zip(bars2, bandwidths):
#     ax2.text(bar.get_x()+bar.get_width()/2, bw*1.3, f"{bw:.2f} MB/s", ha="center", va="bottom")
#
# savings = 100*(1-HOLO_ARTISAN_EFFECTIVE_BW_MBps/RAW_VOLUMETRIC_BW_MBps)
# ax2.text(0.5, 0.87, f"Bandwidth Reduction: {savings:.1f}%", transform=ax2.transAxes, ha="center", bbox=dict(boxstyle="round,pad=0.4", fc="wheat", alpha=0.7))
#
# plt.tight_layout(rect=[0,0,1,0.97])
# plt.savefig("latency_bandwidth_performance.pdf")
# plt.show()

plt.style.use("seaborn-v0_8-whitegrid")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Holo‑Artisan vs. Conventional Cloud Performance", fontsize=16, y=1.04)

bar_width = 0.4  # <--- Shrink bar width from default 0.4

# (a) Latency
bars1 = ax1.bar(architectures_latency, latencies, width=bar_width, color=["#d9534f", "#5cb85c"])
ax1.set_ylabel("End‑to‑End Latency (ms)")
ax1.set_title("Latency Comparison")
ax1.set_ylim(0, max(latencies)*1.25)
for bar in bars1:
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5, f"{bar.get_height():.0f} ms", ha="center", va="bottom")

# (b) Bandwidth (log scale)
bars2 = ax2.bar(architectures_bw, bandwidths, width=bar_width, color=["#d9534f", "#5cb85c"])
ax2.set_ylabel("Average Bandwidth (MB/s)")
ax2.set_title("Bandwidth Consumption Comparison")
ax2.set_yscale("log")
ax2.set_ylim(0.1, 1000)
for bar, bw in zip(bars2, bandwidths):
    ax2.text(bar.get_x()+bar.get_width()/2, bw*1.3, f"{bw:.2f} MB/s", ha="center", va="bottom")

savings = 100*(1-HOLO_ARTISAN_EFFECTIVE_BW_MBps/RAW_VOLUMETRIC_BW_MBps)
ax2.text(0.5, 0.87, f"Bandwidth Reduction: {savings:.1f}%", transform=ax2.transAxes, ha="center", bbox=dict(boxstyle="round,pad=0.4", fc="wheat", alpha=0.7))

plt.tight_layout(rect=[0,0,1,0.97])
plt.savefig("latency_bandwidth_performance_shrink.pdf")
plt.show()
