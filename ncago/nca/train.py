"""Replay sampling with online symmetries, perturbations, TBPTT, and EMA."""
from pathlib import Path
from functools import partial
import time
import numpy as np
import jax
import jax.numpy as jnp
import optax
from flax import serialization
from .model import initialize, init_params, step, supervised_loss, readout
from ncago.baselines.resnet import parameter_count


def augment(state, tokens, labels, task, rng, config):
    states, inputs, targets = [], [], []
    for s, t, y in zip(state,tokens,labels):
        rotation, reflection = int(rng.integers(4)), bool(rng.integers(2))
        s, t, y = [np.rot90(a,rotation,axes=(0,1)).copy() for a in (s,t,y)]
        if reflection:
            s,t,y = s[::-1].copy(),t[::-1].copy(),y[::-1].copy()
        if rng.random() < .5:
            t = np.array([0, 2, 1, 3, 7, 6, 5, 4], np.int8)[t]
            if task == "benson":
                y = np.where(y == 0,1,np.where(y == 1,0,y))
            elif task == "race":
                y = np.where(y == 0, 1, np.where(y == 1, 0, y))
        base = config.input_channels-getattr(config, "identifier_channels", 0)
        s[..., :base] = np.eye(base)[t]
        states.append(s)
        inputs.append(t)
        targets.append(y)
    return np.stack(states),np.stack(inputs),np.stack(targets)


def perturb(states,tokens,targets,boards,labels,model_config,config,rng):
    c = model_config
    for i in range(len(states)):
        if config["target_swap"] and rng.random() < .1:
            j = int(rng.integers(len(boards)))
            tokens[i], targets[i] = boards[j], labels[j]
            base = c.input_channels-getattr(c, "identifier_channels", 0)
            states[i,...,:base] = np.eye(base)[tokens[i]]
        if config["damage"] and rng.random() < .1:
            h,w = tokens.shape[-2:]
            rr,cc = np.ogrid[:h,:w]
            for _ in range(int(rng.integers(1,4))):
                cy,cx = rng.uniform(0,h),rng.uniform(0,w)
                rad = rng.uniform(.1,.4)*w
                mask = ((rr-cy)**2+(cc-cx)**2 <= rad**2)&(tokens[i] != 3)
                states[i,mask,c.input_channels:] = 0
    return states,tokens,targets


def train_nca(model,boards,labels,validation,config,seed,run,name="nca", initial=None):
    c = model.config
    rng = np.random.default_rng(seed)
    key = jax.random.PRNGKey(seed)
    batch = config["batch_size"]
    pool_size = 4*batch
    ids = rng.integers(len(boards),size=pool_size)
    tokens, targets = boards[ids].copy(), labels[ids].copy()
    states = np.array(initialize(jnp.asarray(tokens),key,c))
    params = init_params(model,jnp.asarray(states[:batch]),key) if initial is None else initial
    optimizer = optax.chain(optax.clip_by_global_norm(1.),optax.adamw(config["learning_rate"]))
    opt_state = optimizer.init(params)
    ema, best_ema = params, params
    n, chunk = config["rollout_steps"], config["chunk_steps"]
    if not 0 < chunk <= n:
        raise ValueError("chunk_steps must be in (0, rollout_steps]")

    @jax.jit
    def update(params,opt_state,ema,states,tokens,targets,key):
        start = jax.random.randint(jax.random.fold_in(key,999),(),0,n-chunk+1)
        def objective(p):
            def body(carry,index):
                state, losses = carry
                # Detach before and after the randomly sampled TBPTT window.
                state = jax.lax.cond(index == start, jax.lax.stop_gradient, lambda x:x, state)
                out,_ = step(model,p,state,tokens,jax.random.fold_in(key,index),noise_sigma=.15 if config["noise"] else 0.)
                loss = jax.lax.cond((index >= start)&(index < start+chunk),lambda _:supervised_loss(model,p,out,targets),lambda _:jnp.array(0.),None)
                out = jax.lax.cond(index == start+chunk-1,jax.lax.stop_gradient,lambda x:x,out)
                return (out,losses+loss),None
            (final,loss),_ = jax.lax.scan(body,(states,jnp.array(0.)),jnp.arange(n))
            return loss/chunk,final
        (loss,final),gradients = jax.value_and_grad(objective,has_aux=True)(params)
        updates,opt_state = optimizer.update(gradients,opt_state,params)
        params = optax.apply_updates(params,updates)
        ema = jax.tree_util.tree_map(lambda old,new:config["ema"]*old+(1-config["ema"])*new,ema,params)
        return params,opt_state,ema,final,loss,optax.global_norm(gradients)

    val_boards,val_labels = validation
    @jax.jit
    def validate(p):
        t = jnp.asarray(val_boards)
        s = initialize(t,jax.random.fold_in(key,500000),c)
        def body(state,i):
            return step(model,p,state,t,jax.random.fold_in(key,i))[0],None
        final,_ = jax.lax.scan(body,s,jnp.arange(max(config["evaluation_steps"])))
        pred,_ = readout(model,p,final)
        mask = val_labels >= 0
        return jnp.sum((pred == val_labels)&mask)/jnp.maximum(mask.sum(),1)

    best, started = -1.,time.perf_counter()
    for iteration in range(config["training_steps"]):
        selected = rng.choice(pool_size,batch,replace=False)
        s,t,y = states[selected].copy(),tokens[selected].copy(),targets[selected].copy()
        replace = rng.random(batch) < config["seed_fraction"] if config["replay"] else np.ones(batch,bool)
        fresh = rng.integers(len(boards),size=batch)
        t[replace],y[replace] = boards[fresh[replace]], labels[fresh[replace]]
        s[replace] = np.array(initialize(jnp.asarray(t[replace]),jax.random.fold_in(key,iteration+1),c))
        s,t,y = augment(s,t,y,config["task"],rng,c)
        s,t,y = perturb(s,t,y,boards,labels,c,config,rng)
        params,opt_state,ema,final,loss,grad_norm = update(params,opt_state,ema,jnp.asarray(s),jnp.asarray(t),jnp.asarray(y),jax.random.fold_in(key,iteration+1))
        value = float(loss)
        if not np.isfinite(value):
            raise FloatingPointError(f"Nonfinite loss in {name}, iteration {iteration}")
        states[selected],tokens[selected],targets[selected] = np.array(final),t,y
        if iteration % max(1,config["training_steps"]//10) == 0 or iteration == config["training_steps"]-1:
            score = float(validate(ema))
            if score > best:
                best,best_ema = score,ema
            run.log(event="train",model=name,iteration=iteration+1,loss=value,gradient_norm=float(grad_norm),validation_accuracy=score,elapsed_seconds=time.perf_counter()-started)
            print(f"{config['task']} {name} seed={seed} step={iteration+1}: loss={value:.4f}, validation={score:.4f}",flush=True)
    (run.path/"ckpt"/f"{name}.msgpack").write_bytes(serialization.to_bytes(best_ema))
    return best_ema,{"params":parameter_count(params),"training_seconds":time.perf_counter()-started,"validation_accuracy":best}


def train_resnet(model,boards,labels,validation,config,seed,run,name):
    rng = np.random.default_rng(seed)
    key = jax.random.PRNGKey(seed)
    optimizer = optax.chain(optax.clip_by_global_norm(1.),optax.adamw(config["learning_rate"]))
    params = model.init(key,jax.nn.one_hot(jnp.asarray(boards[:config["batch_size"]]),config["input_channels"]))["params"]
    opt_state = optimizer.init(params)
    ema,best_ema,best = params,params,-1.
    @jax.jit
    def update(params,opt_state,ema,t,y):
        mask = y >= 0
        def loss(p):
            logits = model.apply({"params":p},jax.nn.one_hot(t,config["input_channels"]))
            values = optax.softmax_cross_entropy_with_integer_labels(logits,jnp.maximum(y,0))
            return jnp.sum(jnp.where(mask,values,0))/jnp.maximum(mask.sum(),1)
        value,grads = jax.value_and_grad(loss)(params)
        changes,opt_state = optimizer.update(grads,opt_state,params)
        params = optax.apply_updates(params,changes)
        ema = jax.tree_util.tree_map(lambda a,b:config["ema"]*a+(1-config["ema"])*b,ema,params)
        return params,opt_state,ema,value
    vb,vy = validation
    @jax.jit
    def validate(p):
        pred = jnp.argmax(model.apply({"params":p},jax.nn.one_hot(jnp.asarray(vb),config["input_channels"])),axis=-1)
        mask = vy >= 0
        return jnp.sum((pred == vy)&mask)/jnp.maximum(mask.sum(),1)
    started = time.perf_counter()
    # Exactly the same number of optimizer steps and batch size as the NCA.
    for iteration in range(config["training_steps"]):
        ids = rng.integers(len(boards),size=config["batch_size"])
        t,y = boards[ids].copy(),labels[ids].copy()
        dummy = np.zeros(t.shape+(config["channels"],),np.float32)
        _,t,y = augment(dummy,t,y,config["task"],rng,type("InputConfig",(),{"input_channels":config["input_channels"]})())
        params,opt_state,ema,value = update(params,opt_state,ema,jnp.asarray(t),jnp.asarray(y))
        if not np.isfinite(float(value)):
            raise FloatingPointError(name)
        if iteration % max(1,config["training_steps"]//10) == 0 or iteration == config["training_steps"]-1:
            score = float(validate(ema))
            if score > best:
                best,best_ema = score,ema
            run.log(event="train",model=name,iteration=iteration+1,loss=float(value),validation_accuracy=score)
    (run.path/"ckpt"/f"{name}.msgpack").write_bytes(serialization.to_bytes(best_ema))
    print(f"{config['task']} {name}: validation={best:.4f}",flush=True)
    return best_ema,{"params":parameter_count(params),"training_seconds":time.perf_counter()-started,"validation_accuracy":best,"receptive_field_radius":model.receptive_field_radius}
