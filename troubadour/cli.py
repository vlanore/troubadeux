import click


@click.command()
@click.option("-f", "--flag", is_flag=True)
def main(flag: bool):
    print(f"hello {flag}")
    f = open("index.html", "w")
    f.write("""<html>
<header></header>

<body>
    <h1>Hello</h1>
    testing GH pages w/ actions!
</body>

</html>""")
    f.close()
