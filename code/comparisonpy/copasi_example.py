import COPASI
from COPASI import CDataModel
from basico import model_io
from basico.task_timecourse import __method_name_to_type, __build_result_from_ts


def run_time_course(*args, **kwargs):
    """Simulates the current or given model, returning a data frame with the results

    :param args: positional arguments

     * 1 argument: the duration to simulate the model
     * 2 arguments: the duration and number of steps to take
     * 3 arguments: start time, duration, number of steps

    :param kwargs: additional arguments

     - | `model`: to specify the data model to be used (if not specified
       | the one from :func:`.get_current_model` will be taken)

     - `use_initial_values` (bool): whether to use initial values

     - `scheduled` (bool): sets whether the task is scheduled or not

     - `update_model` (bool): sets whether the model should be updated, or reset to initial conditions.

     - | `method` (str): sets the simulation method to use (otherwise the previously set method will be used)
       | support methods:
       |
       |   * `deterministic` / `lsoda`: the LSODA implementation
       |   * `stochastic`: the Gibson & Bruck Gillespie implementation
       |   * `directMethod`: Gillespie Direct Method
       |   * others: `hybridode45`, `hybridlsoda`, `adaptivesa`, `tauleap`, `radau5`, `sde`

     - `duration` (float): the duration in time units for how long to simulate

     - `automatic` (bool): whether to use automatic determined steps (True), or the specified interval / number of steps

     - `output_event` (bool): if true, output will be collected at the time a discrete event occurs.

     - | `start_time` (float): the output start time. If the model is not at that start time, a simulation
       |  will be performed in one step, to reach it before starting to collect output.

     - | `step_number` or `intervals` (int): the number of output steps. (will only be used if `automatic`
       | or `stepsize` is not used.

     - | `stepsize` (float): the output step size (will only be used if `automatic` is False).

     - | `seed` (int): set the seed that will be used if `use_seed` is true, using this stochastic trajectories can
       | be repeated

     - | 'use_seed' (bool): if true, the specified seed will be used.

     - | `a_tol` (float): the absolute tolerance to be used

     - | `r_tol` (float): the relative tolerance to be used

     - | `max_steps` (int): the maximum number of internal steps the integrator is allowed to use.

     - | `use_concentrations` (bool): whether to return just the concentrations (default)

     - | `use_numbers` (bool): return all elements collected

    :return: data frame with simulation results
    :rtype: pandas.DataFrame
    """
    num_args = len(args)
    model = kwargs.get('model', model_io.get_current_model())
    use_initial_values = kwargs.get('use_initial_values', True)

    task = model.getTask('Time-Course')
    assert (isinstance(task, COPASI.CTrajectoryTask))

    if 'scheduled' in kwargs:
        task.setScheduled(kwargs['scheduled'])

    if 'update_model' in kwargs:
        task.setUpdateModel(kwargs['update_model'])

    if 'method' in kwargs:
        task.setMethodType(__method_name_to_type(kwargs['method']))

    problem = task.getProblem()
    assert (isinstance(problem, COPASI.CTrajectoryProblem))

    if 'duration' in kwargs:
        problem.setDuration(kwargs['duration'])

    if 'automatic' in kwargs:
        problem.setAutomaticStepSize(kwargs['automatic'])

    if 'output_event' in kwargs:
        problem.setOutputEvent(kwargs['output_event'])

    if 'start_time' in kwargs:
        problem.setOutputStartTime(kwargs['start_time'])

    if 'step_number' in kwargs:
        problem.setStepNumber(kwargs['step_number'])

    if 'intervals' in kwargs:
        problem.setStepNumber(kwargs['intervals'])

    if 'stepsize' in kwargs:
        problem.setStepSize(kwargs['stepsize'])

    if num_args == 3:
        problem.setOutputStartTime(args[0])
        problem.setDuration(args[1])
        problem.setStepNumber(args[2])
    elif num_args == 2:
        problem.setDuration(args[0])
        problem.setStepNumber(args[1])
    elif num_args > 0:
        problem.setDuration(args[0])

    problem.setTimeSeriesRequested(True)

    method = task.getMethod()
    if 'seed' in kwargs and method.getParameter('Random Seed'):
        method.getParameter('Random Seed').setIntValue(int(kwargs['seed']))
    if 'use_seed' in kwargs and method.getParameter('Random Seed'):
        method.getParameter('Use Random Seed').setBoolValue(bool(kwargs['use_seed']))
    if 'a_tol' in kwargs and method.getParameter('Absolute Tolerance'):
        method.getParameter('Absolute Tolerance').setDblValue(float(kwargs['a_tol']))
    if 'r_tol' in kwargs and method.getParameter('Relative Tolerance'):
        method.getParameter('Relative Tolerance').setDblValue(float(kwargs['r_tol']))
    if 'max_steps' in kwargs and method.getParameter('Max Internal Steps'):
        method.getParameter('Max Internal Steps').setIntValue(int(kwargs['max_steps']))

    result = task.initializeRaw(COPASI.CCopasiTask.OUTPUT_UI)
    if not result:
        raise RuntimeError("Error while initializing the simulation: " +
                      COPASI.CCopasiMessage.getLastMessage().getText())
    else:
        result = task.processRaw(use_initial_values)
        if not result:
            raise RuntimeError("Error while running the simulation: " +
                          COPASI.CCopasiMessage.getLastMessage().getText())

    use_concentrations = kwargs.get('use_concentrations', True)
    if 'use_numbers' in kwargs and kwargs['use_numbers']:
        use_concentrations = False

    return __build_result_from_ts(task.getTimeSeries(), use_concentrations)


if __name__ == "__main__":

    from code.comparisonpy import MODELS_DIR
    from basico import load_model, model_io  # , run_time_course

    for mid in [
        "BIOMD0000000514",
        "BIOMD0000000515",
        "BIOMD0000000516",
    ]:
        model_path = MODELS_DIR / "biomodels" / f"{mid}.xml"

        model: CDataModel = load_model(str(model_path))
        df = run_time_course(
            model=model,
            start_time=0,
            duration=100,
            step_number=100,
            a_tol=1E-10,
            r_tol=1E-10,
        )

        print(df)