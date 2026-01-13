## PyDialogue <img src="https://pydialogue.com/logo.png" width="20%"> 
![License](https://img.shields.io/badge/License-MIT-orange.svg)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Repo Size](https://img.shields.io/github/repo-size/smartinovski/pydialogue?color=ff1493)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

PyDialogue is a library that generates synthetic dialogue data from rule-based templates. The dialogues are simulated interactions between a user and a conversational agent. The library can be used to generate large-scale dialogue data to train and improve chatbot models. The models can be trained using supervised or reinforcement learning without the need for human-provided feedback. 

We currently have five templates from the reasoning domain in our [Templates Gallery](https://pydialogue.com/gallery). One of the best features of our library is mixing and matching different dialogues within a single chat session to create unique and complex contexts unseen by the model. In addition, PyDialogue provides the necessary tools to develop new templates that can be shared among developers. 

You can see all the ways our library can be used [here.](#what-can-you-do-with-this-library)

## Installation
Using pip:

```bash
pip install pydialogue
```

This project requires the nltk data: wordnet, punkt_tab, and averaged_perceptron_tagger_eng. They will be automatically installed during the first import. 

## Dependencies

- Python 3.10 or greater
- dijkstar
- file-read-backwards
- tqdm
- notebook
- ipywidgets
- nltk
- pyinflect
- torch (optional)
- openai (optional)
- faiss-cpu (optional) 

## Usage

For quickly simulating and running a dialogue using the existing templates:

```python
from pydialogue import DialogueGenerator
import pydialogue.environments.easy as easy_env

easy_world = easy_env.build_world()
generator = DialogueGenerator(easy_world, "error.log", "context.log")
dialogue = generator.generate_dialogue()
dialogue.run()
for utter in dialogue.utterances:
    print(utter.to_string())
```
The error.log and context.log indicate where the errors and the sentences from the context are potentially stored. Please add the full path where you prefer to store them.

## What can you do with this library?
The library is multi-purpose and can be used for the following:
- **Simulate your custom dialogues.** Gathering dialogue data for some domains can be difficult. For example, chats that require the agent to do multi-hop logical reasoning in a long context. To program the logic of such dialogues, reasoning, and querying information from the context is needed. PyDialogue provides features that save developers time and allow them to focus on more creative aspects, such as simulating the interactions between dialogue participants. Please refer to this [notebook](https://github.com/smartinovski/pydialogue/blob/main/notebooks/template_tutorial.ipynb) for an example of how to simulate your custom dialogues.
- **Benchmark your models on already existing simulated dialogues.** Please check the following [notebook](https://github.com/smartinovski/pydialogue/blob/main/notebooks/evaluation.ipynb) to see how to evaluate your models and share your results. 
- **Build your custom benchmarks.** The library allows you to simulate data that you can fully control and evaluate different aspects of your model. By developing and sharing new templates, you also promote collaboration and help the community improve its models.
- **Simulate custom scenarios in a textual world.** PyDialogue includes a textual world, which is a simplified representation of the real world, where the dialogues happen. This allows the dialogues to include actions. For instance, in activities like shopping, the person visits the store, gets and drops items, and interacts with the employees and other customers. This can be useful for gathering realistic customer support data and improving service responses.

## The simulated dialogues
This library simulates dialogues/chats between a real person (user) and a conversational agent.  Besides conversing, the users and agents can act in a simulated textual world, such as picking up an item or opening a door. Below are examples of two brief dialogues, randomly generated from our templates: 
 
 ```
Jim says: Heidi, get the green apple.
Heidi tries going north.
Heidi goes north from the porch path. Heidi looks in the living room. Heidi sees the green apple.
Heidi tries getting the green apple in the living room.
Heidi gets the green apple.
The dialogue is successful.

Otto says: Heidi, look in the toy container.
Heidi says: Heidi can not look in the toy container. The toy container's location is not revealed.
The dialogue is successful.

```

The environment provides feedback each time a user or agent acts (except when executing the action "say"). Therefore, we consider the environment an additional dialogue participant. The agent continues to act until it achieves its goal or exceeds the maximum number of steps.

## How are the dialogues generated?

The dialogues are generated using preprogrammed templates. The templates are Python functions with parameters that specify the user, agent, their policies, and the dialogue's goal. 

The agents and the users respond in the dialogues using *policies*. The policies are Python classes and must be programmed with the logic that provides the agents' and users' responses. We call these policies rule-based, contrary to model-based policies that use a machine learning model to generate the responses. Most of the work when programming the templates goes to developing the policies. 
One of the reasons for this is that the agents must reason based on the context before responding. Our library simplifies this context-driven reasoning, allowing developers to focus on the creative aspects of policy development. This is done by converting the sentences and their parts into Python constructs called *semantic describers*. The describers allow checking whether two sentences are semantically equal, regardless of their syntactic variation up to a certain degree. This way, when the policy developer wants to search whether a specific sentence exists in the dialogue, it does not have to deal with time-consuming pattern matching. Moreover, if they want to extract some information from the sentence, they can easily do it by fetching the verb and the PropBank argument they are interested in.

Please learn more about the describers and other components of our library in the "Approach" section of our [paper](https://pydialogue.com/paper), where we describe the simulation process.

## The benchmark

We invite you to evaluate/benchmark your models on our [dialogues](https://github.com/smartinovski/pydialogue#the-simulated-dialogues). To help you get started, we have created the following notebook that contains an example of how to evaluate your models: [evaluation.ipynb](https://github.com/smartinovski/pydialogue/blob/main/notebooks/evaluation.ipynb). For a detailed description of the benchmark, please visit our [website](https://pydialogue.com/heidi).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/smartinovski/pydialogue/blob/main/notebooks/evaluation.ipynb)

If you have any questions or require assistance, please feel free to open a new GitHub issue. We're happy to inform you that we provide [documentation](https://pydialogue.com/docs) of our code.


## Contribute

### How to contribute

Currently, our core templates focus on logical reasoning. We are looking for community contributions to expand the library into new domains such as Healthcare, E-Commerce, or Casual Chat. If you have a specific use case in mind that you are interested in, please consider developing a new template.

* **Getting started**: We’ve prepared a [jupyter notebook](https://github.com/smartinovski/pydialogue/blob/main/notebooks/template_tutorial.ipynb) to walk you through developing your first template. 
* **Inspiration**: You can browse existing examples in the [Gallery](https://pydialogue.com/gallery) or check the "Limitations" section of our [paper](https://pydialogue.com/paper.html) for ideas on what needs improvement.
* **Earn recognition:** Your dialogue templates will be featured in our [Templates Gallery](https://pydialogue.com/gallery), where they can help other users generate dialogue data for niche or hard-to-obtain scenarios. Moreover, your simulated dialogues may contribute to science by becoming part of benchmarks that researchers use to evaluate and improve machine learning models.

### How to submit
To submit your dialogue template, open a Pull Request and place it in a separate folder under *contrib/* named after your project. Please include a short `README.md` or Jupyter Notebook describing your solution and how to use your template. Any additional materials, such as flow diagrams and a project report, that further describe your policies and templates are very welcome. Templates submitted as free contributions to this project must be licensed under the MIT License.

If you prefer to keep your template in your own repository, please open an *Issue* with the repository's link, and we will add it to our gallery.




