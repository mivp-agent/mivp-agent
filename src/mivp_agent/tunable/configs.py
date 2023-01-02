from mivp_agent.tunable.tunable import Tunable, NOT_SET


def only_unset(value) -> bool:
    return value == NOT_SET


def only_set(value) -> bool:
    return value != NOT_SET


def generate_config(*args, rule=None):
    '''
    This function will generate a dictionary config given any number of `Tunable` objects. The config values will contain the current value for each dimensions within each config (specified or unspecified). Unspecified values (indicated by `NOT_SET`) will use the `__str__` representation of their dimension's set.
    
    Using the `rule` kwarg you can supply a callable which takes in one positional argument (the value of a dimension) and returns a boolean. Any True return values will include the final config. This is used by mivp_agent to create configs which contain
    '''
    namespaces = []
    for arg in args:
        assert isinstance(arg, Tunable), f'Found non-tunable object: {arg}'
        
        assert arg._namespace not in namespaces, f'Found multiple namespaces called"{arg._namespace}" please resolve.'

    config = {}
    for tunable in args:
        namespace = {}
        for key, value in tunable._values.items():
            # If there is a rule & the rule returns false
            if rule is not None and not rule(value):
                continue

            if value == NOT_SET:
                value = str(tunable._feasible_space[key])

            namespace[key] = value
        
        # Set the namespace in the global config
        config[tunable._namespace] = namespace
    
    return config
