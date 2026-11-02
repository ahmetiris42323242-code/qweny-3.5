from duckduckgo_search import DDGS
import ollama
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Yerel AI Asistanı", page_icon="🤖", layout="centered"
)

st.title("🤖 Yerel Yapay Zeka Asistanı (Web Destekli)")
st.caption("Qwen 3.5 & DuckDuckGo entegrasyonu ile çevrimdışı/çevrimiçi hibrit asistan")

# Sidebar (Kenar Çubuğu) - Ayarlar
st.sidebar.header("Ayarlar")
secilen_model = st.sidebar.text_input(
    "Ollama Model Adı", value="qwen3.5:4b"
)
web_arama_acik = st.sidebar.toggle("İnternette Arama Yap (Web Search)", value=True)


def internette_ara(soru, max_sonuc=3):
  """DuckDuckGo üzerinden güncel web araması yapar."""
  try:
    with DDGS() as ddgs:
      sonuclar = ddgs.text(soru, max_results=max_sonuc)
      bilgi_metinleri = []
      for sonuc in sonuclar:
        baslik = sonuc.get("title", "")
        ozet = sonuc.get("body", "")
        bilgi_metinleri.append(f"Kaynak: {baslik}\nİçerik: {ozet}\n")
      return "\n---\n".join(bilgi_metinleri)
  except Exception as e:
    return f"Arama yapılırken hata oluştu: {str(e)}"


# Sohbet Geçmişini Başlat
if "messages" not in st.session_state:
  st.session_state.messages = []

# Geçmiş mesajları ekranda göster
for mesaj in st.session_state.messages:
  with st.chat_message(mesaj["role"]):
    st.markdown(mesaj["content"])

# Kullanıcıdan Girdi Al
if kullanıcı_girdisi := st.chat_input("Yapay zekaya bir şeyler yazın..."):
  # Kullanıcının mesajını ekrana bas ve hafızaya kaydet
  st.session_state.messages.append(
      {"role": "user", "content": kullanıcı_girdisi}
  )
  with st.chat_message("user"):
    st.markdown(kullanıcı_girdisi)

  # Asistan yanıtı hazırlama
  with st.chat_message("assistant"):
    with st.spinner("Yapay zeka düşünüyor..."):
      baglam = ""
      # Eğer web arama açıksa internetten veri çek
      if web_arama_acik:
        with st.status("🔍 İnternette arama yapılıyor...", expanded=False):
          baglam = internette_ara(kullanıcı_girdisi)

      # Modele gönderilecek nihai istemi hazırla
      if baglam:
        istem = f"""
Sen güncel bilgilere erişebilen yerel bir yapay zekasın. 
Aşağıda internetten taranan güncel web sonuçları verilmiştir. Bu bilgileri kullanıcı sorusunu yanıtlamak için kullan.

GÜNCEL WEB SONUÇLARI:
{baglam}

KULLANICI SORUSU:
{kullanıcı_girdisi}
"""
      else:
        istem = kullanıcı_girdisi

      try:
        # Ollama üzerinden yerel modeli çağır
        yanit = ollama.chat(
            model=secilen_model,
            messages=[{"role": "user", "content": istem}],
        )
        asistan_cevabi = yanit["message"]["content"]
      except Exception as e:
        asistan_cevabi = f"⚠️ Ollama bağlantı hatası: Model çalışıyor mu? Hata: {str(e)}"

      st.markdown(asistan_cevabi)

  # Asistanın yanıtını hafızaya kaydet
  st.session_state.messages.append(
      {"role": "assistant", "content": asistan_cevabi}
  )
