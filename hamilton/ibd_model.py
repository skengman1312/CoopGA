from model import *
import networkx as nx


class IBDFamilyAgent(FamilyAgent):

    def altruistic_action(self):
        """
        The Actor has to calculate the Benefit = Sum_i(P_ibd(A, R_i)
        A = actor, R_i = ith recipient
        :return:
        """
        pass


class IBDFamilyModel(FamilyModel):
    pass

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        add graph to attributes
        """
        super().__init__(N=N, r=r, dr=dr, mr=mr)

    def reproduce(self):
        """
        1) Add the agents on the graph and perform generational turnover with a cutoff value
        2) Change reproductive model (larger families and a constrain on inbreeding)
        :return:
        """

    def step(self) -> None:
        """
        Change the social setting for the interactions (larger number of random recipients)
        :return:
        """
        pass
