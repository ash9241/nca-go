"""Local policy/ownership heads with a single pooled pass and winrate readout."""
from dataclasses import dataclass
import numpy as np
import jax
import jax.numpy as jnp
from flax import linen as nn
from .model import NCA,ModelConfig


def inputs(position,recent_moves=(),komi=7.5):
    b = position.board
    features = np.zeros(b.shape+(10,),np.float32)
    features[...,0] = b == position.to_move
    features[...,1] = b == 3-position.to_move
    for i,p in enumerate(list(recent_moves)[-5:][::-1]):
        if p is not None:
            features[p[0],p[1],2+i] = 1
    if position.previous is not None:
        from ncago.go.rules import play_array
        for p in map(tuple,np.argwhere(b == 0).tolist()):
            after,legal = play_array(b,*p,position.to_move)
            if legal and after.tobytes() == position.previous:
                features[p[0],p[1],7] = 1
    features[...,8] = komi/100.
    features[...,9] = 1. if position.to_move == 1 else -1.
    return features


class PlayerNCA(nn.Module):
    config: ModelConfig

    @nn.compact
    def __call__(self,state):
        c = self.config
        delta = NCA(c,name="cells")(state)
        out = state[...,c.input_channels:c.input_channels+c.output_channels]
        local = nn.Dense(2,name="local_heads")(out)
        pooled = jnp.concatenate([out.mean(axis=(-3,-2)),out.max(axis=(-3,-2))],axis=-1)
        global_values = nn.Dense(2,name="pooled_heads")(pooled)
        logits = jnp.concatenate([local[...,0].reshape(state.shape[0],-1),global_values[:,0:1]],axis=-1)
        ownership = jnp.tanh(local[...,1])
        winrate_logit = global_values[:,1]
        return delta,logits,ownership,winrate_logit


def initialize(features,key,c,previous=None):
    state = jax.random.normal(key,features.shape[:-1]+(c.channels,))*c.init_sigma if previous is None else previous
    return state.at[...,:c.input_channels].set(features)


def rollout(model,params,state,features,key,steps,adaptive=False,noise=True,return_states=False,keep_history=True):
    c = model.config
    def body(state,i):
        delta,_,own,_ = model.apply({"params":params},state)
        rate = jnp.where(jnp.abs(own) > .95,.4,c.fire_rate) if adaptive else c.fire_rate
        fire = jax.random.bernoulli(jax.random.fold_in(key,i),rate,state.shape[:-1])
        delta = delta.at[...,:c.input_channels].set(0)
        out = state+fire[...,None]*delta
        if noise:
            k = jax.random.fold_in(key,i+steps+1)
            temporal,spatial,gaussian = jax.random.split(k,3)
            mask = jax.random.bernoulli(temporal,.1,(out.shape[0],1,1))&jax.random.bernoulli(spatial,.2,out.shape[:-1])
            out += mask[...,None]*(jnp.arange(c.channels) >= c.input_channels)*jax.random.normal(gaussian,out.shape)*.15
        _,policy,ownership,win = model.apply({"params":params},out)
        return out,(policy,ownership,win,fire,out) if return_states else (policy,ownership,win,fire)
    if keep_history:
        return jax.lax.scan(body,state,jnp.arange(steps))
    if return_states:
        raise ValueError("return_states requires keep_history")
    def terminal_body(carry,i):
        current,count = carry
        final,values = body(current,i)
        return (final,count+values[3].astype(jnp.int32)),None
    (final,count),_ = jax.lax.scan(terminal_body,(state,jnp.zeros(state.shape[:-1],jnp.int32)),jnp.arange(steps))
    _,policy,ownership,win = model.apply({"params":params},final)
    return final,(policy,ownership,win,count)


@dataclass
class Node:
    position: object
    prior: np.ndarray | None = None
    visits: np.ndarray | None = None
    values: np.ndarray | None = None
    children: dict | None = None
    state: object = None
    recent: tuple = ()


class PUCT:
    """Values are Black win probabilities, negated when selecting for White."""
    def __init__(self,evaluate,c_puct=1.5,warm=True):
        self.evaluate = evaluate
        self.c_puct = c_puct
        self.warm = warm

    def expand(self,node):
        n = len(node.position.board)
        policy,value,state = self.evaluate(node.position,node.state if self.warm else None,node.recent)
        legal = node.position.legal_moves()
        indices = [n*n if p is None else p[0]*n+p[1] for p in legal]
        prior = np.zeros(n*n+1,float)
        prior[indices] = np.asarray(policy)[indices]
        if prior.sum() == 0:
            prior[indices] = 1.
        prior /= prior.sum()
        node.prior,node.state = prior,state
        node.visits = np.zeros_like(prior)
        node.values = np.zeros_like(prior)
        node.children = {}
        return float(value)

    def search(self,root,visits,time_limit=None):
        import time
        started = time.perf_counter()
        if root.prior is None:
            self.expand(root)
        for _ in range(visits):
            if time_limit is not None and time.perf_counter()-started >= time_limit and root.visits.sum() > 0:
                break
            node,path = root,[]
            while node.prior is not None and node.position.passes < 2:
                q = np.divide(node.values,node.visits,out=np.zeros_like(node.values),where=node.visits > 0)
                perspective = q if node.position.to_move == 1 else -q
                score = perspective+self.c_puct*node.prior*np.sqrt(node.visits.sum()+1)/(1+node.visits)
                score[node.prior == 0] = -np.inf
                action = int(np.argmax(score))
                path.append((node,action))
                if action not in node.children:
                    n = len(node.position.board)
                    point = None if action == n*n else divmod(action,n)
                    node.children[action] = Node(node.position.play(point),state=node.state if self.warm else None,recent=(node.recent+(point,))[-5:])
                node = node.children[action]
            if node.position.passes == 2:
                value = 1. if node.position.score() > 0 else 0.
            else:
                value = self.expand(node)
            for parent,action in reversed(path):
                parent.visits[action] += 1
                parent.values[action] += 2*value-1
        action = int(np.argmax(root.visits))
        n = len(root.position.board)
        return (None if action == n*n else divmod(action,n)),root.children[action]
