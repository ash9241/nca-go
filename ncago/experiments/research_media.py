"""Render predetermined learned examples only from a sealed final namespace."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import imageio.v2 as imageio
import jax
import jax.numpy as jnp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from .common import ROOT, write_json
from .research_eval import load_run, pair_test_keys, board_test_keys
from .research_train import class_names
from .checkpoint_audit import chain_features
from ncago.go.research_data import count_labels
from ncago.go.research_tasks import simple_eye_counts
from ncago.nca.model import initialize, step, readout


def trace(model, mc, params, tokens, fire_keys, id_keys, depths):
    depths = tuple(depths)
    @jax.jit
    def run(params, tokens, fire_keys, id_keys):
        initial = jax.vmap(lambda t, k: initialize(t[None], k, mc)[0])(tokens, id_keys)
        saved = jnp.zeros((len(depths),)+initial.shape, initial.dtype)
        previous = readout(model, params, initial)[0]
        def body(carry, index):
            state, previous, saved = carry
            keys = jax.vmap(lambda k: jax.random.fold_in(k, index))(fire_keys)
            final = jax.vmap(lambda s, t, k: step(model, params, s[None], t[None], k)[0][0])(state, tokens, keys)
            p = readout(model, params, final)[0]
            matches = index+1 == jnp.asarray(depths)
            saved = jax.lax.cond(matches.any(), lambda a: a.at[jnp.argmax(matches)].set(final), lambda a: a, saved)
            active = tokens != 3
            mask = (tokens == 1) | (tokens == 2) | (tokens >= 4)
            change = jnp.sqrt(jnp.sum(jnp.where(active[..., None], (final[..., mc.input_channels:]-state[..., mc.input_channels:])**2, 0))/jnp.maximum(active.sum()*(mc.channels-mc.input_channels), 1))
            flips = jnp.sum((p != previous) & mask)/jnp.maximum(mask.sum(), 1)
            return (final, p, saved), jnp.stack((change, flips))
        (_, _, states), dynamics = jax.lax.scan(body, (initial, previous, saved), jnp.arange(max(depths)))
        predictions = jax.vmap(lambda state: readout(model, params, state)[0])(states)
        return states, predictions, dynamics
    return tuple(np.asarray(x) for x in run(params, jnp.asarray(tokens), fire_keys, id_keys))


def heatmap(ax, board, values, query=None, classes=4):
    mask = (board == 1) | (board == 2) | (board >= 4)
    palette = (ListedColormap(["#f4f6f8", "#3288bd", "#fdae61", "#d53e4f", "#6f4c9b"]) if classes == 4
               else ListedColormap(np.vstack(([.957, .965, .973, 1.], plt.cm.viridis(np.linspace(0, 1, classes))))))
    ax.imshow(np.where(mask, values+1, 0), cmap=palette, vmin=0, vmax=classes, interpolation="nearest")
    colors = np.where(board >= 4, np.where(board % 2 == 0, 1, 2), board)
    for color, face in ((1, "#18212a"), (2, "white")):
        stones = np.argwhere(colors == color)
        if len(stones):
            ax.scatter(stones[:, 1], stones[:, 0], s=max(2, 900/len(board)**2),
                       c=face, edgecolors="#18212a", linewidths=.25)
    if query is not None:
        ax.scatter(query[1], query[0], s=70, marker="s", facecolors="none", edgecolors="black", linewidths=1.5)
    ax.axis("off")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--saved", action="store_true", help="Render existing raw states without another rollout")
    args = parser.parse_args()
    model, mc, params, config, digest = load_run(args.run)
    if config['model'] != 'nca':
        raise ValueError("These predetermined animations illustrate learned NCAs")
    root = ROOT / 'results/research_final_data' / args.namespace
    manifest = json.loads((root / 'manifest.json').read_text())
    if not any(row['sha256'] == digest and row.get('primary') for row in manifest['source_checkpoints']):
        raise RuntimeError("Animation checkpoint must belong to the sealed primary cohort")
    for row in manifest['files']:
        if sha256((root / row['name']).read_bytes()).hexdigest() != row['sha256']:
            raise RuntimeError("Frozen final data checksum mismatch")
    out = ROOT / 'reports/research_followup/media' / args.run.name
    out.mkdir(parents=True, exist_ok=True)
    depths = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
    examples = []
    if config['task'] == 'liberties' and config['cap'] == 4:
        with np.load(root / 'boards_9.npz') as data:
            boards, targets = data['boards'][:1], data['labels'][:1]
        whole_fire, whole_ids = board_test_keys(9, 0, namespace=args.namespace)
        fire = jax.random.fold_in(whole_fire, 0)[None]
        ids = jax.random.fold_in(whole_ids, 0)[None]
        examples.append(('first_final_9', boards, targets, None, fire, ids, 'First final board; ID draw0; selected before predictions'))
    kind = {'liberties': 'witness', 'eyes': 'eye_witness', 'race': 'race_witness'}[config['task']]
    with np.load(root / f'{kind}_37.npz') as data:
        eligible = data['geometries'] == 'snake' if 'geometries' in data else None
        if config['task'] == 'liberties' and config['cap'] == 16:
            eligible &= data['base_liberty_count'] > 4
        index = 0 if config['task'] == 'race' else int(np.flatnonzero(eligible)[0])
        boards, queries, labels = data['boards'][index:index+2], data['queries'][index:index+2], data['labels'][index:index+2]
    if config['task'] == 'liberties':
        targets = np.stack([count_labels(b, config['cap']) for b in boards])
    elif config['task'] == 'eyes':
        targets = np.stack([simple_eye_counts(b, config['cap']-1) for b in boards])
    else:
        targets = np.stack([np.where((b == 1) | (b == 2) | (b >= 4), y, -1) for b, y in zip(boards, labels)])
    fixed_fire, fixed_ids = pair_test_keys(37, kind, 0, namespace=args.namespace)
    fire = jnp.stack([jax.random.fold_in(fixed_fire, index//2)]*2)
    ids = jnp.stack([jax.random.fold_in(fixed_ids, index//2)]*2)
    example_name = 'first_snake_37' if config['task'] == 'liberties' else f'first_{kind}_37'
    selection = ('First snake witness above cap4; ' if config['task'] == 'liberties' and config['cap'] == 16
                 else 'First prespecified witness family pair; ')
    examples.append((example_name, boards, targets, queries, fire, ids, selection+'coupled fixed-depth evaluator keys; ID draw0'))
    names = class_names(config['task'], config['cap'])
    records = []
    for name, boards, targets, queries, fire, ids, selection in examples:
        plain = np.where(boards >= 4, np.where(boards % 2 == 0, 1, 2), boards)
        diameter = max(int(chain_features(b)[..., 1].max()) for b in plain)
        depths = tuple(sorted(set(depths+(max(1, diameter), max(1, 2*diameter), max(1, 4*diameter)))))
        if queries is None:
            depths = tuple(sorted(set(depths+(max(1, int(np.ceil(.5*diameter))),))))
        if args.saved:
            with np.load(out / (name+'.npz')) as saved:
                assert np.array_equal(saved['boards'], boards) and np.array_equal(saved['targets'], targets)
                expected_queries = np.asarray(queries) if queries is not None else np.empty((0, 2))
                assert np.array_equal(saved['queries'], expected_queries)
                states, predictions, dynamics = saved['states'], saved['predictions'], saved['dynamics']
                depths = tuple(map(int, saved['depths']))
        else:
            states, predictions, dynamics = trace(model, mc, params, boards, fire, ids, depths)
            np.savez_compressed(out / (name+'.npz'), boards=boards, targets=targets, states=states,
                                predictions=predictions, dynamics=dynamics, depths=depths,
                                queries=np.asarray(queries) if queries is not None else np.empty((0, 2)))
        frames, query_predictions = [], []
        differences = None if queries is None else np.sqrt(np.mean((states[:, 0, ..., mc.input_channels:]-states[:, 1, ..., mc.input_channels:])**2, axis=-1))
        maximum_difference = max(float(differences.max()), 1e-8) if differences is not None else None
        for i, depth in enumerate(depths):
            fig, axes = plt.subplots(1, 3, figsize=(10, 4), dpi=100)
            if queries is None:
                heatmap(axes[0], boards[0], targets[0]); axes[0].set_title('Exact liberty classes')
                heatmap(axes[1], boards[0], predictions[i, 0]); axes[1].set_title('Learned liberty classes')
                mask = targets[0] >= 0
                accuracy = float((predictions[i, 0][mask] == targets[0][mask]).mean())
                axes[2].plot(np.arange(1, 1025), dynamics[:, 1], color='#3288bd')
                axes[2].axvline(128, color='black', ls='--', lw=1)
                axes[2].axvline(depth, color='#d53e4f', lw=1)
                axes[2].set(title=f'This board: {100*accuracy:.1f}% correct', xlabel='Update step', ylabel='Prediction flip fraction', xscale='log')
            else:
                q = tuple(queries[0])
                p = [int(predictions[i, j][tuple(queries[j])]) for j in (0, 1)]
                y = [int(targets[j][tuple(queries[j])]) for j in (0, 1)]
                query_predictions.append(p)
                for j in (0, 1):
                    heatmap(axes[j], boards[j], predictions[i, j], queries[j], mc.classes)
                    for changed in np.argwhere(boards[0] != boards[1]):
                        axes[j].scatter(changed[1], changed[0], s=70, marker='o', facecolors='none', edgecolors='cyan', linewidths=1.5)
                    title = (f'Pair {"AB"[j]}: query {names[p[j]]}\nTruth: {names[y[j]]}' if config['task'] == 'race'
                             else f'Pair {"AB"[j]}: query {names[p[j]]}; truth {names[y[j]]}')
                    axes[j].set_title(title, fontsize=11)
                im = axes[2].imshow(differences[i], vmin=0, vmax=maximum_difference, cmap='magma')
                axes[2].scatter(q[1], q[0], s=70, marker='s', facecolors='none', edgecolors='cyan')
                axes[2].set_title('Mutable-state difference'); axes[2].axis('off')
                fig.colorbar(im, ax=axes[2], shrink=.7)
            active = np.argwhere(boards[0] != 3)
            height, width = np.ptp(active, axis=0)+1
            domain = f'{height}×{width} capture board' if config['task'] == 'race' else f'{len(boards[0])}×{len(boards[0])}'
            fig.suptitle(f"Learned {config['task']} NCA · {domain} · step {depth}", fontsize=13)
            legend = 'blue1 · orange2 · red3 · purple4+' if mc.classes == 4 else ('Black capture / White capture / draw' if config['task'] == 'race' else f'Ordinal classes {names[0]}–{names[-1]}')
            fig.text(.5, .075, legend+'   |   Dot color identifies Black/White stones', ha='center', fontsize=9)
            fig.text(.5, .035, 'Predetermined example; aggregate results are separate', ha='center', fontsize=9)
            fig.subplots_adjust(top=.79, bottom=.18, left=.04, right=.96, wspace=.35)
            fig.canvas.draw(); frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()); plt.close(fig)
        imageio.mimsave(out / (name+'.gif'), frames, duration=700, loop=0)
        records.append(dict(name=name, selection=selection, steps=list(depths), query_predictions=query_predictions,
                            evaluator_files=([f'size9_ratio{ratio}_draw0.npz' for ratio in (.5, 1., 2., 4.)]
                                             if queries is None else [f'{kind}_37_draw0.npz']),
                            evaluator_board_indices=[0] if queries is None else [index, index+1]))
    write_json(out / 'manifest.json', dict(source_run=args.run.name, checkpoint_sha256=digest,
                                          final_namespace=args.namespace, examples=records,
                                          rendered_from_saved_states=args.saved,
                                          scope='Learned-model illustrations; no outcome-based example selection'))
    print(out, flush=True)


if __name__ == '__main__':
    main()
