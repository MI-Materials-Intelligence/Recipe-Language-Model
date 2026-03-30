<p align="center">
  <img src="https://github.com/user-attachments/assets/5463f8f2-7005-4bdf-8ffa-51149098388e" width="150"/>
</p>

<h2 align="center">Recipe Language Model </h2>


## Table of Contents

1. [Introduction](#introduction)
2. [Model Summary](#model-summary)
3. [Model Downloads](#model-downloads)
4. [License](#license)
5. [Citation](#citation)
6. [Contact](#contact)
---

## 1. Introduction

We present a language agent for materials intelligence, with seven AI layers of learning, generating, RecipeQA, fine-tuning, reasoning, evaluation, and optimisation. Guided by a language agent, eleven robotic boxes enabled the controllable synthesis, fabrication, and characterisation of 50,764 samples, while more than 578 million tokens, generated and augmented from tokenised formulas and parameters paired with their corresponding mechanisms. Through the process, a domain-specific Recipe Language Model (RLM) is trained to address the vast combinatorial exploration of recipes in large chemical spaces. Progressively, the capabilities of the RLM in recipe recommendation and mechanistic reasoning have been enhanced to a level comparable to that of an experienced researcher. Herein, with a language agent, robotic boxes for fabricating perovskite solar cells  as a demonstration is to show a general framework and scientific tool for next-generation materials research through a closed recommendation–synthesis–fabrication–characterisation–mechanism loop, enabling exploration of the large space of recipes and their underlying mechanisms. Therefore, RLM enables a closed AI–robotics discovery process in which specialised language modelling and robotic hardware continuously improve one another, suggesting a new form of physical AI for materials research.

---

## 2. Model Summary

### Language Agent with Seven AI Layers Architecture

- On top of the structured formulas and parameters of PSC recipes, we develop a language agent–coordinated seven AI layers architecture for RLM development, enabling unified optimisation of recipes within a single framework.

- We establish a robotic closed loop for recipe learning and refinement, which drives the evolution of the RLM from numerical recipe modelling to semantic and mechanism-grounded reasoning.

---

### Architecture Overview

### [Learning](seven_ai_layers_loop/learning/README.md)

Robotic experimental data serve as the input of the architecture, establishing the data foundation for recipe learning and iterative refinement.

### [Generating](seven_ai_layers_loop/generating/README.md)

Structured robotic recipe reports are generated from experimental data. Formulas, parameters, performance, and mechanistic information are organised into a standardised format.

### [RecipeQA](seven_ai_layers_loop/recipeQA/README.md)

Domain-specific corpora are extracted from robotic recipe reports. Experimental knowledge is transformed into semantically structured QA pairs for recipe understanding and reasoning.

### [Fine-tuning](seven_ai_layers_loop/fine_tuning/README.md)

Low-Rank Adaptation (LoRA) is employed to construct the domain-specific RLM, enabling efficient adaptation to recipe corpora with reduced training cost.

### [Reasoning](seven_ai_layers_loop/reasoning/README.md)

The fine-tuned RLM generates recommended recipes along with mechanistic explanations, serving as inputs for subsequent evaluation.

### [Evaluation](seven_ai_layers_loop/evaluation/README.md)

Both numerical and semantic evaluations are conducted on recommended recipe reports, systematically assessing the capabilities of recipe recommendation and mechanistic reasoning.

### [Optimization](seven_ai_layers_loop/optimization/README.md)

Direct Preference Optimisation (DPO) is applied to further align the RLM, promoting preference-consistent and high-performance recipe recommendations.

---

## 3. Model Downloads

To simplify usage, we release merged models where LoRA weights are already integrated into the base model.

This allows users to:

- Run inference directly  
- Avoid manual LoRA merging  
- Ensure consistent behavior across environments  

---

### Model List

| Model  | Base Model | Type          | Download                                                     |
| ------ | ---------- | ------------- | ------------------------------------------------------------ |
| RLM-v1 | Qwen3-32B  | LoRA (merged) | 🤗 [Hugging Face](https://huggingface.co/MI-Materials-Intelligence/RLM) |

---

## 4. License

This project is released under the MIT License.

---

## 5. Citation

If you find this work useful, please cite:

```bibtex
@misc{miagent_2026,
  author={MI-Materials-Intelligence},
  year={2026},
  howpublished={\url{https://github.com/MI-Materials-Intelligence/MIAgent}}
}
```
---

## 6. Contact

For questions or collaboration，please contact us at Material_Intelligence@outlook.com

---
