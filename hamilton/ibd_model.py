from model import *
import networkx as nx
from nx_script import *


def tree_id(a):  # to be deleted
    pass


class IBDFamilyAgent(FamilyAgent):

    def altruistic_action(self):
        """
        The Actor has to calculate the Benefit = Sum_i(P_ibd(A, R_i)
        A = actor, R_i = ith recipient
        :return:
        """

        A_index = self.model.active.index(self.unique_id)
        A_room = self.model.room[A_index]

        # calculating the benefit
        # suppose tree_id( ) is a function that return the id of the agent in the graph
        b = 0
        for i in A_room:
            if A_room[i].unique_id != self.unique_id:
                b += ibd_coeff(self.model.tree, tree_id(self),
                               tree_id(A_room[i]))

        # self.model.tree
        if self.genotype:
            if b > 1:
                if random.random() > self.model.dr:
                    return
                else:
                    self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer(
            ) if a.family == self.family and a.unique_id != self.unique_id]

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
