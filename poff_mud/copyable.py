from copy import deepcopy


class Copyable:
    def __deepcopy__(self, memo):
        cls = self.__class__  # Extract the class of the object
        result = cls.__new__(
            cls
        )  # Create a new instance of the object based on extracted class
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(
                result, k, deepcopy(v, memo)
            )  # Copy over attributes by copying directly or in case of complex objects like lists for exaample calling the `__deepcopy()__` method defined by them. Thus recursively copying the whole tree of objects.
        return result
