import pandas

from model import *
import networkx as nx
from nx_script import *
from nx_script import IBDFamilyTree

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
        pre = str(self.model.schedule.steps) + "#"

        # self.model.tree
        if self.genotype:
            b = 0
            for i in A_room:
                if i.unique_id != self.unique_id:
                    b += self.model.tree.ibd_coeff(self.model.tree,
                                                   pre + self.unique_id, pre + i.unique_id)
            if b > 1:
                if random.random() > self.model.dr:
                    return
                else:
                    self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer(
            ) if a.family == self.family and a.unique_id != self.unique_id]


class IBDFamilyModel(FamilyModel):
    pass

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        add graph to attributes
        """
        self.tree = IBDFamilyTree(nx.DiGraph(), self)
        super().__init__(N=N, r=r, dr=dr, mr=mr)
        # genalogy of the simulation represented as a tree DAG
        # TODO: adapt the datacollector module

    def add_agents(self, N, r):
        for i in range(int(N * r)):
            agent = IBDFamilyAgent(i, self, 1, i)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            agent = IBDFamilyAgent(i, self, 0, i)
            self.schedule.add(agent)

    def reproduce(self):
        """
        1) Add the agents on the graph and perform generational turnover with a cutoff value
        2) Change reproductive model (larger families and a constrain on inbreeding)
        :return:
        """
        mating_ind = random.sample(
            [agent for agent in self.schedule.agents], k=self.N)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]
        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), "family": p[0].unique_id,
                   "parents id" : [pa.unique_id for pa in p]} for p in
                  mating_pairs for i in range(10)]

        self.tree.remove_generation(self.schedule.steps - 3)
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        for i in range(len(newgen)):
            self.schedule.add(IBDFamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"]))
            self.tree.add_child(newgen[i], i)


    def step(self) -> None:
        """
        Change the social setting for the interactions (larger number of random recipients)
        #add "rooms" "active" as model variable
        :return:
        """

        # suppose 500 parents --> 250 couples --> 2500 offspring (5 per tree)

        danger_number = self.N // 4

        # it has to be generalized for n child, now takes as granted 4 childs
        ufid = list(set([a.family for a in self.schedule.agent_buffer()]))

        danger_fam = random.sample(ufid, danger_number)

        rooms = [[x for x in self.schedule.agent_buffer() if x.family == f]
                 for f in danger_fam]
        active = [random.choice(r).unique_id for r in rooms]

        self.schedule.step(active)

        self.reproduce()
        self.datacollector.collect(self)

        pass
