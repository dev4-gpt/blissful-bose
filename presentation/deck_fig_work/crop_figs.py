import pymupdf, re, sys, json
from PIL import Image
P="../paper_pdfs/"
# (key, pdf, label, kind)  kind: fig (caption below) | tab (caption above, for most ACL/AAAI tables)
T=[("figstep_t1","figstep","Table 1","tab"),("figstep_f2","figstep","Figure 2","fig"),("figstep_f5","figstep","Figure 5","fig"),
("poly_t6","polyjailbreak","TABLE VI","tab"),("poly_f5","polyjailbreak","Fig. 5","fig"),("poly_f6","polyjailbreak","Fig. 6","fig"),
("hades_f2","hades","Fig. 2","fig"),("hades_t2","hades","Table 2","tab"),
("siuo_f1","siuo_acl","Figure 1","fig"),("siuo_f2","siuo_acl","Figure 2","fig"),("siuo_t2","siuo_acl","Table 2","tab"),
("vls_f1","vlsbench_acl","Figure 1","fig"),("vls_t1","vlsbench_acl","Table 1","tab"),
("mmjb_f1","mmjailbench","Figure 1","fig"),("mmjb_t3","mmjailbench","Table 3","tab"),("mmjb_t4","mmjailbench","Table 4","tab"),("mmjb_f4","mmjailbench","Figure 4","fig"),("mmjb_f5","mmjailbench","Figure 5","fig"),
("cmrm_f1","cmrm","Figure 1","fig"),
("jb_f1","jailbound","Figure 1","fig"),("jb_f7","jailbound","Figure 7","fig"),
("sr_f1","safetyreminder_aaai","Figure 1","fig"),("sr_f2","safetyreminder_aaai","Figure 2","fig"),
("adpo_t1","adpo","Table 1","tab"),("safevlm_t3","safevlm","Table 3","tab"),("safevlm_t4","safevlm","Table 4","tab")]
out={}
for key,pdf,label,kind in T:
    d=pymupdf.open(P+pdf+".pdf"); found=None
    for pi,p in enumerate(d):
        for b in p.get_text("blocks"):
            t=b[4].strip().replace("\n"," ")
            if re.match(re.escape(label)+r"\s*[:.]",t,re.I) or (label.isupper() and t.upper().startswith(label)):
                found=(pi,b); break
        if found: break
    if not found: print("MISSING",key); continue
    pi,b=found; p=d[pi]; W=p.rect.width
    x0,y0,x1,y1=b[:4]
    # column: if caption block is narrow (<0.6 W) it's single column, else full-width
    full=(x1-x0)>0.6*W
    cx0,cx1=(30,W-30) if full else (max(30,x0-8),min(W-30,x1+8))
    # table-only: wide-caption may be in two-col but table spans col
    rects=[]
    for im in p.get_images(full=True):
        for r in p.get_image_rects(im[0]): rects.append(r)
    for dr in p.get_drawings(): rects.append(dr["rect"])
    # include text blocks that live inside figure? handled by selection below
    blocks=[bb for bb in p.get_text("blocks")]
    if kind=="fig":
        # caption below: region from top to caption bottom
        cand=[r for r in rects if r.y1<=y0+2 and r.x1>cx0 and r.x0<cx1 and r.height>2]
        top=y0
        # grow upward contiguous
        changed=True
        while changed:
            changed=False
            for r in cand:
                if r.y1>=top-14 and r.y0<top:
                    top=r.y0; changed=True
        top=max(top-3,20)
        rect=(cx0,top,cx1,y1+3)
        # extend to include whole caption block text (may be multi-line)
        rect=(cx0,top,cx1,y1+3)
    else:
        # table: caption above (or below). Start at caption top; end at next text block with long paragraph below table
        # gather following blocks within column; stop at first block with >200 chars not starting with table-ish
        below=sorted([bb for bb in blocks if bb[1]>=y1-1 and bb[2]>cx0 and bb[0]<cx1],key=lambda z:z[1])
        end=y1
        for bb in below:
            txt=bb[4].strip()
            if len(txt)>230 and (bb[2]-bb[0])>0.8*(cx1-cx0): break
            end=bb[3]
            if end-y0>330: break
        rect=(cx0,max(y0-3,20),cx1,end+4)
    out[key]=dict(pdf=pdf,page=pi+1,rect=[round(v,1) for v in rect])
    pix=p.get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(*rect))
    Image.frombytes("RGB",(pix.width,pix.height),pix.samples).save(f"c_{key}.png")
    print(key,"p",pi+1,[round(v) for v in rect])
json.dump(out,open("crops.json","w"),indent=1)
