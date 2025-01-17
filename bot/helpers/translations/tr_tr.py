class TR(object):
    __language__ = 'tr'
#----------------
#
# TEMEL
#
#----------------
    WELCOME_MSG = "Merhaba {}"
    DOWNLOADING = 'İndiriliyor........'
    DOWNLOAD_PROGRESS = """
<b>╭─ İlerleme
│
├ {0}
│
├ Tamamlandı : <code>{1} / {2}</code>
│
├ Başlık : <code>{3}</code>
│
╰─ Tür : <code>{4}</code></b>
"""
    UPLOADING = 'Yükleniyor........'
    ZIPPING = 'Arşivleniyor........'
    TASK_COMPLETED = "İndirme Tamamlandı"

#----------------
#
# AYARLAR PANELİ
#
#----------------
    INIT_SETTINGS_PANEL = '<b>Bot Ayarlarına Hoş Geldiniz</b>'
    LANGUAGE_PANEL = 'Buradan bot dilini seçin'
    CORE_PANEL = 'Ana ayarları buradan düzenleyin'
    PROVIDERS_PANEL = 'Her platformu ayrı ayrı yapılandırın'

    TIDAL_PANEL = "Tidal ayarlarını burada yapılandırın"
    TIDAL_AUTH_PANEL = """
Tidal Hesap yetkisini burada yönetin

<b>Hesap :</b> <code>{}</code>
<b>Mobil HiRes :</b> <code>{}</code>
<b>Mobil Atmos :</b> <code>{}</code>
<b>TV/Auto : </b> <code>{}</code>
"""
    TIDAL_AUTH_URL = "Giriş yapmak için aşağıdaki bağlantıya gidin\n{}"
    TIDAL_AUTH_SUCCESSFULL = 'Tidal\'a başarıyla giriş yapıldı'
    TIDAL_REMOVED_SESSION = 'Tidal için tüm oturumlar başarıyla kaldırıldı'

    TELEGRAM_PANEL = """
<b>Telegram Ayarları</b>

Yöneticiler : {2}
Yetkili Kullanıcılar : {3}
Yetkili Sohbetler : {4}
"""
    BAN_AUTH_FORMAT = '/komut {userid} kullanın'
    BAN_ID = 'Banı kaldırıldı: {}'
    USER_DOEST_EXIST = "Bu ID mevcut değil"
    USER_EXIST = 'Bu ID zaten mevcut'
    AUTH_ID = 'Başarıyla Yetkilendirildi'

#----------------
#
# DÜĞMELER
#
#----------------
    MAIN_MENU_BUTTON = 'ANA MENÜ'
    CLOSE_BUTTON = 'KAPAT'
    PROVIDERS = 'HİZMETLER'
    TELEGRAM = 'Telegram'
    CORE = 'ÇEKİRDEK'
    
    QOBUZ = 'Qobuz'
    DEEZER = 'Deezer'
    TIDAL = 'Tidal'

    BOT_PUBLIC = 'Bot Herkese Açık - {}'
    BOT_LANGUAGE = 'Dil'
    ANTI_SPAM = 'Spam Koruması - {}'
    LANGUAGE = 'Dil'
    QUALITY = 'Kalite'
    AUTHORIZATION = "Yetkilendirmeler"

    POST_ART_BUT = "Posterleri Gönder : {}"
    SORT_PLAYLIST = 'Çalma Listesini Sırala : {}'
    DISABLE_SORT_LINK = 'Sıralama Bağlantısını Devre Dışı Bırak : {}'
    PLAYLIST_CONC_BUT = "Çalma Listesi Toplu İndirme : {}"
    PLAYLIST_ZIP = 'Çalma Listesi Arşivle : {}'
    ARTIST_BATCH_BUT = 'Sanatçı Toplu Yükle : {}'
    ARTIST_ZIP = 'Sanatçı Arşivle : {}'
    ALBUM_ZIP = 'Albüm Arşivle : {}'

    QOBUZ_QUALITY_PANEL = '<b>Qobuz Kalitesini Buradan Düzenle</b>'

    TIDAL_LOGIN_TV = 'TV Girişi'
    TIDAL_REMOVE_LOGIN = "Girişi Kaldır"
    TIDAL_REFRESH_SESSION = 'Yetkilendirmeyi Yenile'

    RCLONE_LINK = 'Doğrudan Bağlantı'
    INDEX_LINK = 'Dizin Bağlantısı'

#----------------
#
# HATALAR
#
#----------------
    ERR_NO_LINK = 'Bağlantı bulunamadı :('
    ERR_LINK_RECOGNITION = "Üzgünüm, verilen bağlantı tanınamadı."
    ERR_QOBUZ_NOT_STREAMABLE = "Bu parça/album indirilemiyor."
    ERR_QOBUZ_NOT_AVAILABLE = "Bu parça sizin bölgenizde mevcut değil"
    ERR_LOGIN_TIDAL_TV_FAILED = "Giriş başarısız oldu : {}"

#----------------
#
# UYARILAR
#
#----------------
    WARNING_NO_TIDAL_TOKEN = 'Hiçbir TV/Auto token-secret eklenmedi'

#----------------
#
# PARÇA & ALBÜM PAYLAŞIMLARI
#
#----------------
    ALBUM_TEMPLATE = """
🎶 <b>Başlık :</b> {title}
👤 <b>Sanatçı :</b> {artist}
📅 <b>Çıkış Tarihi :</b> {date}
🔢 <b>Toplam Parça :</b> {totaltracks}
📀 <b>Toplam Albüm :</b> {totalvolume}
💫 <b>Kalite :</b> {quality}
📡 <b>Sağlayıcı :</b> {provider}
🔞 <b>Açık İçerik :</b> {explicit}
"""

    PLAYLIST_TEMPLATE = """
🎶 <b>Başlık :</b> {title}
🔢 <b>Toplam Parça :</b> {totaltracks}
💫 <b>Kalite :</b> {quality}
📡 <b>Sağlayıcı :</b> {provider}
"""

    SIMPLE_TITLE = """
Adı : {0}
Türü : {1}
Sağlayıcı : {2}
"""

    ARTIST_TEMPLATE = """
👤 <b>Sanatçı :</b> {artist}
💫 <b>Kalite :</b> {quality}
📡 <b>Sağlayıcı :</b> {provider}
"""
