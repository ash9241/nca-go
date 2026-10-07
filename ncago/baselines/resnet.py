from flax import linen as nn


class ResNet(nn.Module):
    classes: int
    blocks: int = 4
    width: int = 16
    residual_scale: float = 1.
    stem_initializer: object = None

    @nn.compact
    def __call__(self, inputs):
        initializer = self.stem_initializer or nn.initializers.lecun_normal()
        x = nn.relu(nn.Conv(self.width,(3,3),name="stem",kernel_init=initializer)(inputs))
        for i in range(self.blocks):
            residual = nn.relu(nn.Conv(self.width,(3,3),name=f"b{i}_a")(x))
            residual = nn.Conv(self.width,(3,3),name=f"b{i}_b")(residual)
            x = nn.relu(x+self.residual_scale*residual)
        return nn.Conv(self.classes,(1,1),name="head")(x)

    @property
    def receptive_field_radius(self):
        return 1+2*self.blocks


def parameter_count(tree):
    import jax
    return sum(x.size for x in jax.tree_util.tree_leaves(tree))


def matched_width(target, blocks, classes, input_channels=8):
    def params(w):
        return (9*input_channels*w+w) + blocks*2*(9*w*w+w)+(w*classes+classes)
    return min(range(1,1025),key=lambda w:abs(params(w)-target))
