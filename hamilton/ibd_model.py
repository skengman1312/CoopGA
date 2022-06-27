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
        self.tree = nx.DiGraph()
        super().__init__(N=N, r=r, dr=dr, mr=mr)
         #genalogy of the simulation represented as a tree DAG
        # TODO: adapt the datacollector module
    def reproduce(self):
        """
        1) Add the agents on the graph and perform generational turnover with a cutoff value
        2) Change reproductive model (larger families and a constrain on inbreeding)
        :return:
        """
        mating_ind = random.sample([agent for agent in self.schedule.agents], k=self.N)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2]) for i in range(len(mating_ind) // 2)]
        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), "family": p[0].unique_id} for p in
                  mating_pairs for i in range(10)]

        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        [self.schedule.add(FamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in
         range(len(newgen))]
    def step(self) -> None:
        """
        Change the social setting for the interactions (larger number of random recipients)
        #add "rooms" "active" as model variable
        :return:
        """
        pass
