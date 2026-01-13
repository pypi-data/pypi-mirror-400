from spb import plot_vector
from sympy import classify_ode, diff, latex, solve
from sympy.abc import y


def plot_ode(ode, x_range, f_range, n=10, **kwargs):
    """Afbild et linjefelt

    Parametre
    ---------
    - ode : Expression
        - 1. ordens differentialligning.

    - x_range : tuple
        - Interval for den uafhængige variabel (x, start, stop)

    - f_range : tuple
        - Interval for den afhængige variabel (f, start, stop)

    - n : int, optional
        - Antallet af punkter (i begge retninger). Standardværdi: 10

    - kwargs : se `vector_field_2d`

    Returnerer
    ---------
    - plt : Plot
        - Plotobjektet.

    Se også
    ---------
    - [SPB: vector_field_2d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/vectors.html#spb.graphics.vectors.vector_field_2d)
    """

    if all(item not in classify_ode(ode) for item in ["1st_linear", "1st_exact", "1st_power_series"]):
        e = "plot_ode virker kun med differentialligninger af første grad."
        raise ValueError(e)

    kwargs.setdefault("use_cm", False)
    kwargs.setdefault("scalar", False)
    kwargs.setdefault("normalize", True)
    kwargs.setdefault("quiver_kw", {"color": "black", "headwidth": 1, "headlength": 0, "pivot": "mid"})
    kwargs.setdefault("aspect", "auto")
    kwargs.setdefault("use_latex", True)

    x, f = x_range[0], f_range[0]
    df = solve(ode, diff(f(x), x))[0].replace(f(x), y)

    f_range = (y, f_range[1], f_range[2])

    dx_scaled = 1 / (x_range[2] - x_range[1])
    df_scaled = df / (f_range[2] - f_range[1])
    kwargs.setdefault("label", f"${latex(ode)}$")

    return plot_vector([dx_scaled, df_scaled], x_range, f_range, n=n, **kwargs)
