from hwo_disra.Yieldinator import Yieldinator


class StellarEvolutionYieldinator(Yieldinator):
    """
    This class extends the Yieldinator to handle stellar evolution-related yield calculations.
    """
    def __init__(self, sources) -> None:
        super().__init__('source count')
        self.sources = sources
