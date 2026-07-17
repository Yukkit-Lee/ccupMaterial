from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "result" / "policy_profit_charts"
WORD = ROOT / "result" / "policy_profit_word_charts"
OUT.mkdir(exist_ok=True); WORD.mkdir(exist_ok=True)
FONT = r"C:\Windows\Fonts\msyh.ttc"; BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
W, H = 1800, 1000
INK, GRID, BLUE, GREEN, AMBER, RED, PURPLE = "#203040", "#D7E1EA", "#2F6B8A", "#4F9355", "#E6A93B", "#C84B4B", "#7867B7"

def f(s, bold=False): return ImageFont.truetype(BOLD if bold else FONT, s)
def t(d, xy, text, s=28, color=INK, bold=False, anchor=None): d.text(xy, text, font=f(s,bold), fill=color, anchor=anchor)
def base(title, ymax, unit, left=250, unit_x=48):
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im); l,top,r,b=left,180,1580,800
    t(d,(W//2,65),title,42,INK,True,"mm")
    for i in range(6):
        y=b-(b-top)*i/5; d.line((l,y,r,y),fill=GRID,width=2); t(d,(l-30,y),f"{ymax*i/5:g}",23,"#4B6273",False,"rm")
    d.line((l,top,l,b),fill="#4B6273",width=4); d.line((l,b,r,b),fill="#4B6273",width=4)
    t(d,(unit_x,(top+b)//2),unit,24,"#4B6273",False,"lm")
    return im,d,l,top,r,b
def save(im,name):
    # 导出 300 DPI 图像；PNG 保留无损版本，Word 使用高质量 JPEG 嵌入。
    big=im.resize((3000,1667),Image.Resampling.LANCZOS)
    big.save(OUT/f"{name}.png",dpi=(300,300))
    big.save(WORD/f"{name}.jpg",quality=100,subsampling=0,dpi=(300,300))
def legend(d, items):
    x=280
    for label,color in items:
        d.rounded_rectangle((x,900,x+30,930),5,fill=color); t(d,(x+42,915),label,23,INK,False,"lm"); x+=260

def customer():
    # 增大左边距并把纵轴标签移至左侧，避免“服务数量”与纵轴重叠。
    im,d,l,top,r,b=base("三年服务数量计划",10,"服务数量（项/节点）",left=380,unit_x=18)
    years=["2027E","2028E","2029E"]; xs=[540,980,1410]
    data=[("付费 POC",[1,2,4],AMBER,-24),("标准部署",[1,3,6],BLUE,0),("订阅节点",[0,4,9],GREEN,24)]
    for label,vals,color,off in data:
        pts=[(x+off,b-(b-top)*v/10) for x,v in zip(xs,vals)]; d.line(pts,fill=color,width=6)
        for x,y,v in [(x,y,v) for (x,y),v in zip(pts,vals)]:
            d.ellipse((x-11,y-11,x+11,y+11),fill=color); t(d,(x+15,y-22),str(v),22,color,True,"ms")
    for x,y in zip(xs,years): t(d,(x,b+55),y,27,INK,False,"mm")
    legend(d,[(x[0],x[2]) for x in data]); save(im,"customer-plan")

def revenue():
    im,d,l,top,r,b=base("三年营业收入构成",200,"营业收入（万元）")
    years=["2027E","2028E","2029E"]; xs=[470,915,1360]
    groups=[("付费 POC",[8,16,32],AMBER),("标准部署",[15,45,90],BLUE),("年度订阅",[0,16,36],GREEN),("定制集成",[0,6,18],PURPLE)]
    for idx,(x,year) in enumerate(zip(xs,years)):
        cur=b
        for _,vals,col in groups:
            v=vals[idx]; h=(b-top)*v/200; d.rectangle((x-80,cur-h,x+80,cur),fill=col)
            if v: t(d,(x,cur-h/2),str(v),20,"white",True,"mm")
            cur-=h
        t(d,(x,cur-25),f"合计 {sum(v[idx] for _,v,_ in groups)}",24,INK,True,"ms"); t(d,(x,b+55),year,27,INK,False,"mm")
    legend(d,[(x[0],x[2]) for x in groups]); save(im,"revenue-composition")

def financial():
    im,d,l,top,r,b=base("营业收入与税前经营性利润预测",200,"营业收入（万元）")
    years=["2027E","2028E","2029E"]; xs=[430,915,1400]; rev=[23,83,176]; pro=[2.3,23.2,56.2]
    for x,y,v in zip(xs,years,rev):
        h=(b-top)*v/200; d.rounded_rectangle((x-85,b-h,x+85,b),10,fill=BLUE); t(d,(x,b-h-24),str(v),25,BLUE,True,"ms"); t(d,(x,b+55),y,27,INK,False,"mm")
    pts=[(x,b-(b-top)*p/60) for x,p in zip(xs,pro)]; d.line(pts,fill=RED,width=6)
    for (x,y),p in zip(pts,pro): d.ellipse((x-12,y-12,x+12,y+12),fill=RED); t(d,(x,y-28),f"{p:g}",22,RED,True,"mm")
    d.rounded_rectangle((520,110,552,142),6,fill=BLUE); t(d,(565,126),"营业收入",24,INK,False,"lm")
    d.rounded_rectangle((800,110,832,142),6,fill=RED); t(d,(845,126),"税前经营性利润",24,INK,False,"lm")
    t(d,(900,855),"注：均为经营预测，不代表已实现收入或利润。",22,"#4B6273",False,"mm")
    save(im,"financial-forecast")

def cash():
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im); t(d,(W//2,65),"轻资产启动与现金纪律",42,INK,True,"mm")
    rows=[("研发与原型工具",8,BLUE),("POC 现场交付与差旅",5,GREEN),("数据治理与合规",3,AMBER),("客户调研与渠道",3,PURPLE),("现金安全垫目标",5,RED)]
    for i,(label,val,col) in enumerate(rows):
        y=190+i*110; t(d,(210,y+25),label,29,INK,False,"lm"); d.rounded_rectangle((630,y,1450,y+55),12,fill="#E7EEF3"); d.rounded_rectangle((630,y,630+820*val/24,y+55),12,fill=col); t(d,(1490,y+28),f"{val} 万元",26,INK,True,"lm")
    d.rounded_rectangle((210,790,1590,920),18,fill="#F4F8FB",outline=BLUE,width=3)
    t(d,(900,842),"首年预算约 24 万元；以合同预付款覆盖交付支出，不将大额外部融资作为启动前提。",25,BLUE,True,"mm")
    t(d,(900,885),"现金安全垫为规划目标，不代表已到账资金。",22,"#4B6273",False,"mm")
    save(im,"cash-use")

def delivery():
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im); t(d,(W//2,65),"智检云盾首期交付闭环",42,INK,True,"mm")
    boxes=[("需求与边界确认","缺陷类别、数据范围、验收指标"),("本地数据治理","标签校验、权限配置、数据不出厂"),("安全协同训练","秘密共享训练、改进 DPSGD 更新"),("模型评测与审计","模型版本、隐私预算、误报漏报"),("本地部署与复检","本地推理、人工复核、结果回写")]
    colors=[BLUE,"#2F8D95",GREEN,PURPLE,AMBER]; x=105; y=330; bw=290; bh=245
    for i,((head,detail),color) in enumerate(zip(boxes,colors)):
        d.rounded_rectangle((x,y,x+bw,y+bh),24,fill="#F8FBFD",outline=color,width=5)
        d.ellipse((x+105,y+28,x+185,y+108),fill=color); t(d,(x+145,y+68),str(i+1),34,"white",True,"mm")
        t(d,(x+145,y+145),head,26,INK,True,"mm")
        d.multiline_text((x+145,y+194),detail,font=f(18),fill="#4B6273",anchor="mm",align="center",spacing=7)
        if i<4: d.polygon([(x+bw+18,y+105),(x+bw+62,y+120),(x+bw+18,y+135)],fill="#8AA1AF")
        x+=335
    t(d,(W//2,735),"所有环节均以任务授权、最小必要处理和日志可追溯为约束",30,"#4B6273",False,"mm")
    save(im,"delivery-flow")

if __name__ == '__main__': customer(); revenue(); financial(); cash(); delivery()
