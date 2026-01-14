from pathlib import Path
import click

from .allure import AllureResults

from .codeberg import CodebergPackageDownloader


@click.group
@click.option("--data_dir", default="./data")
@click.pass_context
def main(ctx: click.Context, data_dir):
    ctx.ensure_object(dict)
    ctx.obj["data_dir"] = Path(data_dir)
    ctx.obj["data_dir"].mkdir(exist_ok=True)


@main.command
@click.option(
    "--package", default="results_funfedi_connect", help="The results to display"
)
@click.option("--package_version", default="0.1.3", help="The version to display")
@click.option(
    "--as_allure_results",
    is_flag=True,
    default=False,
    help="Extracts into the allure-results directory",
)
@click.pass_context
def download(ctx: click.Context, package, package_version, as_allure_results: bool):
    downloader = CodebergPackageDownloader(package, package_version)
    downloader.download_latest(ctx.obj["data_dir"])

    if as_allure_results:
        allure_results = AllureResults()
        file_directory = downloader.target_directory(ctx.obj["data_dir"])
        allure_results.extract(file_directory)


if __name__ == "__main__":
    main()
