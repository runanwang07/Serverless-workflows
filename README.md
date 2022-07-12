# Enhancing Performance Modeling of Serverless Functions via Static Analysis
This repository provides the source code of the serverless workflows evaluated for the proposed performance model in the submission of Paper "*Enhancing Performance Modeling of Serverless Functions via Static Analysis*" to ICSOC 2022.
## Organization of the repository
- example source code: the source code of the example in Figure 3, which has been adopted from [Azure Function with Python](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=azure-cli%2Cbash%2Cbrowser).
- individual serverless functions: several individual serverless functions with the functionalities of pre-processing images and classification. The tensorflow-based method is derived from [Azure Function with Machine Learning](https://docs.microsoft.com/en-us/azure/azure-functions/functions-machine-learning-tensorflow?tabs=bash). Another four image classification functions are developed with the pre-trained models from [Onnx Model Zoo](https://github.com/onnx/models).

- orchestration function: source code of the 4 workflow composition patterns used in the experiments.
All the above serverless functions are developed with Python 3.7 and Azure Function 3.0.

## Prerequisites
- Python 3.7
- Azure Function runtime 3.0

## Workflow Pattern
Different compositions of workflows have been defined with 4 orchestrators based on Azure Function under <code><b>orchestration function</b></code> folder.
- wf1: Sequential workflow
- wf2: Branching workflow conditional on the user inputs
- wf3: Parallel execution workflow with 4 image processing models
- wf4: Complex workflow with branches, parallelism and sequence execution
