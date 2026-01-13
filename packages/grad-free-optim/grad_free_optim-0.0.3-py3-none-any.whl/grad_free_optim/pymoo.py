from typing import Any, List

import numpy as np
import torch as tc
import torch.nn as nn
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from torch.optim.optimizer import ParamsT
from trading_models.utils import (
    DEVICE,
    LOSS_FN_TYPE,
    GIFMaker,
    plot_general,
    to_np,
    transpose_records,
)


def get_param_vec(params: ParamsT):
    return tc.cat([p.detach().flatten() for p in params]).numpy()


def set_param_vec(params: ParamsT, vec):
    idx = 0
    for p in params:
        N = p.numel()
        p.copy_(tc.tensor(vec[idx : idx + N]).reshape(p.shape))
        idx += N


class GradFreeOptim:
    def __init__(
        s,
        bound: List[float],
        net: nn.Module,
        train_data: Any,
        test_data: Any,
        loss_fn: LOSS_FN_TYPE,
        id="GradFreeOptim",
        f_test=50,
        f_plot=100,
    ):
        s.bound, s.net, s.loss_fn = bound, net, loss_fn
        s.train_data, s.test_data = train_data, test_data
        s.id, s.f_test, s.f_plot = id, f_test, f_plot

        net.to(DEVICE)
        s.records, s.gif = [], GIFMaker()
        s.best_score = -np.inf

        s.params = list(net.parameters())
        s.n_var = len(get_param_vec(s.params))
        print(f"n_var: {s.n_var}")

    def _get_loss(s, vec):
        set_param_vec(s.params, vec)

        loss_test, info_test, plots_test = np.nan, {}, {}
        if len(s.records) % s.f_test == 0:
            s.net.eval()
            loss_test, info_test, plots_test = s.loss_fn(s.test_data, "test")
            score = info_test["SCORE_test"]
            if score > s.best_score:
                s.best_score = score
                tc.save(s.net.state_dict(), f"{s.id}.tc")
            s.net.train()
        loss_train, info_train, plots_train = s.loss_fn(s.train_data, "train")
        rec = {"A_loss_train": loss_train, "A_loss_test": loss_test}
        s.records.append({**rec, **info_train, **info_test})
        if len(s.records) % s.f_plot == 0:
            plots = transpose_records(s.records)
            plots = {**plots, **plots_train, **plots_test}
            plot_general(dict(sorted(plots.items())), f"{s.id}.png")
            s.gif.add(f"{s.id}.png")
        return to_np(loss_train)

    @tc.no_grad()
    def run(s, algo):
        class Prob(ElementwiseProblem):
            def __init__(s2):
                xl, xu = s.bound
                super().__init__(n_var=s.n_var, n_obj=1, xl=xl, xu=xu)

            def _evaluate(s2, vec, out, *args, **kwargs):
                out["F"] = s._get_loss(vec)

        minimize(Prob(), algo)
        s.gif.save(s.id)
