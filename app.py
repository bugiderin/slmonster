import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Şampiyonlar Ligi Tahmin Yarışması", page_icon="⚽", layout="wide")

st.title("🏆 Şampiyonlar Ligi Tahmin Yarışması")

# Kullanıcılar (İsimleri daha sonra kendi isimlerinizle değiştirebiliriz)
USERS = ["Buğra", "Hakan", "BFM", "Emre"]

# Örnek Maç Verileri (Daha sonra gerçek API'den gelecek)
MOCK_MATCHES = [
    {"id": 1, "home": "Club Brugge", "away": "Aston Villa", "date": "Bugün 19:45", "status": "TIMED", "home_score": None, "away_score": None},
    {"id": 2, "home": "Porto", "away": "Manchester City", "date": "Bugün 22:00", "status": "TIMED", "home_score": None, "away_score": None},
    {"id": 3, "home": "Real Madrid", "away": "Inter", "date": "Bugün 22:00", "status": "TIMED", "home_score": None, "away_score": None},
    {"id": 4, "home": "AEK", "away": "LASK Linz", "date": "Yarın 19:45", "status": "TIMED", "home_score": None, "away_score": None},
]

# Örnek Puan Durumu
MOCK_LEADERBOARD = pd.DataFrame({
    "Oyuncu": USERS,
    "Puan": [0, 0, 0, 0],
    "Doğru Skor": [0, 0, 0, 0],  # Tam skoru bilme (Örn: 2-1 bitti, 2-1 dedi)
    "Doğru Taraf": [0, 0, 0, 0]   # Sadece kazananı bilme
})

# Sol Menü (Kullanıcı Seçimi)
st.sidebar.title("Giriş Yap")
user = st.sidebar.selectbox("Kimsiniz?", ["Seçiniz..."] + USERS)

# Sekmeler
tab1, tab2 = st.tabs(["Maçlar ve Tahminler", "Puan Durumu"])

with tab1:
    st.header("⚽ Gelecek Maçlar")
    if user == "Seçiniz...":
        st.warning("Tahmin girmek için lütfen soldaki menüden isminizi seçin.")
    
    for match in MOCK_MATCHES:
        # Maç Kartı Tasarımı
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"<h4 style='text-align: right;'>{match['home']}</h4>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h4 style='text-align: center;'>VS</h4>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h4 style='text-align: left;'>{match['away']}</h4>", unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align: center;'>🗓️ {match['date']}</p>", unsafe_allow_html=True)
        
        # Tahmin Giriş Alanı (Sadece kullanıcı seçiliyse görünür)
        if user != "Seçiniz...":
            pred_col1, pred_col2, pred_col3 = st.columns([1, 2, 1])
            with pred_col2:
                # Yan yana iki sayı girişi
                input_c1, input_c2 = st.columns(2)
                with input_c1:
                    home_pred = st.number_input("Ev Sahibi", min_value=0, max_value=15, step=1, key=f"home_{match['id']}")
                with input_c2:
                    away_pred = st.number_input("Deplasman", min_value=0, max_value=15, step=1, key=f"away_{match['id']}")
                
                if st.button("Tahmini Kaydet", key=f"btn_{match['id']}", use_container_width=True):
                    st.success(f"{match['home']} {home_pred} - {away_pred} {match['away']} tahmini {user} için kaydedildi! (Şimdilik test modunda)")
        
        st.divider()

with tab2:
    st.header("🏆 Liderlik Tablosu")
    st.info("Puanlama Sistemi: Doğru skoru bilmek 3 puan, sadece kazananı veya beraberliği bilmek 1 puan.")
    
    # Puan tablosunu Puana göre sıralı gösterme
    st.dataframe(MOCK_LEADERBOARD.sort_values(by="Puan", ascending=False), use_container_width=True, hide_index=True)

st.sidebar.divider()
st.sidebar.caption("v0.1 - Geliştirme Aşaması")
