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

Materials innovation have been undergoing rapid development with the vast combinatorial exploration of recipes; however, the related research suffers from time-consuming trial-and-error synthesis and labour-intensive fabrication. As a promising alternative, robotics enables high-throughput experimentation and data collection; however, the resulting numerical datasets are often insufficiently analysed and fail to provide effective feedback for semantic recipe optimisation. 

Here, we present a domain-specific recipe language model (RLM) developed for an emerging scientific tool of robotic boxes (perovskite solar cell research as a demonstration). For iterative fine-tuning of the RLM, seven artificial intelligence (AI) layers, including learning, generating, RecipeQA, fine-tuning, reasoning, evaluation, and optimisation, have been designed with a language agent. During the loops of seven AI layers, both numerical and semantic recipes were continuously learned and optimised for the RLM. Guided by this RLM, eleven robotic boxes executed the controllable synthesis, fabrication and characterisation of 50,764 samples. Simultaneously, more than 578 million tokens were generated and augmented to improve the ability to recommend a recipe and mechanistic reasoning, reaching a level comparable to that of an experienced researcher. 

Therefore, the integration of the RLM with robotic boxes enables an AI and robotics discovery process in which specialised language modelling and modularised robotic hardware continuously improve one another, suggesting an evolution of physical AI for the Materials Intelligence.

---

## 2. Model Summary

### Fine-tuning of the RLM with robotics

To train this domain-specific RLM, the workflow starts from encoded formulas and parameters as recipe inputs, proceeds through seven AI layers with the language agent, executes synthesis and fabrication within eleven interconnected robotic boxes and produces in situ characterisation and device performance assessment as mechanistic outputs. As a result, the fine-tuned RLM incorporates the encoded recipes, robotics, and characterised results to form a closed recommendation–synthesis–fabrication–characterisation–mechanism loop for exploring the large space of the recipes and their underlying mechanisms. The language agent then encoded these machine-readable recipes into structured formulas and parameters sequences, which were translated into tokens for subsequent fine-tuning of the RLM and execution by the robotic boxes.

---

### Seven AI layers Architecture for RLM Training

### [Learning](seven_ai_layers_robotics/learning/README.md)

In the learning layer, the formulas and parameters are encoded and then tokenised into recipes as inputs. Through atomic skills of data extraction, cleaning, and matching, these data are organised into standardised datasets, providing the basis for RLM training and iterative recipe refinement.

### [Generating](seven_ai_layers_robotics/generating/README.md)

In the generating layer, the tokenised recipes are comprised into the recipe report with fabrication details, mechanistic descriptions, an optimisation summary, and supporting information. Through atomic skills of edge reporting (generation from single experimental data), single-variable reporting (generation from matched data with single variable), and characterization reporting (generation from matched data with in situ characterization), these processed data are converted into robotic recipe reports.

### [RecipeQA](seven_ai_layers_robotics/recipeQA/README.md)

In the RecipeQA layer, the recipe reports are further converted into semantically structured question–answer pairs (RecipeQA). The primary objective of this layer is to construct high-quality, domain-specific training corpora through key atomic skills of Report to QA (convert recipe reports into semantically structured RecipeQA) and Distillation (knowledge distillation for RecipeQA).

### [Fine-Tuning](seven_ai_layers_robotics/fine_tuning/README.md)

In the fine-tuning layer, the base model (Qwen3-32B) together with the RecipeQA corpora are taken as the input of this layer. Through low-rank adaptation (LoRA), the model is efficiently adapted to domain-specific recipe knowledge and transformed into a domain-specific RLM as output. 

### [Reasoning](seven_ai_layers_robotics/reasoning/README.md)

In the reasoning layer, the fine-tuned domain-specific RLM to generate mechanistic interpretations, performance explanations, and recipe optimization suggestions from experimental records. These reasoning results serve as an important bridge between trained model capability and practical scientific decision-making, and also provide candidate knowledge and reasoning evidence for the downstream Evaluation Layer and Optimization Layer.

### [Evaluation](seven_ai_layers_robotics/evaluation/README.md)

In the evaluation layer, the recipe recommendations and mechanistic reasoning are evaluated, in order to measure their effectiveness, reliability, and scientific validity. Through key atomic skills of recipe recommendation and mechanistic reasoning, the aspects of recipe integrity, formula rationality, parameter rationality, experimental validation, domain knowledge, mechanism integrity, interpretation, comprehensiveness and coherence are systematically assessed.

### [Optimization](seven_ai_layers_robotics/optimization/README.md)

In the optimization layer, the RLM to be optimised and preference pairs of positive and negative samples are taken as the input of this layer. Through atomic skill of Direct Preference Optimisation (DPO), an optimised RLM is obtained as output. This layer further aligns the model towards preference-consistent and high-performance recipe recommendation.

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
| RLM-v1 | Qwen3-32B  | LoRA (merged) | 🤗 [Hugging Face](https://huggingface.co/MI-Materials-Intelligence/Recipe-Language-Model) |

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
  howpublished={\url{https://github.com/MI-Materials-Intelligence/Recipe-Language-Model}}
}
```
---

## 6. Contact

For questions or collaboration，please contact us at Material_Intelligence@outlook.com

---
