from chex import Array
from flax import nnx


class TransformeEncoderLayer(nnx.Module):
    def __init__(
        self,
        d_model: int,
        nhead: int,
        dim_feedforward: int,
        dropout_rate: float = 0.1,
        activation=nnx.relu,
        layer_norm_eps: float = 1e-5,
        norm_first: bool = False,
        use_bias: bool = True,
        *,
        rngs: nnx.Rngs,
    ):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.dim_feedforward = dim_feedforward
        self.norm_first = norm_first

        self.self_attn = nnx.MultiHeadAttention(
            d_model,
            nhead,
            dropout=dropout_rate,
            use_bias=use_bias,
            rngs=rngs,
        )
        self.linear1 = nnx.Linear(
            d_model, dim_feedforward, use_bias=use_bias, rngs=rngs
        )
        self.dropout = nnx.Dropout(dropout_rate)
        self.linear2 = nnx.Linear(
            dim_feedforward, d_model, use_bias=use_bias, rngs=rngs
        )

        self.norm1 = nnx.LayerNorm(
            d_model, epsilon=layer_norm_eps, use_bias=use_bias, rngs=rngs
        )
        self.norm2 = nnx.LayerNorm(
            d_model, epsilon=layer_norm_eps, use_bias=use_bias, rngs=rngs
        )
        self.dropout1 = nnx.Dropout(dropout_rate)
        self.dropout2 = nnx.Dropout(dropout_rate)

        self.activation = activation

    def __call__(
        self,
        x: Array,
        mask: Array | None = None,
        key_padding_mask: Array | None = None,
        is_causal: bool = False,
    ) -> Array: ...

    def _sa_block(
        self,
        x: Array,
        mask: Array | None = None,
        key_padding_mask: Array | None = None,
        is_causal: bool = False,
    ) -> Array:
        x = self.self_attn(
            x, mask=mask, key_padding_mask=key_padding_mask, is_causal=is_causal
        )
        x = self.dropout1(x)
        x = self.norm1(x)
        return x
