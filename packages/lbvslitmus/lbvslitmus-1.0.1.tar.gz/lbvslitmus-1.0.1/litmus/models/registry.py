from typing import Any, Dict, Optional, TypedDict


class ModelEntry(TypedDict):
    """
    Single pair of model class and arguments the model will be run with.
    """

    model_class: type
    args: Dict[str, Any]


class ModelRegistry:
    """
    Registry for managing models used for benchmark.
    """

    def __init__(self):
        self.models: Dict[str, ModelEntry] = {}

    def register(
        self,
        model_class: type,
        name: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        """
        Register a model class.

        Parameters
        ----------
        model_class : Type
            The model class to register
        args: [Dict[str, Any]]
            Additional arguments to pass to the model class
        name : str, optional
            Custom name for the model. If None, uses class name
        """
        if name is None:
            name = model_class.__name__
        if args is None:
            args = {}
        self.models[name] = {"model_class": model_class, "args": args}

    def get_model_entry(self, model_name) -> ModelEntry:
        """
        Get a model class by name.

        Parameters
        ----------
        model_name : str
            Name of the model

        Returns
        -------
        Type
            The model class

        Raises
        ------
        KeyError
            If model is not found in registry
        """
        if model_name not in self.models:
            available = list(self.models.keys())
            raise KeyError(
                f"Model '{model_name}' not found. Available models: {available}"
            )

        return self.models[model_name]

    def create_model_instance(self, model_name: str) -> Any:
        """
        Create a new instance of the specified model.

        Parameters
        ----------
        model_name : str
            Name of the model

        Returns
        -------
        Any
            New instance of the model
        """
        model_entry = self.get_model_entry(model_name)
        return model_entry["model_class"](**model_entry["args"])

    def __iter__(self):
        """Allow iteration over model classes."""
        return iter(self.models.values())

    def items(self):
        """Allow iteration over."""
        return self.models.items()

    def keys(self):
        """Iterate over model names."""
        return self.models.keys()

    def values(self):
        """Iterate over model classes."""
        return self.models.values()

    def __len__(self):
        """Amount of models registered."""
        return len(self.models)

    def __contains__(self, model_name: str):
        """Check if a model class is registered."""
        return model_name in self.models


registry = ModelRegistry()
