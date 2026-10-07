import numpy as np
import pytest
import jax
import jax.numpy as jnp
import optax
import json
from argparse import Namespace
from hashlib import sha256
from flax import serialization

from ncago.experiments.maze_control import (MazeNCA, convert_public_maze,
    bfs_path, maze_initialize, maze_step, maze_prediction, augment_maze,
    damage_maze, make_maze_update)
from ncago.experiments.maze_control import clean_qualification, pruning_reference, evaluate_control


def example():
    tokens=np.array([[3,0,2],[2,0,2],[2,0,3]],np.uint8)
    return tokens,bfs_path(tokens)


def rendering(tokens,labels):
    colors=np.array([[1,1,1],[1,1,1],[0,0,0],[1,0,0]],np.uint8)
    rgb=colors[tokens]
    rgb[tuple(np.argwhere(tokens==3)[-1])]=[0,1,0]
    rgb=np.pad(np.repeat(np.repeat(rgb,2,0),2,1),((3,3),(3,3),(0,0)))
    target=np.pad(np.repeat(np.repeat(labels,2,0),2,1),((3,3),(3,3)))
    return rgb.transpose(2,0,1)[None],target[None]


def test_converter_preserves_path_and_rejects_corrupted_cells():
    tokens,labels=example()
    rgb,target=rendering(tokens,labels)
    actual,y=convert_public_maze(rgb,target,3)
    np.testing.assert_array_equal(actual[0],tokens)
    np.testing.assert_array_equal(y[0],labels)
    rgb[0,:,3,4]=0
    with pytest.raises(ValueError,match="2x2 blocks"):
        convert_public_maze(rgb,target,3)


def test_clues_survive_noise_and_damage_and_do_not_predict_wall_paths():
    tokens,_=example()
    t=jnp.asarray(tokens[None])
    model=MazeNCA()
    state=maze_initialize(t,jax.random.PRNGKey(1))
    params=model.init(jax.random.PRNGKey(2),state)["params"]
    # Make residual updates nonzero so the clamp actually gets exercised.
    params["update"]["bias"]=jnp.ones(16)
    for i in range(10):
        state=maze_step(model,params,state,t,jax.random.PRNGKey(i+3),.15)
        state=damage_maze(state,t,jax.random.PRNGKey(i+103))
    expected=np.eye(16)[tokens]
    np.testing.assert_array_equal(np.asarray(state)[0][tokens>=2],expected[tokens>=2])
    prediction=np.asarray(maze_prediction(state,t))[0]
    assert np.all(prediction[tokens==2]==0) and np.all(prediction[tokens==3]==1)


def test_d4_augmentation_preserves_bfs_solution():
    tokens,labels=example()
    t=jnp.repeat(jnp.asarray(tokens[None]),32,0)
    y=jnp.repeat(jnp.asarray(labels[None]),32,0)
    state=maze_initialize(t,jax.random.PRNGKey(1))
    s,t,y=augment_maze(state,t,y,jax.random.split(jax.random.PRNGKey(2),32))
    assert len({x.tobytes() for x in np.asarray(t)})>1
    for board,target in zip(np.asarray(t),np.asarray(y)):
        np.testing.assert_array_equal(bfs_path(board),target)
    np.testing.assert_array_equal(np.asarray(s)[np.asarray(t)>=2],np.eye(16)[np.asarray(t)[np.asarray(t)>=2]])


def test_all_step_loss_has_finite_nonzero_gradient():
    tokens,labels=example()
    t,y=jnp.asarray(tokens[None]),jnp.asarray(labels[None])
    state=maze_initialize(t,jax.random.PRNGKey(1))
    model=MazeNCA()
    params=model.init(jax.random.PRNGKey(2),state)["params"]
    optimizer=optax.chain(optax.clip_by_global_norm(1.),optax.adamw(.0004,weight_decay=0.))
    update=make_maze_update(model,optimizer,depth=4)
    params,opt,state,loss,norm=update(params,optimizer.init(params),state,t,y,jax.random.PRNGKey(3))
    assert np.isfinite(float(loss)) and 0<float(norm)<100
    assert np.isfinite(np.asarray(state)).all()


def test_qualification_excludes_rotated_training_and_duplicate_test_boards():
    a,_=example()
    b=a.copy();b[0,1]=2;b[1,0]=0
    c=b.copy();c[2,0]=0
    indices,audit=clean_qualification(np.array([a]),np.array([np.rot90(a),b,np.rot90(b),c]),2)
    np.testing.assert_array_equal(indices,[1,3])
    assert audit['test_train_d4_overlap']==1 and audit['test_d4_duplicates']==1


def test_local_pruning_oracle_handles_long_dead_end_branches():
    maze=np.full((9,9),2,np.uint8)
    maze[4,1:8]=0;maze[4,1]=maze[4,7]=3
    maze[1:4,4]=0
    prediction,rounds=pruning_reference(maze)
    np.testing.assert_array_equal(prediction,bfs_path(maze))
    assert rounds==3


def test_unqualified_control_cannot_open_larger_maze_sets(tmp_path):
    (tmp_path/'summary.json').write_text('{}')
    (tmp_path/'qualification_clean.json').write_text(json.dumps({'ood_authorized':False}))
    with pytest.raises(RuntimeError,match='must qualify'):
        evaluate_control(Namespace(run=tmp_path,data=tmp_path/'does_not_exist'))
    assert not (tmp_path/'ood_started.json').exists()


def test_changed_or_previously_evaluated_checkpoint_cannot_open_ood(tmp_path):
    (tmp_path/'summary.json').write_text('{}')
    (tmp_path/'ckpt').mkdir()
    payload=b'not even a valid checkpoint: gate must run before restore'
    (tmp_path/'ckpt/final.msgpack').write_bytes(payload)
    (tmp_path/'qualification_clean.json').write_text(json.dumps({'ood_authorized':True,'checkpoint_sha256':'wrong'}))
    args=Namespace(run=tmp_path,data=tmp_path/'does_not_exist',offset59=0,offset201=0,test_noise_sigma=0.)
    with pytest.raises(RuntimeError,match='Checkpoint changed'):
        evaluate_control(args)
    (tmp_path/'qualification_clean.json').write_text(json.dumps({'ood_authorized':True,'checkpoint_sha256':sha256(payload).hexdigest()}))
    (tmp_path/'positive_control_gate.json').write_text('{}')
    with pytest.raises(FileExistsError,match='write-once'):
        evaluate_control(args)
    assert not (tmp_path/'ood_started.json').exists()
