from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "result" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
WORD_OUT = ROOT / "result" / "word_charts"
WORD_OUT.mkdir(parents=True, exist_ok=True)

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

W, H = 1800, 1000
BG = "#FFFFFF"
INK = "#1F2D3D"
GRID = "#CBD5E1"
BLUE = "#2F6B8A"
GREEN = "#4F9355"
AMBER = "#E6A93B"
RED = "#C84B4B"
TEAL = "#2F8D95"
PURPLE = "#7867B7"

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)

def canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)

def text(draw, xy, value, size=28, fill=INK, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)

def title(draw, value):
    text(draw, (W // 2, 70), value, 42, INK, True, "mm")

def line(draw, pts, fill, width=6):
    draw.line(pts, fill=fill, width=width, joint="curve")

def save_chart(img, name):
    img.save(OUT / f"{name}.png", dpi=(180, 180))
    img.save(WORD_OUT / f"{name}.jpg", quality=96, subsampling=0, dpi=(180, 180))

def chart_axes(draw, left=180, top=180, right=1640, bottom=820, ymax=10, unit="数量（个）"):
    for i in range(6):
        y = bottom - (bottom - top) * i / 5
        draw.line((left, y, right, y), fill=GRID, width=2)
        text(draw, (left - 34, y), f"{ymax * i / 5:g}", 24, "#4B6273", anchor="rm")
    draw.line((left, top, left, bottom), fill="#4B6273", width=4)
    draw.line((left, bottom, right, bottom), fill="#4B6273", width=4)
    text(draw, (46, (top + bottom) // 2), unit, 26, "#4B6273", anchor="lm")
    return left, top, right, bottom

def customer_plan():
    img, d = canvas(); title(d, "图 7.1  三年客户服务数量计划")
    left, top, right, bottom = chart_axes(d, ymax=14)
    years = ["2027E", "2028E", "2029E"]
    xs = [left, (left + right)//2, right]
    for x, year in zip(xs, years): text(d, (x, bottom + 62), year, 28, INK, anchor="mm")
    series = [("场景 POC", [2,4,6], AMBER), ("标准部署", [1,4,8], BLUE), ("年度订阅", [1,5,12], GREEN)]
    for name, vals, color in series:
        pts = [(x, bottom - (bottom-top)*v/14) for x,v in zip(xs, vals)]
        line(d, pts, color, 7)
        for (x,y),v in zip(pts, vals):
            d.ellipse((x-12,y-12,x+12,y+12),fill=color)
            text(d,(x,y-32),str(v),24,color,True,"ms")
    startx=420
    for name, _, color in series:
        d.rounded_rectangle((startx,910,startx+32,942),6,fill=color)
        text(d,(startx+46,926),name,25,INK,anchor="lm")
        startx += 250
    save_chart(img, "customer-plan")

def revenue_composition():
    img, d=canvas(); title(d,"图 7.2  三年营业收入构成")
    left, top, right, bottom=chart_axes(d,ymax=350,unit="营业收入（万元）")
    years=["2027E","2028E","2029E"]; xs=[420,900,1380]; barw=160
    groups=[("场景 POC",[12,24,36],AMBER),("标准部署",[18,72,144],BLUE),("年度订阅",[8,40,96],GREEN),("定制集成",[0,20,50],PURPLE)]
    for x,year in zip(xs,years):
        curr=bottom
        for name,vals,color in groups:
            val=vals[years.index(year)]; h=(bottom-top)*val/350
            d.rectangle((x-barw//2,curr-h,x+barw//2,curr),fill=color)
            if val: text(d,(x,curr-h/2),str(val),22,"#FFFFFF",True,"mm")
            curr-=h
        text(d,(x,bottom+55),year,28,INK,anchor="mm")
        total=sum(vals[years.index(year)] for _,vals,_ in groups)
        text(d,(x,curr-28),f"合计 {total}",25,INK,True,"ms")
    startx=260
    for name,_,color in groups:
        d.rounded_rectangle((startx,910,startx+30,940),6,fill=color)
        text(d,(startx+42,925),name,24,INK,anchor="lm")
        startx+=315
    save_chart(img, "revenue-composition")

def financial_forecast():
    img,d=canvas(); title(d,"图 7.3  营业收入与税前经营性利润预测")
    left,top,right,bottom=chart_axes(d,ymax=350,unit="金额（万元）")
    years=["2027E","2028E","2029E"]; xs=[330,900,1470]
    revenue=[38,156,326]; profit=[-31,15,80]
    # x axis at zero (bottom because y range starts at 0); show negative profit below a secondary band
    for x,year,val in zip(xs,years,revenue):
        h=(bottom-top)*val/350
        d.rounded_rectangle((x-95,bottom-h,x+95,bottom),12,fill=BLUE)
        text(d,(x,bottom-h-24),str(val),26,BLUE,True,"ms")
        text(d,(x,bottom+58),year,28,INK,anchor="mm")
    profit_top=850; profit_bottom=940; mid=895
    d.line((left,mid,right,mid),fill=GRID,width=2)
    text(d,(70,mid),"利润",24,"#4B6273",anchor="lm")
    pmax=90
    pts=[]
    for x,p in zip(xs,profit):
        y=mid-p*(mid-profit_top)/pmax if p>=0 else mid+(-p)*(profit_bottom-mid)/35
        pts.append((x,y))
    line(d,pts,RED,6)
    for (x,y),p in zip(pts,profit):
        d.ellipse((x-11,y-11,x+11,y+11),fill=RED)
        text(d,(x,y-23),str(p),24,RED,True,"ms")
    d.rounded_rectangle((520,112,552,144),6,fill=BLUE); text(d,(565,128),"营业收入",25,INK,anchor="lm")
    d.rounded_rectangle((780,112,812,144),6,fill=RED); text(d,(825,128),"税前经营性利润",25,INK,anchor="lm")
    save_chart(img, "financial-forecast")

def cash_use():
    img,d=canvas(); title(d,"图 7.4  启动资金用途与现金缓冲安排")
    values=[30,20,12,8,10]; labels=["原型研发与安全测试","POC 交付与现场适配","数据治理与合规","市场调研与渠道","流动资金缓冲"]
    colors=[BLUE,GREEN,AMBER,PURPLE,TEAL]
    total=sum(values); left=200; top=190; right=1600; bottom=790
    for i,(label,val,color) in enumerate(zip(labels,values,colors)):
        y=top+i*105
        text(d,(left,y+28),label,28,INK,anchor="lm")
        d.rounded_rectangle((620,y,1430,y+60),12,fill="#E7EEF3")
        width=810*val/total
        d.rounded_rectangle((620,y,620+width,y+60),12,fill=color)
        text(d,(1470,y+30),f"{val} 万元（{val/total:.1%}）",27,INK,anchor="lm")
    d.rounded_rectangle((250,820,1550,925),20,outline=BLUE,width=3,fill="#F4F8FB")
    text(d,(900,872),"启动资金池预算：80 万元（预算需求，非已到账融资）",30,BLUE,True,"mm")
    save_chart(img, "cash-use")

def delivery_flow():
    img,d=canvas(); title(d,"图 3.1  智检云盾首期交付闭环")
    boxes=[("需求与边界确认","明确缺陷类别\n数据范围、验收指标"),("本地数据治理","标签校验、权限配置\n数据不出厂"),("安全协同训练","秘密共享训练\n改进 DPSGD 更新"),("模型评测与审计","记录版本、隐私预算\n误报漏报"),("本地部署与复检","输出建议\n质检人员人工复核")]
    colors=[BLUE,TEAL,GREEN,PURPLE,AMBER]; x=120; y=330; bw=285; bh=240
    for i,((head,detail),color) in enumerate(zip(boxes,colors)):
        d.rounded_rectangle((x,y,x+bw,y+bh),24,fill="#F8FBFD",outline=color,width=5)
        d.ellipse((x+102,y+28,x+182,y+108),fill=color)
        text(d,(x+142,y+68),str(i+1),34,"#FFFFFF",True,"mm")
        text(d,(x+142,y+145),head,27,INK,True,"mm")
        d.multiline_text((x+142,y+194), detail, font=font(18), fill="#4B6273", anchor="mm", align="center", spacing=7)
        if i < len(boxes)-1:
            d.polygon([(x+bw+18,y+105),(x+bw+62,y+120),(x+bw+18,y+135)],fill="#8AA1AF")
        x+=335
    text(d,(W//2,735),"所有环节均以任务授权、最小必要处理、日志可追溯为约束",30,"#4B6273",anchor="mm")
    save_chart(img, "delivery-flow")

if __name__ == "__main__":
    customer_plan(); revenue_composition(); financial_forecast(); cash_use(); delivery_flow()
