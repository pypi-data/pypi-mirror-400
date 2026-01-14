import click
from pyfloq import __version__
from pyfloq.chart import plot_bars
from pyfloq.timer import timer_start, format_duration
from pyfloq.database_handler import database_log, database_duration_query, database_list_labels
from pyfloq.timestamps import timestamp_normalize, timestamp_from_unix_ts, next_day_from_iso


@click.group()
@click.version_option(__version__)
def pyflo():
    pass


@pyflo.command()
@click.argument("label")
def track(label):
    click.echo(f"tracking {label}, press Return to stop.")
    start, stop, duration = timer_start(label)
    start, stop = timestamp_from_unix_ts(start), timestamp_from_unix_ts(stop)
    database_log(label, start, stop)
    click.echo(f"{format_duration(duration)} logged under {label}.")


@pyflo.command()
@click.argument("when")
@click.option("--to", help="specify another date to analyze a range")
@click.option(
    "--by",
    type=click.Choice(["day", "week", "label"]),
    default="week",
    show_default=True,
    required=True,
    help="grouping for the data, presented as separate bars",
)
@click.option("--filter", "-f", multiple=True, help="selective filtering for labels")
@click.option("--color", help="color for bars")
def vis(when, to, by, filter, color):
    when = timestamp_normalize(when)
    if to is None:
        to = next_day_from_iso(when)
    when, to = sorted([when, to])
    data = database_duration_query(when, to, by, filter)
    data.reverse()
    if len(data) == 0:
        click.echo('Nothing tracked in this time period.')
        return
    x, y, ylabel = zip(*[(x, float(y), format_duration(y)) for x, y in data])
    plot_bars(x, y, ylabel=ylabel, title='', color=color)


@pyflo.command()
@click.option("--filter", "-f", multiple=True, help="selective filtering")
def list(filter):
    click.echo(database_list_labels(filter))


if __name__ == "__main__":
    pyflo()
