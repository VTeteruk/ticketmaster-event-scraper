# fmt: off
import environs


env = environs.Env()
env.read_env()

DOMAIN        = env.str('DOMAIN')
EVENT         = env.str('EVENT')
PRICE_FROM    = env.int('PRICE_FROM')
PRICE_TO      = env.int('PRICE_TO')
QUANTITY      = env.int('QUANTITY')
EXCLUDE_FIRST = env.int('EXCLUDE_FIRST')
