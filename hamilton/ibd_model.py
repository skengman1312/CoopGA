import pandas
import random
from model import *
import networkx as nx
from nx_script import *
from nx_script import IBDFamilyTree


class IBDFamilyAgent(FamilyAgent):
    """
    Agent class to simulate altruistic behaviour based on relatedness which 
    must be computed based on benefit due to different settings compared to before
    (each interaction room will contain agents belonging to different families). 

    :param FamilyAgent: _description_
    :type FamilyAgent: _type_
    """

    def altruistic_action(self):
        """
        Implementation of a generic altruistic action. 
        If the actor is altruist he can sacrifice or not. The choice is based on the benefit 
        gained by performing the altruistic. The more the recipient is related to the actor
        the higher the benefit. 
        The Actor has to calculate the Benefit = Sum_i(P_ibd(A, R_i)
        A = actor, R_i = ith recipient
        """

        A_index = self.model.active.index(self.unique_id)
        A_room = self.model.rooms[A_index]

        pre = str(self.model.schedule.steps) + "#"

        if self.genotype:
            # computing the benefit
            A_room.remove(self)
            b = sum([self.model.tree.ig_ibd_coeff(pre + str(self.unique_id),
                    pre + str(a.unique_id)) for a in A_room])

            if b > 1:
                if random.random() > self.model.dr:
                    return
                else:
                    self.model.schedule.remove(self)
            else:
                [self.model.schedule.remove(a) for a in A_room if a.unique_id != self.unique_id]

        else:
            [self.model.schedule.remove(a) for a in A_room if a.unique_id != self.unique_id]

class IBDFamilyModel(FamilyModel):
    """
    Extension of the FamilyModel in order to deal with different setting in the interaction rooms

    :param FamilyModel: A model for simulation of the evolution of families. 
    :type FamilyModel: FamilyModel
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
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
                  mating_pairs for i in range(30)]
        # print(newgen)
        # print(len(newgen))

        self.tree.remove_generation(self.schedule.steps - 3)
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        for i in range(len(newgen)):
            self.schedule.add(IBDFamilyAgent(
                i, self, newgen[i]["genotype"], newgen[i]["family"]))
            self.tree.add_child(newgen[i], i)
        self.tree.update_ig()

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
        # print(len(self.schedule.agents))
        self.rooms = np.random.choice(
            self.schedule.agents, (len(self.schedule.agents) // 10, 10), replace=False).tolist()

        self.active = [random.choice(r).unique_id for r in self.rooms]

        self.schedule.step(self.active)
        # print(len(self.schedule.agents))
        self.reproduce()
        # print(len(self.schedule.agents))
        #   self.datacollector.collect(self)


if __name__ == "__main__":
    model = IBDFamilyModel(N=200, mr=0.001, r=0.5)
    print("\naltruists before steps\t", len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())
    for i in range(50):
        print(f">>>Step n{i}<<<")
        model.step()
    print("\naltruists after steps\t",
          len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())