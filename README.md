# Dashboard Analisis Kualitas Udara ✨

## Setup Environment - Anaconda
```
conda create --name AQI-ds python=3.11.7
conda activate AQI-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir air_quality_analysis
cd air_quality_analysis
conda install -c plotly plotly
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```

Berikut merupakan dashboard interaktif yang memungkinkan pengguna untuk melakukan eksplorasi data secara interaktif melalui berbagai filter dan visualisasi dinamis.


🔹 Di sisi kiri, pengguna dapat memilih tahun dan kota yang ingin dianalisis. Terdapat lebih dari 10 pilihan lokasi pengukuran yang tersebar di Beijing, seperti Aotizhongxin, Dongsi, hingga Wanshouxigong.
🔹 Di bagian tengah, tersedia tab navigasi seperti Pola Temporal, Perbandingan Kota, dan Korelasi dengan Cuaca yang memisahkan tiap fokus analisis.
🔹 Dalam tab Pola Temporal, pengguna dapat melihat tren bulanan atau tahunan dari berbagai jenis polutan seperti PM2.5, PM10, CO, dan lainnya. Grafik garis menampilkan konsentrasi polutan berdasarkan bulan dalam satu tahun, dan dapat difilter berdasarkan resolusi waktu serta jenis polutan.
🔹 Tersedia juga opsi untuk menampilkan data mentah secara langsung di bawah visualisasi.
