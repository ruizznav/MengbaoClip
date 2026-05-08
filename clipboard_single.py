"""
萌宝剪贴板 v3 - QQ风格
"""

import sys, os, json, ctypes, traceback, math
from datetime import datetime
# 可选 OCR 依赖（懒加载，不影响主程序）
_HAS_OCR=False
def _check_ocr():
    global _HAS_OCR
    if _HAS_OCR:return True
    try:
        import pytesseract
        from PIL import Image as PILImage
        # 自动查找 Tesseract 路径
        _TESS_PATHS=[
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for p in _TESS_PATHS:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd=p
                _HAS_OCR=True;return True
        import shutil
        if shutil.which("tesseract"):
            _HAS_OCR=True;return True
        return False
    except:
        return False
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QSystemTrayIcon, QMenu, QMessageBox, QFileDialog,
    QDialog, QDialogButtonBox, QTextEdit, QFrame, QSplitter,
    QInputDialog, QButtonGroup, QRadioButton, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QSize, QEvent
from PyQt6.QtGui import QFont, QIcon, QPixmap

# 图标路径
_APP_ICON=os.path.join(os.path.dirname(os.path.abspath(__file__)),"icon_r.png")
if not os.path.exists(_APP_ICON):
    # 自动生成图标
    try:
        from PIL import Image, ImageDraw
        size=256;img=Image.new('RGBA',(size,size),(0,0,0,0));draw=ImageDraw.Draw(img)
        draw.rounded_rectangle([6,6,250,250],radius=50,fill='#fff5f7',outline='#f0a0b8',width=8)
        draw.ellipse([38,38,218,218],fill='#fce4ec',outline='#e8a0c0',width=3)
        # 手绘 R
        draw.rectangle([100,68,112,178],fill='#d87090')
        draw.arc([100,68,160,128],180,0,fill='#d87090',width=12)
        draw.polygon([108,115,112,115,152,175,142,178],fill='#d87090')
        # 四角小星星
        def _star(d,cx,cy,r,clr):
            pts=[]
            for i in range(10):
                a=math.pi*i/5-math.pi/2;rr=r if i%2==0 else r*0.4
                pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
            draw.polygon(pts,fill=clr)
        _star(draw,48,48,14,'#f5c0d0');_star(draw,208,48,10,'#f5c0d0')
        _star(draw,218,205,8,'#f5c0d0');_star(draw,50,215,12,'#f5c0d0')
        img.save(_APP_ICON,"PNG")
    except:
        pass
if not os.path.exists(_APP_ICON):
    _APP_ICON=os.path.expanduser("~/Desktop/logo.jpg")
if not os.path.exists(_APP_ICON):_APP_ICON=""

THEMES = {
    "经典粉": {
        "bg": "#fef7f7", "side": "#fdf0f4", "card": "#ffffff",
        "border": "#f0d4dc", "text": "#5c3d4a", "accent": "#d87090",
        "accent2": "#f5a0b8", "hover": "#fce4ec", "select": "#f5d0d8",
        "title_bg": "#fff0f3", "scroll": "#f0d4dc",
        "header_bg": "#fff0f3", "glass": "#ffffff",
    },
    "奶蓝": {
        "bg": "#f0f5fe", "side": "#e8f0fd", "card": "#ffffff",
        "border": "#c8d8f0", "text": "#3a4a6a", "accent": "#6a8fc0", "accent2": "#8ab0e0",
        "hover": "#dce8f8", "select": "#c8ddf5",
        "title_bg": "#eef4fc", "scroll": "#c8d8f0",
        "header_bg": "#eef4fc", "glass": "#ffffff",
    },
    "暖橙": {
        "bg": "#fef5ed", "side": "#fdf0e4", "card": "#ffffff",
        "border": "#f0d8c0", "text": "#5a4a3a", "accent": "#d09060", "accent2": "#e8b080",
        "hover": "#fce8d8", "select": "#f5ddc8",
        "title_bg": "#fff0e4", "scroll": "#f0d8c0",
        "header_bg": "#fff0e4", "glass": "#ffffff",
    },
    "浅绿清新": {
        "bg": "rgba(240, 250, 240, 0.88)", "side": "rgba(235, 248, 235, 0.92)",
        "card": "rgba(255, 255, 255, 0.7)", "border": "rgba(180, 220, 180, 0.6)",
        "text": "#3a5a3a", "accent": "#5a9a5a", "accent2": "#7ab87a",
        "hover": "rgba(220, 240, 220, 0.8)", "select": "rgba(200, 230, 200, 0.8)",
        "title_bg": "rgba(235, 248, 235, 0.95)",
        "scroll": "rgba(180, 220, 180, 0.5)",
        "header_bg": "rgba(235, 248, 235, 0.9)",
        "glass": "rgba(255, 255, 255, 0.3)",
    },
    "梦幻紫": {
        "bg": "rgba(245, 235, 250, 0.88)", "side": "rgba(240, 228, 248, 0.92)",
        "card": "rgba(255, 255, 255, 0.7)", "border": "rgba(210, 180, 230, 0.6)",
        "text": "#4a305a", "accent": "#9b6db5", "accent2": "#b88dd0",
        "hover": "rgba(235, 220, 245, 0.8)", "select": "rgba(225, 205, 240, 0.8)",
        "title_bg": "rgba(240, 228, 248, 0.95)",
        "scroll": "rgba(210, 180, 230, 0.5)",
        "header_bg": "rgba(240, 228, 248, 0.9)",
        "glass": "rgba(255, 255, 255, 0.3)",
    },
}

def make_style(t):
    c = THEMES.get(t, THEMES["经典粉"])
    return ("QMainWindow,QDialog,QMenu{background-color:"+c['bg']+";border-radius:12px;}"
        "QLabel{color:"+c['text']+";font-size:13px;}"
        "QLineEdit{background-color:"+c['glass']+";border:2px solid "+c['border']+";border-radius:8px;padding:7px 12px;color:"+c['text']+";font-size:13px;}"
        "QLineEdit:focus{border-color:"+c['accent']+"}"
        "QPushButton{background-color:"+c['accent2']+";color:#fff;border:none;border-radius:6px;padding:6px 12px;font-size:12px;min-width:36px;font-weight:bold;}"
        "QPushButton:hover{background-color:"+c['accent']+"}"
        "QPushButton#danger{background-color:#e88080;}QPushButton#danger:hover{background-color:#d46060;}"
        "QPushButton#fav{background-color:#f0c040;}QPushButton#fav:hover{background-color:#e0b030;}"
        "QPushButton#flat{background-color:transparent;border:2px solid "+c['border']+";color:"+c['accent']+";border-radius:6px;padding:5px 10px;min-width:30px;font-weight:normal;font-size:11px;}"
        "QPushButton#flat:hover{background-color:"+c['hover']+";border-color:"+c['accent']+"}"
        "QPushButton#add{background-color:transparent;border:2px dashed "+c['border']+";color:"+c['accent']+";border-radius:6px;padding:8px;font-size:13px;}"
        "QPushButton#add:hover{background-color:"+c['hover']+";border-color:"+c['accent']+"}"
        "QListWidget{background-color:"+c['card']+";border:none;color:"+c['text']+";font-size:13px;outline:none;}"
        "QListWidget::item{padding:10px 16px;border-bottom:1px solid "+c['border']+";min-height:32px;}"
        "QListWidget::item:hover{background-color:"+c['hover']+"}"
        "QListWidget::item:selected{background-color:"+c['select']+";color:"+c['accent']+";font-weight:bold;}"
        "QListWidget#sidebar{background-color:"+c['side']+";border:none;font-size:13px;}"
        "QListWidget#sidebar::item{padding:12px 16px;border-bottom:1px solid "+c['border']+";min-height:36px;}"
        "QListWidget#sidebar::item:hover{background-color:"+c['hover']+"}"
        "QListWidget#sidebar::item:selected{background-color:"+c['select']+";color:"+c['accent']+";border-left:3px solid "+c['accent']+"}"
        "QFrame#titlebar{background-color:"+c['title_bg']+";border-bottom:2px solid "+c['border']+";border-top-left-radius:12px;border-top-right-radius:12px;}"
        "QFrame#header{background-color:"+c['header_bg']+";border-bottom:2px solid "+c['border']+"}"
        "QFrame#sbar{background-color:"+c['header_bg']+";border-top:2px solid "+c['border']+"}"
        "QTextEdit{background-color:"+c['glass']+";color:"+c['text']+";border:2px solid "+c['border']+";border-radius:8px;padding:8px;}"
        "QScrollBar:vertical{background:transparent;width:5px;}"
        "QScrollBar::handle:vertical{background:"+c['scroll']+";border-radius:3px;min-height:20px;}"
        "QScrollBar::handle:vertical:hover{background:"+c['accent']+"}"
        "QMenu{background-color:"+c['side']+";border:2px solid "+c['border']+";border-radius:10px;color:"+c['text']+";padding:4px;}"
        "QMenu::item{padding:8px 28px 8px 12px;border-radius:4px;margin:2px;}"
        "QMenu::item:selected{background-color:"+c['hover']+";color:"+c['accent']+"}"
        "QMenu::separator{height:1px;background:"+c['border']+";margin:4px 8px;}"
        "QRadioButton{color:"+c['text']+";font-size:13px;spacing:8px;}")

def _get_base_dir():
    return os.path.dirname(sys.executable) if getattr(sys,'frozen',False) else os.path.dirname(os.path.abspath(__file__))
def _settings_path():
    return os.path.join(_get_base_dir(),"data","settings.json")
def load_settings():
    p=_settings_path()
    if os.path.exists(p):
        try:
            s=json.load(open(p,"r"))
            if s.get("theme") not in THEMES:s["theme"]="经典粉"
            return s
        except:pass
    return{"theme":"经典粉"}
def save_settings(s):
    d=os.path.dirname(_settings_path());os.makedirs(d,exist_ok=True);open(_settings_path(),"w").write(json.dumps(s,indent=2))
def _get_data_dir():
    s=load_settings();cp=s.get("custom_path","")
    return cp if cp and os.path.isdir(cp) else r"D:\Installation path\MengbaoClip"
DATA_DIR=os.path.join(_get_data_dir(),"data");DATA_FILE=os.path.join(DATA_DIR,"clipboard.json");BACKUP_DIR=os.path.join(DATA_DIR,"backups");SETTINGS_FILE=os.path.join(DATA_DIR,"settings.json");IMG_DIR=os.path.join(DATA_DIR,"images")
def _ensure_dirs():os.makedirs(DATA_DIR,exist_ok=True);os.makedirs(BACKUP_DIR,exist_ok=True);os.makedirs(IMG_DIR,exist_ok=True)
def _load():
    _ensure_dirs()
    if not os.path.exists(DATA_FILE):return{"categories":[],"items":[]}
    try:
        with open(DATA_FILE,"r",encoding="utf-8")as f:d=json.load(f)
        if isinstance(d,list):d={"categories":[],"items":d}
        d.setdefault("categories",[]);d.setdefault("items",[]);return d
    except:return{"categories":[],"items":[]}
def _save(d):_ensure_dirs();open(DATA_FILE,"w",encoding="utf-8").write(json.dumps(d,ensure_ascii=False,indent=2))
def init_database():
    d=_load()
    if not d["categories"]:d["categories"]=[{"id":1,"name":"全部","icon":"📋"},{"id":2,"name":"工作","icon":"💼"},{"id":3,"name":"日常","icon":"🏠"}]
    # 确保回收站分类存在（id=-1）
    has_trash=any(c["id"]==-1 for c in d["categories"])
    if not has_trash:d["categories"].append({"id":-1,"name":"回收站","icon":"🗑️"})
    for it in d["items"]:it.setdefault("category",1);it.setdefault("note","");it.setdefault("type","text");it.setdefault("img_path","");it.setdefault("html","");it.setdefault("deleted",0)
    _save(d)
def get_categories():return _load()["categories"]
def add_category(n,ic="📂"):
    d=_load();c=d["categories"];nid=max((x["id"]for x in c),default=0)+1;c.append({"id":nid,"name":n,"icon":ic});_save(d);return nid
def rename_category(cid,n):
    d=_load()
    for c in d["categories"]:
        if c["id"]==cid:c["name"]=n;break
    _save(d)
def delete_category(cid):
    d=_load();d["categories"]=[c for c in d["categories"]if c["id"]!=cid]
    for it in d["items"]:
        if it.get("category")==cid:it["category"]=1
    _save(d)
def reorder_categories(o):
    d=_load();idx={cid:i for i,cid in enumerate(o)};d["categories"].sort(key=lambda c:idx.get(c["id"],999));_save(d)
def add_item(content,cat=1,html=""):
    if not content or not content.strip():return None
    d=_load()
    for it in d["items"]:
        if it["content"]==content:it["updated_at"]=datetime.now().isoformat();_save(d);return None
    ai=d["items"];nid=max((x["id"]for x in ai),default=0)+1
    ai.insert(0,{"id":nid,"content":content,"category":cat,"is_favorite":0,"note":"","html":html,"type":"text","created_at":datetime.now().isoformat(),"updated_at":datetime.now().isoformat()});_save(d);return nid
def move_item_category(iid,nc):
    d=_load()
    for it in d["items"]:
        if it["id"]==iid:it["category"]=nc;break
    _save(d)
def move_item_up(iid):
    d=_load();items=sorted(d["items"],key=lambda x:x["updated_at"],reverse=True);idx=next((i for i,it in enumerate(items)if it["id"]==iid),None)
    if idx and idx>0:items[idx]["updated_at"],items[idx-1]["updated_at"]=items[idx-1]["updated_at"],items[idx]["updated_at"];_save(d);return True
    return False
def move_item_down(iid):
    d=_load();items=sorted(d["items"],key=lambda x:x["updated_at"],reverse=True);idx=next((i for i,it in enumerate(items)if it["id"]==iid),None)
    if idx is not None and idx<len(items)-1:items[idx]["updated_at"],items[idx+1]["updated_at"]=items[idx+1]["updated_at"],items[idx]["updated_at"];_save(d);return True
    return False
def set_item_note(iid,note):
    d=_load()
    for it in d["items"]:
        if it["id"]==iid:
            if note:it["note"]=note
            else:it.pop("note",None);break
    _save(d)
def toggle_favorite(iid):
    d=_load()
    for it in d["items"]:
        if it["id"]==iid:it["is_favorite"]=1-it["is_favorite"];_save(d);return bool(it["is_favorite"])
    return False
def delete_item(iid):
    d=_load()
    for it in d["items"]:
        if it["id"]==iid:it["deleted"]=1;it["category"]=-1;break
    _save(d)
def restore_item(iid):
    d=_load()
    for it in d["items"]:
        if it["id"]==iid:it["deleted"]=0;it["category"]=1;break
    _save(d)
def empty_trash():
    d=_load();d["items"]=[it for it in d["items"]if not it.get("deleted")];_save(d)
def clear_all():d=_load();d["items"]=[];_save(d)
def get_items(cat=None,kw=None,fav=False,typ=None,sort="time",limit=500):
    d=_load();items=d["items"]
    if cat==-1:items=[it for it in items if it.get("deleted")]
    else:items=[it for it in items if not it.get("deleted")]
    if cat and cat>1:items=[it for it in items if it.get("category")==cat]
    if fav:items=[it for it in items if it["is_favorite"]]
    if typ:items=[it for it in items if it.get("type")==typ]
    if kw:items=[it for it in items if kw.lower()in it["content"].lower()]
    if sort=="time":items.sort(key=lambda x:x["updated_at"],reverse=True)
    elif sort=="alpha":items.sort(key=lambda x:x["content"].lower())
    return items[:limit]
def get_statistics():d=_load();items=d["items"];return{"total":len(items),"favorites":sum(1 for it in items if it["is_favorite"]),"last_content":(items[0]["content"][:100]if items else"无")}
def export_backup():
    _ensure_dirs();ts=datetime.now().strftime("%Y%m%d_%H%M%S");p=os.path.join(BACKUP_DIR,f"clipboard_backup_{ts}.json")
    open(p,"w",encoding="utf-8").write(json.dumps(_load(),ensure_ascii=False,indent=2));return p
def import_backup(fp):
    imp=json.load(open(fp,"r",encoding="utf-8"));d=_load();exist={it["content"]:it for it in d["items"]};added=0;max_id=max((it["id"]for it in d["items"]),default=0)
    for item in imp.get("items",[]):
        c=item.get("content","")
        if c and c.strip()and c not in exist:
            max_id+=1;exist[c]={"id":max_id,"content":c,"html":item.get("html",""),"category":item.get("category",1),"is_favorite":item.get("is_favorite",0),"note":item.get("note",""),"created_at":item.get("created_at",datetime.now().isoformat()),"updated_at":item.get("updated_at",datetime.now().isoformat())};added+=1
    if added:
        ecat={c["id"]for c in d["categories"]}
        for c in imp.get("categories",[]):
            if c["id"]not in ecat:d["categories"].append(c)
        d["items"]=list(exist.values());_save(d)
    return added
def list_backups():
    _ensure_dirs();bs=[]
    if os.path.exists(BACKUP_DIR):
        for f in sorted(os.listdir(BACKUP_DIR),reverse=True):
            if f.endswith(".json"):p=os.path.join(BACKUP_DIR,f);bs.append({"name":f,"path":p,"size":f"{os.path.getsize(p)/1024:.1f}KB"})
    return bs

def _confirm(parent,title,msg):
    d=QDialog(parent,Qt.WindowType.FramelessWindowHint);d.setStyleSheet(parent.styleSheet()if parent else"")
    d.setFixedSize(340,160);lo=QVBoxLayout(d);lo.setContentsMargins(0,0,0,0);lo.setSpacing(0)
    # 主题色
    if parent and hasattr(parent,'_theme'):c=THEMES.get(parent._theme,THEMES["经典粉"])
    else:c=THEMES["经典粉"]
    # 自定义标题栏
    tb=QFrame();tb.setObjectName("titlebar");tlo=QHBoxLayout(tb);tlo.setContentsMargins(12,6,8,6)
    tl=QLabel(title);tl.setStyleSheet("font-size:12px;font-weight:bold;color:"+c['accent'])
    tlo.addWidget(tl);tlo.addStretch()
    cb=QPushButton("X");cb.setFixedSize(28,22)
    cb.setStyleSheet("QPushButton{background:transparent;color:#888;border:none;border-radius:4px;font-size:12px;}QPushButton:hover{background:#e88080;color:#fff;}")
    cb.clicked.connect(d.reject);tlo.addWidget(cb);lo.addWidget(tb)
    # 消息内容区
    ml=QVBoxLayout();ml.setContentsMargins(20,16,20,12);ml.setSpacing(0)
    mlb=QLabel(msg);mlb.setAlignment(Qt.AlignmentFlag.AlignCenter);mlb.setWordWrap(True)
    mlb.setStyleSheet("font-size:13px;color:"+c['text'])
    ml.addWidget(mlb);ml.addStretch();lo.addLayout(ml,1)
    # 按钮区
    bb=QHBoxLayout();bb.setContentsMargins(20,4,20,12);bb.setSpacing(10)
    bb.addStretch()
    yes=QPushButton("确定");yes.setFixedSize(80,28)
    yes.setStyleSheet("QPushButton{background:"+c['accent2']+";color:#fff;border:none;border-radius:6px;font-size:12px;font-weight:bold;}QPushButton:hover{background:"+c['accent']+"}")
    yes.clicked.connect(d.accept)
    no=QPushButton("取消");no.setFixedSize(80,28)
    no.setStyleSheet("QPushButton{background:"+c['glass']+";border:2px solid "+c['border']+";color:"+c['text']+";border-radius:6px;font-size:12px;}QPushButton:hover{background:"+c['hover']+";border-color:"+c['accent']+"}")
    no.clicked.connect(d.reject)
    bb.addWidget(yes);bb.addWidget(no);lo.addLayout(bb)
    # 居中显示在父窗口上
    if parent:
        try:
            g=parent.geometry()
            x=g.center().x()-170;y=g.center().y()-80
            d.move(x,y)
        except:d.move(200,200)
    return d.exec()==QDialog.DialogCode.Accepted

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cur_cat=1;self._sort_mode="time";self._type_filter=None
        self._clip=QApplication.clipboard();self._last="";self._copying=False
        self._theme=load_settings().get("theme","经典粉")
        if self._theme not in THEMES:self._theme="经典粉"
        self._setup_ui();self._reload_sidebar();self._load_items()
        self._clip.dataChanged.connect(self._on_copy)
        self._hk_pressed=False;self._hk_show=self._load_hotkey()
        self._hk_timer=QTimer();self._hk_timer.timeout.connect(self._check_hotkey);self._hk_timer.start(100)
    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowMinimizeButtonHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,False)
        self.setWindowTitle("萌宝剪贴板");self.setGeometry(100,100,760,560);self.setMinimumSize(560,400)
        if _APP_ICON:self.setWindowIcon(QIcon(_APP_ICON))
        self._apply_theme();self._center()
        c=QWidget();self.setCentralWidget(c);lo=QVBoxLayout(c);lo.setContentsMargins(0,0,0,0);lo.setSpacing(0)
        tb=QFrame();tb.setObjectName("titlebar");tlo=QHBoxLayout(tb);tlo.setContentsMargins(12,6,8,6)
        self._drag_label=QLabel("萌宝剪贴板 v3");self._drag_label.setStyleSheet("font-size:13px;font-weight:bold;color:"+THEMES[self._theme]['accent'])
        tlo.addWidget(self._drag_label);tlo.addStretch()
        hb=QPushButton("-");hb.setFixedSize(32,24);hb.setStyleSheet("QPushButton{background:transparent;color:#888;border:none;border-radius:4px;font-size:14px;}QPushButton:hover{background:#f0d4dc;}")
        hb.clicked.connect(self.showMinimized);tlo.addWidget(hb)
        cb=QPushButton("X");cb.setFixedSize(32,24);cb.setStyleSheet("QPushButton{background:transparent;color:#888;border:none;border-radius:4px;font-size:14px;}QPushButton:hover{background:#e88080;color:#fff;}")
        cb.clicked.connect(lambda:self.hide());tlo.addWidget(cb);lo.addWidget(tb)
        body=QWidget();blo=QHBoxLayout(body);blo.setContentsMargins(0,0,0,0);blo.setSpacing(0)
        lp=QFrame();lp.setFixedWidth(150);ll=QVBoxLayout(lp);ll.setContentsMargins(0,0,0,6);ll.setSpacing(0)
        st=QLabel("分类");st.setStyleSheet("font-size:13px;font-weight:bold;padding:10px 12px 6px;color:"+THEMES[self._theme]['accent'])
        ll.addWidget(st)
        self._st=st
        self._cl=QListWidget();self._cl.setObjectName("sidebar");self._cl.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._cl.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._cl.setDropIndicatorShown(True)
        self._cl.itemClicked.connect(self._on_cat_click)
        self._cl.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._cl.customContextMenuRequested.connect(self._cat_menu)
        self._cl.model().rowsMoved.connect(self._on_cat_reorder)
        ll.addWidget(self._cl,1)
        ab=QPushButton("+ 添加分类");ab.setObjectName("add");ab.clicked.connect(self._add_cat_dialog);ll.addWidget(ab)
        # 回收站（独立于分类列表）
        sep=QFrame();sep.setFrameShape(QFrame.Shape.HLine);sep.setStyleSheet("color:"+THEMES[self._theme]['border']+";margin:4px 10px;");ll.addWidget(sep)
        self._trash_btn=QPushButton("🗑️ 回收站");self._trash_btn.setObjectName("flat")
        self._trash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._trash_btn.setStyleSheet("QPushButton#flat{text-align:left;padding:8px 12px;font-size:12px;border:none;border-radius:0;background:transparent;color:"+THEMES[self._theme]['accent']+";}"
            "QPushButton#flat:hover{background:"+THEMES[self._theme]['hover']+"}")
        self._trash_btn.clicked.connect(self._show_trash);ll.addWidget(self._trash_btn)
        blo.addWidget(lp)
        rp=QWidget();rl=QVBoxLayout(rp);rl.setContentsMargins(0,0,0,0);rl.setSpacing(0)
        h=QFrame();h.setObjectName("header");hl=QHBoxLayout(h);hl.setContentsMargins(10,7,10,7);hl.setSpacing(5)
        self._ct=QLabel("全部");self._ct.setStyleSheet("font-size:13px;font-weight:bold;color:"+THEMES[self._theme]['accent']);hl.addWidget(self._ct)
        self.s=QLineEdit();self.s.setPlaceholderText("搜索");self.s.setMaximumHeight(30);self.s.textChanged.connect(self._search);hl.addWidget(self.s,1)
        sd=QPushButton("排序");sd.setObjectName("flat");sd.setMaximumHeight(26);sd.clicked.connect(self._toggle_sort);hl.addWidget(sd)
        bk=QPushButton("备份");bk.setObjectName("flat");bk.setMaximumHeight(26);bk.clicked.connect(self._backup_dlg);hl.addWidget(bk)
        sg=QPushButton("设置");sg.setObjectName("flat");sg.setMaximumHeight(26);sg.clicked.connect(self._show_settings);hl.addWidget(sg);rl.addWidget(h)
        # 类型筛选条
        tf=QFrame();tf.setObjectName("header");tfl=QHBoxLayout(tf);tfl.setContentsMargins(10,4,10,6);tfl.setSpacing(4)
        self._tf_all=QPushButton("全部");self._tf_all.setObjectName("flat");self._tf_all.setMaximumHeight(22)
        self._tf_all.setStyleSheet("QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:"+THEMES[self._theme]['accent']+";color:#fff;border:none;}QPushButton#flat:hover{opacity:0.8;}")
        self._tf_all.clicked.connect(lambda:self._set_type_filter(None))
        self._tf_text=QPushButton("文本");self._tf_text.setObjectName("flat");self._tf_text.setMaximumHeight(22)
        self._tf_text.setStyleSheet("QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:transparent;color:"+THEMES[self._theme]['accent']+";border:1px solid "+THEMES[self._theme]['border']+"}QPushButton#flat:hover{background:"+THEMES[self._theme]['hover']+"}")
        self._tf_text.clicked.connect(lambda:self._set_type_filter("text"))
        self._tf_img=QPushButton("图片");self._tf_img.setObjectName("flat");self._tf_img.setMaximumHeight(22)
        self._tf_img.setStyleSheet("QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:transparent;color:"+THEMES[self._theme]['accent']+";border:1px solid "+THEMES[self._theme]['border']+"}QPushButton#flat:hover{background:"+THEMES[self._theme]['hover']+"}")
        self._tf_img.clicked.connect(lambda:self._set_type_filter("image"))
        tfl.addWidget(self._tf_all);tfl.addWidget(self._tf_text);tfl.addWidget(self._tf_img);tfl.addStretch()
        rl.addWidget(tf)
        self.l=QListWidget();self.l.setWordWrap(True);self.l.setSpacing(1)
        self.l.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.l.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.l.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.l.setDropIndicatorShown(True)
        self.l.model().rowsMoved.connect(self._on_item_reorder)
        self.l.itemDoubleClicked.connect(self._copy_item)
        self.l.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.l.customContextMenuRequested.connect(self._ctx_menu);rl.addWidget(self.l,1)
        sb=QFrame();sb.setObjectName("sbar");sl=QHBoxLayout(sb);sl.setContentsMargins(8,4,8,4);sl.setSpacing(3)
        self.st=QLabel("就绪");self.st.setStyleSheet("font-size:11px;color:"+THEMES[self._theme]['accent']);sl.addWidget(self.st);sl.addStretch()
        def mkb(t,o,f):b=QPushButton(t);b.setObjectName(o);b.setMaximumHeight(24);f(b);sl.addWidget(b)
        mkb("星标","fav",lambda b:b.clicked.connect(self._fav))
        self._pb=QPushButton("屏幕置顶");self._pb.setObjectName("flat");self._pb.setMaximumHeight(24);self._pb.clicked.connect(self._toggle_pin);sl.addWidget(self._pb)
        self._ab=QPushButton("开机自启");self._ab.setObjectName("flat");self._ab.setMaximumHeight(24);self._ab.clicked.connect(self._toggle_autostart);sl.addWidget(self._ab)
        rl.addWidget(sb);blo.addWidget(rp,1);lo.addWidget(body,1);self._tray()
    def _center(self):
        sc=QApplication.primaryScreen()
        if sc:g=self.frameGeometry();g.moveCenter(sc.availableGeometry().center());self.move(g.topLeft())
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton and e.position().y()<36:self._drag_pos=e.globalPosition().toPoint()
        super().mousePressEvent(e)
    def changeEvent(self,e):
        if e.type()==QEvent.Type.WindowStateChange:
            if self.windowState()&Qt.WindowState.WindowMinimized:
                # 最小化到任务栏，不隐藏
                self.showMinimized()
            elif self.windowState()==Qt.WindowState.WindowNoState:
                # 从任务栏恢复时正常显示
                self.show();self.raise_();self.activateWindow()
        super().changeEvent(e)
    def mouseMoveEvent(self,e):
        if self._drag_pos and e.buttons()==Qt.MouseButton.LeftButton:self.move(self.pos()+e.globalPosition().toPoint()-self._drag_pos);self._drag_pos=e.globalPosition().toPoint()
    def mouseReleaseEvent(self,e):self._drag_pos=None;super().mouseReleaseEvent(e)
    def _apply_theme(self):self.setStyleSheet(make_style(self._theme))
    def _mkdlg(self,t,w=440,h=400):
        """创建无框弹窗，带自定义标题栏和拖拽"""
        d=QDialog(self,Qt.WindowType.FramelessWindowHint);d.setStyleSheet(self.styleSheet())
        d.setFixedSize(w,h);lo=QVBoxLayout(d);lo.setContentsMargins(0,0,0,0);lo.setSpacing(0)
        tb=QFrame();tb.setObjectName("titlebar");tlo=QHBoxLayout(tb);tlo.setContentsMargins(10,4,6,4)
        tl=QLabel(t);tl.setStyleSheet("font-size:12px;font-weight:bold;color:"+THEMES[self._theme]['accent'])
        tlo.addWidget(tl);tlo.addStretch()
        cb=QPushButton("X");cb.setFixedSize(28,22)
        cb.setStyleSheet("QPushButton{background:transparent;color:#888;border:none;border-radius:4px;font-size:12px;}QPushButton:hover{background:#e88080;color:#fff;}")
        cb.clicked.connect(d.reject);tlo.addWidget(cb);lo.addWidget(tb)
        self._dlg_drag=None
        def mp(e):
            if e.button()==Qt.MouseButton.LeftButton:self._dlg_drag=e.globalPosition().toPoint()
        def mm(e):
            if self._dlg_drag:d.move(d.pos()+e.globalPosition().toPoint()-self._dlg_drag);self._dlg_drag=e.globalPosition().toPoint()
        def mr(e):self._dlg_drag=None
        tb.mousePressEvent=mp;tb.mouseMoveEvent=mm;tb.mouseReleaseEvent=mr
        # 用 geometry() 居中——和备份版一样的方法
        g=self.geometry();d.move(g.center().x()-w//2,g.center().y()-h//2)
        return d,lo
    def _center_dlg(self,d):
        """居中对话框"""
        g=self.geometry();d.move(g.center().x()-d.width()//2,g.center().y()-d.height()//2)
    def _input_dlg(self,title,label,default=""):
        """自定义输入弹窗（替代 QInputDialog）"""
        d,lo=self._mkdlg(title,400,160)
        lo.setContentsMargins(20,16,20,16);lo.setSpacing(12)
        lo.addWidget(QLabel(label))
        ed=QLineEdit(default);ed.setMinimumHeight(32)
        ed.setStyleSheet("font-size:14px;padding:4px 8px;")
        ed.returnPressed.connect(d.accept)
        lo.addWidget(ed)
        bl=QHBoxLayout();bl.addStretch()
        okb=QPushButton("确定");okb.clicked.connect(d.accept)
        cb=QPushButton("取消");cb.clicked.connect(d.reject)
        bl.addWidget(okb);bl.addWidget(cb);lo.addLayout(bl)
        return (ed.text().strip(),True) if d.exec()==QDialog.DialogCode.Accepted else ("",False)
    def _reload_sidebar(self):
        self._cl.blockSignals(True);self._cl.clear()
        for c in get_categories():
            if c["id"]!=-1:
                it=QListWidgetItem(c['name']);it.setData(Qt.ItemDataRole.UserRole,c["id"]);it.setData(Qt.ItemDataRole.UserRole+1,c["name"]);self._cl.addItem(it)
        for i in range(self._cl.count()):
            if self._cl.item(i).data(Qt.ItemDataRole.UserRole)==self._cur_cat:self._cl.setCurrentRow(i);break
        # 如果当前选中的是回收站，高亮清除
        if self._cur_cat==-1:self._cl.clearSelection()
        self._cl.blockSignals(False)
    def _on_cat_click(self,it):
        self._cur_cat=it.data(Qt.ItemDataRole.UserRole)
        self._ct.setText(it.data(Qt.ItemDataRole.UserRole+1));self.s.clear()
        self._reset_type_filter();self._load_items()
        # 取消回收站按钮高亮
        self._trash_btn.setStyleSheet("QPushButton#flat{text-align:left;padding:8px 12px;font-size:12px;border:none;border-radius:0;background:transparent;color:"+THEMES[self._theme]['accent']+";}"
            "QPushButton#flat:hover{background:"+THEMES[self._theme]['hover']+"}")
    def _on_cat_reorder(self):
        ids=[self._cl.item(i).data(Qt.ItemDataRole.UserRole)for i in range(self._cl.count())];reorder_categories(ids)
    def _on_item_reorder(self):
        """条目拖拽排序后保存新顺序"""
        ids=[self.l.item(i).data(Qt.ItemDataRole.UserRole)for i in range(self.l.count())]
        # Swap updated_at to match new order
        d=_load();items={it["id"]:it for it in d["items"]}
        for pos,iid in enumerate(ids):
            if iid in items:
                # Set timestamp based on position (newest at top)
                from datetime import timedelta
                items[iid]["updated_at"]=(datetime.now()-timedelta(seconds=pos)).isoformat()
        _save(d)
    def _cat_menu(self,pos):
        it=self._cl.itemAt(pos)
        if not it:return
        cid=it.data(Qt.ItemDataRole.UserRole)
        if cid==1:
            m=QMenu();m.addAction("清空全部",self._clear_all);m.exec(self._cl.mapToGlobal(pos));return
        m=QMenu()
        m.addAction("重命名",lambda:self._rename_cat(cid));m.addAction("删除",lambda:self._del_cat(cid));m.exec(self._cl.mapToGlobal(pos))
    def _add_cat_dialog(self):
        n,ok=self._input_dlg("新建分类","名称：")
        if ok and n:add_category(n);self._reload_sidebar()
    def _rename_cat(self,cid):
        n,ok=self._input_dlg("重命名","新名称：")
        if ok and n:rename_category(cid,n);self._reload_sidebar()
    def _del_cat(self,cid):
        if _confirm(self,"确认","删除分类？条目移到全部"):
            delete_category(cid);self._cur_cat=1;self._reload_sidebar();self._ct.setText("全部");self._load_items()
    def _set_type_filter(self,typ):
        self._type_filter=typ
        # 更新按钮样式
        c=THEMES[self._theme]
        active="QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:"+c['accent']+";color:#fff;border:none;}"
        inactive="QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:transparent;color:"+c['accent']+";border:1px solid "+c['border']+"}QPushButton#flat:hover{background:"+c['hover']+"}"
        self._tf_all.setStyleSheet(active if typ is None else inactive)
        self._tf_text.setStyleSheet(active if typ=="text" else inactive)
        self._tf_img.setStyleSheet(active if typ=="image" else inactive)
        self._load_items()
    def _reset_type_filter(self):
        self._type_filter=None
        c=THEMES[self._theme]
        inactive="QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:transparent;color:"+c['accent']+";border:1px solid "+c['border']+"}QPushButton#flat:hover{background:"+c['hover']+"}"
        self._tf_all.setStyleSheet("QPushButton#flat{padding:2px 10px;font-size:11px;border-radius:10px;background:"+c['accent']+";color:#fff;border:none;}")
        self._tf_text.setStyleSheet(inactive)
        self._tf_img.setStyleSheet(inactive)
    def _load_items(self):
        self.l.clear()
        self.l.setIconSize(QSize(120,120))
        for it in get_items(cat=self._cur_cat,typ=self._type_filter,sort=self._sort_mode):self._add_row(it)
        if self.l.count():self._last=self.l.item(0).data(Qt.ItemDataRole.UserRole+4)or""
        self.st.setText(f"共{self.l.count()}条")
    def _add_row(self,it):
        c=it["content"];note=it.get("note","");img=it.get("img_path","");typ=it.get("type","text");html=it.get("html","")
        # 格式化时间
        ts=it.get("updated_at","") or it.get("created_at","")
        t_str=""
        if ts:
            try:
                dt=datetime.fromisoformat(ts)
                t_str=dt.strftime("%m/%d %H:%M")
            except:t_str=""
        p="⭐"if it["is_favorite"]else""
        # 有备注时显示 图标+备注，不显示原内容
        if note:
            icon="📷"if typ=="image"else"📄"
            item=QListWidgetItem(f"{p}{icon}{note}  {t_str}")
        elif typ=="image"and img:
            # 创建缩略图
            try:
                from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter, QFont as QF
                px=QPixmap(img)
                if not px.isNull():
                    thumb=px.scaled(120,120,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
                    if p:
                        painter=QPainter(thumb)
                        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                        painter.setPen(QColor("#f0c040"))
                        painter.setFont(QF("Microsoft YaHei",16))
                        painter.drawText(thumb.rect(),Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,"⭐")
                        painter.end()
                    item=QListWidgetItem(QIcon(thumb),t_str)
                    item.setSizeHint(QSize(thumb.width()+10,thumb.height()+30))
                else:
                    item=QListWidgetItem(f"{p}🖼️")
            except:
                item=QListWidgetItem(f"{p}🖼️")
        elif note:
            d=f"📝{note}"
            item=QListWidgetItem(f"{p}{d}  {t_str}")
        else:
            prefix="📄"if html else""
            d=prefix+(c[:100]if len(c)>120 else c).replace("\n"," ")
            item=QListWidgetItem(f"{p}{d}  {t_str}")
        item.setData(Qt.ItemDataRole.UserRole,it["id"]);item.setData(Qt.ItemDataRole.UserRole+1,it.get("category",1))
        item.setData(Qt.ItemDataRole.UserRole+2,it["is_favorite"]);item.setData(Qt.ItemDataRole.UserRole+3,note);item.setData(Qt.ItemDataRole.UserRole+4,c);item.setData(Qt.ItemDataRole.UserRole+5,img);item.setData(Qt.ItemDataRole.UserRole+6,typ);item.setData(Qt.ItemDataRole.UserRole+7,html)
        self.l.addItem(item)
    def _on_copy(self):
        if self._copying:return
        try:
            mime=self._clip.mimeData()
            # 检测到复制文件/文件夹
            if mime.hasUrls():
                urls=mime.urls()
                # 检查是否为图片文件
                img_exts={".png",".jpg",".jpeg",".gif",".bmp",".webp",".ico",".tiff",".tif"}
                is_all_files=all(os.path.isfile(u.toLocalFile()) for u in urls if u.toLocalFile())
                if is_all_files:
                    # 如果全是图片文件，转成图片处理
                    local_files=[u.toLocalFile() for u in urls if u.toLocalFile()]
                    img_files=[f for f in local_files if os.path.splitext(f)[1].lower() in img_exts]
                    if img_files and len(img_files)==len(local_files):
                        # 全是图片文件，用第一张
                        fp=img_files[0]
                        from PyQt6.QtGui import QPixmap
                        px=QPixmap(fp)
                        if px and not px.isNull():
                            ts=datetime.now().strftime("%Y%m%d_%H%M%S")
                            _ensure_dirs();img_fp=os.path.join(IMG_DIR,f"img_{ts}.png")
                            px.save(img_fp,"PNG")
                            d=_load();ai=d["items"];nid=max((x["id"]for x in ai),default=0)+1
                            target_cat=self._cur_cat if self._cur_cat!=-1 else 1
                            ai.insert(0,{"id":nid,"content":"[图片]","category":target_cat,"is_favorite":0,"note":"","type":"image","img_path":img_fp,"created_at":datetime.now().isoformat(),"updated_at":datetime.now().isoformat()})
                            _save(d);self._load_items();self._set_status("已复制图片");self._last="__image__";return
                    # 非图片文件，跳过不在剪贴板显示
                    return
            # 检查图片
            if mime.hasImage():
                img=mime.imageData()
                if img and not img.isNull():
                    from PyQt6.QtCore import QDateTime
                    ts=QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss")
                    _ensure_dirs();fp=os.path.join(IMG_DIR,f"img_{ts}.png")
                    img.save(fp,"PNG")
                    d=_load();ai=d["items"];nid=max((x["id"]for x in ai),default=0)+1
                    target_cat=self._cur_cat if self._cur_cat!=-1 else 1
                    ai.insert(0,{"id":nid,"content":"[图片]","category":target_cat,"is_favorite":0,"note":"","type":"image","img_path":fp,"created_at":datetime.now().isoformat(),"updated_at":datetime.now().isoformat()})
                    _save(d);self._load_items();self._set_status("已复制图片");self._last="__image__";return
            t=self._clip.text()
            if t and t!=self._last:
                target_cat=self._cur_cat if self._cur_cat!=-1 else 1
                # 检测富文本/HTML
                html=""
                try:
                    m=self._clip.mimeData()
                    if m.hasHtml():html=m.html()
                except:pass
                self._last=t;uid=add_item(t,cat=target_cat,html=html)
                if uid:
                    self._load_items()
                    # 滚动到顶部，让新条目可见
                    if self.l.count():self.l.scrollToTop()
                    self._set_status("已复制")
        except:pass
    def _search(self,t):
        if not t.strip():self._load_items();return
        self.l.clear()
        for it in get_items(cat=self._cur_cat,typ=self._type_filter,kw=t):self._add_row(it)
        self.st.setText(f"找到{self.l.count()}条")
    def _toggle_sort(self):
        self._sort_mode="alpha"if self._sort_mode=="time"else"time"
        s="按字母"if self._sort_mode=="alpha"else"按时间";self._set_status(s);self._load_items()
    def _fav(self):
        cur=self.l.currentItem()
        if not cur:return
        uid=cur.data(Qt.ItemDataRole.UserRole);ok=toggle_favorite(uid)
        cur.setData(Qt.ItemDataRole.UserRole+2,int(ok));t=cur.text()
        if t.startswith("⭐"):t=t[1:]
        cur.setText(("⭐"if ok else"")+t);self._set_status("已星标"if ok else"取消星标")
    def _del(self):
        cur=self.l.currentItem()
        if not cur:return
        if _confirm(self,"删除","确定删除这条记录？"):
            delete_item(cur.data(Qt.ItemDataRole.UserRole));self.l.takeItem(self.l.row(cur));self._set_status("已移到回收站")
    def _copy_item(self,it=None):
        if not it:it=self.l.currentItem()
        if not it:return
        self._copying=True
        try:
            uid=it.data(Qt.ItemDataRole.UserRole)
            d=_load()
            for x in d["items"]:
                if x["id"]!=uid:continue
                c=x.get("content","");html=x.get("html","");typ=x.get("type","text");img=x.get("img_path","")
                if typ=="image"and img and os.path.exists(img):
                    from PyQt6.QtGui import QPixmap
                    QApplication.clipboard().setPixmap(QPixmap(img))
                elif c:
                    if html:
                        md=QMimeData();md.setText(c);md.setHtml(html)
                        QApplication.clipboard().setMimeData(md)
                    else:QApplication.clipboard().setText(c)
                self._set_status("已复制");break
        except Exception as e:self._set_status(f"复制失败:{e}")
        QTimer.singleShot(500,lambda:setattr(self,"_copying",False))
    def _show_trash(self):
        """切换到回收站视图"""
        self._cur_cat=-1;self._ct.setText("回收站");self.s.clear();self._reset_type_filter();self._load_items()
        self._cl.clearSelection()
        self._trash_btn.setStyleSheet("QPushButton#flat{text-align:left;padding:8px 12px;font-size:12px;border:none;border-radius:0;background:"+THEMES[self._theme]['select']+";color:"+THEMES[self._theme]['accent']+"}")
        self._set_status(f"回收站 {self.l.count()}条")
    def _restore_item(self,uid,it):
        restore_item(uid);self.l.takeItem(self.l.row(it));self._set_status("已恢复")
    def _del_permanent(self,uid,it):
        if _confirm(self,"彻底删除","确定彻底删除？不可恢复！"):
            d=_load();d["items"]=[x for x in d["items"]if x["id"]!=uid];_save(d)
            self.l.takeItem(self.l.row(it));self._set_status("已彻底删除")
    def _empty_trash(self):
        if _confirm(self,"清空回收站","确定清空回收站？不可恢复！"):
            empty_trash();self._load_items();self._set_status("回收站已清空")
    def _clear_all(self):
        if _confirm(self,"清空全部","确定清空全部记录？不可恢复！"):
            clear_all();self.l.clear();self._last="";self._set_status("已清空全部")
    def _ctx_menu(self,pos):
        it=self.l.itemAt(pos)
        # 空白处右键
        if not it:
            if self._cur_cat==-1:
                m=QMenu();m.addAction("🗑️清空回收站",self._empty_trash);m.exec(self.l.mapToGlobal(pos))
            elif self._cur_cat==1:
                m=QMenu();m.addAction("清空全部",self._clear_all);m.exec(self.l.mapToGlobal(pos))
            return
        uid=it.data(Qt.ItemDataRole.UserRole);is_fav=bool(it.data(Qt.ItemDataRole.UserRole+2))
        c=it.data(Qt.ItemDataRole.UserRole+4)or"";note=it.data(Qt.ItemDataRole.UserRole+3)or""
        img=it.data(Qt.ItemDataRole.UserRole+5)or"";typ=it.data(Qt.ItemDataRole.UserRole+6)or"text"
        cats=get_categories();m=QMenu()
        # 回收站特殊菜单
        if self._cur_cat==-1:
            m.addAction("♻️恢复",lambda:self._restore_item(uid,it))
            m.addAction("🗑️彻底删除",lambda:self._del_permanent(uid,it))
            m.addSeparator()
            m.addAction("🗑️清空回收站",self._empty_trash)
            m.exec(self.l.mapToGlobal(pos));return
        m.addAction("📋复制",lambda:self._copy_item(it))
        if typ=="image"and img:
            try:
                if _check_ocr():m.addAction("🔍 识别文字",lambda:self._ocr_image(img,None))
            except:pass
        m.addAction("取消星标"if is_fav else"星标",self._fav);m.addSeparator()
        if note:m.addAction("修改备注",lambda:self._edit_note(uid));m.addAction("删备注",lambda:self._del_note(uid,it))
        else:m.addAction("加备注",lambda:self._edit_note(uid))
        m.addSeparator()
        row=self.l.row(it)
        if row>0:m.addAction("上移",lambda:self._move_item_up(uid,row))
        if row<self.l.count()-1:m.addAction("下移",lambda:self._move_item_down(uid,row))
        m.addSeparator();mm=m.addMenu("移动到")
        for cat in cats:
            if cat["id"] not in(1,-1):mm.addAction(cat['name'],lambda cid=cat["id"]:self._move_item(uid,cid))
        m.addSeparator();m.addAction("删除",self._del);m.addSeparator()
        if typ=="image"and img:m.addAction("🖼️查看完整",lambda:self._show_image(img))
        else:m.addAction("📄查看完整",lambda:self._show_full(c))
        m.exec(self.l.mapToGlobal(pos))
        return
    def _show_full(self,c):
        d,lo=self._mkdlg("完整内容",520,300)
        tx=QTextEdit();tx.setPlainText(c);tx.setReadOnly(True);lo.addWidget(tx,1)
        bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);bb.rejected.connect(d.reject);lo.addWidget(bb);d.exec()
    def _show_image(self,img_path):
        if not os.path.exists(img_path):
            QMessageBox.warning(self,"图片","文件不存在: "+img_path);return
        d,lo=self._mkdlg("图片",600,500)
        lo.setContentsMargins(12,4,12,8)
        from PyQt6.QtGui import QPixmap
        p=QPixmap(img_path)
        if p.isNull():
            QMessageBox.warning(self,"图片","无法加载图片");return
        lb=QLabel()
        lb.setPixmap(p.scaled(560,420,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lo.addWidget(lb,1)
        bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);bb.rejected.connect(d.reject);lo.addWidget(bb)
        d.exec()
    def _ocr_image(self,img_path,parent_dlg):
        """使用 OCR 提取图片中的文字"""
        try:
            from PIL import Image as PILImage
            import pytesseract
            img=PILImage.open(img_path)
            text=pytesseract.image_to_string(img,lang='chi_sim+eng')
            if text and text.strip():
                # 显示结果
                rd,lo=self._mkdlg("OCR 识别结果",480,320)
                tx=QTextEdit();tx.setPlainText(text.strip());tx.setReadOnly(True);lo.addWidget(tx,1)
                # 复制按钮
                cbb=QHBoxLayout();cbb.setContentsMargins(12,4,12,8)
                cp_btn=QPushButton("📋 复制结果");cp_btn.setObjectName("flat")
                cp_btn.clicked.connect(lambda:(
                    QApplication.clipboard().setText(text.strip()),
                    self._set_status("已复制 OCR 结果"),
                    rd.close()))
                cbb.addWidget(cp_btn);cbb.addStretch()
                cbb_bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);cbb_bb.rejected.connect(rd.reject);cbb.addWidget(cbb_bb)
                lo.addLayout(cbb);rd.exec()
            else:
                QMessageBox.information(self,"OCR","未识别到文字")
        except Exception as e:
            QMessageBox.warning(self,"OCR 出错",str(e))
    def _move_item(self,iid,nc):
        move_item_category(iid,nc)
        if self._cur_cat!=1 and self._cur_cat!=nc:
            for i in range(self.l.count()):
                if self.l.item(i).data(Qt.ItemDataRole.UserRole)==iid:self.l.takeItem(i);break
        self._set_status("已移动")
    def _move_item_up(self,iid,row):
        if move_item_up(iid):self._load_items()
        if row>0 and row-1<self.l.count():self.l.setCurrentRow(row-1);self._set_status("已上移")
    def _move_item_down(self,iid,row):
        if move_item_down(iid):self._load_items()
        if row+1<self.l.count():self.l.setCurrentRow(row+1);self._set_status("已下移")
    def _edit_note(self,iid):
        n,ok=self._input_dlg("备注","输入备注名（替代原文显示）：")
        if ok:
            set_item_note(iid,n.strip())
            self._load_items()
            self._set_status("备注已保存"if n.strip()else"备注已清除")
    def _del_note(self,iid,w):
        set_item_note(iid,"")
        self._load_items()
        self._set_status("备注已删")
    def closeEvent(self,e):e.ignore();self.hide()
    def _toggle(self):
        if self.isVisible():self.hide()
        else:self.show();self.raise_();self.activateWindow();self._load_items()
    def _tray(self):
        self.tr=QSystemTrayIcon(self)
        self.tr.setIcon(QIcon(_APP_ICON)if _APP_ICON else self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogListView))
        hk_text=self._hk_show["text"]if hasattr(self,'_hk_show')else"Ctrl+Alt+V"
        self.tr.setToolTip(f"萌宝剪贴板\n{hk_text}")
        m=QMenu()
        m.addAction("显示",lambda:(self.show(),self.raise_(),self.activateWindow(),self._load_items()))
        m.addSeparator();m.addAction("备份",self._quick_backup);m.addAction("恢复",self._quick_restore)
        m.addSeparator();m.addAction("退出",self._quit)
        self.tr.setContextMenu(m)
        self.tr.activated.connect(lambda r:self._toggle()if r==QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tr.show()
    def _quit(self):self.tr.hide();QApplication.instance().quit();os._exit(0)
    def _load_hotkey(self):
        s=load_settings();hk=s.get("hotkey_show","ctrl+alt+v")
        parts=hk.lower().split("+");ck=ca=cw=cs=False
        for p in parts[:-1]:
            if p=="ctrl":ck=True
            elif p=="alt":ca=True
            elif p=="shift":cs=True
            elif p=="win":cw=True
        vk={"v":0x56,"c":0x43,"x":0x58,"z":0x5a,"a":0x41,"s":0x53,"d":0x44,"f":0x46,"q":0x51,"w":0x57,"e":0x45,"r":0x52,"t":0x54}
        return{"ctrl":ck,"alt":ca,"shift":cs,"win":cw,"key":vk.get(parts[-1]if parts else"v",0x56),"text":hk}
    def _check_hotkey(self):
        try:
            hk=self._hk_show
            c=(ctypes.windll.user32.GetAsyncKeyState(0x11)&0x8000)!=0
            a=(ctypes.windll.user32.GetAsyncKeyState(0x12)&0x8000)!=0
            s=(ctypes.windll.user32.GetAsyncKeyState(0x10)&0x8000)!=0
            w=(ctypes.windll.user32.GetAsyncKeyState(0x5b)&0x8000)!=0
            k=(ctypes.windll.user32.GetAsyncKeyState(hk["key"])&0x8000)!=0
            # 检查修饰键：只要指定的键按下了就行（忽略其他按键）
            mod_ok=True
            if hk["ctrl"]:mod_ok=mod_ok and c
            if hk["alt"]:mod_ok=mod_ok and a
            if hk["shift"]:mod_ok=mod_ok and s
            if hk["win"]:mod_ok=mod_ok and w
            if hk["win"]:mod_ok=mod_ok and w
            else:mod_ok=mod_ok and not w
            if mod_ok and k:
                if not self._hk_pressed:self._hk_pressed=True;self._toggle()
            else:self._hk_pressed=False
        except:pass
    def _toggle_pin(self):
        f=self.windowFlags()
        if f&Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(f&~Qt.WindowType.WindowStaysOnTopHint);self._pb.setText("屏幕置顶");self._set_status("取消屏幕置顶")
        else:self.setWindowFlags(f|Qt.WindowType.WindowStaysOnTopHint);self._pb.setText("已置顶");self._set_status("已屏幕置顶")
        self.show()
    def _toggle_autostart(self):
        try:
            import winreg
            k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE|winreg.KEY_QUERY_VALUE)
            try:
                winreg.QueryValueEx(k,"ClipboardManager");winreg.DeleteValue(k,"ClipboardManager")
                self._ab.setText("开机自启");self._set_status("已关开机自启")
            except FileNotFoundError:
                exe=sys.executable if getattr(sys,'frozen',False)else sys.argv[0]
                winreg.SetValueEx(k,"ClipboardManager",0,winreg.REG_SZ,f'"{exe}"')
                self._ab.setText("开机自启中");self._set_status("已开开机自启")
            winreg.CloseKey(k)
        except Exception as e:QMessageBox.warning(self,"自启失败",str(e))
    def _backup_dlg(self):
        d,lo=self._mkdlg("备份管理",480,380)
        lo.setContentsMargins(0,0,0,0);lo.setSpacing(0)
        # 操作按钮区
        opl=QHBoxLayout();opl.setContentsMargins(12,8,12,4);opl.setSpacing(8)
        ex_btn=QPushButton("📤 导出备份");ex_btn.setObjectName("flat")
        ex_btn.clicked.connect(lambda:self._do_export(d));opl.addWidget(ex_btn)
        im_btn=QPushButton("📥 导入备份");im_btn.setObjectName("flat")
        im_btn.clicked.connect(lambda:self._do_import_file(d));opl.addWidget(im_btn)
        rs_btn=QPushButton("🔄 恢复选中");rs_btn.setObjectName("flat")
        rs_btn.clicked.connect(lambda:self._do_restore(d));opl.addWidget(rs_btn)
        opl.addStretch();lo.addLayout(opl)
        # 备份列表
        sep=QFrame();sep.setFrameShape(QFrame.Shape.HLine);sep.setStyleSheet("color:"+THEMES[self._theme]['border']+";margin:0 12px;");lo.addWidget(sep)
        lo.addWidget(QLabel("  已有备份："))
        self._bl=QListWidget()
        for b in list_backups():it=QListWidgetItem(f"{b['name']}({b['size']})");it.setData(Qt.ItemDataRole.UserRole,b["path"]);self._bl.addItem(it)
        if not self._bl.count():self._bl.addItem("（无）")
        self._bl.itemDoubleClicked.connect(lambda:self._do_restore(d));lo.addWidget(self._bl,1)
        # 关闭按钮
        bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);bb.rejected.connect(d.reject)
        lo.addWidget(bb);d.exec()
    def _do_export(self,d):p=export_backup();QMessageBox.information(self,"导出成功",f"已保存：{p}");d.close();self._backup_dlg()
    def _do_import_file(self,d):
        fp,_=QFileDialog.getOpenFileName(self,"选择备份","","JSON(*.json);;所有(*.*)")
        if fp:
            try:n=import_backup(fp);QMessageBox.information(self,"导入成功",f"已恢复{n}条");self._reload_sidebar();self._load_items();d.close()
            except Exception as e:QMessageBox.critical(self,"导入失败",str(e))
    def _do_restore(self,d):
        cur=self._bl.currentItem()
        if not cur:return
        p=cur.data(Qt.ItemDataRole.UserRole)
        if p and QMessageBox.question(self,"确认","从备份恢复？")==QMessageBox.StandardButton.Yes:
            n=import_backup(p);QMessageBox.information(self,"恢复完成",f"已恢复{n}条");self._reload_sidebar();self._load_items();d.close()
    def _quick_backup(self):p=export_backup();self.tr.showMessage("备份",os.path.basename(p),QSystemTrayIcon.MessageIcon.Information,3000)
    def _quick_restore(self):
        bl=list_backups()
        if not bl:self.tr.showMessage("提示","无备份",QSystemTrayIcon.MessageIcon.Information,3000);return
        n=import_backup(bl[0]["path"]);self.tr.showMessage("已恢复",f"{n}条",QSystemTrayIcon.MessageIcon.Information,3000)
    def _stats(self):
        s=get_statistics();QMessageBox.information(self,"统计",f"总记录：{s['total']}条  星标：{s['favorites']}条")
    def _show_settings(self):
        d,lo=self._mkdlg("设置",440,520)
        lo.setContentsMargins(12,8,12,8);lo.setSpacing(6)
        lo.addWidget(QLabel("主题颜色"))
        tg=QButtonGroup(d);tl=QHBoxLayout()
        for n in THEMES:rb=QRadioButton(n);rb.setChecked(n==self._theme);tg.addButton(rb);tl.addWidget(rb)
        lo.addLayout(tl)
        # 预设热键
        lo.addWidget(QLabel("呼出热键"))
        self._hk_group=QButtonGroup(d)
        hk_presets=[("Ctrl+Alt+V","ctrl+alt+v"),("Alt+C","alt+c"),("Alt+X","alt+x"),("Alt+Z","alt+z"),("Ctrl+Shift+V","ctrl+shift+v")]
        hk_layout=QHBoxLayout()
        current_hk=self._hk_show["text"]if hasattr(self,'_hk_show')else"ctrl+alt+v"
        for label,val in hk_presets:
            rb=QRadioButton(label)
            rb.setChecked(val==current_hk)
            self._hk_group.addButton(rb)
            hk_layout.addWidget(rb)
        lo.addLayout(hk_layout)
        # 自定义缓存路径
        lo.addWidget(QLabel("数据存储路径"))
        cp_layout=QHBoxLayout()
        self._cp_edit=QLineEdit(load_settings().get("custom_path","")or DATA_DIR)
        cp_layout.addWidget(self._cp_edit,1)
        def pick_path():
            from PyQt6.QtWidgets import QFileDialog
            p=QFileDialog.getExistingDirectory(self,"选择数据目录")
            if p:self._cp_edit.setText(p)
        cp_layout.addWidget(QPushButton("浏览...",clicked=pick_path))
        lo.addLayout(cp_layout)
        abtn=QPushButton("应用");lo.addWidget(abtn)
        # 关于信息
        af=QFrame();af.setStyleSheet("QFrame{background:"+THEMES[self._theme]['glass']+";border:2px solid "+THEMES[self._theme]['border']+";border-radius:10px;padding:10px 14px;}")
        al=QVBoxLayout(af);al.setContentsMargins(0,0,0,0);al.setSpacing(2)
        al.addWidget(QLabel("萌宝剪贴板 v3"))
        al.addWidget(QLabel("Ruizz  |  Q 1367014277  |  2026.05.07"))
        lo.addWidget(af)
        # 使用说明（简洁版）
        lo.addWidget(QLabel("使用说明"))
        c=THEMES[self._theme]
        hf=QFrame();hf.setStyleSheet("QFrame{background:"+c['glass']+";border:2px solid "+c['border']+";border-radius:10px;padding:8px 12px;}")
        hl=QVBoxLayout(hf);hl.setSpacing(2)
        tips=[
            "⌨️ 热键呼出  📋 双击复制  ⭐ 右键星标  📝 备注",
            "📂 分类排序  📷 图片识别  🔄 备份  🗑️ 回收站",
        ]
        for t in tips:
            lb=QLabel(t);lb.setStyleSheet("font-size:11px;color:"+c['text']+";padding:1px 0;")
            hl.addWidget(lb)
        lo.addWidget(hf,1)
        bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);bb.rejected.connect(d.reject);lo.addWidget(bb)
        def apply():
            for rb in tg.buttons():
                if rb.isChecked():
                    self._theme=rb.text();s=load_settings();s["theme"]=self._theme
                    # 读取选中的热键
                    hk_val="ctrl+alt+v"
                    hk_map={"Ctrl+Alt+V":"ctrl+alt+v","Alt+C":"alt+c","Alt+X":"alt+x","Alt+Z":"alt+z","Ctrl+Shift+V":"ctrl+shift+v"}
                    for hrb in self._hk_group.buttons():
                        if hrb.isChecked():
                            hk_val=hk_map.get(hrb.text(),"ctrl+alt+v");break
                    s["hotkey_show"]=hk_val
                    s["custom_path"]=self._cp_edit.text().strip()
                    # 如果路径和默认路径一样，不存自定义路径（保持为空）
                    if s["custom_path"]==DATA_DIR:s["custom_path"]=""
                    save_settings(s)
                    self._apply_theme()
                    QApplication.instance().setStyleSheet(self.styleSheet())
                    self._drag_label.setStyleSheet("font-size:13px;font-weight:bold;color:"+THEMES[self._theme]['accent'])
                    if hasattr(self,'_st'):self._st.setStyleSheet("font-size:13px;font-weight:bold;padding:10px 12px 6px;color:"+THEMES[self._theme]['accent'])
                    self._ct.setStyleSheet("font-size:13px;font-weight:bold;color:"+THEMES[self._theme]['accent'])
                    self.st.setStyleSheet("font-size:11px;color:"+THEMES[self._theme]['accent'])
                    # 更新回收站按钮样式
                    c=THEMES[self._theme]
                    if self._cur_cat==-1:
                        self._trash_btn.setStyleSheet("QPushButton#flat{text-align:left;padding:8px 12px;font-size:12px;border:none;border-radius:0;background:"+c['select']+";color:"+c['accent']+"}")
                    else:
                        self._trash_btn.setStyleSheet("QPushButton#flat{text-align:left;padding:8px 12px;font-size:12px;border:none;border-radius:0;background:transparent;color:"+c['accent']+";}QPushButton#flat:hover{background:"+c['hover']+"}")
                    # 更新类型筛选按钮样式
                    if self._type_filter is None:self._reset_type_filter()
                    else:self._set_type_filter(self._type_filter)
                    self._hk_show=self._load_hotkey()
                    self._set_status("设置已保存");d.close();break
        abtn.clicked.connect(apply);d.exec()
    def _set_status(self,m):self.st.setText(m);QTimer.singleShot(4000,lambda:self.st.setText(f"共{self.l.count()}条"))

if __name__=="__main__":
    try:
        app=QApplication(sys.argv);app.setApplicationName("萌宝剪贴板");app.setQuitOnLastWindowClosed(False)
        init_database();w=MainWindow();w.show()
        app.setStyleSheet(w.styleSheet())
        sys.exit(app.exec())
    except BaseException as e:
        lp=os.path.join(_get_base_dir(),"crash.log")
        try:open(lp,"w",encoding="utf-8").write(f"CRASH:{type(e).__name__}:{e}\n");traceback.print_exc(file=open(lp,"a"))
        except:pass
        print(f"CRASH:{e}");input("按Enter退出...")
