#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module introduces the functions needed for evaluating an agent's self.
"""
import pickle
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..generation import helpers


def generate_dialogue(dia_generator, agent, users, agent_prob=None):
    """
    Generates a dialogue where the user issues a request to the agent.

    Parameters
    ----------
    dia_generator : DialogueGenerator
        The dialogue generator is used for generating the dialogue.
    agent : Entity
        The agent that receives a command from a user.
    users : list
        A list of users that can issue commands.
    agent_prob : float, optional
        The probability that the agent will participate in the generated dialogue.
        If the agent is not selected, then some random user will get a command from
        another user.

    Returns
    -------
    Dialogue
        The generated dialogue.

    """
    if agent_prob is None:
        agent_prob = 1/(len(users)+1)

    rand_num = dia_generator.random_gen.choices([0, 1], weights=[1-agent_prob, agent_prob], k=1)[0]
    if rand_num != 1:
        agent = dia_generator.random_gen.choice(users)

    user = dia_generator.random_gen.choice(users)

    structure_list = helpers.generate_primitive_structure(dia_generator.random_gen, dia_generator.primitive_templates)
    default_args_list = [{"agent": agent,
                          "user": user}]

    out = dia_generator.generate_dialogue(structure_list=structure_list,
                                          default_args_list=default_args_list)
    return out


def eval_dialogue(agent_policy, dialogue):
    """ Evaluates a dialogue by replacing the default rule-based self with the agent_policy.
        But first, it checks whether the dialogue goal can be fulfilled with the rule-based self.
    """

    result = None
    dialogue_players = dialogue.get_players()

    if agent_policy.player in dialogue_players:

        state = dialogue.save_state()

        dialogue.run()
        if dialogue.evaluate_goal() == 1:
            max_episode_len = dialogue.counter
            dialogue.recover_state(state)

            dialogue.max_episode_length = max_episode_len
            old_policies = dialogue.get_player_policies(agent_policy.player)
            dialogue.replace_player_policies([agent_policy]*len(old_policies))

            dialogue.run()
            result = dialogue.evaluate_goal()

        else:

            dialogue.recover_state(state)

    return result


def eval_dialogues(agent_policy, dialogues, save_state=True):
    """
    Evaluates multiple dialogues using the eval_dialogue function.

    Parameters
    ----------
    agent_policy : Policy
        This self replaces the rule-based self in the dialogue.
    dialogues : list
        A list of Dialogue instances to be evaluated.
    save_state : bool, optional
        If True, it saves the dialogues' state and recovers it after the execution of the dialogues.
     
    Returns
    -------
    results : list
        The list of evaluated dialogues.

    """
    dialogues_states = []
    results = []
    for dia in dialogues:
        if not save_state:
            dialogues_states.append(dia.save_state())
        results.append(eval_dialogue(agent_policy, dia))

    if not save_state:
        for idx in range(len(dialogues_states)-1, -1, -1):
            dialogues[idx].recover_state(dialogues_states[idx])

    return results


def generate_and_eval(dia_generator, min_num_dialogues, min_agent_dialogues, agent_policy, flush_after=None,
                      agent_prob=None, forgetful=False, return_dias=False, notebook_run=False,
                      generate_dialogue_func=generate_dialogue, warm_up=0):
    """
    Generates a number of dialogues and evaluates
    how many of the generated dialogues are a success when using the agent_policy.

    Parameters
    ----------
    dia_generator : DialogueGenerator
        The object used for generating dialogues.
    min_num_dialogues : int
        The minimum number of dialogues to be generated.
    min_agent_dialogues : int
        The minimum number of dialogues to be generated where the agent participates in the dialogue.
    agent_policy : Policy
        The agent self generates utterances in the dialogues.
    flush_after: int
        It calls the dia_generator.flush() after the context reaches a certain length. It is done because
        the context size might grow large and not fit in RAM.
    agent_prob : float
        The probability that the player will be a participant and an agent in the next generated dialogue.
        The player is the owner of the agent_policy. The probability value ranges from 0 to 1.
    forgetful: bool
        If True, it saves the dialogue state before the dialogue execution and later recovers the state.
        For example, a dialogue changes the context state when a player utters. Later, this change is reverted.
    return_dias: bool
        If False, the generated dialogues are not returned. This might save RAM, otherwise all dialogues
        are appended to a list that may fill the RAM after some time.
    notebook_run : bool
        This parameter indicates whether the function is run from a jupyter notebook (True) or not (False).
        This parameter ensures the progress bars are shown correctly in a jupyter notebook.
    generate_dialogue_func : func
        The function used for generating a dialogue before it's evaluated.
    warm_up : int
        The number of dialogues generated before the evaluation starts. The evaluated agent can learn from them
        on how to respond in the dialogues that follow.

    Returns
    -------
    dias : list
        The list of generated dialogues.
        The list contains all dialogues (including the ones where the agent is not a participant).
        If return_dias is False, an empty list is returned.
    individual_accuracies : dict
        The accuracy the agent has achieved per dialogue type.
    total_accuracy : int
        The number of successful dialogues where the agent participates divided by the total number of dialogues
        where the agent participates.
    total_num_dias : int
        The total number of dialogues generated where the agent participates.
    time_points : list
        A list of tuples (dia_type, eval_result, context_size). It helps evaluate how the agent
        performs over time.
    succ_total : dict
        A mapping from the dialogue type to the tuple (#num_succ, #num_total), where #num_succ is
        the total number of successful dialogues and #num_total is the total number of dialogues from that specific type
    accuracy_per_step : dict
        A mapping from the maximum number of steps needed for a dialogue to be successful to
        the accuracy of all dialogues that have that particular maximum number of steps.
    succ_total_per_step : dict
        A mapping from the maximum number of steps needed for a dialogue to be successful to
        the tuple (#num_succ, #num_total), where #num_succ is the number of successful dialogues
        that have that particular maximum number of steps and #num_total is the total number of dialogues
        that have that particular maximum number of steps.



    """
    if notebook_run:
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm

    agent = agent_policy.player
    world = dia_generator.world
    other_agents = world.players
    other_agents = [p for p in other_agents if p != agent]

    dias = []
    d = 0
    ad = 0
    dialogues_states = []
    dia_type_success = {}
    dia_type_total = {}
    success_per_step = {}
    total_per_step = {}
    time_points = []

    if min_num_dialogues is None:
        min_num_dialogues = 0

    if min_agent_dialogues is None:
        min_agent_dialogues = 0

    progress_bar_num = tqdm(total=min_num_dialogues, position=1)
    progress_bar_agent = tqdm(total=min_agent_dialogues, position=0)

    for _ in range(warm_up):
        dialogue = dia_generator.generate_dialogue()
        if dialogue is None:
            continue
        dialogue.run()
        if forgetful:
            dialogues_states.append(dialogue.save_state())
        if return_dias or forgetful:
            dias.append(dialogue)

    last_context_id = 0
    total_context_size = 0
    while d < min_num_dialogues or ad < min_agent_dialogues:

        dialogue = generate_dialogue_func(dia_generator, agent, other_agents, agent_prob)
        if dialogue is None:
            continue
        if forgetful:
            dialogues_states.append(dialogue.save_state())

        eval_result = eval_dialogue(agent_policy, dialogue)
        dia_type = dialogue.policies[0].__class__.__name__.split("Policy")[0]
        if eval_result is not None:
            ad += 1
            progress_bar_agent.update(1)
            update_acc_table(dia_type_success, dia_type_total, dia_type, eval_result, dialogue.max_episode_length, success_per_step, total_per_step)

            for sent in dia_generator.context_strings[last_context_id:]:
                total_context_size += len(sent.split())
            last_context_id = len(dia_generator.context_strings)
            time_points.append((dia_type, max(eval_result, 0), total_context_size))
        else:
            dialogue.run()

        progress_bar_num.update(1)

        d += 1
        if return_dias or forgetful:
            dias.append(dialogue)

        if flush_after is not None and len(dia_generator.context) >= flush_after:
            dia_generator.flush()

    progress_bar_agent.close()
    progress_bar_num.close()

    if forgetful:
        for idx in range(len(dialogues_states)-1, -1, -1):
            dias[idx].recover_state(dialogues_states[idx])

    individual_accuracies = {key: 100*val / dia_type_total[key] for key, val in dia_type_success.items()}
    succ_total = {key: (val, dia_type_total[key]) for key, val in dia_type_success.items()}
    total_num_dias = sum(dia_type_total.values())
    total_accuracy = 100*sum(dia_type_success.values())/total_num_dias
    accuracy_per_step = {key: 100*val/total_per_step[key] for key, val in success_per_step.items()}
    succ_total_per_step = {key: (val, total_per_step[key]) for key, val in success_per_step.items()}
    return dias, individual_accuracies, total_accuracy, total_num_dias, time_points, succ_total, accuracy_per_step, succ_total_per_step


def update_acc_table(dia_type_success, dia_type_total, dia_type, eval_result, num_steps, success_per_step, total_per_step):
    """ Updates the number of successful dialogues per dialogue type and the total number of dialogues per type.

    Parameters
    ----------
    dia_type_success : dict
        A mapping from a dialogue type to the number of successful dialogues per dialogue type.
    dia_type_total : dict
        A mapping from a dialogue type to the number of total dialogues per dialogue type.
    dia_type : Dialogue
        The dialogue is used to fetch the user self in order to get the dialogue type. The user request
        dictates the dialogue type. For example, the user request can be: Hannah get the apple or
        Hannah, Is the apple red?
    eval_result : int
        It indicates whether the dialogue was successful. A value of 1 indicates success.
    num_steps : int
        The maximum number of steps that the dialogue needs to finish successfully.
    success_per_step : dict
        A mapping from the maximum number of steps to the number of successful dialogues that require that number.
    total_per_step : dict
        A mapping from the maximum number of steps to the total number of dialogues that require that number.


    Returns
    -------
    None
    """

    if dia_type not in dia_type_total:
        dia_type_total[dia_type] = 0
    if dia_type not in dia_type_success:
        dia_type_success[dia_type] = 0
    if num_steps not in success_per_step:
        success_per_step[num_steps] = 0
    if num_steps not in total_per_step:
        total_per_step[num_steps] = 0

    dia_type_total[dia_type] += 1
    total_per_step[num_steps] += 1
    if eval_result == 1:
        dia_type_success[dia_type] += 1
        success_per_step[num_steps] += 1


def accuracy_dia_type(main_player, dias, eval_results):
    """
    Shows the accuracy for each dialogue type.
    The accuracy is computed by dividing the number of successful dialogues by the total number of dialogues.

    Parameters
    ----------
    main_player : Entity
        The agent that is trained.
    dias : list
        The list of dialogues that were evaluated.
    eval_results : list
        The results from the dialogues' evaluation.
        if eval_results[idx] is 1 means that the dialogue dias[idx] was successful.

    Returns
    ----------
    accuracies : list
        A list of tuples in the form: (dia_type, accuracy)
    """
    dia_type_total = {}
    dia_type_success = {}
    for idx, dia in enumerate(dias):
        dia_type = dia.policies[0].__class__.__name__.split("Policy")[0]
        if dia_type not in dia_type_total:
            dia_type_total[dia_type] = 0
        if dia_type not in dia_type_success:
            dia_type_success[dia_type] = 0

        dialogue_players = dia.get_players()
        if main_player in dialogue_players:
            dia_type_total[dia_type] += 1
            if eval_results[idx] == 1:
                dia_type_success[dia_type] += 1
    accuracies = [(key, str(val)+"/"+str(dia_type_total[key])+"="+str(val/dia_type_total[key])) for key, val in dia_type_success.items()]

    return accuracies


def pretty_print_eval(sol_name, individual_accuracies, total_accuracy, succ_total, num_agent_dias):
    """ Prints the metrics for the leaderboard.

        Parameters
        ----------
        sol_name : str
            The unique solution's name.
        individual_accuracies : dict
            A mapping task_name : task_accuracy.
        total_accuracy : int
            The accuracy across all tasks.
        num_agent_dias : int
            The number of dialogues used for computing the accuracies where the agent participates.


        Returns
        ----------
        None

    """

    tasks = list(individual_accuracies.keys())

    print(f"{sol_name:^40}")  # Centered in 40 characters
    print("=" * 40)
    print(f"{'Type':<15}{'Accuracy (%)':<15}{'Num. Dialogues':<10}")
    print("-" * 40)
    for acc_name in tasks:
        acc = individual_accuracies[acc_name]
        num_dias = succ_total[acc_name][1]
        print(f"{acc_name:<15}{acc:<15.2f}{num_dias:<10}")
    print(f"The total accuracy (%): {total_accuracy:.2f}")
    print("The total number of dialogues: ", num_agent_dias)


def pretty_print_acc_per_step(sol_name, acc_per_step, total_per_step):
    """ Prints the accuracy of the dialogues
    relative to the number of steps needed for the dialogue to be successful. """

    print(f"{sol_name:^40}")  # Centered in 40 characters
    print("=" * 40)
    print(f"{'Num. Steps':<15}{'Accuracy (%)':<15}{'Num. Dialogues':<10}")
    num_steps = list(acc_per_step.keys())
    num_steps.sort()
    for key in num_steps:
        num_dias = total_per_step[key][1]
        print(f"{key:<15}{acc_per_step[key]:<15.2f}{num_dias:<10}")


def plot_context_sizes(time_points, instructions_size, token_factor=1.3):
    """ Plot the context size over time. """
    # the size of the context in tokens
    context_sizes = [int((pnt[2]+instructions_size)*token_factor) for pnt in time_points]
    epochs = [idx+1 for idx in range(len(context_sizes))]

    plt.plot(epochs, context_sizes)


def plot_acc(outcomes, label, epochs=None, smooth_over=10, show_plot=True):
    """
    Plot the accuracy over time.

    Parameters
    ----------
    outcomes : list
        A list of 1s and 0s where 1 is a success.
    label : str
        The title of the plot.
    epochs : list
        A list of the x-axis values
    smooth_over : int
        The number of outcomes taken and averaged over in a sliding window fashion.
    show_plot : bool
        A value indicating whether the plot should be shown.

    """
    successes = 0
    accuracy = []
    window = deque(maxlen=smooth_over)
    if epochs is None:
        epochs = [idx for idx in range(smooth_over-1, len(outcomes))]

    for i, outcome in enumerate(outcomes, start=1):
        successes += outcome
        window.append(successes / i)

        if len(window) == window.maxlen:
            accuracy.append(sum(window) / len(window))

    def human_format(x, pos=None):
        """Format tick labels with K/M/B suffixes and drop .0 when unnecessary."""
        if x >= 1_000_000_000:
            value = x / 1_000_000_000
            suffix = "B"
        elif x >= 1_000_000:
            value = x / 1_000_000
            suffix = "M"
        elif x >= 1_000:
            value = x / 1_000
            suffix = "K"
        else:
            value = x
            suffix = ""

        # Format with one decimal, but drop .0 if not needed
        if value.is_integer():
            return f"{int(value)}{suffix}"
        else:
            return f"{value:.1f}{suffix}"

    plt.gca().xaxis.set_major_formatter(FuncFormatter(human_format))

    plt.plot(epochs, accuracy, label=label)
    plt.ylim(0, 1)
    plt.grid(True)
    plt.legend()
    if show_plot:
        plt.show()


def plot_acc_individual(test_points, smooth_over=50, show_plot=False):
    """ Plot accuracy over time graphs for each dialogue type and merge them in one. """
    task_types = {}
    for pnt in test_points:
        if pnt[0] not in task_types:
            task_types[pnt[0]] = []
        task_types[pnt[0]].append(pnt[1])
    for key, val in task_types.items():
        plot_acc(val, key, smooth_over=smooth_over, show_plot=False)
    if show_plot:
        plt.show()


def save_results(filename, test_points, succ_total, succ_total_per_step):
    """
    Save variables to a pickle file.
    """
    data = {
        "test_points": test_points,
        "succ_total": succ_total,
        "succ_total_per_step": succ_total_per_step
    }

    with open(filename, "wb") as f:
        pickle.dump(data, f)

    print(f"Data saved to {filename}")


def load_and_merge_results(filenames):
    """
    Load multiple pickle files containing all the saved dictionaries from the results and merge them.
    The dictionaries stored are: test_points, succ_total, succ_total_per_step

    Later, the dictionaries individual_accuracies, total_accuracy, total_num_dias are recomputed
    which are necessary for printing the results. They are returned together with the merged dictionaries.

    """

    dia_type_success = {}
    dia_type_total = {}
    succ_per_step = {}
    total_per_step = {}
    test_points = []
    for file in filenames:
        with open(file, "rb") as f:
            data = pickle.load(f)
            succ_total = data.get("succ_total", {})
            for key, val in succ_total.items():
                if key not in dia_type_success:
                    dia_type_success[key] = 0
                if key not in dia_type_total:
                    dia_type_total[key] = 0
                dia_type_success[key] += val[0]
                dia_type_total[key] += val[1]
            succ_total_per_step = data.get("succ_total_per_step", {})
            for key, val in succ_total_per_step.items():
                if key not in succ_per_step:
                    succ_per_step[key] = 0
                if key not in total_per_step:
                    total_per_step[key] = 0
                succ_per_step[key] += val[0]
                total_per_step[key] += val[1]
            tp = data.get("test_points", [])
            test_points += tp
    individual_accuracies = {key: 100 * val / dia_type_total[key] for key, val in dia_type_success.items()}
    acc_per_step = {key: 100 * val / total_per_step[key] for key, val in succ_per_step.items()}

    succ_total_per_step = {key: (val, total_per_step[key]) for key, val in succ_per_step.items()}
    succ_total = {key: (val, dia_type_total[key]) for key, val in dia_type_success.items()}
    total_num_dias = sum(dia_type_total.values())
    total_accuracy = 100 * sum(dia_type_success.values()) / total_num_dias
    return individual_accuracies, total_accuracy, total_num_dias, test_points, succ_total, acc_per_step, succ_total_per_step
