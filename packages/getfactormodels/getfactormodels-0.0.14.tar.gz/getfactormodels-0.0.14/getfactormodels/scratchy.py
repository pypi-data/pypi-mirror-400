"""Key: R11_6

Source: CarhartFactors (or the underlying FF Momentum file)

Transformation: lambda x: x.rolling(6).mean()

Citation: Fama and French (1996); Hou, Xue, and Zhang (2015)

"""


from abc import abstractmethod

# Example: we want to implement the R^{11}1 and R^{11}6 and R^{11}12 from 
# "A Comparison of New Factor Models". 
#
# It's "Price momentum 11-month prior returns, {1,6,12}-month holding period), 
# Fama-French (1996)"
#
#
#
"""


"""
def FactorComputer(ABC):

    @abstractmethod
    def get_data(self):
        """Get data required for calculation."""
        ...

    @abstractmethod
    def transform(self):
        """Transform data, return a pa.Table of 'date' and 'factor' columns."""
        ...




