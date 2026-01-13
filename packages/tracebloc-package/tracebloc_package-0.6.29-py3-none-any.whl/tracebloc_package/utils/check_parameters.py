import tensorflow


def get_optimizer(optimizer_name, learning_rate):
    """
    Returns an optimizer based on the specified name and learning rate.

    Args:
        optimizer_name (str): The name of the optimizer to use.
        learning_rate (float or callable): The learning rate to use.
        **kwargs: Additional keyword arguments for the optimizer.

    Returns:
        An instance of the specified optimizer class.
    """
    type = learning_rate.get("type")
    if type == "constant":
        learning_rate_func = get_learning_rate(learning_rate_name="constant")
    elif type == "custom":
        # Check if the learning_rate is a function (callable)
        if "name" not in learning_rate["value"]:
            learning_rate_func = create_learning_rate_callable(
                learning_rate["original"]
            )
        elif callable(learning_rate["value"]["name"]):
            learning_rate_func = create_learning_rate_callable(learning_rate["value"])
        else:
            error = "Custom function is not callable"
            return False, error
    elif type == "adaptive":
        # Use a fixed learning rate
        # Create a learning rate schedule if specified
        lr_schedule_name = learning_rate["value"].get("schedular")
        try:
            learning_rate_func, kwargs = get_learning_rate(
                learning_rate_name=lr_schedule_name, **learning_rate["value"]
            )
        except Exception as e:
            return False, e
    else:
        return False, ValueError("Unsupported learning type: {}".format(learning_rate))

    # Define the available optimizers
    optimizers = {
        "sgd": tensorflow.keras.optimizers.SGD,
        "rmsprop": tensorflow.keras.optimizers.RMSprop,
        "adam": tensorflow.keras.optimizers.Adam,
        "adagrad": tensorflow.keras.optimizers.Adagrad,
        "adadelta": tensorflow.keras.optimizers.Adadelta,
        "adamax": tensorflow.keras.optimizers.Adamax,
        "nadam": tensorflow.keras.optimizers.Nadam,
        "ftrl": tensorflow.keras.optimizers.Ftrl,
    }

    # Check if the specified optimizer is available
    if optimizer_name.lower() not in optimizers:
        return False, ValueError("Unsupported optimizer: {}".format(optimizer_name))

    # Get the optimizer class
    optimizer_class = optimizers[optimizer_name.lower()]

    try:
        # Create an instance of the optimizer class
        optimizer_class(learning_rate=learning_rate_func)
        # if Valid optimiser and Return the True
        return True, None
    except Exception as e:
        # if not a valid optimiser/learning rate and Return error
        return False, e


def get_learning_rate(learning_rate_name, **kwargs):
    if learning_rate_name == "constant":
        lr = kwargs.get("value", 0.01)
        return lr
    elif learning_rate_name == "ExponentialDecay":
        lr = kwargs.get("initial_learning_rate")
        decay_rate = kwargs.get("decay_rate")
        decay_steps = kwargs.get("decay_steps")
        staircase = kwargs.get("staircase", False)
        return (
            tensorflow.keras.optimizers.schedules.ExponentialDecay(
                lr, decay_steps, decay_rate, staircase
            ),
            kwargs,
        )
    elif learning_rate_name == "PiecewiseConstantDecay":
        boundaries = kwargs.get("boundaries")
        values = kwargs.get("values")
        return (
            tensorflow.keras.optimizers.schedules.PiecewiseConstantDecay(
                boundaries, values
            ),
            kwargs,
        )
    elif learning_rate_name == "PolynomialDecay":
        lr = kwargs.get("initial_learning_rate")
        decay_steps = kwargs.get("decay_steps")
        end_learning_rate = kwargs.get("end_learning_rate", 0.0001)
        power = kwargs.get("power", 1.0)
        cycle = kwargs.get("cycle", False)
        return (
            tensorflow.keras.optimizers.schedules.PolynomialDecay(
                lr, decay_steps, end_learning_rate, power, cycle
            ),
            kwargs,
        )
    elif learning_rate_name == "InverseTimeDecay":
        lr = kwargs.get("initial_learning_rate")
        decay_steps = kwargs.get("decay_steps")
        decay_rate = kwargs.get("decay_rate")
        staircase = kwargs.get("staircase", False)
        return (
            tensorflow.keras.optimizers.schedules.InverseTimeDecay(
                lr, decay_steps, decay_rate, staircase
            ),
            kwargs,
        )
    elif learning_rate_name == "CosineDecay":
        lr = kwargs.get("initial_learning_rate")
        decay_steps = kwargs.get("decay_steps")
        alpha = kwargs.get("alpha", 0.0)
        return (
            tensorflow.keras.optimizers.schedules.CosineDecay(lr, decay_steps, alpha),
            kwargs,
        )
    elif learning_rate_name == "CosineDecayRestarts":
        lr = kwargs.get("initial_learning_rate")
        first_decay_steps = kwargs.get("first_decay_steps")
        t_mul = kwargs.get("t_mul", 2.0)
        m_mul = kwargs.get("m_mul", 1.0)
        alpha = kwargs.get("aplha", 0.0)
        return (
            tensorflow.keras.optimizers.schedules.CosineDecayRestarts(
                lr, first_decay_steps, t_mul, m_mul, alpha
            ),
            kwargs,
        )
    elif (
        learning_rate_name == "LinearCosineDecay"
        or learning_rate_name == "NoisyLinearCosineDecay"
    ):
        raise ValueError(
            f"{learning_rate_name} not supported in latest tensorflow version"
        )
    else:
        raise ValueError("Invalid learning rate schedular name:", learning_rate_name)


def create_learning_rate_callable(learning_rate):
    # Use the specified function to compute the learning rate
    learning_rate_func_args = learning_rate.copy()
    learning_rate_func = learning_rate_func_args["name"]
    del learning_rate_func_args["name"]
    learning_rate_func = learning_rate_func(**learning_rate_func_args)
    return learning_rate_func


# get_optimizer(optimizer_name="sgd", learning_rate={"type": "constant", "value": 0.001})
