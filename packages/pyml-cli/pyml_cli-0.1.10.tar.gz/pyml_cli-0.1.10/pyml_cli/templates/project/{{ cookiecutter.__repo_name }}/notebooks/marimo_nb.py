import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import numpy as np
    return (np,)


@app.cell
def _(np):
    A = np.array([0, 1, 2])
    B = np.array([3, 4, 5])
    return A, B


@app.cell
def _(A, B):
    C = A + B
    return (C,)


@app.cell
def _(C):
    print(C)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
