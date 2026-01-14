import abc
from typing import Any, List, Callable, Union

from .quote import Quote, QuoteSet


class Framework(abc.ABC):
    """
    Base class for the Sentinel Rating Framework.

    This abstract base class is the core of the rating framework system.
    It is designed for generating quotes based on test cases provided by the
    user.

    Derived classes should implement the `setup` and `calculation` methods to
    configure the framework and perform quote calculations, respectively.

    Frameworks are never intended to be initialised by the end user. You should
    be calling the class methods 'quote' and 'quote_many'. In addition, set up
    methods from parent classes are inherited and executed in order during
    instantiation. This allows frameworks to build on one another without
    overriding crucial initialization steps.

    Example:
        class YourFramework(Framework):
            def setup(self):
                # Load rating tables and initialize resources
                ...

            def calculation(self, quote):
                # Perform quote calculation logic
                ...

        class YourFrameworkVersion2(YourFramework):
            def setup(self):
                # Additional initialization for version 2
                ...
            def calculation(self, quote):
                # Overridden calculation logic for version 2
                ...
    """

    # Private class attributes to hold inherited set up methods and instances.
    _setup_methods: List[Callable[[Any], None]] = []

    # Public attributes.
    name: Union[str, None] = None

    # These aren't really in use yet, but serve as a reminder that dates are
    # a pain point I want to address.
    effective_date: Any = None
    expiry_date: Any = None

    def __init__(self) -> None:
        """
        Initialize a new instance of the Framework.

        During initialization, all inherited set up methods are executed first,
        followed by the subclass's own `setup` method.
        """
        self._run_inherited_setup_methods()
        self.setup()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Inherit set up methods from parent Framework classes.

        This method ensures that setup functions defined in parent classes are
        carried over to subclasses, enabling cumulative configuration.
        """
        super().__init_subclass__(**kwargs)
        # Copy set up methods from the first parent that is a Framework
        # subclass
        for base in cls.__bases__:
            if issubclass(base, Framework) and base is not Framework:
                cls._setup_methods = base._setup_methods.copy()
                cls._setup_methods.append(base.setup)
                break

    def __str__(self) -> str:
        """
        Return a human-readable representation of the framework.

        Returns:
            A string representation, typically the framework's name.
        """
        return self.name or self.__class__.__name__

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the framework.

        Returns:
            A string representation, typically the framework's name.
        """
        return str(self)

    def _run_inherited_setup_methods(self) -> None:
        """
        Execute all inherited set up methods.

        This method runs each set up method inherited from parent frameworks,
        ensuring that the configuration from all ancestors is applied.
        """
        for setup_method in self._setup_methods:
            setup_method(self)

    def _calculate_wrapper(self, test: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Internal helper to wrap the quote calculation.

        If `test` is not a Quote instance, it converts it to one before
        performing the calculation.

        Args:
            test: A test case data structure or a Quote instance.
            *args: Additional positional arguments for the calculation method.
            **kwargs: Additional keyword arguments for the calculation method.

        Returns:
            The result of the calculation, typically a Quote.
        """
        # Convert test to a Quote instance if it isn't one already.
        q = test if isinstance(test, Quote) else Quote(test)
        return self.calculation(q, *args, **kwargs)

    @abc.abstractmethod
    def setup(self) -> None:
        """
        Configure the framework.

        This method should be overridden in derived classes to load necessary
        resources (e.g., rating tables) and perform any initialization required
        before processing quotes.

        It is recommended that rating tables be assigned directly to instance
        attributes rather than nested within another structure.
        """
        pass

    @abc.abstractmethod
    def calculation(self, quote: Any) -> Any:
        """
        Calculate a quote.

        This method should be overridden to implement the logic that uses the
        configured framework to generate a quote based on the provided test
        case.

        Args:
            quote: A Quote instance containing test case data and framework
                info.

        Returns:
            The calculated quote.
        """
        pass

    @classmethod
    def quote_many(cls, tests: List[Any], *args: Any, **kwargs: Any) -> Any:
        """
        Calculate multiple quotes using the framework.

        This class method creates an instance of the framework and applies the
        calculation method to each test case in the provided list.

        Args:
            tests (List[Any]): A list of test case data structures or Quote
                instances.
            *args: Additional positional arguments for the calculation method.
            **kwargs: Additional keyword arguments for the calculation method.

        Returns:
            A Quoteset containing the calculated quotes.
        """
        instance = cls()
        quote_set = QuoteSet(
            [
                instance._calculate_wrapper(test, *args, **kwargs)
                for test in tests
            ],
            framework=cls,
        )

        return quote_set

    @classmethod
    def quote(cls, test: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Calculate a single quote using the framework.

        This class method creates an instance of the framework and applies the
        calculation method to the provided test case.

        Args:
            test: A test case data structure or a Quote instance.
            *args: Additional positional arguments for the calculation method.
            **kwargs: Additional keyword arguments for the calculation method.

        Returns:
            The calculated quote.
        """
        instance = cls()
        return instance._calculate_wrapper(test, *args, **kwargs)
