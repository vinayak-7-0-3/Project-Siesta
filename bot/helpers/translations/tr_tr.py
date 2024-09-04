class EN(object):

#----------------
#
# TEMELLER
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
# PANEL AYARLARI
#
#----------------
    INIT_SETTINGS_PANEL = '<b>Bot Ayarlarına Hoş Geldiniz</b>'


    TELEGRAM_PANEL = """
<b>Telegram Ayarları</b>

Yöneticiler : {2}
Yetkili Kullanıcılar : {3}
Yetkili Sohbetler : {4}

"""
    BAN_AUTH_FORMAT = '/komut {userid} kullanın'
    BAN_ID = '{} kaldırıldı'
    USER_DOEST_EXIST = "Bu ID mevcut değil"
    USER_EXIST = 'Bu ID zaten mevcut'
    AUTH_ID = 'Başarıyla Yetkilendirildi'



#----------------
#
# BUTONLAR
#
#----------------
    MAIN_MENU_BUTTON = 'ANA MENÜ'
    CLOSE_BUTTON = 'KAPAT'
    TELEGRAM = 'Telegram'
    QOBUZ = 'Qobuz'
    DEEZER = 'Deezer'
    BOT_PUBLIC = 'Bot Public - {}'
    BOT_LANGUAGE = 'Dil'
    ANTI_SPAM = 'Anti Spam - {}'
    
    POST_ART_BUT = "Sanatçı Posteri : {}"
    
    SORT_PLAYLIST = 'Çalma Listesini Sırala : {}'
    
    PLAYLIST_CONC_BUT = "Eş Zamanlı Çalma Listesi : {}"
    ARTIST_BATCH_BUT = 'Sanatçı Toplu Yükleme : {}'
    
    QOBUZ_QUALITY_PANEL = '<b>Qobuz Kalitesini Buradan Düzenleyin</b>'
    
    RCLONE_LINK = 'Doğrudan Bağlantı'
    INDEX_LINK = 'Index Bağlantısı'


#----------------
#
# HATALAR
#
#----------------
    ERR_NO_LINK = 'Bağlantı bulunamadı :('
    ERR_LINK_RECOGNITION = "Üzgünüm, verilen bağlantı tanınamadı."
    ERR_QOBUZ_NOT_STREAMABLE = "Bu parça/album indirilemez durumda."

#----------------
#
# PARÇA & ALBÜM PAYLAŞIMLARI
#
#----------------

    ALBUM_TEMPLATE = """
🎶 <b>Başlık :</b> {title}
👤 <b>Sanatçı :</b> {artist}
📅 <b>Çıkış Tarihi :</b> {date}
🔢 <b>Toplam Parça Sayısı :</b> {totaltracks}
📀 <b>Toplam Albüm Sayısı :</b> {totalvolume}
💫 <b>Kalite :</b> {quality}
📡 <b>Sağlayıcı :</b> {provider}
🔞 <b>Müstehcen İçerik :</b> {explicit}
"""

    PLAYLIST_TEMPLATE = """
🎶 <b>Başlık :</b> {title}
🔢 <b>Toplam Parça Sayısı :</b> {totaltracks}
💫 <b>Kalite :</b> {quality}
📡 <b>Sağlayıcı :</b> {provider}
"""

    SIMPLE_TITLE = """
Ad : {0}
Tür : {1}
Sağlayıcı : {2}
"""
