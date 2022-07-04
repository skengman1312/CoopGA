import pandas
import random
from model import *
import networkx as nx
from utils import IBDFamilyTree

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
            b = sum([1 * self.model.tree.ig_ibd_coeff(pre + str(self.unique_id),
                    pre + str(a.unique_id)) for a in A_room])

            if b > 1:
                #print("alt done")
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
    Extension of the FamilyModel in order to deal with different setting in the interaction rooms.
    Genealogy of the agents in the simulation is represented as a tree DAG. The DAG stores 3 generations only

    :param FamilyModel: A model for simulation of the evolution of families. 
    :type FamilyModel: FamilyModel
    """

    def __init__(self, N=500, r=0.5, dr=0.9, mr=0.001):
        """
        Extension of the FamilyModel in order to deal with different setting in the interaction rooms.

        :param N: total number of agents, defaults to 500
        :type N: int, optional
        :param r: initial ratio of altruistic allele, defaults to 0.5
        :type r: float, optional
        :param dr: death rate for sacrificing altruist, defaults to 0.95
        :type dr: float, optional
        :param mr: mutation rate, defaults to 0.001
        :type mr: float, optional
        """
        self.tree = IBDFamilyTree(nx.DiGraph(), self)
        super().__init__(N=N, r=r, dr=dr, mr=mr)

        self.datacollector = DataCollector(model_reporters={
            "altruistic fraction": lambda x: len(
                [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count(),
        })

    def add_agents(self, N, r):
        """
        Add agents to the model with the right proportion (r) of altruistic allele

        :param N: total number of agents
        :type N: int
        :param r: initial ratio of altruistic allele
        :type r: float
        """
        # adding altruist agents (genotype = 1)
        for i in range(int(N * r)):
            agent = IBDFamilyAgent(i, self, 1, i)
            self.schedule.add(agent)

        # adding non-altruist agents (genotype = 0)
        for i in range(int(N * r), N):
            agent = IBDFamilyAgent(i, self, 0, i)
            self.schedule.add(agent)

    def reproduce(self):
        """
        Function to generate the new population from the parent individuals
        1. Sample N individuals from current population
        2. Generate pairs of inidividuals
        3. Create the new generation, defining inherited genotype (mutation applied), family ID and parents ID
        4. Remove oldest generation from the DAG
        5. Remove all the "old" agents from the model
        6. Add the new generation of agents to the model and the DAG
        """
        # 1
        mating_ind = random.sample([agent for agent in self.schedule.agents], k=self.N)
        # 2
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]

        # 3
        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), 
                   "family": p[0].unique_id,
                   "parents id": [pa.unique_id for pa in p]} for p in mating_pairs for i in range(20)]
    
        # 4 
        self.tree.remove_generation(self.schedule.steps - 3)
        
        # 5
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        
        # 6
        for i in range(len(newgen)):
            self.schedule.add(IBDFamilyAgent(
                i, self, newgen[i]["genotype"], newgen[i]["family"]))
            self.tree.add_child(newgen[i], i)
        
        self.tree.update_ig()

    def step(self) -> None:
        """
        Model step: agents are randomly assigned to interaction rooms which are all dangerous. Depending
        on the selected actor an altruist action could be performed or not.
        """
        
        # even in the worst case scenario at least N individuals survive so we can have all rooms as dangerous
        self.rooms = np.random.choice(self.schedule.agents, (len(self.schedule.agents) // 40, 30), replace=False).tolist()

        self.active = [random.choice(r).unique_id for r in self.rooms]

        self.schedule.step(self.active)

        self.reproduce()
        
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = IBDFamilyModel(N=30, mr=0.001, r=0.5)
    print("\naltruists before steps\t", len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())
    for i in range(500):
        print(f">>>Step n{i}<<<")
        model.step()
    print("\naltruists after steps\t",
          len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())