import jax.numpy as jnp


def nimbus_softmax(logits):
    m = jnp.max(logits, axis=-1, keepdims=True)
    z = logits - m
    e = jnp.exp(z)
    s = jnp.sum(e, axis=-1, keepdims=True)
    return e / s


def nimbus_logsumexp(x):
    m = jnp.max(x, axis=-1, keepdims=True)
    y = x - m
    return jnp.squeeze(m, axis=-1) + jnp.log(jnp.sum(jnp.exp(y), axis=-1))


