import click


@click.command()
@click.option("-f", "--flag", is_flag=True)
def main(flag:bool):
    print(f"hello {flag}")
