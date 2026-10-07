import numpy as np
import jax
import jax.numpy as jnp
from ncago.go.rules import Position
from ncago.go.engines import coordinate,parse_coordinate,teacher_arrays
from ncago.nca.model import ModelConfig
from ncago.nca.player import PlayerNCA,inputs,initialize,rollout,PUCT,Node
from ncago.go.sgfio import read_sgf,write_sgf


def test_coordinate_and_teacher_orientation():
    for size in (9,19,37):
        for p in ((0,0),(size-1,size-1),(3,7)):
            assert parse_coordinate(coordinate(p),size) == p
    n = 5
    reply = {"policy":list(range(n*n+1)),"ownership":list(range(n*n)),"rootInfo":{"scoreLead":3.,"winrate":.8}}
    policy,ownership,score,win = teacher_arrays(reply,n)
    assert ownership[0,0] == 20
    assert policy[0] > policy[n*(n-1)]
    np.testing.assert_allclose(policy.sum(),1.,atol=2e-7)


def test_player_frozen_features_and_heads():
    c = ModelConfig(channels=24,input_channels=10,heads=2)
    model = PlayerNCA(c)
    key = jax.random.PRNGKey(4)
    p = Position.empty(5).play((1,1))
    x = jnp.asarray(inputs(p,[(1,1)]))[None]
    state = initialize(x,key,c)
    params = model.init(key,state)["params"]
    final,values = rollout(model,params,state,x,key,3)
    np.testing.assert_array_equal(final[...,:10],x)
    assert values[0].shape == (3,1,26)
    assert values[1].shape == (3,1,5,5)
    assert values[2].shape == (3,1)
    terminal,heads = rollout(model,params,state,x,key,3,keep_history=False)
    np.testing.assert_allclose(terminal,final,atol=1e-6)
    for output,history in zip(heads[:3],values[:3]):
        np.testing.assert_allclose(output,history[-1],atol=1e-6)
    np.testing.assert_array_equal(heads[3],np.asarray(values[3]).sum(axis=0))


def test_player_training_with_labeled_child_perturbations():
    from ncago.experiments.player import train
    class RecordingRun:
        def __init__(self):
            self.events = []
        def log(self,**event):
            self.events.append(event)
    c = ModelConfig(channels=24,input_channels=10,heads=2)
    model = PlayerNCA(c)
    positions = [Position.empty(5).play((i,1)) for i in range(3)]
    x = np.stack([inputs(p) for p in positions])
    child = np.stack([inputs(p.play((i,2))) for i,p in enumerate(positions)])
    policy = np.ones((3,26),np.float32)/26
    own = np.zeros((3,5,5),np.float32)
    score = np.full(3,-7.5,np.float32)
    win = np.full(3,.5,np.float32)
    data = x,policy,own,score,win,child,policy,own,score,win
    run = RecordingRun()
    params = train(model,data,{"batch_size":2,"rollout_steps":2,"training_steps":3,
        "learning_rate":.0004,"ema":.9,"damage":True},0,run)
    assert all(np.isfinite(np.asarray(p)).all() for p in jax.tree_util.tree_leaves(params))
    assert len(run.events) == 3


def test_puct_legal_moves_and_color_perspective():
    p = Position.empty(5)
    def evaluate(position,state,recent):
        policy = np.ones(26)/26
        return policy,.7,None
    search = PUCT(evaluate)
    move,child = search.search(Node(p),3)
    assert move in p.legal_moves()
    assert child.position.to_move == 2
    assert child.position.board[move] == 1


def test_sgf_roundtrip(tmp_path):
    path = tmp_path/"game.sgf"
    moves = [(1,(0,0)),(2,(1,1)),(1,None)]
    write_sgf(path,9,moves)
    positions = read_sgf(path)
    assert len(positions) == 4
    assert positions[-1].board[0,0] == 1
    assert positions[-1].board[1,1] == 2
