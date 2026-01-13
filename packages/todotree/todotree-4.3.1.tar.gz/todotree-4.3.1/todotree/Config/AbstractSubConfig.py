from abc import abstractmethod, ABC


class AbstractSubConfig(ABC):

    @abstractmethod
    def apply_to_dict(self, dict_to_modify: dict):
        """Modify the dictionary to include the values for writing the config file."""
        pass

    @abstractmethod
    def read_from_dict(self, new_values: dict):
        """Read the values from a dictionary for reading the yaml file."""
        pass

    def __eq__(self, other):
        """Equality check by comparing the representation."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return repr(self) == repr(other)
