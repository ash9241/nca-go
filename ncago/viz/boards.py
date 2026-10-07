from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import imageio.v2 as imageio

CONFIDENCE_CMAP = "cividis"
OWNERSHIP_CMAP = "BrBG"


def board(ax,stones,overlay=None,cmap=CONFIDENCE_CMAP,vmin=0,vmax=1,title=None):
    n = len(stones)
    ax.set_facecolor("#dfbe88")
    for i in range(n):
        ax.plot([0,n-1],[i,i],color="#554738",lw=.5,zorder=1)
        ax.plot([i,i],[0,n-1],color="#554738",lw=.5,zorder=1)
    stars = [2,n//2,n-3] if n <= 13 else [3,n//2,n-4]
    for r in stars:
        for c in stars:
            ax.add_patch(Circle((c,r),.07,color="#554738",zorder=2))
    artist = None
    if overlay is not None:
        artist = ax.imshow(overlay,origin="lower",extent=(-.5,n-.5,-.5,n-.5),cmap=cmap,vmin=vmin,vmax=vmax,alpha=.68,zorder=2)
    for r,c in np.argwhere(stones != 0):
        ax.add_patch(Circle((c,r),.43,facecolor="#171b20" if stones[r,c] == 1 else "#fffaf2",edgecolor="#171b20",lw=.6,zorder=3))
    ax.set(xlim=(-.7,n-.3),ylim=(-.7,n-.3),aspect="equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title,fontsize=9)
    return artist


def hidden_rgb(states,input_channels,output_channels):
    hidden = states[...,input_channels+output_channels:]
    flat = hidden.reshape(-1,hidden.shape[-1]).astype(np.float64)
    if not np.isfinite(flat).all():
        raise FloatingPointError("Nonfinite hidden state in saved rollout")
    flat -= flat.mean(0)
    flat /= max(1.,float(np.abs(flat).max()))
    _,_,vt = np.linalg.svd(flat,full_matrices=False)
    rgb = np.einsum("ij,kj->ik",flat,vt[:3],optimize=False)
    if rgb.shape[1] < 3:
        rgb = np.pad(rgb,((0,0),(0,3-rgb.shape[1])))
    lo,hi = np.quantile(rgb,[.01,.99],axis=0)
    rgb = np.clip((rgb-lo)/np.maximum(hi-lo,1e-8),0,1)
    return rgb.reshape(hidden.shape[:-1]+(3,))


def filmstrip(source,destination):
    values = np.load(source)
    steps = values["steps"]
    indices = np.unique(np.linspace(0,len(steps)-1,8).astype(int))
    rgb = hidden_rgb(values["states"],int(values["input_channels"]),int(values["output_channels"])) if "states" in values else None
    rows = 5 if rgb is not None else 4
    fig,axes = plt.subplots(rows,len(indices),figsize=(20,rows*2.5),squeeze=False,layout="constrained")
    y = values["target"]
    for column,index in enumerate(indices):
        board(axes[0,column],values["board"],title=f"Step {int(steps[index])}")
        artist = axes[1,column].imshow(np.ma.masked_where(y < 0,values["predictions"][index]),origin="lower",cmap="viridis",vmin=0,vmax=max(3,int(y.max())))
        axes[1,column].set_title("Decoded class",fontsize=9)
        fig.colorbar(artist,ax=axes[1,column],shrink=.65)
        for row,key in ((2,"confidence"),(rows-1,"fire")):
            im = axes[row,column].imshow(values[key][index],origin="lower",cmap=CONFIDENCE_CMAP,vmin=0,vmax=1)
            axes[row,column].set_title(key.capitalize(),fontsize=9)
            fig.colorbar(im,ax=axes[row,column],shrink=.65)
        if rgb is not None:
            axes[3,column].imshow(rgb[index],origin="lower")
            axes[3,column].set_title("Hidden state PCA",fontsize=9)
        for row in range(1,rows):
            axes[row,column].set_xticks([])
            axes[row,column].set_yticks([])
    destination = Path(destination)
    fig.savefig(destination,dpi=120)
    plt.close(fig)
    frames = []
    for index in np.unique(np.linspace(0,len(steps)-1,min(24,len(steps))).astype(int)):
        fig,axes = plt.subplots(1,3,figsize=(9,3),layout="constrained")
        board(axes[0],values["board"],title=f"Step {int(steps[index])}")
        im = axes[1].imshow(values["predictions"][index],origin="lower",cmap="viridis",vmin=0,vmax=3)
        axes[1].set_title("Decoded class")
        fig.colorbar(im,ax=axes[1],shrink=.7)
        im = axes[2].imshow(values["confidence"][index],origin="lower",cmap=CONFIDENCE_CMAP,vmin=0,vmax=1)
        axes[2].set_title("Confidence")
        fig.colorbar(im,ax=axes[2],shrink=.7)
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy())
        plt.close(fig)
    gif = destination.with_suffix(".gif")
    imageio.mimsave(gif,frames,duration=180,loop=0)
    return destination,gif
