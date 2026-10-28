"""Export a precise VLM attack/pipeline map; no model/data execution."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch

NAVY='#172E49';MUTED='#53677D';TEAL='#087E8B';ORANGE='#C96725';PURPLE='#7151A9'
GRAY='#697686';BG='#F3F6FA';WHITE='#FFFFFF'


def build():
    fig,ax=plt.subplots(figsize=(25.6,18.6),dpi=150)
    fig.patch.set_facecolor(BG);ax.set_facecolor(BG)
    ax.set(xlim=(0,2560),ylim=(1860,0));ax.axis('off')
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    def text(x,y,s,size=17,color=NAVY,weight='normal',ha='left'):
        return ax.text(x,y,s,fontsize=size,color=color,weight=weight,ha=ha,va='top',
                       fontfamily='DejaVu Sans',linespacing=1.45)
    def box(x,y,w,h,title,body,edge=TEAL,fill=WHITE,size=16,title_size=19):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=18',
                     fc=fill,ec=edge,lw=1.8))
        text(x+22,y+19,title,title_size,edge,'bold')
        if body:text(x+22,y+61,body,size)
    def arrow(points,color=NAVY,dashed=False,lw=2):
        for a,b in zip(points[:-2],points[1:-1]):
            ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=lw,ls='--' if dashed else '-')
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=18,
                     color=color,lw=lw,linestyle='--' if dashed else '-'))

    text(65,35,'Where visual attacks act in a frozen VLM',34,weight='bold')
    text(65,94,'One shared pipeline; different controlled inputs, objectives, access and evaluation.',20,MUTED)
    text(65,139,'Solid navy = forward processing     Orange = changed input     Dashed purple = optimization gradient',16,MUTED)
    text(65,174,'MEASURED means our development adaptation ran; REVIEWED means the original method has not been reproduced.',15,MUTED)

    box(65,230,780,280,'A  Pixel-level attacks  |  MEASURED ADAPTATIONS',
        'FGSM: one signed-gradient step\nPGD: repeated steps + projection\nShared image: mean loss over a released corpus\nDefense-aware / flip-aware PGD: changed objective\nReleased Qi image: artifact transfer, no reoptimization',ORANGE,size=16,title_size=18)
    box(890,230,780,280,'B  Patch attacks  |  MEASURED ADAPTATIONS',
        'Localized bounded patch: masked pixel updates\nShared bounded patch: one patch across targets\nReplacement EOT patch: average over transforms\nImage composition: x′ = (1 − M) ⊙ x + M ⊙ p\nEOT completed on Smol; Qwen EOT failed',ORANGE,size=16,title_size=18)
    box(1715,230,780,280,'C  Instruction-bearing inputs  |  MIXED STATUS',
        'Visual injection: text/instructions in an image\nImage input changes; no gradient is required\nSmol marker diagnostic ran; Qwen parity blocked\nBAP adds feedback-driven text changes: REVIEWED\nPhysical selection/capture: REVIEWED, not run',ORANGE,size=16,title_size=18)
    # A single shared input bus avoids implying that any attack edits model weights.
    arrow([(455,510),(455,552),(205,552),(205,717)],ORANGE)
    ax.plot([455,1280,2105],[552,552,552],color=ORANGE,lw=2)
    ax.plot([1280,1280],[510,552],color=ORANGE,lw=2)
    ax.plot([2105,2105],[510,552],color=ORANGE,lw=2)
    text(470,570,'All visual branches deliver a changed image x′ to the normal input interface.',17,ORANGE)

    box(65,720,290,150,'Image  x′','Published carrier\nor released artifact',NAVY,size=15,title_size=20)
    box(400,720,340,150,'Preprocessing  P','Resize / normalize\nPatch or token layout',NAVY,size=15,title_size=20)
    box(785,720,360,150,'Visual encoder  E','Model-specific vision\nfeatures / visual tokens',NAVY,size=15,title_size=20)
    box(1190,720,330,150,'Connector  C','Projection / merger\nQ-Former in some VLMs',NAVY,size=15,title_size=20)
    box(1565,720,430,150,'Language decoder  D','p(yₜ | y<ₜ, question, visual tokens)\nAutoregressive generation',NAVY,size=15,title_size=20)
    box(2040,720,455,150,'Response  r','Generated text\nNot automatically a jailbreak',NAVY,size=15,title_size=20)
    for a,b in ((355,400),(740,785),(1145,1190),(1520,1565),(1995,2040)):
        arrow([(a,795),(b,795)])
    box(1565,600,430,85,'Question / prompt  q','',TEAL,title_size=19)
    arrow([(1780,685),(1780,720)],TEAL)
    box(2040,600,455,85,'Defense prefix  |  TESTED','',TEAL,title_size=17)
    arrow([(2040,642),(1995,642)],TEAL)
    arrow([(2105,552),(2105,580),(1780,580),(1780,600)],GRAY,True)
    text(1050,632,'BAP text branch: reviewed, not run',15,GRAY)
    text(850,900,'All model weights θ stay frozen. Input gradients do not require weight updates.',19,TEAL,'bold')

    box(785,970,520,125,'Encoder objective  |  REVIEWED',
        'Match E(x′) to an original trigger embedding.\nNo language-decoder gradient is needed.',PURPLE,size=14,title_size=18)
    arrow([(965,870),(965,970)],PURPLE,True)
    box(1405,970,590,125,'Generative objective  |  OPTIMIZATION',
        'Target sequence NLL, or teacher behavior loss.\nLoss progress ≠ measured attack success.',PURPLE,size=14,title_size=18)
    arrow([(1780,870),(1780,970)],PURPLE,True)
    arrow([(1690,1095),(1690,1160),(205,1160),(205,870)],PURPLE,True)
    text(330,1174,'Backpropagation through the selected path → update pixels inside the declared constraint.',17,PURPLE)
    box(2040,970,455,240,'Behavioral evaluation',
        'Safety: unsafe assistance / planned cases\nInjection: unauthorized task deviation\nPerception: incorrect / targeted answer\nAlso report utility, failures and cost.\nHuman validation remains pending.',TEAL,size=14,title_size=19)
    arrow([(2267,870),(2267,970)],TEAL)

    box(65,1260,1180,240,'D  Jailbreak in Pieces  |  REVIEWED ORIGINAL METHOD',
        'Control: image pixels. Target: CLIP encoder embedding.\nMethod: Adam minimizes L2 distance to released text / OCR / visual / combined triggers.\nThe attack still enters at x′; it does not directly overwrite internal embeddings.\nOriginal example/code is available; our native-paper reproduction is NOT_RUN.',PURPLE,size=16,title_size=19)
    box(1315,1260,1180,240,'E  Image Hijacks + Qi / BAP objectives  |  DIFFERENT METHODS',
        'Qi: corpus sequence likelihood; our short common-benchmark version is an adaptation.\nImage Hijacks: behavior matching; prompt matching uses a teacher distribution over contexts.\nBAP: visual optimization plus iterative text feedback, not a fixed candidate list.\nFull original Image Hijacks / BAP reproductions are NOT_RUN.',PURPLE,size=16,title_size=19)
    arrow([(1090,1260),(1090,1218),(1240,1218),(1240,1095)],PURPLE,True)
    arrow([(1885,1260),(1885,1218),(1950,1218),(1950,1095)],PURPLE,True)

    text(65,1540,'Research strategy: coverage is earned by evidence, not by an attack name',24,weight='bold')
    stages=[('1  Original-method audit','Paper + code + data + rubric\n12 readings; 22 source files checked',TEAL),
            ('2  Native reproduction','Run exact feasible original setup\nCurrent original runs: NOT_RUN',GRAY),
            ('3  Matched comparison','Same held-out cases and scorer\nPrior adaptations: 136 / 144 cases',TEAL),
            ('4  New contribution','Test a prespecified, held-out claim\nNovelty and human review pending',GRAY)]
    for i,(title,body,color) in enumerate(stages):
        x=65+i*620;box(x,1600,570,135,title,body,color,size=14,title_size=18)
        if i<3:arrow([(x+570,1667),(x+620,1667)],GRAY)
    text(65,1770,'Sources: Goodfellow • Madry • Brown • Qi • Shayegani • Bailey • Ying • Ling. Survey / MMJ-Bench / AdaShield / JailGuard have separate roles.',14,MUTED)
    text(65,1805,'Important: attacks change inputs or optimize an input objective. Generic prompting is not AdaShield; flip-aware PGD is not JailGuard.  |  28 October 2026',13,MUTED)
    return fig


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    fig=build()
    for ext in ('svg','png','pdf'):
        path=args.out_dir/('vlm_attack_architecture.'+ext)
        fig.savefig(path,facecolor=BG,dpi=150)
        print(path)
    plt.close(fig)


if __name__=='__main__':main()
