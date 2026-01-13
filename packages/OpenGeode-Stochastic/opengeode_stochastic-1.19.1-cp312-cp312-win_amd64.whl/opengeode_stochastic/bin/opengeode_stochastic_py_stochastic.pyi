"""
OpenGeode-Stochastic Python binding
"""
from __future__ import annotations
import opengeode.bin.opengeode_py_geometry
import typing
__all__: list[str] = ['Distribution', 'DistributionType', 'DoubleDistributionDescription', 'DoubleSampler', 'FractureSetDescription', 'FractureSimulationRunner', 'Gaussian', 'RandomEngine', 'SimulationConfigurator', 'SimulationPrinterConfigurator', 'SpatialDomain2D', 'SpatialDomain3D', 'StatisticsMonitor', 'StochasticLibrary', 'TruncatedGaussian', 'TruncatedLogNormal', 'TruncatedPowerLaw', 'UniformClosed', 'UniformClosedOpen', 'VonMises']
class Distribution:
    pass
class DistributionType:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: str) -> None:
        ...
    def get(self) -> str:
        ...
    def matches(self, arg0: DistributionType) -> bool:
        ...
class DoubleDistributionDescription:
    distribution_type: DistributionType
    max_value: float | None
    mean: float | None
    min_value: float | None
    name: str
    standard_deviation: float | None
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def string(self) -> str:
        """
        Return a detailed description of the Distribution law
        """
    @property
    def alpha(self) -> float | None:
        """
        Set up alpha which is the exponent parameter for power law Distribution law
        """
    @alpha.setter
    def alpha(self, arg0: float | None) -> None:
        ...
    @property
    def kappa(self) -> float | None:
        """
        Set up kappa which is the concentration parameter for Von Mises Distribution law
        """
    @kappa.setter
    def kappa(self, arg0: float | None) -> None:
        ...
class DoubleSampler:
    @staticmethod
    def create_distribution(desc: DoubleDistributionDescription) -> UniformClosed | UniformClosedOpen | Gaussian | TruncatedGaussian | VonMises | TruncatedLogNormal | TruncatedPowerLaw:
        """
        Create a distribution from a description
        """
    @staticmethod
    def create_rad_angle_distribution_from_degree(desc: DoubleDistributionDescription) -> UniformClosed | UniformClosedOpen | Gaussian | TruncatedGaussian | VonMises | TruncatedLogNormal | TruncatedPowerLaw:
        """
        Create a angle distribution in radian from a description provided in degree
        """
    @staticmethod
    def sample(engine: RandomEngine, dist: UniformClosed | UniformClosedOpen | Gaussian | TruncatedGaussian | VonMises | TruncatedLogNormal | TruncatedPowerLaw) -> float:
        """
        Sample a value from a distribution using a RandomEngine
        """
class FractureSetDescription:
    azimuth: DoubleDistributionDescription
    birth_ratio: float
    change_ratio: float
    death_ratio: float
    length: DoubleDistributionDescription
    minimal_spacing: float
    name: str
    p20: float
    p21: float
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def add_observed_fracture(self, arg0: opengeode.bin.opengeode_py_geometry.Point2D, arg1: opengeode.bin.opengeode_py_geometry.Point2D) -> None:
        ...
    def string(self) -> str:
        """
        Return a detailed description of the fracture set
        """
class FractureSimulationRunner:
    def __init__(self, box: SpatialDomain2D) -> None:
        ...
    def add_fracture_set_descriptor(self, descriptor: FractureSetDescription) -> None:
        """
        Add a fracture set configuration to the simulation.
        """
    def add_x_node_monitoring(self, double: float) -> None:
        """
        Add a monitoring value for x node, value should be in[0.,1.].
        """
    def check_statistics(self, statistic_monitoring: StatisticsMonitor) -> None:
        """
        Check computed statistics after simulation.
        """
    def initialize(self) -> None:
        """
        Initialize internal samplers, energy terms, and proposal kernels.
        """
    def run(self, engine: RandomEngine, config: SimulationConfigurator) -> StatisticsMonitor:
        """
        Run the simulation and return statistics monitoring results.
        """
    def string(self) -> str:
        """
        Return a detailed description of the simulation configurator.
        """
class Gaussian:
    mean: float
    standard_deviation: float
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
class RandomEngine:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def sample_bernoulli(self, probability_of_success: float) -> bool:
        """
        Sample a boolean with given success probability
        """
    def sample_gaussian(self, law: Gaussian) -> float:
        """
        Sample a value from a Gaussian distribution
        """
    def sample_log(self) -> float:
        """
        Return a logarithmically uniform random value
        """
    def sample_truncated_gaussian(self, law: TruncatedGaussian) -> float:
        """
        Sample a value from a truncated Gaussian
        """
    def sample_truncated_lognormal(self, law: TruncatedLogNormal) -> float:
        """
        Sample a value from a Truncated Log Normal
        """
    def sample_truncated_powerlaw(self, law: TruncatedPowerLaw) -> float:
        """
        Sample a value from a Truncated Power Law
        """
    def sample_uniform_closed(self, law: UniformClosed) -> float:
        """
        Sample a double from a uniform closed distribution
        """
    def sample_uniform_closed_open(self, law: UniformClosedOpen) -> float:
        """
        Sample a double from a uniform closed-open distribution
        """
    def sample_von_mises(self, law: VonMises) -> float:
        """
        Sample a value from a Von Mises-Fisher
        """
    @typing.overload
    def set_seed(self, number: int) -> None:
        """
        Set RNG seed using integer
        """
    @typing.overload
    def set_seed(self, word: str) -> None:
        """
        Set RNG seed using string
        """
class SimulationConfigurator:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def string(self) -> str:
        """
        Return a detailed description of the object set simulation configurator
        """
    @property
    def burn_in_steps(self) -> int:
        """
        Number of burn-in steps before recording realizations
        """
    @burn_in_steps.setter
    def burn_in_steps(self, arg0: int) -> None:
        ...
    @property
    def metropolis_hasting_steps(self) -> int:
        """
        Number of Metropolis-Hastings steps per realization
        """
    @metropolis_hasting_steps.setter
    def metropolis_hasting_steps(self, arg0: int) -> None:
        ...
    @property
    def printer(self) -> SimulationPrinterConfigurator | None:
        """
        Optional SimulationPrinter for output
        """
    @printer.setter
    def printer(self, arg0: SimulationPrinterConfigurator | None) -> None:
        ...
    @property
    def realizations(self) -> int:
        """
        Number of realizations to generate
        """
    @realizations.setter
    def realizations(self, arg0: int) -> None:
        ...
class SimulationPrinterConfigurator:
    output_folder: str
    print_realisations: bool
    print_statistics: bool
    print_statistics_summary: bool
    realisations_prefix: str
    realisations_print_frequency: int
    statistics_filename: str
    statistics_summary_filename: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class SpatialDomain2D:
    def __init__(self, domain: opengeode.bin.opengeode_py_geometry.BoundingBox2D, buffer_size: float) -> None:
        """
                        Create a spatial domain composed of:
        
                        - a core domain (the VOI)
                        - a buffer zone
                        - the extended domain (domain + buffer)
        
                        Arguments:
                            domain (BoundingBox): main domain / VOI
                            buffer_size (float): buffer thickness
        """
class SpatialDomain3D:
    def __init__(self, domain: opengeode.bin.opengeode_py_geometry.BoundingBox3D, buffer_size: float) -> None:
        """
                        Create a spatial domain composed of:
        
                        - a core domain (the VOI)
                        - a buffer zone
                        - the extended domain (domain + buffer)
        
                        Arguments:
                            domain (BoundingBox): main domain / VOI
                            buffer_size (float): buffer thickness
        """
class StatisticsMonitor:
    def __init__(self, nb_energy_terms: int) -> None:
        """
        Create a StatisticsMonitor for a given number of energy terms
        """
    def __repr__(self) -> str:
        ...
    def add_realization(self, values: list[float]) -> None:
        """
        Add a realization (vector of doubles) to update statistics
        """
    def statiscal_count(self) -> int:
        """
        Return the number of realizations added
        """
    @property
    def means(self) -> list[float]:
        """
        Return the computed mean values for each energy term
        """
    @property
    def variances(self) -> list[float]:
        """
        Return the computed variances for each energy term
        """
class StochasticLibrary:
    @staticmethod
    def initialize() -> None:
        ...
class TruncatedGaussian:
    max_value: float | None
    mean: float
    min_value: float | None
    standard_deviation: float
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
class TruncatedLogNormal:
    max_value: float | None
    min_value: float | None
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
    @property
    def mean(self) -> float:
        """
        Mean value of the underlying normal distribution
        """
    @mean.setter
    def mean(self, arg0: float) -> None:
        ...
    @property
    def standard_deviation(self) -> float:
        """
        Standard deviation value of the underlying normal distribution
        """
    @standard_deviation.setter
    def standard_deviation(self, arg0: float) -> None:
        ...
class TruncatedPowerLaw:
    max_value: float | None
    min_value: float | None
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
    @property
    def alpha(self) -> float:
        """
        Alpha value of the power law
        """
    @alpha.setter
    def alpha(self, arg0: float) -> None:
        ...
class UniformClosed:
    max_value: float
    min_value: float
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
class UniformClosedOpen:
    max_value: float
    min_value: float
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
class VonMises:
    concentration: float
    mean: float
    @staticmethod
    def distribution_type_static() -> DistributionType:
        ...
    def __init__(self) -> None:
        ...
    def distribution_type(self) -> DistributionType:
        ...
    def is_valid(self) -> bool:
        ...
    def string(self) -> str:
        ...
