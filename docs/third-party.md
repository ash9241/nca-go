# Attribution and related work

Original project source and generated scientific artifacts use the repository's MIT license. Third-party work retains its own license. Python dependencies are installed separately; their licenses are not replaced by this repository's license.

## Maze benchmark

The converted maze data in `maze-control-v1.zip` come from the University of Maryland's [Easy-to-Hard Data](https://github.com/aks2203/easy-to-hard-data) project by Avi Schwarzschild and collaborators. The source project and version 1.0.0 distribution declare MIT. Its [complete copyright and license notice](EASY_TO_HARD_LICENSE.txt) accompanies the converted data. Conversion, checksums, original archive URLs, and BFS label checks are recorded in `results/maze_data/*.json` inside the release.

We convert the published rendered RGB boards into logical cells by validating/collapsing 2×2 blocks and cropping the rendering border. This changes representation, not labels. The maze implementation in this repository is independently written from the cited paper's methods. No author endorsement or official reproduction status is implied.

## Research context

- Alexander Mordvintsev, Ettore Randazzo, Eyvind Niklasson, and Michael Levin. [Growing Neural Cellular Automata](https://distill.pub/2020/growing-ca/). Distill, 2020. Shared local neural updates, persistent state, and regeneration motivate the NCA framework.
- Arpit Bansal et al. [End-to-end Algorithm Synthesis with Recurrent Networks: Logical Extrapolation Without Overthinking](https://arxiv.org/abs/2202.05826). 2022. Input recall and progressive recurrent training motivate the positive-control requirement. The authors' [Deep Thinking implementation](https://github.com/aks2203/deep-thinking) was consulted as related work; a DT-Recall training reproduction was not run here.
- Mayalen Etcheverry et al. [Reasoning with Neural Cellular Automata](https://arxiv.org/abs/2609.36126). 2026, v1. The paper-based Maze-OOD implementation and replay/perturbation experiments use this as the primary methodological reference. Differences and failed reproduction gates are explicit in the README and methods.
- Tony T. Wang et al. [Adversarial Policies Beat Superhuman Go AIs](https://arxiv.org/abs/2211.00241). 2023 version. Cyclic Go positions motivate questions about global structure. Our synthetic tests do not evaluate their adversarial policies or establish the same failure mechanism.

These works provide context and methods. Their reported scores are not pooled with the experiments in this repository.
