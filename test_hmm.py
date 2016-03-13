import pytest
import numpy as np
import tensorflow as tf

from hmm import HMMNumpy, HMMTensorflow


@pytest.fixture
def latch_P():
    P = np.array([[0.5, 0.5], [0.0, 1.0]])
    # P = np.array([[0.5, 0.5], [0.5, 0.5]])
    # P = np.array([[0.5, 0.5], [0.0000000001, 0.9999999999]])
    # P = np.array([[0.5, 0.5], [1e-50, 1 - 1e-50]])

    for i in range(2):
        for j in range(2):
            print 'from', i, 'to', j, P[i, j]
    return P


@pytest.fixture
def latch_w():
    return np.array([0., 1.0])


@pytest.fixture
def hmm_latch(latch_w, latch_P):
    return HMMNumpy(latch_w, latch_P)


@pytest.fixture
def fair_w():
    return np.array([0.0, 1.0])


@pytest.fixture
def fair_P():
    return np.array([[0.5, 0.5], [0.5, 0.5]])


@pytest.fixture
def hmm_fair(fair_w, fair_P):
    return HMMNumpy(fair_w, fair_P)


@pytest.fixture
def hmm_tf_fair(fair_w, fair_P):
    return HMMTensorflow(fair_w, fair_P)


@pytest.fixture
def hmm_tf_latch(latch_w, latch_P):
    return HMMTensorflow(latch_w, latch_P)


def test_hmm_fair_forward_backward(hmm_fair):
    y = np.array([0, 0, 1, 1])
    posterior, f, b = hmm_fair.forward_backward(y)

    # if P is filled with 0.5, the only thing that matters is the emission
    # liklihood.  assert that the posterior is = the liklihood of y
    for i, yi in enumerate(y):
        liklihood = hmm_fair.lik(yi) / np.sum(hmm_fair.lik(yi))
        assert np.isclose(posterior[i,:], liklihood).all()

    # assert that posterior for any given t sums to 1
    assert np.isclose(np.sum(posterior, 1), 1).all()


def test_hmm_fair_forward_backward(hmm_fair):
    y = np.array([0, 0, 1, 1])
    posterior, f, b = hmm_fair.forward_backward(y)

    # if P is filled with 0.5, the only thing that matters is the emission
    # liklihood.  assert that the posterior is = the liklihood of y
    for i, yi in enumerate(y):
        liklihood = hmm_fair.lik(yi) / np.sum(hmm_fair.lik(yi))
        assert np.isclose(posterior[i,:], liklihood).all()

    # assert that posterior for any given t sums to 1
    assert np.isclose(np.sum(posterior, 1), 1).all()


def test_hmm_latch_two_step_no_noise(hmm_latch):
    for i in range(2):
        for j in range(2):
            y = [i, i, j, j]
            # y = [i, j]

            if i == 1 and j == 0:
                continue

            print '*'*80
            print y
            states, scores = hmm_latch.viterbi_decode(y)

            assert all(states == y)


def test_hmm_tf_partial_forward(hmm_tf_latch, hmm_latch):
    scoress = [
        np.log(np.array([0, 1])),
        np.log(np.array([1, 0])),
        np.log(np.array([0.25, 0.75])),
        np.log(np.array([0.5, 0.5])),
    ]

    for scores in scoress:
        tf_ret = tf.Session().run(hmm_tf_latch._viterbi_partial_forward(scores))
        np_ret = hmm_latch._viterbi_partial_forward(scores)

        assert (tf_ret == np_ret).all()


def test_hmm_tf_viterbi_decode(hmm_tf_latch, hmm_latch):
    ys = [
        np.array([0, 0]),
        np.array([1, 1]),
        np.array([0, 1]),
        np.array([0, 0.25, 0.5, 0.75, 1]),
    ]

    for y in ys:
        print y

        tf_s_graph, tf_scores_graph = hmm_tf_latch.viterbi_decode(y, len(y))
        tf_s = tf.Session().run(tf_s_graph)
        tf_scores = [tf_scores_graph[0]]
        tf_scores.extend([tf.Session().run(g) for g in tf_scores_graph[1:]])
        print np.array(tf_scores)

        np_s, np_scores = hmm_latch.viterbi_decode(y)
        print np_scores

        assert (tf_s == np_s).all()
        print
