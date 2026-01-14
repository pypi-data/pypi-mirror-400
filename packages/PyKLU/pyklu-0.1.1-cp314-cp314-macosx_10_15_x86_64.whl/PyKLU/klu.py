from ._klu import Klu
import warnings
warnings.warn(
            "PyKLU.klu is the legacy way of importing PyKLU. Use 'import PyKLU' instead",
            DeprecationWarning,
            stacklevel=2,
        )
