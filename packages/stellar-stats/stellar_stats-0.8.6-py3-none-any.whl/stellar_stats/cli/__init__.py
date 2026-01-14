import click

from .run import run
from .gen_investors import gen_investors
from .gen_rebates import gen_rebates

# Optional imports for data generation commands
try:
    from .gen_data_from_cfmmc import gen_data_from_cfmmc
    HAS_CFMMC = True
except ImportError:
    HAS_CFMMC = False

try:
    from .gen_data_from_ibflex import gen_data_from_ibflex
    HAS_IBFLEX = True
except ImportError:
    HAS_IBFLEX = False


@click.group()
def main():
    """CLI tool for running Streamlit app"""
    pass


main.add_command(run)
main.add_command(gen_investors)
main.add_command(gen_rebates)

# Add optional commands only if dependencies are available
if HAS_CFMMC:
    main.add_command(gen_data_from_cfmmc)

if HAS_IBFLEX:
    main.add_command(gen_data_from_ibflex)


if __name__ == "__main__":
    main()
