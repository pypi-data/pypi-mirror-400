import warnings

from fluidattacks_core.logging import init_logging, set_product_id

warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

set_product_id("labels")
init_logging()
