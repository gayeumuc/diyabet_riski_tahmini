"""
Diyabet Risk Tahmin Uygulaması — Modern Mavi Arayüz
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pickle
import os
import sys
import numpy as np
import pandas as pd
import subprocess
import threading
from datetime import datetime

# ─── TEMA PALETLERİ ─────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG_MAIN":      "#0B1A2E",
        "BG_SIDEBAR":   "#0D2137",
        "BG_CARD":      "#112240",
        "BG_CARD2":     "#0F1E35",
        "ACCENT":       "#1976D2",
        "ACCENT_LIGHT": "#42A5F5",
        "ACCENT_GLOW":  "#00B0FF",
        "TEXT_WHITE":   "#F0F8FF",
        "TEXT_LIGHT":   "#B0C4DE",
        "TEXT_MUTED":   "#4A6080",
        "BORDER":       "#1A3A5C",
        "BORDER_GLOW":  "#1976D2",
        "SUCCESS":      "#00E676",
        "WARNING":      "#FFD740",
        "DANGER":       "#FF5252",
        "ENTRY_BG":     "#0A1628",
        "BTN_PRIMARY":  "#1565C0",
        "BTN_HOVER":    "#1976D2",
        "HEADER_BG":    "#091525",
    },
    "light": {
        "BG_MAIN":      "#F0F4F8",
        "BG_SIDEBAR":   "#E3EAF2",
        "BG_CARD":      "#FFFFFF",
        "BG_CARD2":     "#F5F8FC",
        "ACCENT":       "#1565C0",
        "ACCENT_LIGHT": "#1976D2",
        "ACCENT_GLOW":  "#0D47A1",
        "TEXT_WHITE":   "#1A237E",
        "TEXT_LIGHT":   "#37474F",
        "TEXT_MUTED":   "#90A4AE",
        "BORDER":       "#BBDEFB",
        "BORDER_GLOW":  "#1565C0",
        "SUCCESS":      "#2E7D32",
        "WARNING":      "#F57F17",
        "DANGER":       "#C62828",
        "ENTRY_BG":     "#FFFFFF",
        "BTN_PRIMARY":  "#1565C0",
        "BTN_HOVER":    "#1976D2",
        "HEADER_BG":    "#1565C0",
    }
}

# Aktif tema (başlangıçta koyu)
_CURRENT_THEME = "dark"

def _T(key):
    """Aktif temadan renk döndür"""
    return THEMES[_CURRENT_THEME][key]

# Global kısayollar (geriye dönük uyumluluk için)
def _refresh_globals():
    global BG_MAIN, BG_SIDEBAR, BG_CARD, BG_CARD2, ACCENT, ACCENT_LIGHT
    global ACCENT_GLOW, TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, BORDER, BORDER_GLOW
    global SUCCESS, WARNING, DANGER, ENTRY_BG, BTN_PRIMARY, BTN_HOVER, HEADER_BG
    t = THEMES[_CURRENT_THEME]
    BG_MAIN      = t["BG_MAIN"]
    BG_SIDEBAR   = t["BG_SIDEBAR"]
    BG_CARD      = t["BG_CARD"]
    BG_CARD2     = t["BG_CARD2"]
    ACCENT       = t["ACCENT"]
    ACCENT_LIGHT = t["ACCENT_LIGHT"]
    ACCENT_GLOW  = t["ACCENT_GLOW"]
    TEXT_WHITE   = t["TEXT_WHITE"]
    TEXT_LIGHT   = t["TEXT_LIGHT"]
    TEXT_MUTED   = t["TEXT_MUTED"]
    BORDER       = t["BORDER"]
    BORDER_GLOW  = t["BORDER_GLOW"]
    SUCCESS      = t["SUCCESS"]
    WARNING      = t["WARNING"]
    DANGER       = t["DANGER"]
    ENTRY_BG     = t["ENTRY_BG"]
    BTN_PRIMARY  = t["BTN_PRIMARY"]
    BTN_HOVER    = t["BTN_HOVER"]
    HEADER_BG    = t["HEADER_BG"]

_refresh_globals()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── SORULAR ────────────────────────────────────────────────────────────────
QUESTIONS = [
    {"key": "HighBP",              "label": "Yüksek Tansiyon",        "icon": "🩺",
     "desc": "Hipertansiyon teşhisi konuldu mu?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "HighChol",            "label": "Yüksek Kolesterol",       "icon": "🧪",
     "desc": "Yüksek kolesterol teşhisi konuldu mu?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "CholCheck",           "label": "Kolesterol Kontrolü",     "icon": "📋",
     "desc": "Son 5 yılda kolesterol kontrolü yaptırdınız mı?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "BMI",                 "label": "Vücut Kitle İndeksi",     "icon": "⚖️",
     "desc": "BMI değeriniz (kg/m²) — Normal: 18.5–24.9",
     "type": "bmi_calc", "min": 10, "max": 80, "default": 25},
    {"key": "Smoker",              "label": "Sigara Kullanımı",        "icon": "🚬",
     "desc": "Hayatınız boyunca en az 100 sigara içtiniz mi?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "Stroke",              "label": "İnme (Felç)",             "icon": "🧠",
     "desc": "Daha önce inme geçirdiniz mi?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "HeartDiseaseorAttack","label": "Kalp Hastalığı",          "icon": "❤️",
     "desc": "Koroner kalp hastalığı veya kalp krizi geçirdiniz mi?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "PhysActivity",        "label": "Fiziksel Aktivite",       "icon": "🏃",
     "desc": "Son 30 günde iş dışında fiziksel aktivite yaptınız mı?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "Fruits",              "label": "Meyve Tüketimi",          "icon": "🍎",
     "desc": "Günde en az 1 kez meyve tüketiyor musunuz?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "Veggies",             "label": "Sebze Tüketimi",          "icon": "🥦",
     "desc": "Günde en az 1 kez sebze tüketiyor musunuz?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "HvyAlcoholConsump",   "label": "Ağır Alkol Tüketimi",    "icon": "🍷",
     "desc": "Erkekler haftada >14, kadınlar haftada >7 alkollü içecek?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "GenHlth",             "label": "Genel Sağlık Durumu",     "icon": "💊",
     "desc": "Genel sağlık durumunuzu değerlendirin",
     "type": "scale",
     "options": ["1 – Mükemmel", "2 – Çok İyi", "3 – İyi", "4 – Orta", "5 – Kötü"],
     "values": [1, 2, 3, 4, 5]},
    {"key": "MentHlth",            "label": "Ruh Sağlığı (Gün)",       "icon": "🧘",
     "desc": "Son 30 günde kaç gün ruh sağlığınız kötüydü?",
     "type": "slider", "min": 0, "max": 30, "default": 0},
    {"key": "PhysHlth",            "label": "Fiziksel Sağlık (Gün)",   "icon": "🏥",
     "desc": "Son 30 günde kaç gün fiziksel sağlığınız kötüydü?",
     "type": "slider", "min": 0, "max": 30, "default": 0},
    {"key": "DiffWalk",            "label": "Yürüme Güçlüğü",          "icon": "🦯",
     "desc": "Merdiven çıkmakta veya yürümekte güçlük çekiyor musunuz?",
     "type": "binary", "options": ["Hayır", "Evet"]},
    {"key": "Sex",                 "label": "Cinsiyet",                "icon": "👤",
     "desc": "Cinsiyetinizi seçin",
     "type": "binary", "options": ["Kadın", "Erkek"]},
    {"key": "Age",                 "label": "Yaş Grubu",               "icon": "🎂",
     "desc": "Yaş grubunuzu seçin",
     "type": "scale",
     "options": ["1: 18–24","2: 25–29","3: 30–34","4: 35–39","5: 40–44",
                 "6: 45–49","7: 50–54","8: 55–59","9: 60–64","10: 65–69",
                 "11: 70–74","12: 75–79","13: 80+"],
     "values": list(range(1, 14))},
]

FEATURES = [q["key"] for q in QUESTIONS]


def load_model():
    paths = [os.path.join(BASE_DIR, f)
             for f in ["diabetes_model.pkl","diabetes_scaler.pkl","diabetes_features.pkl"]]
    if not all(os.path.exists(p) for p in paths):
        return None, None, None
    with open(paths[0],'rb') as f: model = pickle.load(f)
    with open(paths[1],'rb') as f: scaler = pickle.load(f)
    with open(paths[2],'rb') as f: info = pickle.load(f)
    return model, scaler, info


# ─── YUVARLAK KÖŞE CANVAS YARDIMCISI ────────────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,   extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,  style="pieslice", **kwargs)
    canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
    canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)


# ─── ANA UYGULAMA ────────────────────────────────────────────────────────────
class DiabetesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diyabet Risk Tahmin Sistemi")
        self.geometry("1150x780")
        self.minsize(950, 680)
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)

        try: self.iconbitmap(default='')
        except: pass

        self.model, self.scaler, self.model_info = load_model()
        self.widgets = {}
        self.last_result = None   # son analiz sonucu (PDF için)
        self._theme = "dark"      # aktif tema

        self._setup_styles()
        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 1150, 780
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure("TScrollbar", background=ACCENT, troughcolor=BG_CARD,
                    arrowcolor=TEXT_WHITE, borderwidth=0, relief="flat")
        s.configure("Slim.Vertical.TScrollbar", background=BORDER,
                    troughcolor=BG_MAIN, arrowcolor=BG_MAIN,
                    borderwidth=0, relief="flat", width=6)
        s.configure("Blue.Horizontal.TScale", background=BG_CARD,
                    troughcolor=BORDER, sliderlength=16, sliderrelief="flat")
        s.configure("Blue.TCombobox", fieldbackground=ENTRY_BG,
                    background=ACCENT, foreground=TEXT_WHITE,
                    selectbackground=ACCENT_LIGHT, selectforeground=TEXT_WHITE,
                    arrowcolor=ACCENT_GLOW, borderwidth=0)
        s.map("Blue.TCombobox",
              fieldbackground=[('readonly', ENTRY_BG)],
              foreground=[('readonly', TEXT_WHITE)])
        s.configure("Accent.Horizontal.TProgressbar",
                    troughcolor=BORDER, background=ACCENT_GLOW,
                    thickness=6, borderwidth=0)

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 14))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)
        self._build_form(body)
        self._build_result(body)
        self._build_footer()

    # ── HEADER ───────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=HEADER_BG, height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Sol: logo + başlık
        left = tk.Frame(hdr, bg=HEADER_BG)
        left.pack(side=tk.LEFT, padx=20, pady=10)

        badge = tk.Frame(left, bg=ACCENT, width=46, height=46)
        badge.pack(side=tk.LEFT)
        badge.pack_propagate(False)
        tk.Label(badge, text="🩺", font=("Segoe UI Emoji", 22),
                 bg=ACCENT, fg=TEXT_WHITE).place(relx=.5, rely=.5, anchor="center")

        title_f = tk.Frame(left, bg=HEADER_BG)
        title_f.pack(side=tk.LEFT, padx=(12, 0))
        tk.Label(title_f, text="Diyabet Risk Tahmin Sistemi",
                 font=("Segoe UI", 16, "bold"),
                 bg=HEADER_BG, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(title_f, text="BRFSS 2015  •  Random Forest  •  17 Klinik Gösterge",
                 font=("Segoe UI", 8),
                 bg=HEADER_BG, fg=TEXT_MUTED).pack(anchor="w")

        # Sağ: tema butonu + model durumu
        right = tk.Frame(hdr, bg=HEADER_BG)
        right.pack(side=tk.RIGHT, padx=20)

        # Tema geçiş butonu
        theme_icon = "☀️" if self._theme == "dark" else "🌙"
        theme_tip  = "Açık Tema" if self._theme == "dark" else "Koyu Tema"
        self.theme_btn = tk.Button(
            right,
            text=f"{theme_icon}  {theme_tip}",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD, fg=TEXT_LIGHT,
            activebackground=BORDER, activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2",
            padx=10, pady=4,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=(0, 12))

        if self.model and self.model_info:
            acc = self.model_info.get('accuracy', 0)
            auc = self.model_info.get('auc', 0)
            self._stat_badge(right, "Doğruluk", f"{acc*100:.1f}%", SUCCESS)
            self._stat_badge(right, "AUC-ROC",  f"{auc:.3f}",      ACCENT_GLOW)
        else:
            tk.Label(right, text="⚠  Model yüklenmedi",
                     font=("Segoe UI", 9, "bold"),
                     bg=HEADER_BG, fg=WARNING).pack(side=tk.LEFT)

        # Alt çizgi
        tk.Frame(self, bg=ACCENT, height=2).pack(fill=tk.X)

    def _stat_badge(self, parent, label, value, color):
        f = tk.Frame(parent, bg=BG_CARD, padx=12, pady=6)
        f.pack(side=tk.LEFT, padx=5)
        tk.Label(f, text=label, font=("Segoe UI", 7),
                 bg=BG_CARD, fg=TEXT_MUTED).pack()
        tk.Label(f, text=value, font=("Segoe UI", 12, "bold"),
                 bg=BG_CARD, fg=color).pack()

    # ── FORM ─────────────────────────────────────────────────────────────────
    def _build_form(self, parent):
        outer = tk.Frame(parent, bg=BG_MAIN)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        # Başlık satırı
        hdr_f = tk.Frame(outer, bg=BG_MAIN)
        hdr_f.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(hdr_f, text="Hasta Bilgileri",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_MAIN, fg=ACCENT_GLOW).pack(side=tk.LEFT)
        tk.Label(hdr_f, text=f"({len(QUESTIONS)} gösterge)",
                 font=("Segoe UI", 9),
                 bg=BG_MAIN, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=6)

        # Kaydırılabilir alan
        wrap = tk.Frame(outer, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        wrap.grid(row=1, column=0, sticky="nsew")

        canvas = tk.Canvas(wrap, bg=BG_CARD, highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview,
                            style="Slim.Vertical.TScrollbar")
        self.sf = tk.Frame(canvas, bg=BG_CARD)
        self.sf.bind("<Configure>",
                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sf, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._build_questions()

    def _build_questions(self):
        cols = 2
        for idx, q in enumerate(QUESTIONS):
            r, c = divmod(idx, cols)
            self._question_card(self.sf, q, r, c)
            self.sf.columnconfigure(c, weight=1)

    def _question_card(self, parent, q, row, col):
        card = tk.Frame(parent, bg=BG_CARD2,
                        highlightbackground=BORDER,
                        highlightthickness=1)
        card.grid(row=row, column=col, padx=7, pady=5, sticky="nsew")

        # Üst şerit (ikon + başlık)
        top = tk.Frame(card, bg=ACCENT, height=32)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text=q.get("icon","•") + "  " + q["label"],
                 font=("Segoe UI", 9, "bold"),
                 bg=ACCENT, fg=TEXT_WHITE,
                 anchor="w").pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Açıklama
        tk.Label(card, text=q["desc"],
                 font=("Segoe UI", 8),
                 bg=BG_CARD2, fg=TEXT_LIGHT,
                 wraplength=210, justify="left",
                 anchor="w").pack(anchor="w", padx=10, pady=(6, 4))

        # Giriş alanı
        inp = tk.Frame(card, bg=BG_CARD2)
        inp.pack(fill=tk.X, padx=10, pady=(0, 10))

        if q["type"] == "binary":
            var = tk.IntVar(value=0)
            for i, opt in enumerate(q["options"]):
                color = SUCCESS if i == 0 else DANGER
                rb = tk.Radiobutton(inp, text=opt, variable=var, value=i,
                                    bg=BG_CARD2, fg=TEXT_WHITE,
                                    selectcolor=BG_MAIN,
                                    activebackground=BG_CARD2,
                                    activeforeground=color,
                                    font=("Segoe UI", 9, "bold"),
                                    cursor="hand2",
                                    indicatoron=0,
                                    relief="flat",
                                    padx=14, pady=4,
                                    bd=1)
                rb.pack(side=tk.LEFT, padx=(0, 6))
                rb.config(highlightbackground=BORDER, highlightthickness=1)
            self.widgets[q["key"]] = var

        elif q["type"] == "slider":
            var = tk.DoubleVar(value=q["default"])
            row_f = tk.Frame(inp, bg=BG_CARD2)
            row_f.pack(fill=tk.X)

            # Min etiketi
            tk.Label(row_f, text=str(q["min"]),
                     font=("Segoe UI", 7), bg=BG_CARD2, fg=TEXT_MUTED,
                     width=3).pack(side=tk.LEFT)

            slider = ttk.Scale(row_f, from_=q["min"], to=q["max"],
                               variable=var, orient=tk.HORIZONTAL,
                               style="Blue.Horizontal.TScale")
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

            # Max etiketi
            tk.Label(row_f, text=str(q["max"]),
                     font=("Segoe UI", 7), bg=BG_CARD2, fg=TEXT_MUTED,
                     width=3).pack(side=tk.LEFT)

            # Sayı giriş kutusu
            entry_var = tk.StringVar(value=str(q["default"]))
            entry = tk.Entry(row_f, textvariable=entry_var,
                             width=5, font=("Segoe UI", 10, "bold"),
                             bg=ENTRY_BG, fg=ACCENT_GLOW,
                             insertbackground=ACCENT_GLOW,
                             relief="flat",
                             highlightbackground=ACCENT,
                             highlightthickness=1,
                             justify="center")
            entry.pack(side=tk.LEFT, padx=(6, 0))

            def _on_slider(v, ev=entry_var, dv=var):
                ev.set(str(int(float(v))))
                dv.set(int(float(v)))

            def _on_entry(name, idx2, mode,
                          ev=entry_var, dv=var,
                          mn=q["min"], mx=q["max"]):
                try:
                    iv = max(mn, min(mx, int(float(ev.get()))))
                    dv.set(iv)
                except ValueError:
                    pass

            slider.configure(command=_on_slider)
            entry_var.trace_add("write", _on_entry)
            self.widgets[q["key"]] = var

        elif q["type"] == "scale":
            var = tk.IntVar(value=q["values"][0])
            combo_var = tk.StringVar(value=q["options"][0])
            combo = ttk.Combobox(inp, textvariable=combo_var,
                                 values=q["options"],
                                 state="readonly",
                                 style="Blue.TCombobox",
                                 font=("Segoe UI", 8))
            combo.pack(fill=tk.X)

            def on_sel(event, v=var, opts=q["options"],
                       vals=q["values"], cb=combo_var):
                try: v.set(vals[opts.index(cb.get())])
                except ValueError: pass
            combo.bind("<<ComboboxSelected>>", on_sel)
            self.widgets[q["key"]] = var

        elif q["type"] == "bmi_calc":
            var = tk.DoubleVar(value=q["default"])

            # ttk Notebook (sekme)
            nb_style = ttk.Style()
            nb_style.configure("BMI.TNotebook", background=BG_CARD2, borderwidth=0)
            nb_style.configure("BMI.TNotebook.Tab",
                               background=BORDER, foreground=TEXT_MUTED,
                               padding=[10, 4], font=("Segoe UI", 8))
            nb_style.map("BMI.TNotebook.Tab",
                         background=[("selected", ACCENT)],
                         foreground=[("selected", TEXT_WHITE)])

            nb = ttk.Notebook(inp, style="BMI.TNotebook")
            nb.pack(fill=tk.X)

            # ── Sekme 1: Direkt BMI ──────────────────────────────────────────
            tab1 = tk.Frame(nb, bg=BG_CARD2)
            nb.add(tab1, text="  Direkt BMI Gir  ")

            t1_row = tk.Frame(tab1, bg=BG_CARD2)
            t1_row.pack(fill=tk.X, pady=6)

            tk.Label(t1_row, text=str(q["min"]),
                     font=("Segoe UI", 7), bg=BG_CARD2, fg=TEXT_MUTED,
                     width=3).pack(side=tk.LEFT)

            slider1 = ttk.Scale(t1_row, from_=q["min"], to=q["max"],
                                variable=var, orient=tk.HORIZONTAL,
                                style="Blue.Horizontal.TScale")
            slider1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

            tk.Label(t1_row, text=str(q["max"]),
                     font=("Segoe UI", 7), bg=BG_CARD2, fg=TEXT_MUTED,
                     width=3).pack(side=tk.LEFT)

            bmi_entry_var = tk.StringVar(value=str(q["default"]))
            bmi_entry = tk.Entry(t1_row, textvariable=bmi_entry_var,
                                 width=5, font=("Segoe UI", 10, "bold"),
                                 bg=ENTRY_BG, fg=ACCENT_GLOW,
                                 insertbackground=ACCENT_GLOW,
                                 relief="flat",
                                 highlightbackground=ACCENT,
                                 highlightthickness=1,
                                 justify="center")
            bmi_entry.pack(side=tk.LEFT, padx=(6, 0))

            bmi_cat = tk.Label(tab1, text="Normal",
                               font=("Segoe UI", 8, "bold"),
                               bg=BG_CARD2, fg=SUCCESS)
            bmi_cat.pack(pady=(0, 4))

            def _bmi_category(bmi_val):
                if bmi_val < 18.5: return "Zayıf", WARNING
                elif bmi_val < 25:  return "Normal", SUCCESS
                elif bmi_val < 30:  return "Fazla Kilolu", WARNING
                else:               return "Obez", DANGER

            def _on_bmi_slider(v, ev=bmi_entry_var, dv=var, lbl=bmi_cat):
                iv = int(float(v))
                ev.set(str(iv))
                dv.set(iv)
                cat, col = _bmi_category(iv)
                lbl.config(text=f"BMI: {iv}  →  {cat}", fg=col)

            def _on_bmi_entry(name, idx2, mode,
                              ev=bmi_entry_var, dv=var, lbl=bmi_cat,
                              mn=q["min"], mx=q["max"]):
                try:
                    iv = max(mn, min(mx, int(float(ev.get()))))
                    dv.set(iv)
                    cat, col = _bmi_category(iv)
                    lbl.config(text=f"BMI: {iv}  →  {cat}", fg=col)
                except ValueError:
                    pass

            slider1.configure(command=_on_bmi_slider)
            bmi_entry_var.trace_add("write", _on_bmi_entry)

            # ── Sekme 2: Boy/Kilo ile Hesapla ───────────────────────────────
            tab2 = tk.Frame(nb, bg=BG_CARD2)
            nb.add(tab2, text="  Boy/Kilo ile Hesapla  ")

            calc_row = tk.Frame(tab2, bg=BG_CARD2)
            calc_row.pack(fill=tk.X, padx=4, pady=6)

            # Boy
            tk.Label(calc_row, text="Boy (cm):",
                     font=("Segoe UI", 8), bg=BG_CARD2,
                     fg=TEXT_LIGHT).pack(side=tk.LEFT)
            boy_var = tk.StringVar(value="170")
            tk.Entry(calc_row, textvariable=boy_var, width=5,
                     font=("Segoe UI", 9, "bold"),
                     bg=ENTRY_BG, fg=ACCENT_GLOW,
                     insertbackground=ACCENT_GLOW,
                     relief="flat",
                     highlightbackground=ACCENT,
                     highlightthickness=1,
                     justify="center").pack(side=tk.LEFT, padx=(4, 12))

            # Kilo
            tk.Label(calc_row, text="Kilo (kg):",
                     font=("Segoe UI", 8), bg=BG_CARD2,
                     fg=TEXT_LIGHT).pack(side=tk.LEFT)
            kilo_var = tk.StringVar(value="70")
            tk.Entry(calc_row, textvariable=kilo_var, width=5,
                     font=("Segoe UI", 9, "bold"),
                     bg=ENTRY_BG, fg=ACCENT_GLOW,
                     insertbackground=ACCENT_GLOW,
                     relief="flat",
                     highlightbackground=ACCENT,
                     highlightthickness=1,
                     justify="center").pack(side=tk.LEFT, padx=(4, 10))

            result_lbl = tk.Label(tab2, text="BMI: —",
                                  font=("Segoe UI", 9, "bold"),
                                  bg=BG_CARD2, fg=TEXT_MUTED)
            result_lbl.pack(pady=(0, 4))

            def _calc_bmi(dv=var, bv=boy_var, kv=kilo_var,
                          lbl=result_lbl, ev=bmi_entry_var):
                try:
                    boy_m = float(bv.get()) / 100
                    kilo  = float(kv.get())
                    if boy_m <= 0: return
                    bmi = round(kilo / (boy_m ** 2), 1)
                    bmi_clamped = max(10, min(80, int(bmi)))
                    dv.set(bmi_clamped)
                    ev.set(str(bmi_clamped))
                    cat, col = _bmi_category(bmi)
                    lbl.config(text=f"BMI: {bmi}  →  {cat}", fg=col)
                except (ValueError, ZeroDivisionError):
                    lbl.config(text="Geçersiz değer", fg=DANGER)

            tk.Button(tab2, text="  Hesapla  ",
                      font=("Segoe UI", 8, "bold"),
                      bg=ACCENT, fg=TEXT_WHITE,
                      activebackground=BTN_HOVER,
                      relief="flat", cursor="hand2", pady=3,
                      command=_calc_bmi).pack(pady=(0, 6))

            self.widgets[q["key"]] = var

    # ── SONUÇ PANELİ ─────────────────────────────────────────────────────────
    def _build_result(self, parent):
        outer = tk.Frame(parent, bg=BG_MAIN)
        outer.grid(row=0, column=1, sticky="nsew", pady=8)
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        tk.Label(outer, text="Tahmin Sonucu",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_MAIN, fg=ACCENT_GLOW).grid(row=0, column=0,
                                                    sticky="w", pady=(0, 8))

        card = tk.Frame(outer, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew")

        # İkon alanı
        icon_frame = tk.Frame(card, bg=BG_CARD2, height=130)
        icon_frame.pack(fill=tk.X)
        icon_frame.pack_propagate(False)

        self.risk_icon = tk.Label(icon_frame, text="❓",
                                  font=("Segoe UI Emoji", 48),
                                  bg=BG_CARD2, fg=TEXT_MUTED)
        self.risk_icon.place(relx=.5, rely=.45, anchor="center")

        # Risk başlığı
        self.risk_label = tk.Label(card, text="Analiz Bekleniyor",
                                   font=("Segoe UI", 13, "bold"),
                                   bg=BG_CARD, fg=TEXT_MUTED)
        self.risk_label.pack(pady=(10, 2))

        # Yüzde
        self.risk_pct = tk.Label(card, text="— %",
                                 font=("Segoe UI", 32, "bold"),
                                 bg=BG_CARD, fg=TEXT_MUTED)
        self.risk_pct.pack()

        self.risk_sub = tk.Label(card, text="Formu doldurup analiz edin",
                                 font=("Segoe UI", 8),
                                 bg=BG_CARD, fg=TEXT_MUTED,
                                 wraplength=270, justify="center")
        self.risk_sub.pack(pady=(4, 10))

        # Risk çubuğu
        bar_outer = tk.Frame(card, bg=BORDER, height=10)
        bar_outer.pack(fill=tk.X, padx=20, pady=(0, 4))
        bar_outer.pack_propagate(False)
        self.risk_bar = tk.Frame(bar_outer, bg=TEXT_MUTED, height=10)
        self.risk_bar.place(x=0, y=0, relheight=1, relwidth=0)

        self.bar_lbl = tk.Label(card, text="",
                                font=("Segoe UI", 7),
                                bg=BG_CARD, fg=TEXT_MUTED)
        self.bar_lbl.pack()

        # Ayırıcı
        tk.Frame(card, bg=BORDER, height=1).pack(fill=tk.X, padx=15, pady=8)

        # Öneriler başlığı
        tk.Label(card, text="💡  Öneriler",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=ACCENT_LIGHT,
                 anchor="w").pack(anchor="w", padx=18)

        self.advice_frame = tk.Frame(card, bg=BG_CARD)
        self.advice_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 10))
        self._default_advice()

        # Model bilgisi
        if self.model_info:
            acc = self.model_info.get('accuracy', 0)
            auc = self.model_info.get('auc', 0)
            info_bar = tk.Frame(card, bg=HEADER_BG)
            info_bar.pack(fill=tk.X)
            tk.Label(info_bar,
                     text=f"Random Forest  |  Doğruluk: {acc*100:.1f}%  |  AUC: {auc:.3f}",
                     font=("Segoe UI", 7),
                     bg=HEADER_BG, fg=TEXT_MUTED).pack(pady=5)

    def _default_advice(self):
        for w in self.advice_frame.winfo_children(): w.destroy()
        for tip in ["📋 Tüm alanları doldurun",
                    "🔍 'Analiz Et' butonuna tıklayın",
                    "⚕️ Sonuçlar tıbbi teşhis değildir"]:
            tk.Label(self.advice_frame, text=tip,
                     font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_MUTED,
                     anchor="w", wraplength=260).pack(anchor="w", pady=2)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    def _build_footer(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X)
        footer = tk.Frame(self, bg=HEADER_BG, height=52)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)

        btn_f = tk.Frame(footer, bg=HEADER_BG)
        btn_f.pack(side=tk.LEFT, padx=18, pady=8)

        # Analiz butonu
        self.analyze_btn = tk.Button(
            btn_f,
            text="  🔍  Diyabet Riskini Analiz Et  ",
            font=("Segoe UI", 11, "bold"),
            bg=BTN_PRIMARY, fg=TEXT_WHITE,
            activebackground=BTN_HOVER, activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2", pady=6,
            command=self.analyze
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_f,
            text="  🔄  Temizle  ",
            font=("Segoe UI", 9),
            bg=BG_CARD, fg=TEXT_LIGHT,
            activebackground=BORDER, activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2", pady=6,
            command=self.reset_form
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_f,
            text="  ⚙️  Modeli Yeniden Eğit  ",
            font=("Segoe UI", 9),
            bg=BG_CARD, fg=TEXT_MUTED,
            activebackground=BORDER, activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2", pady=6,
            command=self.train_model
        ).pack(side=tk.LEFT, padx=(0, 16))

        # Hasta adı + PDF butonu
        tk.Label(btn_f, text="Hasta Adı:",
                 font=("Segoe UI", 8), bg=HEADER_BG,
                 fg=TEXT_LIGHT).pack(side=tk.LEFT)
        self.hasta_adi = tk.Entry(btn_f, width=18,
                                  font=("Segoe UI", 9),
                                  bg=ENTRY_BG, fg=TEXT_WHITE,
                                  insertbackground=ACCENT_GLOW,
                                  relief="flat",
                                  highlightbackground=ACCENT,
                                  highlightthickness=1)
        self.hasta_adi.pack(side=tk.LEFT, padx=(4, 8), ipady=3)

        tk.Button(
            btn_f,
            text="  📄  PDF Rapor  ",
            font=("Segoe UI", 9, "bold"),
            bg="#1B5E20", fg=TEXT_WHITE,
            activebackground="#2E7D32", activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2", pady=6,
            command=self.save_pdf
        ).pack(side=tk.LEFT)

        tk.Label(footer,
                 text="⚠️  Bu uygulama tıbbi teşhis aracı değildir.",
                 font=("Segoe UI", 8),
                 bg=HEADER_BG, fg=TEXT_MUTED).pack(side=tk.RIGHT, padx=18)

    # ── ANALİZ ───────────────────────────────────────────────────────────────
    def analyze(self):
        if not self.model:
            messagebox.showwarning("Model Yok",
                "Önce 'Modeli Yeniden Eğit' butonuna tıklayın.")
            return

        values = {}
        for q in QUESTIONS:
            raw = self.widgets[q["key"]].get()
            values[q["key"]] = int(float(raw))

        X = pd.DataFrame([values], columns=FEATURES)
        X_scaled = self.scaler.transform(X)
        prob = self.model.predict_proba(X_scaled)[0][1]
        pct = prob * 100

        if pct < 30:
            level, color, icon = "DÜŞÜK RİSK", SUCCESS, "✅"
            advice = [
                "✅ Diyabet riskiniz düşük görünüyor.",
                "🥗 Sağlıklı beslenmeye devam edin.",
                "🏃 Haftada 150 dk fiziksel aktivite yapın.",
                "🩺 Yıllık sağlık kontrollerinizi yaptırın.",
                "💧 Günde en az 8 bardak su için.",
            ]
            sub = "Mevcut yaşam tarzınızı koruyun."
        elif pct < 60:
            level, color, icon = "ORTA RİSK", WARNING, "⚠️"
            advice = [
                "⚠️ Orta düzeyde diyabet riski var.",
                "🩺 En kısa sürede doktorunuza başvurun.",
                "🍬 Şeker ve işlenmiş gıdaları azaltın.",
                "⚖️ Sağlıklı kilo aralığını koruyun.",
                "🚶 Günlük yürüyüş alışkanlığı edinin.",
                "🩸 Kan şekerinizi düzenli takip edin.",
            ]
            sub = "Yaşam tarzı değişiklikleri riskinizi azaltır."
        else:
            level, color, icon = "YÜKSEK RİSK", DANGER, "🚨"
            advice = [
                "🚨 Yüksek diyabet riski tespit edildi!",
                "🏥 Lütfen vakit kaybetmeden doktora gidin.",
                "🩸 Açlık kan şekeri testi yaptırın.",
                "🍽️ Diyetisyen desteği alın.",
                "📊 Kan şekerinizi günlük takip edin.",
                "🚫 Sigara ve alkolden uzak durun.",
            ]
            sub = "Acilen bir sağlık uzmanına danışın!"

        # Son sonucu PDF için sakla
        self.last_result = {
            "level": level, "pct": pct, "color": color,
            "sub": sub, "advice": advice,
            "values": values,
            "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        self._update_result(icon, level, pct, color, sub, advice)

    def _update_result(self, icon, level, pct, color, sub, advice):
        self.risk_icon.config(text=icon, fg=color)
        self.risk_label.config(text=level, fg=color)
        self.risk_pct.config(text=f"%{pct:.1f}", fg=color)
        self.risk_sub.config(text=sub, fg=TEXT_LIGHT)
        self.risk_bar.config(bg=color)
        self.risk_bar.place(x=0, y=0, relheight=1, relwidth=pct/100)
        self.bar_lbl.config(text=f"Risk Oranı: %{pct:.1f}", fg=color)

        for w in self.advice_frame.winfo_children(): w.destroy()
        for tip in advice:
            tk.Label(self.advice_frame, text=tip,
                     font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_WHITE,
                     anchor="w", wraplength=260).pack(anchor="w", pady=2)

    # ── FORM TEMİZLE ─────────────────────────────────────────────────────────
    def reset_form(self):
        for q in QUESTIONS:
            key = q["key"]
            if q["type"] == "binary":
                self.widgets[key].set(0)
            elif q["type"] == "slider":
                self.widgets[key].set(q["default"])
            elif q["type"] == "scale":
                self.widgets[key].set(q["values"][0])

        self.risk_icon.config(text="❓", fg=TEXT_MUTED)
        self.risk_label.config(text="Analiz Bekleniyor", fg=TEXT_MUTED)
        self.risk_pct.config(text="— %", fg=TEXT_MUTED)
        self.risk_sub.config(text="Formu doldurup analiz edin", fg=TEXT_MUTED)
        self.risk_bar.place(x=0, y=0, relheight=1, relwidth=0)
        self.bar_lbl.config(text="", fg=TEXT_MUTED)
        self._default_advice()

    # ── TEMA GEÇİŞİ ──────────────────────────────────────────────────────────
    def toggle_theme(self):
        global _CURRENT_THEME, BG_MAIN, BG_SIDEBAR, BG_CARD, BG_CARD2, ACCENT
        global ACCENT_LIGHT, ACCENT_GLOW, TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED
        global BORDER, BORDER_GLOW, SUCCESS, WARNING, DANGER, ENTRY_BG
        global BTN_PRIMARY, BTN_HOVER, HEADER_BG

        # Temayı değiştir
        self._theme = "light" if self._theme == "dark" else "dark"
        _CURRENT_THEME = self._theme
        _refresh_globals()

        # Mevcut UI'ı tamamen yok et ve yeniden oluştur
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=BG_MAIN)
        self.widgets = {}
        self.last_result = None

        self._setup_styles()
        self._build_ui()

    # ── PDF RAPOR ────────────────────────────────────────────────────────────
    def save_pdf(self):
        if not self.last_result:
            messagebox.showwarning("Uyarı", "Önce analiz yapın, ardından PDF kaydedin.")
            return

        hasta = self.hasta_adi.get().strip() or "Belirtilmedi"
        r = self.last_result

        # Kayıt yeri seç
        default_name = f"diyabet_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dosyası", "*.pdf")],
            initialfile=default_name,
            title="PDF Raporunu Kaydet"
        )
        if not path:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            Table, TableStyle, HRFlowable)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            doc = SimpleDocTemplate(path, pagesize=A4,
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            # Özel stiller
            title_style = ParagraphStyle("title", parent=styles["Title"],
                                         fontSize=20, textColor=colors.HexColor("#1565C0"),
                                         spaceAfter=4, alignment=TA_CENTER)
            sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
                                         fontSize=10, textColor=colors.HexColor("#546E7A"),
                                         alignment=TA_CENTER, spaceAfter=12)
            h2_style    = ParagraphStyle("h2", parent=styles["Heading2"],
                                         fontSize=13, textColor=colors.HexColor("#1565C0"),
                                         spaceBefore=14, spaceAfter=6)
            body_style  = ParagraphStyle("body", parent=styles["Normal"],
                                         fontSize=10, textColor=colors.HexColor("#212121"),
                                         leading=16)
            advice_style = ParagraphStyle("advice", parent=styles["Normal"],
                                          fontSize=10, textColor=colors.HexColor("#1B5E20"),
                                          leading=18, leftIndent=10)

            # Risk rengi
            pct = r["pct"]
            if pct < 30:   risk_hex = "#00C853"
            elif pct < 60: risk_hex = "#FFD600"
            else:          risk_hex = "#D50000"
            risk_color = colors.HexColor(risk_hex)

            story = []

            # ── Başlık ──────────────────────────────────────────────────────
            story.append(Paragraph("🩺 Diyabet Risk Tahmin Raporu", title_style))
            story.append(Paragraph("BRFSS 2015 Veri Seti  •  Random Forest Modeli", sub_style))
            story.append(HRFlowable(width="100%", thickness=2,
                                    color=colors.HexColor("#1565C0")))
            story.append(Spacer(1, 0.4*cm))

            # ── Hasta Bilgileri ──────────────────────────────────────────────
            story.append(Paragraph("Hasta Bilgileri", h2_style))
            hasta_data = [
                ["Hasta Adı / Soyadı", hasta],
                ["Analiz Tarihi", r["tarih"]],
                ["Model Doğruluğu",
                 f"{self.model_info.get('accuracy',0)*100:.1f}%  |  AUC: {self.model_info.get('auc',0):.3f}"
                 if self.model_info else "—"],
            ]
            hasta_tbl = Table(hasta_data, colWidths=[5*cm, 12*cm])
            hasta_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E3F2FD")),
                ("TEXTCOLOR",  (0,0), (0,-1), colors.HexColor("#1565C0")),
                ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 10),
                ("ROWBACKGROUNDS", (1,0), (1,-1),
                 [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#BBDEFB")),
                ("PADDING",    (0,0), (-1,-1), 7),
            ]))
            story.append(hasta_tbl)
            story.append(Spacer(1, 0.4*cm))

            # ── Risk Sonucu ──────────────────────────────────────────────────
            story.append(Paragraph("Risk Sonucu", h2_style))
            risk_data = [
                [Paragraph(f"<b>{r['level']}</b>", ParagraphStyle(
                    "rl", fontSize=16, textColor=risk_color, alignment=TA_CENTER)),
                 Paragraph(f"<b>%{pct:.1f}</b>", ParagraphStyle(
                    "rp", fontSize=22, textColor=risk_color, alignment=TA_CENTER))],
                [Paragraph(r["sub"], ParagraphStyle(
                    "rs", fontSize=10, textColor=colors.HexColor("#424242"),
                    alignment=TA_CENTER)), ""],
            ]
            risk_tbl = Table(risk_data, colWidths=[8.5*cm, 8.5*cm])
            risk_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E8F5E9") if pct < 30
                               else colors.HexColor("#FFFDE7") if pct < 60
                               else colors.HexColor("#FFEBEE")),
                ("BOX",        (0,0), (-1,-1), 1.5, risk_color),
                ("SPAN",       (0,1), (1,1)),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("PADDING",    (0,0), (-1,-1), 10),
            ]))
            story.append(risk_tbl)
            story.append(Spacer(1, 0.4*cm))

            # ── Öneriler ────────────────────────────────────────────────────
            story.append(Paragraph("Öneriler", h2_style))
            for tip in r["advice"]:
                story.append(Paragraph(tip, advice_style))
            story.append(Spacer(1, 0.4*cm))

            # ── Girilen Değerler ─────────────────────────────────────────────
            story.append(Paragraph("Girilen Sağlık Verileri", h2_style))
            q_map = {q["key"]: q for q in QUESTIONS}
            tbl_data = [["Gösterge", "Değer"]]
            for key, val in r["values"].items():
                q = q_map.get(key, {})
                label = q.get("label", key)
                # Binary için Evet/Hayır
                if q.get("type") == "binary":
                    opts = q.get("options", ["Hayır", "Evet"])
                    display = opts[int(val)] if int(val) < len(opts) else str(val)
                elif q.get("type") == "scale":
                    opts = q.get("options", [])
                    vals = q.get("values", [])
                    try:
                        display = opts[vals.index(int(val))]
                    except (ValueError, IndexError):
                        display = str(val)
                else:
                    display = str(val)
                tbl_data.append([label, display])

            val_tbl = Table(tbl_data, colWidths=[8*cm, 9*cm])
            val_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
                ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS",(0,1), (-1,-1),
                 [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#BBDEFB")),
                ("PADDING",       (0,0), (-1,-1), 6),
            ]))
            story.append(val_tbl)
            story.append(Spacer(1, 0.6*cm))

            # ── Yasal Uyarı ──────────────────────────────────────────────────
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor("#BBDEFB")))
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(
                "⚠️  Bu rapor yapay zeka destekli bir risk tahmin aracı tarafından oluşturulmuştur. "
                "Tıbbi teşhis yerine geçmez. Sağlık sorunları için mutlaka bir doktora başvurunuz.",
                ParagraphStyle("warn", fontSize=8,
                               textColor=colors.HexColor("#B71C1C"),
                               alignment=TA_CENTER)))

            doc.build(story)
            messagebox.showinfo("Başarılı", f"PDF raporu kaydedildi:\n{path}")

            # PDF'i otomatik aç
            os.startfile(path)

        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulurken hata:\n{e}")

    # ── MODEL EĞİT ───────────────────────────────────────────────────────────
    def train_model(self):
        script = os.path.join(BASE_DIR, "train_model.py")
        if not os.path.exists(script):
            messagebox.showerror("Hata", "train_model.py bulunamadı!")
            return

        win = tk.Toplevel(self)
        win.title("Model Eğitimi")
        win.geometry("620x440")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)

        tk.Frame(win, bg=ACCENT, height=4).pack(fill=tk.X)

        tk.Label(win, text="⚙️  Model Eğitimi",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_MAIN, fg=ACCENT_GLOW).pack(pady=(18, 4))
        tk.Label(win, text="Lütfen bekleyin — bu işlem birkaç dakika sürebilir",
                 font=("Segoe UI", 9), bg=BG_MAIN, fg=TEXT_MUTED).pack()

        pb = ttk.Progressbar(win, style="Accent.Horizontal.TProgressbar",
                             mode='indeterminate', length=540)
        pb.pack(pady=12, padx=30)
        pb.start(8)

        log_wrap = tk.Frame(win, bg=ENTRY_BG,
                            highlightbackground=BORDER, highlightthickness=1)
        log_wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        log = tk.Text(log_wrap, bg=ENTRY_BG, fg=SUCCESS,
                      font=("Consolas", 8), relief="flat",
                      state="disabled", wrap="word")
        lsb = ttk.Scrollbar(log_wrap, command=log.yview,
                            style="Slim.Vertical.TScrollbar")
        log.configure(yscrollcommand=lsb.set)
        lsb.pack(side=tk.RIGHT, fill=tk.Y)
        log.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        def append(msg):
            log.configure(state="normal")
            log.insert(tk.END, msg + "\n")
            log.see(tk.END)
            log.configure(state="disabled")

        def run():
            try:
                proc = subprocess.Popen(
                    [sys.executable, script],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding='utf-8', errors='replace')
                for line in proc.stdout:
                    win.after(0, append, line.rstrip())
                proc.wait()
                if proc.returncode == 0:
                    win.after(0, pb.stop)
                    win.after(0, append, "\n✅ Eğitim tamamlandı!")
                    self.model, self.scaler, self.model_info = load_model()
                    win.after(0, lambda: messagebox.showinfo(
                        "Başarılı", "Model eğitimi tamamlandı!", parent=win))
                    win.after(500, lambda: (win.destroy(), self.destroy(),
                                            os.execl(sys.executable, sys.executable, *sys.argv)))
                else:
                    win.after(0, pb.stop)
                    win.after(0, append, "\n❌ Hata oluştu!")
            except Exception as e:
                win.after(0, append, f"\n❌ {e}")
                win.after(0, pb.stop)

        threading.Thread(target=run, daemon=True).start()


# ─── BAŞLAT ──────────────────────────────────────────────────────────────────
def _init_theme():
    global _CURRENT_THEME
    _CURRENT_THEME = os.environ.get("DIABETES_APP_THEME", "dark")
    _refresh_globals()

if __name__ == "__main__":
    _init_theme()
    app = DiabetesApp()
    app._theme = _CURRENT_THEME
    app.mainloop()