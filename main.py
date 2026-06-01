import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

# Harici veritabanımızı içe aktarıyoruz
from veri_tabani import KPSS_TUM_KONULAR

Window.size = (400, 700)
Window.clearcolor = (0.95, 0.95, 0.97, 1)

İLERLEME_DOSYASI = "ilerleme.json"

def ilerlemeyi_yukle():
    if os.path.exists(İLERLEME_DOSYASI):
        with open(İLERLEME_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def ilerlemeyi_kaydet(veri):
    with open(İLERLEME_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

# --- ARAYÜZ EKRANLARI ---
class MenuEkrani(Screen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        ILERLEME = ilerlemeyi_yukle()
        
        ana_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        baslik = Label(text="[b]KPSS TARİH[/b]", markup=True, font_size='28sp', color=(0.1, 0.1, 0.2, 1), size_hint=(1, 0.15))
        ana_layout.add_widget(baslik)
        
        scroll = ScrollView(size_hint=(1, 0.85))
        liste_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        liste_layout.bind(minimum_height=liste_layout.setter('height'))
        
        for konu in KPSS_TUM_KONULAR.keys():
            durum = ILERLEME.get(konu, {})
            tamamlandi = durum.get("tamamlandi", False)
            
            arkaplan_rengi = (0.2, 0.7, 0.4, 1) if tamamlandi else (0.3, 0.5, 0.8, 1)
            buton_metni = konu
            if tamamlandi:
                buton_metni += f"\n(Doğru: {durum.get('dogru',0)} | Yanlış: {durum.get('yanlis',0)})"
            
            btn = Button(
                text=buton_metni, size_hint_y=None, height=90, 
                background_normal='', background_color=arkaplan_rengi,
                font_size='16sp', halign='center'
            )
            btn.bind(on_press=lambda instance, k=konu: self.konuya_git(k))
            liste_layout.add_widget(btn)
            
        scroll.add_widget(liste_layout)
        ana_layout.add_widget(scroll)
        self.add_widget(ana_layout)
        
    def konuya_git(self, konu_adi):
        App.get_running_app().secili_konu = konu_adi
        self.manager.current = 'konu_ekrani'


class KonuEkrani(Screen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        konu_adi = App.get_running_app().secili_konu
        icerik = KPSS_TUM_KONULAR[konu_adi]["ozet"]
        
        layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        baslik = Label(text=f"[b]{konu_adi}[/b]", markup=True, font_size='22sp', color=(0.1, 0.1, 0.2, 1), size_hint=(1, 0.15), halign='center')
        
        metin_alani = ScrollView(size_hint=(1, 0.7))
        metin = Label(text=icerik, color=(0.2, 0.2, 0.2, 1), font_size='17sp', size_hint_y=None, halign='left', valign='top')
        metin.bind(width=lambda *x: metin.setter('text_size')(metin, (metin.width, None)), texture_size=lambda *x: metin.setter('height')(metin, metin.texture_size[1]))
        metin_alani.add_widget(metin)
        
        btn_teste_gec = Button(text="Konuyu Anladım, Teste Geç", size_hint=(1, 0.15), background_normal='', background_color=(0.8, 0.4, 0.1, 1), font_size='18sp', bold=True)
        btn_teste_gec.bind(on_press=self.teste_git)
        
        btn_geri = Button(text="Geri Dön", size_hint=(1, 0.1), background_normal='', background_color=(0.6, 0.6, 0.6, 1))
        btn_geri.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu_ekrani'))
        
        layout.add_widget(baslik)
        layout.add_widget(metin_alani)
        layout.add_widget(btn_teste_gec)
        layout.add_widget(btn_geri)
        self.add_widget(layout)
        
    def teste_git(self, instance):
        self.manager.current = 'soru_ekrani'


class SoruEkrani(Screen):
    def on_pre_enter(self, *args):
        self.konu_adi = App.get_running_app().secili_konu
        self.sorular = KPSS_TUM_KONULAR[self.konu_adi]["sorular"]
        self.mevcut_soru = 0
        self.dogru_sayisi = 0
        self.yanlis_sayisi = 0
        self.arayuzu_olustur()
        
    def arayuzu_olustur(self):
        self.clear_widgets()
        if self.mevcut_soru >= len(self.sorular):
            self.testi_bitir()
            return
            
        soru_verisi = self.sorular[self.mevcut_soru]
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        sayac = Label(text=f"Soru {self.mevcut_soru + 1} / {len(self.sorular)}", color=(0.4, 0.4, 0.4, 1), size_hint=(1, 0.05))
        soru_label = Label(text=soru_verisi["soru"], color=(0.1, 0.1, 0.2, 1), font_size='18sp', bold=True, size_hint=(1, 0.3), halign='center', valign='middle')
        soru_label.bind(size=soru_label.setter('text_size'))
        
        layout.add_widget(sayac)
        layout.add_widget(soru_label)
        
        self.bildirim = Label(text="", size_hint=(1, 0.1), font_size='16sp', bold=True)
        layout.add_widget(self.bildirim)
        
        secenekler_layout = GridLayout(cols=1, spacing=10, size_hint=(1, 0.55))
        for secenek in soru_verisi["secenekler"]:
            btn = Button(text=secenek, background_normal='', background_color=(0.9, 0.9, 0.9, 1), color=(0.2, 0.2, 0.2, 1), font_size='16sp')
            btn.bind(on_press=lambda instance, s=secenek, c=soru_verisi["cevap"]: self.cevap_kontrol(s, c))
            secenekler_layout.add_widget(btn)
            
        layout.add_widget(secenekler_layout)
        self.add_widget(layout)

    def cevap_kontrol(self, secilen, dogru_cevap):
        if secilen == dogru_cevap:
            self.dogru_sayisi += 1
            self.mevcut_soru += 1
            self.arayuzu_olustur()
        else:
            self.yanlis_sayisi += 1
            self.bildirim.text = f"Yanlış! Doğru Cevap: {dogru_cevap}"
            self.bildirim.color = (0.8, 0.1, 0.1, 1)

    def testi_bitir(self):
        ilerleme = ilerlemeyi_yukle()
        ilerleme[self.konu_adi] = {
            "tamamlandi": True,
            "dogru": self.dogru_sayisi,
            "yanlis": self.yanlis_sayisi
        }
        ilerlemeyi_kaydet(ilerleme)
        
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        sonuc_baslik = Label(text="[b]TEST TAMAMLANDI![/b]", markup=True, font_size='26sp', color=(0.2, 0.6, 0.3, 1), size_hint=(1, 0.3))
        istatistik = Label(text=f"Doğru: {self.dogru_sayisi}\nYanlış: {self.yanlis_sayisi}", font_size='22sp', color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.4), halign='center')
        
        btn_menu = Button(text="Ana Menüye Dön", size_hint=(1, 0.2), background_normal='', background_color=(0.2, 0.5, 0.8, 1), font_size='18sp')
        btn_menu.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu_ekrani'))
        
        layout.add_widget(sonuc_baslik)
        layout.add_widget(istatistik)
        layout.add_widget(btn_menu)
        self.add_widget(layout)
        
class KpssTarihApp(App):
    secili_konu = ""
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuEkrani(name='menu_ekrani'))
        sm.add_widget(KonuEkrani(name='konu_ekrani'))
        sm.add_widget(SoruEkrani(name='soru_ekrani'))
        return sm

if __name__ == '__main__':
    KpssTarihApp().run()