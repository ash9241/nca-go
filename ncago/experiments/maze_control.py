"""Paper-based Maze-OOD positive control, isolated from Go checkpoints.

Source: https://arxiv.org/html/2609.36126v1 (Table 3, Appendix B).
The public easy-to-hard files contain doubled RGB renderings; we validate
their block structure before converting to logical cells. No Go sealed set
is accessed by this module.
"""
import argparse
from collections import deque
from dataclasses import asdict, dataclass
from functools import partial
from hashlib import sha256
import io
import json
from pathlib import Path
import tarfile
import tempfile
import time

from flax import linen as nn, serialization
import jax
import jax.numpy as jnp
import numpy as np
import optax

from .common import ROOT, Run, write_json


def bfs_path(tokens):
    """Independent four-neighbor shortest-path oracle, including endpoints."""
    ends = list(map(tuple, np.argwhere(tokens == 3)))
    if len(ends) != 2:
        raise ValueError("A maze must have exactly two endpoints")
    start, end = ends
    parents, queue = {start: None}, deque([start])
    while queue and end not in parents:
        r, c = queue.popleft()
        for p in ((r-1,c), (r+1,c), (r,c-1), (r,c+1)):
            if (0 <= p[0] < tokens.shape[0] and 0 <= p[1] < tokens.shape[1]
                    and tokens[p] != 2 and p not in parents):
                parents[p] = (r,c)
                queue.append(p)
    if end not in parents:
        raise ValueError("Disconnected endpoints")
    path = np.zeros_like(tokens, np.uint8)
    p = end
    while p is not None:
        path[p] = 1
        p = parents[p]
    return path


def pruning_reference(tokens):
    """Synchronous local leaf pruning on the public tree-maze domain.

    The queue is an efficient implementation of binary local CA rounds,
    not the learned model. It also reports how many rounds are required.
    """
    active=(tokens!=2).copy()
    protected=tokens==3
    degree=np.zeros_like(tokens,np.int32)
    degree[1:]+=active[:-1];degree[:-1]+=active[1:]
    degree[:,1:]+=active[:,:-1];degree[:,:-1]+=active[:,1:]
    queued=(degree<=1)&active&~protected
    queue=deque((int(r),int(c),1) for r,c in np.argwhere(queued))
    rounds=0
    while queue:
        r,c,round_index=queue.popleft()
        active[r,c]=False
        rounds=max(rounds,round_index)
        for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if 0<=rr<len(tokens) and 0<=cc<tokens.shape[1] and active[rr,cc]:
                degree[rr,cc]-=1
                if degree[rr,cc]<=1 and not queued[rr,cc] and not protected[rr,cc]:
                    queued[rr,cc]=True
                    queue.append((rr,cc,round_index+1))
    return active.astype(np.uint8),rounds


def canonical_maze(board):
    return min(x.tobytes() for i in range(4) for x in (np.rot90(board,i),np.rot90(board,i)[::-1]))


def clean_qualification(training, testing, count):
    """Remove train overlap and duplicate mazes, including all D4 symmetries."""
    seen={canonical_maze(b) for b in training}
    selected=[]
    overlap=0
    duplicate=0
    test_seen=set()
    for i,board in enumerate(testing):
        key=canonical_maze(board)
        if key in seen:
            overlap+=1
        elif key in test_seen:
            duplicate+=1
        else:
            test_seen.add(key)
            if len(selected)<count:
                selected.append(i)
    if len(selected)!=count:
        raise ValueError("Insufficient genuinely held-out qualification mazes")
    return np.asarray(selected),dict(test_train_d4_overlap=overlap,test_d4_duplicates=duplicate,
                                    selected_official_indices=selected,qualification_count=count)


def convert_public_maze(inputs, solutions, size):
    inputs, solutions = np.asarray(inputs), np.asarray(solutions)
    expected = 2*size+6
    if inputs.shape[1:] != (3,expected,expected) or solutions.shape != (len(inputs),expected,expected):
        raise ValueError(f"Unexpected rendering dimensions: {inputs.shape}, {solutions.shape}")
    if not np.all((inputs == 0) | (inputs == 1)) or not np.all((solutions == 0) | (solutions == 1)):
        raise ValueError("Nonbinary pixels")
    border = np.ones((expected,expected), bool)
    border[3:-3,3:-3] = False
    if np.any(inputs[:,:,border]) or np.any(solutions[:,border]):
        raise ValueError("Nonempty rendering border")
    inner, target = inputs[:,:,3:-3,3:-3], solutions[:,3:-3,3:-3]
    rgb, labels = inner[:,:,::2,::2], target[:,::2,::2]
    for dr in range(2):
        for dc in range(2):
            if not np.array_equal(inner[:,:,dr::2,dc::2],rgb) or not np.array_equal(target[:,dr::2,dc::2],labels):
                raise ValueError("Rendering cells are not constant 2x2 blocks")
    rgb = rgb.transpose(0,2,3,1).astype(np.uint8)
    wall = np.all(rgb == (0,0,0), -1)
    empty = np.all(rgb == (1,1,1), -1)
    red, green = np.all(rgb == (1,0,0), -1), np.all(rgb == (0,1,0), -1)
    if not np.all(wall | empty | red | green) or not np.all(red.sum((1,2)) == 1) or not np.all(green.sum((1,2)) == 1):
        raise ValueError("Invalid colors or endpoints")
    tokens = np.where(wall,2,np.where(red | green,3,0)).astype(np.uint8)
    labels = labels.astype(np.uint8)
    if np.any(labels[wall]) or not np.all(labels[red | green] == 1):
        raise ValueError("Invalid path on walls/endpoints")
    return tokens, labels


def prepare_archive(archive, destination, size):
    """Read only the two expected NPY members; never execute/extract an archive."""
    archive, destination = Path(archive), Path(destination)
    with tempfile.TemporaryDirectory(prefix="ncago-maze-") as scratch:
        with tarfile.open(archive) as tar:
            arrays = []
            for name in ("inputs.npy","solutions.npy"):
                members = [m for m in tar.getmembers() if Path(m.name).name == name and m.isfile()]
                if len(members) != 1:
                    raise ValueError(f"Expected one {name}")
                # Explicit safe destination; no archive member paths extracted.
                path=Path(scratch)/name
                with path.open("wb") as output, tar.extractfile(members[0]) as source:
                    import shutil
                    shutil.copyfileobj(source,output)
                arrays.append(np.load(path,allow_pickle=False,mmap_mode="r"))
        tokens=np.empty((len(arrays[0]),size,size),np.uint8)
        labels=np.empty_like(tokens)
        for first in range(0,len(tokens),64):
            boards,targets=convert_public_maze(arrays[0][first:first+64],arrays[1][first:first+64],size)
            for i,(board,target) in enumerate(zip(boards,targets)):
                if not np.array_equal(bfs_path(board),target):
                    raise ValueError(f"Public label disagrees with BFS at {first+i}")
            tokens[first:first+len(boards)],labels[first:first+len(boards)]=boards,targets
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination, tokens=tokens, labels=labels)
    manifest = dict(size=size, count=len(tokens), archive_sha256=sha256(archive.read_bytes()).hexdigest(),
                    converted_sha256=sha256(destination.read_bytes()).hexdigest(),
                    oracle="independent four-neighbor BFS; all labels checked",
                    conversion="crop 3-pixel border, verify constant 2x2 blocks, downsample",
                    source=f"https://cs.umd.edu/~tomg/download/Easy_to_Hard_Datav2/maze_data_{'train' if 'train' in archive.name else 'test'}_{size}.tar.gz")
    write_json(destination.with_suffix(".json"),manifest)
    return manifest


@dataclass(frozen=True)
class MazeConfig:
    channels: int = 16
    heads: int = 4
    expansion: int = 2
    fire_rate: float = .8
    init_sigma: float = .15


class MazeNCA(nn.Module):
    config: MazeConfig = MazeConfig()

    @nn.compact
    def __call__(self, state):
        c = self.config
        wall = jax.nn.one_hot(2,c.channels)
        # Padding is a fixed wall embedding, including at corner cells.
        padded = jnp.pad(state, ((0,0),(1,1),(1,1),(0,0)))
        interior = jnp.pad(jnp.ones(state.shape[1:3],bool), ((1,1),(1,1)))
        padded = jnp.where(interior[None,...,None],padded,wall)
        perception = nn.Conv(c.channels*c.heads,(3,3),padding="VALID",name="perception")(padded)
        hidden = nn.relu(nn.Dense(c.expansion*c.channels,name="expand")(perception))
        return nn.Dense(c.channels,kernel_init=nn.initializers.zeros,name="update")(hidden)


@partial(jax.jit, static_argnames=("config",))
def maze_initialize(tokens, key, config=MazeConfig()):
    noise = jax.random.normal(key,tokens.shape+(config.channels,))*config.init_sigma
    return jnp.where((tokens >= 2)[...,None],jax.nn.one_hot(tokens,config.channels),noise)


def maze_step(model, params, state, tokens, key, noise_sigma=0.):
    fire_key, time_key, cell_key, noise_key = jax.random.split(key,4)
    free = tokens == 0
    fire = jax.random.bernoulli(fire_key,model.config.fire_rate,tokens.shape) & free
    out = state + fire[...,None]*model.apply({"params":params},state)
    noisy = jax.random.bernoulli(time_key,.1,(len(tokens),1,1)) & jax.random.bernoulli(cell_key,.2,tokens.shape) & free
    out = out + noisy[...,None]*jax.random.normal(noise_key,state.shape)*noise_sigma
    return jnp.where(free[...,None],out,jax.nn.one_hot(tokens,model.config.channels))


def maze_prediction(state, tokens):
    # Nearest orthonormal output vector, equivalent to argmax of first 2.
    return jnp.where(tokens == 3,1,jnp.where(tokens == 2,0,jnp.argmax(state[...,:2],-1)))


@jax.jit
def augment_maze(state, tokens, labels, keys):
    def one(s,t,y,k):
        k1,k2 = jax.random.split(k)
        rotation = jax.random.randint(k1,(),0,4)
        s,t,y = jax.lax.switch(rotation,[lambda v,i=i: tuple(jnp.rot90(a,i,(0,1)) for a in v) for i in range(4)],(s,t,y))
        return jax.lax.cond(jax.random.bernoulli(k2),lambda v:tuple(jnp.flip(a,0) for a in v),lambda v:v,(s,t,y))
    return jax.vmap(one)(state,tokens,labels,keys)


@jax.jit
def damage_maze(state, tokens, key):
    choose_key, center_key, radius_key, count_key = jax.random.split(key,4)
    batch,h,w = tokens.shape
    centers = jax.random.uniform(center_key,(batch,3,2))*jnp.array([h,w])
    radii = jax.random.uniform(radius_key,(batch,3),minval=.1,maxval=.4)*w
    counts = jax.random.randint(count_key,(batch,),1,4)
    rr,cc = jnp.ogrid[:h,:w]
    circles = ((rr[None,None,:,:]-centers[:,:,0,None,None])**2
               +(cc[None,None,:,:]-centers[:,:,1,None,None])**2) <= radii[:,:,None,None]**2
    circles &= (jnp.arange(3)[None,:] < counts[:,None])[:,:,None,None]
    mask = circles.any(1) & jax.random.bernoulli(choose_key,.1,(batch,1,1)) & (tokens == 0)
    return jnp.where(mask[...,None],0.,state)


def make_maze_update(model, optimizer, depth=100):
    @jax.jit
    def update(params, opt_state, incoming, tokens, labels, key):
        def objective(p):
            mask = tokens == 0
            target = jax.nn.one_hot(labels,2)
            def body(state,i):
                out = maze_step(model,p,state,tokens,jax.random.fold_in(key,i),.15)
                error = jnp.sum((out[...,:2]-target)**2,-1)
                # Fixed clues have zero gradient/error; the paper still
                # normalizes by the entire grid area (Appendix B.1).
                loss = jnp.sum(jnp.where(mask,error,0.))/mask.size
                return out,loss
            final, losses = jax.lax.scan(jax.checkpoint(body),incoming,jnp.arange(depth))
            return jnp.mean(losses),final
        (loss,final), gradients = jax.value_and_grad(objective,has_aux=True)(params)
        updates,opt_state = optimizer.update(gradients,opt_state,params)
        return optax.apply_updates(params,updates),opt_state,final,loss,optax.global_norm(gradients)
    return update


def make_maze_rollout(model, depth, noise_sigma=0.):
    @jax.jit
    def predict(params,tokens,key):
        initial = maze_initialize(tokens,jax.random.fold_in(key,100001),model.config)
        def body(state,i):
            sigma=jnp.where(i<depth//4,noise_sigma,0.)
            return maze_step(model,params,state,tokens,jax.random.fold_in(key,i),sigma),None
        final,_ = jax.lax.scan(body,initial,jnp.arange(depth))
        return maze_prediction(final,tokens),final
    return predict


def maze_metrics(prediction,labels,tokens):
    free = tokens == 0
    correct = prediction == labels
    path = labels == 1
    return dict(exact_path_accuracy=float(correct.all((1,2)).mean()),
                mutable_cell_accuracy=float(correct[free].mean()),
                path_recall=float(correct[path & free].mean()),
                off_path_recall=float(correct[~path & free].mean()),
                board_count=len(tokens))


def evaluate_maze(model,params,tokens,labels,depth,seed=20001,batch_size=32,noise_sigma=0.):
    predict = make_maze_rollout(model,depth,noise_sigma)
    preds=[]
    for start in range(0,len(tokens),batch_size):
        board = tokens[start:start+batch_size]
        # Fixed batch shape; padding is removed before scoring.
        padded = np.concatenate([board,np.repeat(board[-1:],batch_size-len(board),0)])
        pred,state = predict(params,jnp.asarray(padded),jax.random.fold_in(jax.random.PRNGKey(seed),start))
        if not np.isfinite(np.asarray(state)).all():
            raise FloatingPointError("Maze rollout diverged")
        preds.append(np.asarray(pred)[:len(board)])
    preds=np.concatenate(preds)
    return maze_metrics(preds,labels,tokens),preds


def train_maze(args):
    config=dict(source="https://arxiv.org/html/2609.36126v1",recipe="Table 3 Maze-OOD",
                model=asdict(MazeConfig()),training_steps=args.updates,batch_size=args.batch,
                depth=100,learning_rate=.0004,weight_decay=0.,ema_decay=.999,
                pool_multiplier=4,seed_fraction=.25,damage_probability=.1,target_swap_probability=.1,
                noise_time_probability=.1,noise_cell_probability=.2,noise_sigma=.15,
                data_sha256=sha256(Path(args.train).read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                mse_reduction="sum over output channels, mean over all grid cells and all 100 steps",
                selection="fixed final EMA; no OOD checkpoint selection",seed=args.seed)
    if args.resume:
        config["continuation_from"]=str(args.resume)
        config["continuation_sha256"]=sha256((Path(args.resume)/"ckpt/resume.msgpack").read_bytes()).hexdigest()
        config["recipe_deviation"]="Continuation beyond published 5000 updates; exploratory positive-control repair"
    run=Run("maze_control",config,args.seed)
    (run.path/"maze_control_source.py").write_bytes(Path(__file__).read_bytes())
    print(run.path,flush=True)
    with np.load(args.train) as d:
        boards,labels=d["tokens"],d["labels"]
    with np.load(args.validation) as d:
        validation_tokens,validation_labels=d["tokens"],d["labels"]
    indices,audit=clean_qualification(boards,validation_tokens,args.validation_count)
    validation=(validation_tokens[indices],validation_labels[indices])
    write_json(run.path/"data/qualification_manifest.json",dict(**audit,
               source_sha256=sha256(Path(args.validation).read_bytes()).hexdigest(),
               selection="first requested number of D4-disjoint, D4-unique official test9 boards"))
    if boards.shape[1:] != (9,9):
        raise ValueError("Positive control is trained on logical 9x9 only")
    rng=np.random.default_rng(args.seed)
    model=MazeNCA()
    key=jax.random.PRNGKey(args.seed)
    key,init_key,param_key=jax.random.split(key,3)
    ids=rng.integers(len(boards),size=args.batch*4)
    pool_tokens,pool_labels=boards[ids].copy(),labels[ids].copy()
    pool=np.asarray(maze_initialize(jnp.asarray(pool_tokens),init_key)).copy()
    params=model.init(param_key,jnp.asarray(pool[:1]))["params"]
    ema=params
    optimizer=optax.chain(optax.clip_by_global_norm(1.),optax.adamw(.0004,weight_decay=0.))
    opt_state=optimizer.init(params)
    first_update=0
    if args.resume:
        parent=Path(args.resume)
        import yaml
        old=yaml.safe_load((parent/"config.yaml").read_text())
        if old["seed"]!=args.seed or old["batch_size"]!=args.batch or old["data_sha256"]!=config["data_sha256"]:
            raise ValueError("Continuation must preserve seed, batch size and training data")
        template=dict(params=params,ema=ema,opt_state=opt_state,key=key,pool=pool,
                      pool_tokens=pool_tokens,pool_labels=pool_labels,update=0,numpy_rng_json="")
        restored=serialization.from_bytes(template,(parent/"ckpt/resume.msgpack").read_bytes())
        params,ema,opt_state,key=[restored[n] for n in ("params","ema","opt_state","key")]
        pool,pool_tokens,pool_labels=[np.array(restored[n],copy=True) for n in ("pool","pool_tokens","pool_labels")]
        rng.bit_generator.state=json.loads(restored["numpy_rng_json"])
        first_update=int(restored["update"])
        if first_update>=args.updates:raise ValueError("Continuation needs a larger total update count")
    update=make_maze_update(model,optimizer)
    started=time.perf_counter()
    for index in range(first_update+1,args.updates+1):
        chosen=rng.choice(len(pool),args.batch,replace=False)
        fresh=rng.random(args.batch)<.25
        swap=rng.random(args.batch)<.1
        incoming=pool[chosen].copy()
        tokens,targets=pool_tokens[chosen].copy(),pool_labels[chosen].copy()
        replaced=fresh | swap
        ids=rng.integers(len(boards),size=int(replaced.sum()))
        tokens[replaced],targets[replaced]=boards[ids],labels[ids]
        key,seed_key,aug_key,damage_key,roll_key=jax.random.split(key,5)
        seed_states=np.asarray(maze_initialize(jnp.asarray(tokens),seed_key))
        incoming[fresh]=seed_states[fresh]
        incoming=np.where((tokens>=2)[...,None],np.eye(16,dtype=np.float32)[tokens],incoming)
        incoming,tokens,targets=augment_maze(jnp.asarray(incoming),jnp.asarray(tokens),jnp.asarray(targets),jax.random.split(aug_key,args.batch))
        incoming=damage_maze(incoming,tokens,damage_key)
        params,opt_state,final,loss,grad_norm=update(params,opt_state,incoming,tokens,targets,roll_key)
        ema=jax.tree_util.tree_map(lambda e,p:.999*e+.001*p,ema,params)
        pool[chosen],pool_tokens[chosen],pool_labels[chosen]=np.asarray(final),np.asarray(tokens),np.asarray(targets)
        if index == 1 or index % args.log_every == 0:
            loss_value=float(loss)
            if not np.isfinite(loss_value) or not np.isfinite(float(grad_norm)):
                run.finish("failed_nonfinite",update=index)
                raise FloatingPointError("Nonfinite maze optimization")
            row=dict(update=index,loss=loss_value,gradient_norm=float(grad_norm),elapsed_seconds=time.perf_counter()-started)
            run.log(**row)
            print(json.dumps(row),flush=True)
        if index % 1000 == 0 or index == args.updates:
            state=dict(params=params,ema=ema,opt_state=opt_state,key=key,pool=pool,
                       pool_tokens=pool_tokens,pool_labels=pool_labels,update=index,
                       numpy_rng_json=json.dumps(rng.bit_generator.state))
            (run.path/"ckpt/resume.msgpack").write_bytes(serialization.to_bytes(jax.device_get(state)))
            (run.path/"ckpt/final.msgpack").write_bytes(serialization.to_bytes(ema))
    measurements=[]
    for depth in (100,400,800):
        metric,preds=evaluate_maze(model,ema,*validation,depth,seed=20001,batch_size=args.batch)
        measurements.append(dict(size=9,depth=depth,**metric))
        np.savez_compressed(run.path/f"eval/qualification_9_d{depth}.npz",predictions=preds,tokens=validation[0],labels=validation[1])
        print(json.dumps(measurements[-1]),flush=True)
    qualified=all(x["exact_path_accuracy"] >= .99 for x in measurements)
    return run.finish("qualified" if qualified else "positive_control_small_failed",
                      qualification=measurements,ood_authorized=qualified,
                      parameter_count=int(sum(np.prod(x.shape) for x in jax.tree_util.tree_leaves(params))))


def evaluate_control(args):
    run=Path(args.run)
    summary=json.loads((run/"summary.json").read_text())
    clean_path=run/"qualification_clean.json"
    if not clean_path.exists():
        raise RuntimeError("D4-disjoint small-maze qualification is required before OOD")
    clean=json.loads(clean_path.read_text())
    if not clean.get("ood_authorized",False):
        raise RuntimeError("Small-maze positive control must qualify before opening larger test mazes")
    # Fixed final EMA only: larger sets cannot select a checkpoint.
    model=MazeNCA()
    dummy=maze_initialize(jnp.zeros((1,9,9),jnp.int32),jax.random.PRNGKey(0))
    template=model.init(jax.random.PRNGKey(0),dummy)["params"]
    checkpoint=run/"ckpt/final.msgpack"
    digest=sha256(checkpoint.read_bytes()).hexdigest()
    if digest!=clean["checkpoint_sha256"]:
        raise RuntimeError("Checkpoint changed after small-maze qualification")
    if (run/"positive_control_gate.json").exists() or (run/"ood_started.json").exists():
        raise FileExistsError("OOD evaluation is write-once; preserve the existing result and use a new experiment")
    write_json(run/"ood_started.json",dict(checkpoint_sha256=digest,offset59=args.offset59,
               offset201=args.offset201,test_noise_sigma=args.test_noise_sigma))
    params=serialization.from_bytes(template,checkpoint.read_bytes())
    measurements=[]
    for size,count,depth,batch in ((59,256,2000,16),(201,64,13000,4)):
        path=Path(args.data)/f"test_{size}.npz"
        offset=args.offset59 if size==59 else args.offset201
        with np.load(path) as d:
            tokens,labels=d["tokens"][offset:offset+count],d["labels"][offset:offset+count]
        if len(tokens)!=count:raise ValueError("Not enough untouched confirmation mazes")
        rows=[]
        for seed in (20001,20002,20003):
            metric,pred=evaluate_maze(model,params,tokens,labels,depth,seed,batch,args.test_noise_sigma)
            row=dict(size=size,depth=depth,inference_seed=seed,official_start_index=offset,test_noise_sigma=args.test_noise_sigma,**metric)
            rows.append(row);measurements.append(row)
            np.savez_compressed(run/f"eval/ood_{size}_s{seed}.npz",predictions=pred,tokens=tokens,labels=labels)
            print(json.dumps(row),flush=True)
        write_json(run/f"eval/ood_{size}.json",dict(measurements=rows,data_sha256=sha256(path.read_bytes()).hexdigest()))
    passed=all(x["exact_path_accuracy"]>=.95 for x in measurements)
    result=dict(positive_control_passed=passed,checkpoint_sha256=sha256(checkpoint.read_bytes()).hexdigest(),
                qualification=clean["qualification"],ood=measurements,
                scope="paper-based architecture/training reproduction; prespecified subsets, three inference seeds",
                small_gate="at least 99% exact path at D=100,400,800 on first 512 D4-disjoint, D4-unique official 9x9 test mazes",
                ood_gate=f"at least 95% exact path in each inference seed: 256 59x59 from index {args.offset59} at D=2000; 64 201x201 from index {args.offset201} at D=13000",
                richer_tasks_paused=True)
    write_json(run/"positive_control_gate.json",result)
    return result


def qualify_control(args):
    """Score a fixed final checkpoint on clean small mazes without retraining."""
    run=Path(args.run)
    model=MazeNCA()
    dummy=maze_initialize(jnp.zeros((1,9,9),jnp.int32),jax.random.PRNGKey(0))
    template=model.init(jax.random.PRNGKey(0),dummy)["params"]
    checkpoint=run/"ckpt/final.msgpack"
    params=serialization.from_bytes(template,checkpoint.read_bytes())
    with np.load(Path(args.data)/"train_9.npz") as d:training=d["tokens"]
    with np.load(Path(args.data)/"test_9.npz") as d:tokens,labels=d["tokens"],d["labels"]
    indices,audit=clean_qualification(training,tokens,512)
    tokens,labels=tokens[indices],labels[indices]
    results=[]
    for depth in (100,400,800):
        metric,pred=evaluate_maze(model,params,tokens,labels,depth,20001,64)
        results.append(dict(size=9,depth=depth,**metric))
        np.savez_compressed(run/f"eval/clean_9_d{depth}.npz",tokens=tokens,labels=labels,predictions=pred)
        print(json.dumps(results[-1]),flush=True)
    out=dict(qualification=results,ood_authorized=all(x["exact_path_accuracy"]>=.99 for x in results),
             checkpoint_sha256=sha256(checkpoint.read_bytes()).hexdigest(),split_audit=audit,
             selection="fixed final EMA, no OOD checkpoint selection")
    write_json(run/"qualification_clean.json",out)
    return out


def audit_maze_depth(args):
    """Diagnostic reuse of opened control boards; never a fresh final test."""
    run=Path(args.run)
    model=MazeNCA()
    dummy=maze_initialize(jnp.zeros((1,9,9),jnp.int32),jax.random.PRNGKey(0))
    template=model.init(jax.random.PRNGKey(0),dummy)["params"]
    checkpoint=run/"ckpt/final.msgpack"
    params=serialization.from_bytes(template,checkpoint.read_bytes())
    with np.load(Path(args.data)/"test_201.npz") as d:
        tokens,labels=d["tokens"][:args.count],d["labels"][:args.count]
    depths=(13000,26000,52000)
    @jax.jit
    def predict(t,key):
        initial=maze_initialize(t,jax.random.fold_in(key,100001))
        saved=jnp.zeros((len(depths),)+t.shape,jnp.uint8)
        def body(carry,i):
            state,preds=carry
            out=maze_step(model,params,state,t,jax.random.fold_in(key,i))
            for slot,depth in enumerate(depths):
                preds=jax.lax.cond(i==depth-1,lambda p:p.at[slot].set(maze_prediction(out,t)),lambda p:p,preds)
            return (out,preds),None
        (final,saved),_=jax.lax.scan(body,(initial,saved),jnp.arange(max(depths)))
        return saved,jnp.all(jnp.isfinite(final))
    predictions=[]
    for start in range(0,len(tokens),4):
        board=tokens[start:start+4]
        padded=np.concatenate([board,np.repeat(board[-1:],4-len(board),0)])
        pred,finite=predict(jnp.asarray(padded),jax.random.fold_in(jax.random.PRNGKey(20001),start))
        if not bool(finite):raise FloatingPointError("Depth audit diverged")
        predictions.append(np.asarray(pred)[:,:len(board)])
        print(json.dumps(dict(event="depth_audit_batch",completed=min(start+4,len(tokens)),total=len(tokens))),flush=True)
    predictions=np.concatenate(predictions,axis=1)
    rows=[dict(size=201,depth=depth,**maze_metrics(p,labels,tokens)) for depth,p in zip(depths,predictions)]
    out=dict(scope="diagnostic reuse of first opened 201x201 mazes; not a fresh final test",results=rows,
             checkpoint_sha256=sha256(checkpoint.read_bytes()).hexdigest())
    np.savez_compressed(run/"eval/depth_audit_201.npz",tokens=tokens,labels=labels,predictions=predictions,depths=depths)
    write_json(run/"depth_audit_201.json",out)
    return out


def record_maze_animation(args):
    """Record exactly the evaluation RNG stream for an explicitly selected board."""
    run=Path(args.run)
    size=args.size
    batch=16 if size==59 else 4
    depth=2000 if size==59 else 13000
    start=(args.index//batch)*batch
    slot=args.index-start
    model=MazeNCA()
    template=model.init(jax.random.PRNGKey(0),maze_initialize(jnp.zeros((1,9,9),jnp.int32),jax.random.PRNGKey(0)))["params"]
    params=serialization.from_bytes(template,(run/"ckpt/final.msgpack").read_bytes())
    with np.load(Path(args.data)/f"test_{size}.npz") as d:
        tokens,labels=d["tokens"][start:start+batch],d["labels"][args.index]
    save_steps=np.unique(np.rint(np.linspace(0,depth,65)).astype(int))
    @jax.jit
    def record(t,key):
        state=maze_initialize(t,jax.random.fold_in(key,100001))
        saved=jnp.zeros((len(save_steps),size,size,2)).at[0].set(state[slot,...,:2])
        def body(carry,i):
            state,snapshots=carry
            out=maze_step(model,params,state,t,jax.random.fold_in(key,i))
            save=jnp.any(i+1==jnp.asarray(save_steps[1:]))
            index=jnp.sum(jnp.asarray(save_steps)<=i+1)-1
            snapshots=jax.lax.cond(save,lambda s:s.at[index].set(out[slot,...,:2]),lambda s:s,snapshots)
            return (out,snapshots),None
        (final,saved),_=jax.lax.scan(body,(state,saved),jnp.arange(depth))
        return saved,maze_prediction(final,t)[slot]
    scores,pred=record(jnp.asarray(tokens),jax.random.fold_in(jax.random.PRNGKey(20001),start))
    path=run/f"eval/animation_{size}_i{args.index}.npz"
    np.savez_compressed(path,tokens=tokens[slot],labels=labels,scores=np.asarray(scores),steps=save_steps,predictions=np.asarray(pred))
    return dict(file=str(path),official_index=args.index,size=size,final_errors=int((np.asarray(pred)!=labels).sum()),
                scope="same batch shape, common RNG and checkpoint as inference seed20001 evaluation")


def main():
    parser=argparse.ArgumentParser(__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    prepare=sub.add_parser("prepare")
    prepare.add_argument("archive");prepare.add_argument("destination");prepare.add_argument("--size",type=int,required=True)
    train=sub.add_parser("train")
    train.add_argument("--train",required=True);train.add_argument("--validation",required=True)
    train.add_argument("--seed",type=int,default=0);train.add_argument("--updates",type=int,default=5000)
    train.add_argument("--batch",type=int,default=64);train.add_argument("--validation-count",type=int,default=512)
    train.add_argument("--log-every",type=int,default=100)
    train.add_argument("--resume",type=Path)
    evaluate=sub.add_parser("evaluate")
    evaluate.add_argument("--run",required=True);evaluate.add_argument("--data",required=True)
    evaluate.add_argument("--offset59",type=int,default=0);evaluate.add_argument("--offset201",type=int,default=0)
    evaluate.add_argument("--test-noise-sigma",type=float,default=0.)
    qualify=sub.add_parser("qualify")
    qualify.add_argument("--run",required=True);qualify.add_argument("--data",required=True)
    audit=sub.add_parser("depth-audit")
    audit.add_argument("--run",required=True);audit.add_argument("--data",required=True)
    audit.add_argument("--count",type=int,default=16)
    animation=sub.add_parser("animation")
    animation.add_argument("--run",required=True);animation.add_argument("--data",required=True)
    animation.add_argument("--size",type=int,choices=(59,201),required=True);animation.add_argument("--index",type=int,required=True)
    args=parser.parse_args()
    if args.command == "prepare":
        print(json.dumps(prepare_archive(args.archive,args.destination,args.size),indent=2))
    elif args.command == "train":
        print(json.dumps(train_maze(args),indent=2))
    elif args.command == "evaluate":
        print(json.dumps(evaluate_control(args),indent=2))
    elif args.command == "qualify":
        print(json.dumps(qualify_control(args),indent=2))
    elif args.command == "depth-audit":
        print(json.dumps(audit_maze_depth(args),indent=2))
    else:
        print(json.dumps(record_maze_animation(args),indent=2))


if __name__ == "__main__":
    main()
