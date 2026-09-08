import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# --- API AYARLARI ---
API_KEY = "2686e46f5091c007cf16ad8c3df7ef8d"
LEAGUE_ID = 2 # UEFA Champions League
SEASON = 2024
# --------------------

st.set_page_config(page_title="Şampiyonlar Ligi Tahmin Yarışması", page_icon="⚽", layout="wide")

st.title("🏆 Şampiyonlar Ligi Tahmin Yarışması")

USERS = ["Buğra", "Hakan", "BFM", "Emre"]
DATA_FILE = "predictions.json"

# --- VERİ TABANI YARDIMCI FONKSİYONLARI ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"predictions": {}, "scores": {user: {"Puan": 0, "Doğru Tahmin": 0} for user in USERS}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- API YARDIMCI FONKSİYONLARI ---
@st.cache_data(ttl=3600) # 1 saatte bir yenile (API limitine takılmamak için)
def get_matches():
    url = f"https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": API_KEY
    }
    # Gelecek 7 günün ve geçmiş 3 günün maçlarını al
    from_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    params = {
        "league": LEAGUE_ID,
        "season": SEASON,
        "from": from_date,
        "to": to_date
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        st.error(f"Maçlar çekilirken hata oluştu: {e}")
        return []

matches = get_matches()

# --- PUAN HESAPLAMA ---
# Gerçek skorlar geldikçe tahminleri karşılaştır (Sadece 1-X-2 taraf baz alınır)
def calculate_scores():
    # Skorları sıfırla
    for user in USERS:
        db["scores"][user] = {"Puan": 0, "Doğru Tahmin": 0}
        
    for match in matches:
        match_id = str(match["fixture"]["id"])
        status = match["fixture"]["status"]["short"]
        
        # Maç bittiyse (FT, AET, PEN) hesapla
        if status in ["FT", "AET", "PEN"]:
            real_home = match["goals"]["home"]
            real_away = match["goals"]["away"]
            
            # Beraberlik, Ev, Deplasman
            real_result = "D" if real_home == real_away else ("H" if real_home > real_away else "A")
            
            for user in USERS:
                if match_id in db["predictions"] and user in db["predictions"][match_id]:
                    pred = db["predictions"][match_id][user]
                    pred_home = pred["home"]
                    pred_away = pred["away"]
                    pred_result = "D" if pred_home == pred_away else ("H" if pred_home > pred_away else "A")
                    
                    if real_result == pred_result:
                        # Maçın kazananı veya beraberlik doğru bilindi
                        db["scores"][user]["Puan"] += 1
                        db["scores"][user]["Doğru Tahmin"] += 1

calculate_scores()
save_data(db) # Güncel puanları kaydet

# --- ARAYÜZ ---
st.sidebar.title("Giriş Yap")
user = st.sidebar.selectbox("Kimsiniz?", ["Seçiniz..."] + USERS)

tab1, tab2 = st.tabs(["Maçlar ve Tahminler", "Puan Durumu"])

with tab1:
    st.header("⚽ Şampiyonlar Ligi Maçları")
    if user == "Seçiniz...":
        st.warning("Tahmin girmek için lütfen soldaki menüden isminizi seçin.")
    
    if not matches:
        st.info("Şu an için gösterilecek maç bulunmuyor veya API limitine takıldınız.")
        
    for match in matches:
        match_id = str(match["fixture"]["id"])
        home_team = match["teams"]["home"]["name"]
        away_team = match["teams"]["away"]["name"]
        home_logo = match["teams"]["home"]["logo"]
        away_logo = match["teams"]["away"]["logo"]
        date_str = match["fixture"]["date"]
        # API'den gelen UTC tarihini çevirme
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = date_obj.strftime("%d %b %Y - %H:%M")
        status = match["fixture"]["status"]["short"]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.image(home_logo, width=40)
            st.markdown(f"**{home_team}**")
        with col2:
            if status in ["FT", "AET", "PEN", "1H", "2H", "HT"]:
                st.markdown(f"<h3 style='text-align: center;'>{match['goals']['home']} - {match['goals']['away']}</h3>", unsafe_allow_html=True)
                if status != "FT":
                    st.caption(f"Canlı ({status})")
            else:
                st.markdown("<h4 style='text-align: center;'>VS</h4>", unsafe_allow_html=True)
        with col3:
            st.image(away_logo, width=40)
            st.markdown(f"**{away_team}**")
            
        st.caption(f"🗓️ {formatted_date}")
        
        # Sadece maç başlamadıysa (NS - Not Started) tahmin girilebilir
        if status == "NS" and user != "Seçiniz...":
            # Mevcut tahmini getir
            current_pred_home = 0
            current_pred_away = 0
            if match_id in db["predictions"] and user in db["predictions"][match_id]:
                current_pred_home = db["predictions"][match_id][user]["home"]
                current_pred_away = db["predictions"][match_id][user]["away"]

            with st.expander("Tahmin Gir / Güncelle"):
                pred_col1, pred_col2 = st.columns(2)
                with pred_col1:
                    home_pred = st.number_input(f"{home_team} Gol", min_value=0, max_value=15, step=1, value=current_pred_home, key=f"home_{match_id}")
                with pred_col2:
                    away_pred = st.number_input(f"{away_team} Gol", min_value=0, max_value=15, step=1, value=current_pred_away, key=f"away_{match_id}")
                
                if st.button("Kaydet", key=f"btn_{match_id}", width="stretch"):
                    if match_id not in db["predictions"]:
                        db["predictions"][match_id] = {}
                    db["predictions"][match_id][user] = {"home": home_pred, "away": away_pred}
                    save_data(db)
                    st.success("Tahmininiz kaydedildi!")
        
        elif status != "NS":
            st.info("Bu maç başladı veya bittiği için tahmin yapılamaz.")
            # Herkesin tahminlerini göster
            if match_id in db["predictions"]:
                st.write("**Yapılan Tahminler:**")
                for u, p in db["predictions"][match_id].items():
                    st.write(f"- {u}: {p['home']} - {p['away']}")
            else:
                st.write("Bu maç için tahmin girilmemiş.")
                
        st.divider()

with tab2:
    st.header("🏆 Liderlik Tablosu")
    st.info("Puanlama Sistemi: Maçın sonucunu (Ev Sahibi, Beraberlik, Deplasman) doğru bilen 1 puan alır. Yazdığınız net skor dikkate alınmaz, sadece taraf önemlidir.")
    
    leaderboard_data = []
    for u, stats in db["scores"].items():
        leaderboard_data.append({
            "Oyuncu": u,
            "Puan": stats["Puan"],
            "Doğru Tahmin": stats["Doğru Tahmin"]
        })
        
    df = pd.DataFrame(leaderboard_data)
    # Puan durumunu sırala
    df = df.sort_values(by=["Puan", "Doğru Tahmin"], ascending=False)
    # Streamlit Cloud'daki width hatasını önlemek için width='stretch' eklendi
    st.dataframe(df, hide_index=True, width="stretch")
