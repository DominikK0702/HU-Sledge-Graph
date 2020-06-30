import csv

x = []
y = []

with open('.\\PulsDaten\\Crash_2_60_2019-10-29_16kHz_15g.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f,delimiter=';')
    for row in reader:
        x.append(float(row[0].replace(',','.')))
        y.append(float(row[1].replace(',', '.')))


speed_kmh = 0
speed_ms = 0
last_t = 0
for cnt, t in enumerate(x):
    current_g = y[cnt]
    inc_kmh = current_g * 9.81 * (t - last_t) * 3.6
    speed_kmh += inc_kmh
    last_t = t
speed_ms = speed_kmh/3.6
print(speed_kmh)