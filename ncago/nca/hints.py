"""Exact local teacher for intermediate capped-liberty discovery states.

IDs and teacher states are used only to construct training labels. They are
never supplied to the neural cell or used in neural inference.
"""
import jax.numpy as jnp


def initial_ids(tokens):
    cap = tokens.shape[-2]*tokens.shape[-1]+1
    return jnp.full(tokens.shape+(4,), cap, jnp.int32)


def id_step(state, tokens, firing):
    h, w = tokens.shape[-2:]
    cap = h*w+1
    padded_tokens = jnp.pad(tokens, ((0, 0), (1, 1), (1, 1)), constant_values=3)
    padded_state = jnp.pad(state, ((0, 0), (1, 1), (1, 1), (0, 0)), constant_values=cap)
    ids = jnp.broadcast_to(jnp.arange(h*w).reshape(h, w), tokens.shape)
    padded_ids = jnp.pad(ids, ((0, 0), (1, 1), (1, 1)), constant_values=cap)
    candidates = [state]
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        neighbor = padded_tokens[:, 1+dr:1+dr+h, 1+dc:1+dc+w]
        received = padded_state[:, 1+dr:1+dr+h, 1+dc:1+dc+w]
        empty_id = padded_ids[:, 1+dr:1+dr+h, 1+dc:1+dc+w]
        candidates.append(jnp.where((neighbor == tokens)[..., None], received, cap))
        candidates.append(jnp.where(neighbor == 0, empty_id, cap)[..., None])
    ordered = jnp.sort(jnp.concatenate(candidates, -1), axis=-1)
    distinct = jnp.concatenate([jnp.ones(ordered.shape[:-1]+(1,), bool),
                                ordered[..., 1:] != ordered[..., :-1]], -1)
    next_ids = jnp.sort(jnp.where(distinct, ordered, cap), axis=-1)[..., :4]
    active = (tokens == 1) | (tokens == 2)
    return jnp.where((active & firing)[..., None], next_ids, state)


def discovered_count(state, tokens):
    cap = tokens.shape[-2]*tokens.shape[-1]+1
    return jnp.sum(state < cap, axis=-1)
