"""Freeze fresh final sets and evaluate proportional depth and causal pairs."""
import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import time
import numpy as np
import yaml
import jax
import jax.numpy as jnp
from flax import serialization
from ncago.go.research_data import OnlineStream, witness_set
from ncago.go.research_tasks import minimal_cycle_pair, simple_eye_counts, minimal_eye_cycle_pair, balanced_eye_cycle_pair, capturing_cycle_pair, balanced_capture_cycle_pair
from ncago.go.generators import canonical_key
from ncago.nca.model import initialize, init_params, step, readout, perception_inputs
from functools import partial
from .checkpoint_audit import chain_features
from .common import ROOT, Run, write_json
from .research_train import build_model, make_predict, evaluate, metrics, validation_data, stability_assessment, class_names


def load_run(path, checkpoint="final.msgpack"):
    path = Path(path)
    config = yaml.safe_load((path / "config.yaml").read_text())
    config.setdefault("task", "liberties")
    model, mc = build_model(config)
    state = initialize(jnp.zeros((1, 9, 9), jnp.int32), jax.random.PRNGKey(0), mc)
    template = (model.init(jax.random.PRNGKey(0), state[..., :mc.input_channels])["params"]
                if config["model"] == "resnet" else init_params(model, state, jax.random.PRNGKey(0)))
    blob = (path / "ckpt" / checkpoint).read_bytes()
    return model, mc, serialization.from_bytes(template, blob), config, sha256(blob).hexdigest()


def opened_board_hashes():
    """Snapshot previously saved board positions, without reading predictions."""
    hashes, datasets, seen_raw = set(), [], set()
    paths = set((ROOT / 'results').glob('*/**/data/*.npz'))
    paths.update((ROOT / 'results/research_validation').glob('*/*.npz'))
    paths.update((ROOT / 'results/research_final_data').glob('*/*.npz'))
    for path in sorted(paths):
        with np.load(path) as data:
            name = 'boards' if 'boards' in data else ('board' if 'board' in data else None)
            if name is None:
                continue
            boards = data[name]
            if boards.ndim == 2:
                boards = boards[None]
            if boards.ndim != 3 or boards.shape[1] != boards.shape[2]:
                continue
            added = 0
            for board in boards:
                if len(board) not in (9, 13, 19, 25, 37):
                    continue
                raw = len(board), board.tobytes()
                if raw in seen_raw:
                    continue
                seen_raw.add(raw)
                hashes.add(sha256(canonical_key(board)).digest())
                added += 1
            datasets.append(dict(file=str(path.relative_to(ROOT)), sha256=sha256(path.read_bytes()).hexdigest(),
                                 newly_seen_raw_boards=added))
    return hashes, datasets


def paired_edit_distances(boards, queries):
    """A local prediction can react as soon as its nearest edited cell arrives."""
    nearest, farthest = [], []
    for index in range(0, len(boards), 2):
        edited = np.argwhere(boards[index] != boards[index+1])
        if not len(edited):
            raise ValueError('A witness pair must contain a changed input cell')
        distances = np.abs(edited-np.asarray(queries[index])).max(1)
        nearest.extend([int(distances.min())]*2)
        farthest.extend([int(distances.max())]*2)
    return np.asarray(nearest), np.asarray(farthest)


def board_test_keys(size, draw, identifiers=True, namespace='main'):
    salt = int.from_bytes(sha256(namespace.encode()).digest()[:4], 'little')
    fire = jax.random.fold_in(jax.random.fold_in(jax.random.PRNGKey(101001 if identifiers else 101001+draw), salt), size)
    ids = jax.random.fold_in(jax.random.fold_in(jax.random.PRNGKey(102001+draw if identifiers else 102001), salt), size)
    return fire, ids


def pair_test_keys(size, kind, draw, identifiers=True, proportional=False, namespace='main'):
    """Fresh fields by size/family; matched models and pair members share keys."""
    context = 100*('witness', 'cycle_pairs', 'race_witness', 'eye_witness').index(kind)+size
    fire_base, id_base = (105001, 106001) if proportional else (103001, 104001)
    salt = int.from_bytes(sha256(namespace.encode()).digest()[:4], 'little')
    fire = jax.random.fold_in(jax.random.fold_in(jax.random.PRNGKey(fire_base if identifiers else fire_base+draw), salt), context)
    ids = jax.random.fold_in(jax.random.fold_in(jax.random.PRNGKey(id_base+draw), salt), context) if identifiers else None
    return fire, ids


def freeze_sets(runs, namespace, seed=100001, count=256, require_gates=True, primary_runs=None):
    sources = [load_run(r) for r in runs]
    config = sources[0][3]
    if any(s[3]["cap"] != config["cap"] or s[3]["task"] != config["task"] for s in sources):
        raise ValueError("Matched final evaluation requires the same task and cap")
    designated = primary_runs if primary_runs is not None else [p for p, s in zip(runs, sources)
                                                               if s[3]['model'] == 'nca' and s[1].identifier_channels]
    primary_paths = {str(Path(p).resolve()) for p in designated}
    if not primary_paths.issubset({str(Path(p).resolve()) for p in runs}):
        raise ValueError("Primary runs must be included among the sealed source checkpoints")
    if require_gates:
        qualified = []
        primary_seeds = set()
        primary_recipes = []
        for path, source in zip(runs, sources):
            summary = json.loads((Path(path) / "summary.json").read_text())
            if str(Path(path).resolve()) in primary_paths and source[3]["model"] == "nca" and source[1].identifier_channels:
                primary_seeds.add(source[3]["seed"])
                nine = [r["stone_accuracy"] for r in summary["results"] if r["size"] == 9 and r["depth"] == 128]
                invariance = max(nine)-min(nine) <= .002
                assessment = stability_assessment(summary["results"])
                qualified.append(bool(assessment["stability_gate"] and assessment["useful_accuracy"] and invariance))
                if source[3].get("warmstart_sha256") or (Path(path) / "initialization.json").exists():
                    raise RuntimeError("Primary replication must use independent scratch initialization")
                primary_recipes.append({k: v for k, v in source[3].items() if k != "seed"})
        if not qualified or not all(qualified):
            raise RuntimeError("Final larger tests blocked: a designated primary ID NCA has not passed stability and ID-range gates")
        if len(primary_seeds) < 3:
            raise RuntimeError("Primary final evaluation requires three independent ID-NCA training seeds")
        if any(recipe != primary_recipes[0] for recipe in primary_recipes[1:]):
            raise RuntimeError("Primary training seeds must share a single prospective recipe")
    out = ROOT / "results/research_final_data" / namespace
    if (out / "manifest.json").exists():
        raise FileExistsError("A frozen final namespace cannot be regenerated")
    # Snapshot exclusions before creating any new namespace files. Previous
    # checkpoint tests are descriptive evidence, never new final examples.
    previously_opened_hashes, opened_datasets = opened_board_hashes()
    out.mkdir(parents=True, exist_ok=True)
    manifest = dict(namespace=namespace, seed=seed, count=count, cap=config["cap"], task=config["task"],
                    main_stability_and_ID_gate_enforced=require_gates,
                    source_checkpoints=[dict(run=Path(p).name, seed=s[3]["seed"], kind=s[3]["model"],
                                             sha256=s[4], primary=str(Path(p).resolve()) in primary_paths,
                                             model_config=asdict(s[1])) for p, s in zip(runs, sources)],
                    label_definition=config.get("label_definition", "distinct liberty count capped at "+str(config["cap"])),
                    selection="recipe frozen before final data generation", files=[])
    manifest['previously_opened_datasets'] = opened_datasets
    manifest['excluded_previously_opened_canonical_positions'] = len(previously_opened_hashes)
    training_hashes = set()
    for source in runs:
        hashfile = Path(source) / "data/training_canonical_hashes.npz"
        if not hashfile.exists():
            raise RuntimeError("Final split requires saved or reconstructed online training canonical hashes")
        with np.load(hashfile) as d:
            training_hashes.update(bytes(row) for row in d["hashes"])
    manifest["excluded_training_canonical_positions"] = len(training_hashes)
    def pair_overlap(boards):
        keys = [sha256(canonical_key(board)).digest() for board in boards]
        return dict(training_overlap=np.asarray([key in training_hashes for key in keys]),
                    previously_opened_overlap=np.asarray([key in previously_opened_hashes for key in keys]))
    for size in (9, 13, 19, 25, 37):
        stream = OnlineStream(seed+size, (size,), size, config["cap"], task=config["task"])
        exclusions = {canonical_key(b) for pair in validation_data(config).values() for b in pair[0]}
        boards, labels, accepted_sources = [], [], []
        rejected_training, rejected_opened = 0, 0
        for _ in range(count*100):
            b, y = stream.draw(1)
            key = canonical_key(b[0])
            if sha256(key).digest() in training_hashes:
                rejected_training += 1
                continue
            if sha256(key).digest() in previously_opened_hashes:
                rejected_opened += 1
                continue
            if key in exclusions:
                continue
            exclusions.add(key)
            boards.append(b[0]); labels.append(y[0])
            accepted_sources.append(stream.last_sources[0])
            if len(boards) == count:
                break
        if len(boards) != count:
            raise RuntimeError("Fresh final board generation exhausted")
        features = np.stack([chain_features(np.where(b >= 4, np.where(b % 2 == 0, 1, 2), b)) for b in boards])
        max_diameter = np.asarray([max(1, int(f[..., 1].max())) for f in features])
        path = out / f"boards_{size}.npz"
        np.savez_compressed(path, boards=np.stack(boards), labels=np.stack(labels),
                            sources=np.asarray(accepted_sources), features=features, maximum_chain_diameter=max_diameter)
        manifest["files"].append(dict(name=path.name, sha256=sha256(path.read_bytes()).hexdigest(),
                                     sampled_sources=stream.source_draw_counts,
                                     accepted_sources={s: accepted_sources.count(s) for s in set(accepted_sources)},
                                     rejected_training_positions=rejected_training,
                                     rejected_previously_opened_positions=rejected_opened,
                                     class_stone_support=np.bincount(np.stack(labels)[np.stack(labels)>=0], minlength=config["cap"]).tolist()))
        if config["task"] == "liberties":
            path = out / f"witness_{size}.npz"
            high_counts = (1, 5, 6, 8, 10, 12, 14, 15) if config['cap'] == 16 else None
            data = witness_set(size, per_geometry=8, seed=seed+1000+size, liberty_counts=high_counts, cap=config['cap'])
            np.savez_compressed(path, **data, **pair_overlap(data['boards']))
            manifest["files"].append(dict(name=path.name, sha256=sha256(path.read_bytes()).hexdigest(),
                                         witness_base_liberty_counts=list(high_counts or (1,))))
        if config["task"] == "race":
            boards, queries, labels, nodes = [], [], [], []
            rng = np.random.default_rng(seed+3000+size)
            for i in range(16):
                answer = balanced_capture_cycle_pair(size, rng, to_move=1+i % 2)
                if answer is None:
                    continue
                pair, q, y, solved = answer
                boards.extend(pair); queries.extend((q, q)); labels.extend(y)
                nodes.extend(a.nodes for a in solved)
            path = out / f"race_witness_{size}.npz"
            plain = [np.where(b >= 4, np.where(b % 2 == 0, 1, 2), b) for b in boards]
            nearest, farthest = paired_edit_distances(boards, queries)
            np.savez_compressed(path, boards=np.stack(boards), queries=np.asarray(queries), labels=np.asarray(labels),
                                oracle_nodes=np.asarray(nodes), **pair_overlap(boards),
                                causal_distance=nearest, farthest_edit_distance=farthest,
                                geometries=np.asarray(["two_point_eye"]*len(boards)))
            manifest["files"].append(dict(name=path.name, sha256=sha256(path.read_bytes()).hexdigest(),
                                         interpretation="outcome-changing two-stone witness at fixed6-vs-6 liberties; separate from invariant cycle controls"))
        if config["task"] == "eyes":
            boards, queries, labels, geometries = [], [], [], []
            rng = np.random.default_rng(seed+4000+size)
            for geometry in ("straight", "elbow", "snake", "comb", "branched"):
                for _ in range(8):
                    a, b, q = balanced_eye_cycle_pair(size, rng, geometry)
                    boards.extend((a, b)); queries.extend((q, q)); geometries.extend((geometry, geometry))
                    labels.extend((int(simple_eye_counts(a, config["cap"]-1)[q]), int(simple_eye_counts(b, config["cap"]-1)[q])))
            distances = [int(np.abs(np.argwhere(boards[i] != boards[i+1])-queries[i]).max()) for i in range(0, len(boards), 2)]
            path = out / f"eye_witness_{size}.npz"
            np.savez_compressed(path, boards=np.stack(boards), queries=np.asarray(queries), labels=np.asarray(labels),
                                geometries=np.asarray(geometries), causal_distance=np.repeat(distances, 2), **pair_overlap(boards))
            manifest["files"].append(dict(name=path.name, sha256=sha256(path.read_bytes()).hexdigest(),
                                         interpretation="outcome-changing corner-eye witness at an unchanged exact liberty set; diagonal and cycle change together"))
        if config["task"] in ("liberties", "eyes", "race"):
            pairs, queries, targets = [], [], []
            rng = np.random.default_rng(seed+2000+size)
            for i in range(16):
                if config["task"] == "race":
                    answer = capturing_cycle_pair(size, rng, liberty_count=1+i//4, to_move=1+i % 2)
                    if answer is None:
                        continue
                    (a, b), q, y, _ = answer
                elif config["task"] == "eyes":
                    a, b, q = minimal_eye_cycle_pair(size, rng, ("straight", "elbow", "snake", "comb", "branched")[i % 5])
                else:
                    a, b, q = minimal_cycle_pair(size, rng, inner_empty=config['cap'] <= 4 and i % 2 == 0,
                                                 liberty_count=min(config['cap'], i+1) if config['cap'] > 4 else (1+i//2 if i % 2 else None))
                pairs.extend((a, b)); queries.extend((q, q))
                if config["task"] == "eyes":
                    targets.extend((int(simple_eye_counts(a, config["cap"]-1)[q]), int(simple_eye_counts(b, config["cap"]-1)[q])))
                elif config["task"] == "liberties":
                    from ncago.go.research_data import count_labels
                    targets.extend((int(count_labels(a, config["cap"])[q]), int(count_labels(b, config["cap"])[q])))
                else:
                    targets.extend(y)
            if not pairs:
                raise RuntimeError("No cycle race pairs received proved labels")
            path = out / f"cycle_pairs_{size}.npz"
            nearest, farthest = paired_edit_distances(pairs, queries)
            np.savez_compressed(path, boards=np.stack(pairs), queries=np.asarray(queries), labels=np.asarray(targets),
                                causal_distance=nearest, farthest_edit_distance=farthest, **pair_overlap(pairs))
            manifest["files"].append(dict(name=path.name, sha256=sha256(path.read_bytes()).hexdigest()))
        print(f"Frozen final data size{size}", flush=True)
    write_json(out / "manifest.json", manifest)
    return out


def make_coupled_predict(predict):
    @partial(jax.jit, static_argnames=("depths",))
    def coupled(params, tokens, fire_keys, id_keys, depths):
        result = jax.vmap(lambda t, f, i: predict(params, t[None], f, depths, i)[0][:, 0])(tokens, fire_keys, id_keys)
        return jnp.swapaxes(result, 0, 1)
    return coupled


def paired_predict(predict, params, data, depths, fire_key, id_key, batch=16):
    """Pair members share EVERY random input and firing draw by construction."""
    boards, queries = data["boards"], data["queries"]
    output = np.empty((len(depths), len(boards)), np.int32)
    for start in range(0, len(boards), batch):
        indices = np.arange(start, min(start+batch, len(boards)))
        pair_ids = jnp.asarray(indices//2)
        fire = jax.vmap(lambda i: jax.random.fold_in(fire_key, i))(pair_ids)
        ids = fire if id_key is None else jax.vmap(lambda i: jax.random.fold_in(id_key, i))(pair_ids)
        p = np.asarray(predict(params, jnp.asarray(boards[indices]), fire, ids, depths))
        q = queries[indices]
        output[:, indices] = p[:, np.arange(len(indices)), q[:, 0], q[:, 1]]
    if np.any(output < 0):
        raise FloatingPointError("Nonfinite paired prediction")
    return output


def make_variable_predict(model, mc, feedforward=False):
    """Exact per-board D, fixed scan shape, and stable per-board random keys."""
    @partial(jax.jit, static_argnames=("maximum_depth",))
    def predict(params, tokens, fire_keys, id_keys, required, maximum_depth):
        initial = jax.vmap(lambda t, k: initialize(t[None], k, mc)[0])(tokens, id_keys)
        if feedforward:
            logits = model.apply({"params": params}, perception_inputs(initial, mc)[..., :mc.input_channels])
            return jnp.where(jnp.all(jnp.isfinite(logits), axis=-1), jnp.argmax(logits, -1), -2)
        def body(state, index):
            keys = jax.vmap(lambda k: jax.random.fold_in(k, index))(fire_keys)
            out = jax.vmap(lambda s, t, k: step(model, params, s[None], t[None], k)[0][0])(state, tokens, keys)
            return jnp.where((index < required)[:, None, None, None], out, state), None
        final, _ = jax.lax.scan(body, initial, jnp.arange(maximum_depth))
        return readout(model, params, final)[0]
    return predict


def make_multi_variable_predict(model, mc, feedforward=False):
    """Gather several exact per-board horizons from one shared forward path."""
    @partial(jax.jit, static_argnames=("maximum_depth",))
    def predict(params, tokens, fire_keys, id_keys, required, maximum_depth):
        initial = jax.vmap(lambda t, k: initialize(t[None], k, mc)[0])(tokens, id_keys)
        if feedforward:
            logits = model.apply({"params": params}, perception_inputs(initial, mc)[..., :mc.input_channels])
            p = jnp.where(jnp.all(jnp.isfinite(logits), axis=-1), jnp.argmax(logits, -1), -2)
            return jnp.broadcast_to(p, (required.shape[0],)+p.shape)
        saved = jnp.full((required.shape[0],)+tokens.shape, -2, jnp.int32)
        def body(carry, index):
            state, saved = carry
            keys = jax.vmap(lambda k: jax.random.fold_in(k, index))(fire_keys)
            final = jax.vmap(lambda s, t, k: step(model, params, s[None], t[None], k)[0][0])(state, tokens, keys)
            state = jnp.where((index < required.max(0))[:, None, None, None], final, state)
            prediction = readout(model, params, state)[0]
            saved = jnp.where((index+1 == required)[..., None, None], prediction[None], saved)
            return (state, saved), None
        (_, saved), _ = jax.lax.scan(body, (initial, saved), jnp.arange(maximum_depth))
        return saved
    return predict


def variable_predictions(predict, params, boards, required, fire_seed, id_seed, paired=False, batch=16, pad_batches=True):
    output = np.full((required.shape[0],)+boards.shape, -2, np.int32)
    buckets = 2**np.ceil(np.log2(required.max(0))).astype(int)
    for bucket in sorted(set(buckets)):
        selected = np.flatnonzero(buckets == bucket)
        for start in range(0, len(selected), batch):
            indices = selected[start:start+batch]
            # Repeat the last independent board to keep every compilation's
            # batch shape fixed. Real boards retain their original RNG keys
            # and exact horizons; discard the extra independent predictions.
            compute_indices = np.pad(indices, (0, batch-len(indices)), mode='edge') if pad_batches else indices
            ids = jnp.asarray(compute_indices//2 if paired else compute_indices)
            fire = jax.vmap(lambda i: jax.random.fold_in(fire_seed, i))(ids)
            keys = jax.vmap(lambda i: jax.random.fold_in(id_seed, i))(ids)
            result = np.asarray(predict(params, jnp.asarray(boards[compute_indices]), fire, keys,
                                        jnp.asarray(required[:, compute_indices]), int(bucket)))
            output[:, indices] = result[:, :len(indices)]
    return output


def paired_variable_predict(predict, params, data, required, fire_key, id_key, batch=16):
    boards = data["boards"]
    output = np.full(len(boards), -2, np.int32)
    buckets = 2**np.ceil(np.log2(required)).astype(int)
    for bucket in sorted(set(buckets)):
        selected = np.flatnonzero(buckets == bucket)
        for start in range(0, len(selected), batch):
            indices = selected[start:start+batch]
            pair_ids = jnp.asarray(indices//2)
            fire = jax.vmap(lambda i: jax.random.fold_in(fire_key, i))(pair_ids)
            ids = jax.vmap(lambda i: jax.random.fold_in(id_key, i))(pair_ids)
            prediction = np.asarray(predict(params, jnp.asarray(boards[indices]), fire, ids,
                                            jnp.asarray(required[indices]), int(bucket)))
            queries = data["queries"][indices]
            output[indices] = prediction[np.arange(len(indices)), queries[:, 0], queries[:, 1]]
    if np.any(output < 0):
        raise FloatingPointError("Nonfinite pair prediction")
    return output


def evaluate_run(path, namespace, ratios=(.5, 1., 2., 4.), draws=8):
    model, mc, params, config, digest = load_run(path)
    feedforward = config["model"] == "resnet"
    predict = make_predict(model, mc, feedforward)
    coupled_predict = make_coupled_predict(predict)
    variable_predict = make_multi_variable_predict(model, mc, feedforward)
    data_path = ROOT / "results/research_final_data" / namespace
    manifest = json.loads((data_path / "manifest.json").read_text())
    for file in manifest["files"]:
        if sha256((data_path / file["name"]).read_bytes()).hexdigest() != file["sha256"]:
            raise RuntimeError(f"Frozen data checksum mismatch: {file['name']}")
    if not any(r["sha256"] == digest for r in manifest["source_checkpoints"]):
        raise RuntimeError("Checkpoint was not included when the final dataset was sealed")
    run = Run("research_evaluation", dict(namespace=namespace, checkpoint_sha256=digest,
                                         model=config["model"], task=config["task"], cap=config["cap"],
                                         ratios=list(ratios), draws=draws,
                                         pair_key_scope='namespace,size,family,draw,and fixed/proportional trajectory;coupled within pairs and across models'), config["seed"])
    records, paired, id_checks = [], [], []
    for size in (9, 13, 19, 25, 37):
        with np.load(data_path / f"boards_{size}.npz") as d:
            boards, labels, diameters = d["boards"], d["labels"], d["maximum_chain_diameter"]
        depths_per_board = {ratio: np.maximum(1, np.ceil(ratio*diameters)).astype(int) for ratio in ratios}
        # Fixed array scan lengths avoid a separate compile for every diameter.
        # Bucket to powers of two; predictions are gathered at the exact D.
        previous_draw = {}
        for draw in range(draws if mc.identifier_channels else 3):
            fire_seed, id_seed = board_test_keys(size, draw, bool(mc.identifier_channels), namespace)
            all_required = np.stack([depths_per_board[ratio] for ratio in ratios])
            all_output = variable_predictions(variable_predict, params, boards, all_required, fire_seed, id_seed)
            for ratio, required, output in zip(ratios, all_required, all_output):
                np.savez_compressed(run.path / "eval" / f"size{size}_ratio{ratio}_draw{draw}.npz", predictions=output, depths=required)
                records.append(dict(size=size, ratio=ratio, draw=draw, min_depth=int(required.min()), max_depth=int(required.max()),
                                    **metrics(output, labels, mc.classes, config["task"])))
                if mc.identifier_channels and ratio in previous_draw:
                    mask = labels >= 0
                    id_checks.append(dict(size=size, ratio=ratio, draw=draw,
                                          disagreement_from_draw0=float((output[mask] != previous_draw[ratio][mask]).mean())))
                previous_draw.setdefault(ratio, output.copy())
            print(f"{config['model']} s{config['seed']} final{size} draw{draw}", flush=True)
        for kind in ("witness", "cycle_pairs", "race_witness", "eye_witness"):
            filename = data_path / f"{kind}_{size}.npz"
            if not filename.exists():
                continue
            with np.load(filename) as d:
                data = {k: d[k] for k in d.files}
            features = [chain_features(np.where(b >= 4, np.where(b % 2 == 0, 1, 2), b)) for b in data["boards"]]
            max_diameter = max(int(f[..., 1].max()) for f in features)
            depths = tuple(sorted(set((32, 128, 512, 1024, max(1, max_diameter), 2*max_diameter, 4*max_diameter))))
            for draw in range(draws if mc.identifier_channels else 3):
                fixed_fire, fixed_ids = pair_test_keys(size, kind, draw, bool(mc.identifier_channels), namespace=namespace)
                p = paired_predict(coupled_predict, params, data, depths,
                                   fixed_fire, fixed_ids)
                np.savez_compressed(run.path / "eval" / f"{kind}_{size}_draw{draw}.npz", predictions=p, depths=depths)
                for depth, pred in zip(depths, p):
                    if 'causal_distance' in data and config["model"] != "resnet":
                        radius = depth*(2 if config["model"] == "rcnn" else 1)
                        outside_cone = radius < data["causal_distance"][::2]
                        if np.any(pred[::2][outside_cone] != pred[1::2][outside_cone]):
                            raise AssertionError("Causal witness violated its coupled local receptive field")
                    for geometry in (sorted(set(data["geometries"])) if "geometries" in data else ["minimal_corner_break"]):
                        mask = data["geometries"] == geometry if "geometries" in data else np.ones(len(pred), bool)
                        correct = pred[mask] == data["labels"][mask]
                        training_seen = np.any(data.get('training_overlap', np.zeros(len(pred), bool))[mask].reshape(-1, 2), axis=1)
                        opened_seen = np.any(data.get('previously_opened_overlap', np.zeros(len(pred), bool))[mask].reshape(-1, 2), axis=1)
                        unseen = ~(training_seen | opened_seen)
                        matrix = np.bincount(mc.classes*data["labels"][mask]+pred[mask], minlength=mc.classes**2).reshape(mc.classes, mc.classes)
                        paired.append(dict(kind=kind, size=size, depth=depth, depth_over_maximum_diameter=depth/max(1, max_diameter),
                                           draw=draw, geometry=str(geometry), pairs=int(mask.sum()//2),
                                           pair_both_correct=float(np.all(correct.reshape(-1, 2), axis=1).mean()),
                                           training_overlap_pairs=int(training_seen.sum()), previously_opened_overlap_pairs=int(opened_seen.sum()), unseen_pairs=int(unseen.sum()),
                                           unseen_pair_both_correct=float(np.all(correct.reshape(-1, 2), axis=1)[unseen].mean()) if unseen.any() else None,
                                           query_accuracy=float(correct.mean()), prediction_invariance=float((pred[mask][::2] == pred[mask][1::2]).mean()),
                                           confusion=matrix.tolist(), overcounts=int(np.triu(matrix, 1).sum()) if config["task"] != "race" else None, undercounts=int(np.tril(matrix, -1).sum()) if config["task"] != "race" else None))
                query_diameters = np.asarray([max(1, int(f[tuple(q)][1])) for f, q in zip(features, data["queries"])])
                pair_diameters = np.repeat(query_diameters.reshape(-1, 2).max(1), 2)
                all_required = np.stack([np.maximum(1, np.ceil(ratio*pair_diameters)).astype(int) for ratio in ratios])
                ratio_fire, ratio_ids = pair_test_keys(size, kind, draw, bool(mc.identifier_channels), proportional=True, namespace=namespace)
                grid_predictions = variable_predictions(variable_predict, params, data['boards'], all_required,
                                                        ratio_fire, jax.random.PRNGKey(106001) if ratio_ids is None else ratio_ids, paired=True)
                query = data['queries']
                all_predictions = grid_predictions[:, np.arange(len(query)), query[:, 0], query[:, 1]]
                if np.any(all_predictions < 0):
                    raise FloatingPointError("Nonfinite paired prediction")
                for ratio, required, pred in zip(ratios, all_required, all_predictions):
                    np.savez_compressed(run.path / "eval" / f"{kind}_{size}_ratio{ratio}_draw{draw}.npz", predictions=pred, depths=required)
                    for geometry in (sorted(set(data["geometries"])) if "geometries" in data else ["minimal_corner_break"]):
                        mask = data["geometries"] == geometry if "geometries" in data else np.ones(len(pred), bool)
                        correct = pred[mask] == data["labels"][mask]
                        training_seen = np.any(data.get('training_overlap', np.zeros(len(pred), bool))[mask].reshape(-1, 2), axis=1)
                        opened_seen = np.any(data.get('previously_opened_overlap', np.zeros(len(pred), bool))[mask].reshape(-1, 2), axis=1)
                        unseen = ~(training_seen | opened_seen)
                        matrix = np.bincount(mc.classes*data["labels"][mask]+pred[mask], minlength=mc.classes**2).reshape(mc.classes, mc.classes)
                        # Coupled randomness makes the receptive-field bound
                        # deterministic for witnesses (except full-board FF).
                        if 'causal_distance' in data and config["model"] != "resnet":
                            radius = required*(2 if config["model"] == "rcnn" else 1)
                            outside_cone = radius[::2] < data["causal_distance"][::2]
                            if np.any(pred[::2][outside_cone] != pred[1::2][outside_cone]):
                                raise AssertionError("Causal witness violated its coupled local receptive field")
                        paired.append(dict(kind=kind, size=size, ratio=ratio, draw=draw, geometry=str(geometry),
                                           pairs=int(mask.sum()//2), min_depth=int(required[mask].min()), max_depth=int(required[mask].max()),
                                           pair_both_correct=float(np.all(correct.reshape(-1, 2), axis=1).mean()),
                                           training_overlap_pairs=int(training_seen.sum()), previously_opened_overlap_pairs=int(opened_seen.sum()), unseen_pairs=int(unseen.sum()),
                                           unseen_pair_both_correct=float(np.all(correct.reshape(-1, 2), axis=1)[unseen].mean()) if unseen.any() else None,
                                           query_accuracy=float(correct.mean()), prediction_invariance=float((pred[mask][::2] == pred[mask][1::2]).mean()),
                                           confusion=matrix.tolist(), overcounts=int(np.triu(matrix, 1).sum()) if config["task"] != "race" else None, undercounts=int(np.tril(matrix, -1).sum()) if config["task"] != "race" else None))
    return run.finish("complete", source_run=Path(path).name, model=config["model"],
                      task=config["task"], cap=config["cap"], model_config=asdict(mc), class_names=class_names(config["task"], config["cap"]),
                      records=records, paired=paired, identifier_checks=id_checks)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("freeze", "evaluate"))
    p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--count", type=int, default=256)
    p.add_argument("--seed", type=int, default=100001)
    p.add_argument("--draws", type=int, default=8)
    p.add_argument("--primary-runs", nargs="+", help="Designated prospective three-seed cohort; other runs are diagnostic")
    p.add_argument("--primary-gates-already-passed", action="store_true")
    args = p.parse_args()
    if args.action == "freeze":
        if args.primary_gates_already_passed:
            evidence_path = ROOT / 'results/cloud/research/main_qualification.json'
            evidence = json.loads(evidence_path.read_text())
            if not evidence.get('primary_gate_passed') or len(evidence['runs']) != 3:
                raise RuntimeError('Richer final tests require saved, passed three-seed main qualification')
        freeze_sets(args.runs, args.namespace, args.seed, args.count, require_gates=not args.primary_gates_already_passed, primary_runs=args.primary_runs)
        if args.primary_gates_already_passed:
            manifest_path = ROOT / 'results/research_final_data' / args.namespace / 'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['parent_gate_evidence_sha256'] = sha256(evidence_path.read_bytes()).hexdigest()
            manifest['parent_gate_source_runs'] = [row['run'] for row in evidence['runs']]
            write_json(manifest_path, manifest)
    else:
        for run in args.runs:
            evaluate_run(run, args.namespace, draws=args.draws)


if __name__ == "__main__":
    main()
