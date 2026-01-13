from abc import ABC, abstractmethod
from .polymer_classifier import PolymerClassifier
import random
import os
from aldepyde.data.distribution import Distribution, load, available_distributions
from aldepyde.data.distributions.standards import distribution_head
import json

class ResidueGenerator(ABC):
    def __init__(self, classifier:PolymerClassifier):
        self.classifier = classifier

    def _generate(self):
        pass

    # Just pure, random generation. Nothing fancy
    def random(self, length:int, n:int=1) -> list:
        alphabet = list(self.classifier.alphabet)
        sequences = []
        for i in range(n):
            sequences.append("".join(random.choices(alphabet, k=length)))
        return sequences

    def random_from_distribution(self, distribution: os.PathLike|str|dict[str, float]|Distribution, length:int|tuple[int,int], n:int=1, exclude:tuple=()) -> list:
        if isinstance(distribution, str) and os.path.isfile(distribution): # Given a file
            with open(distribution) as fp:
                data = json.load(fp)
                if distribution_head not in data.keys():
                    raise ValueError(f"Key '{distribution_head}' must be in the top level of your provided file")
            usable_distribution = Distribution(None, data[distribution_head])
        elif isinstance(distribution, str) and not os.path.isfile(distribution): # Given a preload
            usable_distribution = load(distribution)
        elif isinstance(distribution, Distribution): # Given a distribution
            usable_distribution = distribution
        elif isinstance(distribution, dict): # Given a dictionary
            usable_distribution = Distribution(None, distribution)
        else:
            raise ValueError('Invalid distribution')
        for r in exclude:
            usable_distribution.eliminate_entry(r)
        if not isinstance(length, int):
            size = lambda: random.randint(length[0], length[1])
        else:
            size = lambda: length
        usable_distribution.normalize_map()
        sequences = []
        for _ in range(n):
            sequence = random.choices(population=list(usable_distribution.frequency_map.keys()), weights=list(usable_distribution.frequency_map.values()), k=size())
            sequences.append("".join(sequence))
        return sequences

