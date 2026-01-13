import click
from .conf import DIGITOS


def exibir_vwap(valor, symbol, verbose=False):
    if valor is None:
        click.echo("Nenhuma barra encontrada para calcular o VWAP.")
        return
    if verbose:
        click.echo(f"\nVWAP {symbol} {valor:.{DIGITOS}f}\n")
    else:
        click.echo(f"\n{valor:.{DIGITOS}f}\n")
