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

def chart_axes(draw, left=180, top=180, right=1640, bottom=820, ymax=10, unit="数量（个）", unit_x=46):
    for i in range(6):
        y = bottom - (bottom - top) * i / 5
        draw.line((left, y, right, y), fill=GRID, width=2)
        text(draw, (left - 34, y), f"{ymax * i / 5:g}", 24, "#4B6273", anchor="rm")
    draw.line((left, top, left, bottom), fill="#4B6273", width=4)
    draw.line((left, bottom, right, bottom), fill="#4B6273", width=4)
    text(draw, (unit_x, (top + bottom) // 2), unit, 26, "#4B6273", anchor="lm")
    return left, top, right, bottom

def marker(draw, x, y, color, kind):
    if kind == "circle":
        draw.ellipse((x-13, y-13, x+13, y+13), fill=color)
    elif kind == "square":
        draw.rounded_rectangle((x-13, y-13, x+13, y+13), 4, fill=color)
    else:
        draw.polygon([(x, y-16), (x-15, y+12), (x+15, y+12)], fill=color)

def dashed_horizontal(draw, x1, x2, y, fill, width=3, dash=14, gap=9):
    x = x1
    while x < x2:
        draw.line((x, y, min(x + dash, x2), y), fill=fill, width=width)
        x += dash + gap

def customer_plan():
    img, d = canvas(); title(d, "图 7.1  三年客户服务数量计划")
    left, top, right, bottom = chart_axes(d, left=220, right=1600, ymax=14, unit_x=42)
    years = ["2027E", "2028E", "2029E"]
    xs = [left + 95, (left + right)//2, right - 25]
    for x, year in zip(xs, years): text(d, (x, bottom + 62), year, 28, INK, anchor="mm")
    # 使用横向微错位、不同点形和错开标签，保留真实数值但避免同值点重叠。
    series = [
        ("场景 POC", [2,4,6], AMBER, "circle", -22, -34),
        ("标准部署", [1,4,8], BLUE, "square", 0, 32),
        ("年度订阅", [1,5,12], GREEN, "triangle", 22, -34),
    ]
    for name, vals, color, kind, xoffset, label_offset in series:
        pts = [(x + xoffset, bottom - (bottom-top)*v/14) for x,v in zip(xs, vals)]
        line(d, pts, color, 6)
        for (x,y),v in zip(pts, vals):
            marker(d, x, y, color, kind)
            text(d, (x + 18, y + label_offset), str(v), 23, color, True, "ms")
    startx=430
    for name, _, color, kind, _, _ in series:
        d.rounded_rectangle((startx,910,startx+32,942),6,fill=color)
        text(d,(startx+46,926),name,25,INK,anchor="lm")
        startx += 250
    save_chart(img, "customer-plan")

def revenue_composition():
    img, d=canvas(); title(d,"图 7.2  三年营业收入构成")
    # 加大左边距，确保纵轴名称与刻度、轴线完全分离。
    left, top, right, bottom=chart_axes(d,left=330,right=1630,ymax=350,unit="营业收入（万元）",unit_x=38)
    years=["2027E","2028E","2029E"]; xs=[510,980,1450]; barw=160
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
    startx=270
    for name,_,color in groups:
        d.rounded_rectangle((startx,910,startx+30,940),6,fill=color)
        text(d,(startx+42,925),name,24,INK,anchor="lm")
        startx+=315
    save_chart(img, "revenue-composition")

def financial_forecast():
    img,d=canvas(); title(d,"图 7.3  营业收入与税前经营性利润预测")
    # 收入使用左轴、利润使用右轴；柱和折线横向错位，避免利润数据压在柱状图或年份标签上。
    left, top, right, bottom = 240, 190, 1510, 820
    ymax = 350
    for i in range(6):
        y = bottom - (bottom-top) * i / 5
        d.line((left, y, right, y), fill=GRID, width=2)
        text(d, (left-30, y), f"{ymax*i/5:g}", 24, "#4B6273", anchor="rm")
    d.line((left, top, left, bottom), fill="#4B6273", width=4)
    d.line((left, bottom, right, bottom), fill="#4B6273", width=4)
    text(d, (42, (top+bottom)//2), "营业收入（万元）", 25, "#4B6273", anchor="lm")
    profit_min, profit_max = -40, 100
    def profit_y(value):
        return bottom - (value-profit_min) * (bottom-top) / (profit_max-profit_min)
    d.line((right, top, right, bottom), fill=RED, width=3)
    for value in [-40, 0, 40, 80]:
        y = profit_y(value)
        d.line((right, y, right+14, y), fill=RED, width=3)
        text(d, (right+26, y), str(value), 22, RED, anchor="lm")
    zero_y = profit_y(0)
    dashed_horizontal(d, left, right, zero_y, "#D78989", 2)
    text(d, (right+26, top-36), "税前经营性利润（万元）", 23, RED, True, "lm")
    years=["2027E","2028E","2029E"]; xs=[420,900,1380]
    revenue=[38,156,326]; profit=[-31,15,80]
    line_pts = [(x+82, profit_y(p)) for x, p in zip(xs, profit)]
    # 折线先绘制、柱状图后覆盖其穿越柱体的部分，避免两类数据视觉重叠。
    line(d, line_pts, RED, 6)
    for x,year,val,p in zip(xs,years,revenue,profit):
        h=(bottom-top)*val/350
        bar_x=x-72
        d.rounded_rectangle((bar_x-82,bottom-h,bar_x+82,bottom),12,fill=BLUE)
        text(d,(bar_x,bottom-h-24),str(val),26,BLUE,True,"ms")
        text(d,(x,bottom+58),year,28,INK,anchor="mm")
    for (x,y),p in zip(line_pts,profit):
        d.ellipse((x-12,y-12,x+12,y+12),fill=RED)
        text(d,(x, y-30),str(p),24,RED,True,"mm")
    d.rounded_rectangle((510,112,542,144),6,fill=BLUE); text(d,(555,128),"营业收入（左轴）",25,INK,anchor="lm")
    d.rounded_rectangle((830,112,862,144),6,fill=RED); text(d,(875,128),"税前经营性利润（右轴）",25,INK,anchor="lm")
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
