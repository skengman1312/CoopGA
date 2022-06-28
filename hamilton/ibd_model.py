import pandas
import random
from model import *
import networkx as nx
from nx_script import *
from nx_script import IBDFamilyTree


class IBDFamilyAgent(FamilyAgent):

    def altruistic_action(self):
        """
        The Actor has to calculate the Benefit = Sum_i(P_ibd(A, R_i)
        A = actor, R_i = ith recipient
        :return:
        """

        print("#############################################\nROOMS")
        for r in self.model.rooms:
            print(r)
        print("#############################################")

        A_index = self.model.active.index(self.unique_id)
        A_room = self.model.rooms[A_index]

        pre = str(self.model.schedule.steps) + "#"

        if self.genotype:

            print("Actor ID", self.unique_id,
                  "\tID in G ", pre + str(self.unique_id))
            print("A_index ", A_index)
            print("A_room ", A_room)
            for a in A_room:
                print(a.genotype, a.unique_id)

            # calculating the benefit
            A_room.remove(self)
            b = sum([self.model.tree.ibd_coeff(pre + str(self.unique_id),
                    pre + str(a.unique_id)) for a in A_room])

            print("total benefit ", b)
            # it has to be tested yet
            # for i in A_room:
            #     if i.unique_id != self.unique_id:
            #         b += self.model.tree.ibd_coeff(self.model.tree,
            #                                        pre + self.unique_id, pre + i.unique_id)
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

    def __init__(self, N=50, r=0.5, dr=0.95, mr=0.001):
        """
        add graph to attributes
        """
        self.tree = IBDFamilyTree(nx.DiGraph(), self)
        super().__init__(N=N, r=r, dr=dr, mr=mr)
        # genalogy of the simulation represented as a tree DAG

        self.datacollector = DataCollector(model_reporters={
            "altruistic fraction": lambda x: len(
                [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count(),
        })

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
                   "parents id": [pa.unique_id for pa in p]} for p in
                  mating_pairs for i in range(10)]

        self.tree.remove_generation(self.schedule.steps - 3)
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        for i in range(len(newgen)):
            self.schedule.add(IBDFamilyAgent(
                i, self, newgen[i]["genotype"], newgen[i]["family"]))
            self.tree.add_child(newgen[i], i)

    def step(self) -> None:
        """
        Change the social setting for the interactions (larger number of random recipients)
        #add "rooms" "active" as model variable
        :return:
        """

        # suppose 50 parents --> 25 couples --> 250 offspring (5 per tree)
        # since we have 50 tree (250/5) all the trees can be dangerous bc
        # even in the worst case scenario at least 50 individuals survive

        all_ids = [a.unique_id for a in self.schedule.agent_buffer()]
        random.shuffle(all_ids)

        self.rooms = np.random.choice(
            self.schedule.agents, (len(self.schedule.agents) // 5, 5)).tolist()


        self.active = [random.choice(r).unique_id for r in self.rooms]

        self.schedule.step(self.active)

        self.reproduce()
        #   self.datacollector.collect(self)


if __name__ == "__main__":
    model = IBDFamilyModel(N=50, mr=0.001, r=0.5)

    model.step()
