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

Here, we present a domain-specific recipe language model (RLM) developed for an emerging scientific tool of robotic boxes (perovskite solar cell research as a demonstration). For iterative fine-tuning of the RLM, seven artificial intelligence (AI) layers, including learning, generating, RecipeQA, fine-tuning, reasoning, evaluation, and optimisation, have been designed with a language agent. During the loops of seven AI layers, both numerical and semantic recipes were continuously learned and optimised for the RLM. Guided by this RLM, eleven robotic boxes executed the controllable synthesis, fabrication and characterisation of 50,764 samples. Simultaneously, more than 578 million tokens were generated and augmented to improve the ability to recommend a recipe and mechanistic reasoning, reaching a level comparable to that of an experienced researcher. Therefore, the integration of the RLM with robotic boxes enables a closed AI–robotics discovery process in which specialised language modelling and robotic hardware continuously improve one another, suggesting an evolution of physical AI for materials research.

---

## 2. Model Summary

### Seven AI Layers Architecture for RLM Training

- We develop a seven AI layers architecture for a domain-specific RLM from structured formulas and parameters of recipes.

- With closed AI–robotics loop for recipes learning and refinement, the RLM advances from numerical recipe modelling to semantic and mechanism-grounded reasoning.


---

### Architecture Overview

### [Learning](seven_ai_layers_robotics/learning/README.md)

Robotic experimental data are taken as the input of this layer, including formulas, parameters, in situ characterisation results, and device performance. Through data extraction, cleaning, and matching, these data are organised into standardised datasets, providing the basis for RLM training and iterative recipe refinement.

### [Generating](seven_ai_layers_robotics/generating/README.md)

Standardised datasets are taken as the input of this layer. Through edge reporting, single-variable reporting and characterization reporting, these processed data are converted into robotic recipe reports integrating formulas, parameters, performance, and mechanistic information. This layer provides structured textual data for corpus construction and RLM development.

### [RecipeQA](seven_ai_layers_robotics/recipeQA/README.md)

Standardised robotic recipe reports are taken as the input of this layer. Through report-to-QA conversion and knowledge distillation, experimental knowledge is transformed into semantically structured RecipeQA corpora as output. This layer converts structured reports into domain-specific training data for RLM training.

### [Fine-tuning](seven_ai_layers_robotics/fine_tuning/README.md)

The base model (Qwen3-32B) together with the RecipeQA corpora are taken as the input of this layer. Through low-rank adaptation (LoRA), the model is efficiently adapted to domain-specific recipe knowledge and transformed into a domain-specific RLM as output. This layer establishes the specialised language modelling capability required for recipe understanding.

### [Reasoning](seven_ai_layers_robotics/reasoning/README.md)

The base recipe report is taken as the input of this layer. Through the domain-specific RLM, it is refined into an recommended recipe report together with a corresponding mechanistic explanation as output. This layer supports model-guided recipe recommendation and provides interpretable rationales for subsequent evaluation.

### [Evaluation](seven_ai_layers_robotics/evaluation/README.md)

Recommended recipe reports are taken as the input of this layer. Through joint numerical and semantic evaluation, the capabilities of recipe recommendation and mechanistic reasoning are systematically assessed. This layer outputs structured evaluation results that provide the basis for RLM capability assessment and subsequent optimisation.

### [Optimization](seven_ai_layers_robotics/optimization/README.md)

The RLM to be optimised and preference pairs of positive and negative samples are taken as the input of this layer. Through Direct Preference Optimisation (DPO), an optimised RLM is obtained as output. This layer further aligns the model towards preference-consistent and high-performance recipe recommendation.

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
