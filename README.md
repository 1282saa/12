# 🦜️🔗 LangChain

⚡ Build context-aware reasoning applications ⚡

[![Release Notes](https://img.shields.io/github/release/langchain-ai/langchain?style=flat-square)](https://github.com/langchain-ai/langchain/releases)
[![CI](https://github.com/langchain-ai/langchain/actions/workflows/check_diffs.yml/badge.svg)](https://github.com/langchain-ai/langchain/actions/workflows/check_diffs.yml)
[![PyPI - License](https://img.shields.io/pypi/l/langchain-core?style=flat-square)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-core?style=flat-square)](https://pypistats.org/packages/langchain-core)
[![GitHub star chart](https://img.shields.io/github/stars/langchain-ai/langchain?style=flat-square)](https://star-history.com/#langchain-ai/langchain)
[![Dependency Status](https://img.shields.io/librariesio/github/langchain-ai/langchain?style=flat-square)](https://libraries.io/github/langchain-ai/langchain)
[![Open Issues](https://img.shields.io/github/issues-raw/langchain-ai/langchain?style=flat-square)](https://github.com/langchain-ai/langchain/issues)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode&style=flat-square)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/langchain-ai/langchain)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/langchain-ai/langchain)
[![](https://dcbadge.vercel.app/api/server/6adMQxSpJS?compact=true&style=flat)](https://discord.gg/6adMQxSpJS)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/langchainai.svg?style=social&label=Follow%20%40LangChainAI)](https://twitter.com/langchainai)

Looking for the JS/TS library? Check out [LangChain.js](https://github.com/langchain-ai/langchainjs).

To help you ship LangChain apps to production faster, check out [LangSmith](https://smith.langchain.com). 
[LangSmith](https://smith.langchain.com) is a unified developer platform for building, testing, and monitoring LLM applications. 
Fill out [this form](https://www.langchain.com/contact-sales) to speak with our sales team.

## Quick Install

With pip:
```bash
pip install langchain
```

With conda:
```bash
conda install langchain -c conda-forge
```

## 🤔 What is LangChain?

**LangChain** is a framework for developing applications powered by large language models (LLMs).

For these applications, LangChain simplifies the entire application lifecycle:

- **Open-source libraries**:  Build your applications using LangChain's open-source [building blocks](https://python.langchain.com/v0.2/docs/concepts#langchain-expression-language-lcel), [components](https://python.langchain.com/v0.2/docs/concepts), and [third-party integrations](https://python.langchain.com/v0.2/docs/integrations/platforms/).
Use [LangGraph](/docs/concepts/#langgraph) to build stateful agents with first-class streaming and human-in-the-loop support.
- **Productionization**: Inspect, monitor, and evaluate your apps with [LangSmith](https://docs.smith.langchain.com/) so that you can constantly optimize and deploy with confidence.
- **Deployment**: Turn your LangGraph applications into production-ready APIs and Assistants with [LangGraph Cloud](https://langchain-ai.github.io/langgraph/cloud/).

### Open-source libraries
- **`langchain-core`**: Base abstractions and LangChain Expression Language.
- **`langchain-community`**: Third party integrations.
  - Some integrations have been further split into **partner packages** that only rely on **`langchain-core`**. Examples include **`langchain_openai`** and **`langchain_anthropic`**.
- **`langchain`**: Chains, agents, and retrieval strategies that make up an application's cognitive architecture.
- **[`LangGraph`](https://langchain-ai.github.io/langgraph/)**: A library for building robust and stateful multi-actor applications with LLMs by modeling steps as edges and nodes in a graph. Integrates smoothly with LangChain, but can be used without it.

### Productionization:
- **[LangSmith](https://docs.smith.langchain.com/)**: A developer platform that lets you debug, test, evaluate, and monitor chains built on any LLM framework and seamlessly integrates with LangChain.

### Deployment:
- **[LangGraph Cloud](https://langchain-ai.github.io/langgraph/cloud/)**: Turn your LangGraph applications into production-ready APIs and Assistants.

![Diagram outlining the hierarchical organization of the LangChain framework, displaying the interconnected parts across multiple layers.](docs/static/svg/langchain_stack_062024.svg "LangChain Architecture Overview")

## 🧱 What can you build with LangChain?

**❓ Question answering with RAG**

- [Documentation](https://python.langchain.com/v0.2/docs/tutorials/rag/)
- End-to-end Example: [Chat LangChain](https://chat.langchain.com) and [repo](https://github.com/langchain-ai/chat-langchain)

**🧱 Extracting structured output**

- [Documentation](https://python.langchain.com/v0.2/docs/tutorials/extraction/)
- End-to-end Example: [SQL Llama2 Template](https://github.com/langchain-ai/langchain-extract/)

**🤖 Chatbots**

- [Documentation](https://python.langchain.com/v0.2/docs/tutorials/chatbot/)
- End-to-end Example: [Web LangChain (web researcher chatbot)](https://weblangchain.vercel.app) and [repo](https://github.com/langchain-ai/weblangchain)

And much more! Head to the [Tutorials](https://python.langchain.com/v0.2/docs/tutorials/) section of the docs for more.

## 🚀 How does LangChain help?
The main value props of the LangChain libraries are:
1. **Components**: composable building blocks, tools and integrations for working with language models. Components are modular and easy-to-use, whether you are using the rest of the LangChain framework or not
2. **Off-the-shelf chains**: built-in assemblages of components for accomplishing higher-level tasks

Off-the-shelf chains make it easy to get started. Components make it easy to customize existing chains and build new ones. 

## LangChain Expression Language (LCEL)

LCEL is the foundation of many of LangChain's components, and is a declarative way to compose chains. LCEL was designed from day 1 to support putting prototypes in production, with no code changes, from the simplest “prompt + LLM” chain to the most complex chains.

- **[Overview](https://python.langchain.com/v0.2/docs/concepts/#langchain-expression-language-lcel)**: LCEL and its benefits
- **[Interface](https://python.langchain.com/v0.2/docs/concepts/#runnable-interface)**: The standard Runnable interface for LCEL objects
- **[Primitives](https://python.langchain.com/v0.2/docs/how_to/#langchain-expression-language-lcel)**: More on the primitives LCEL includes
- **[Cheatsheet](https://python.langchain.com/v0.2/docs/how_to/lcel_cheatsheet/)**: Quick overview of the most common usage patterns

## Components

Components fall into the following **modules**:

**📃 Model I/O**

This includes [prompt management](https://python.langchain.com/v0.2/docs/concepts/#prompt-templates), [prompt optimization](https://python.langchain.com/v0.2/docs/concepts/#example-selectors), a generic interface for [chat models](https://python.langchain.com/v0.2/docs/concepts/#chat-models) and [LLMs](https://python.langchain.com/v0.2/docs/concepts/#llms), and common utilities for working with [model outputs](https://python.langchain.com/v0.2/docs/concepts/#output-parsers).

**📚 Retrieval**

Retrieval Augmented Generation involves [loading data](https://python.langchain.com/v0.2/docs/concepts/#document-loaders) from a variety of sources, [preparing it](https://python.langchain.com/v0.2/docs/concepts/#text-splitters), then [searching over (a.k.a. retrieving from)](https://python.langchain.com/v0.2/docs/concepts/#retrievers) it for use in the generation step.

**🤖 Agents**

Agents allow an LLM autonomy over how a task is accomplished. Agents make decisions about which Actions to take, then take that Action, observe the result, and repeat until the task is complete. LangChain provides a [standard interface for agents](https://python.langchain.com/v0.2/docs/concepts/#agents), along with [LangGraph](https://github.com/langchain-ai/langgraph) for building custom agents.

## 📖 Documentation

Please see [here](https://python.langchain.com) for full documentation, which includes:

- [Introduction](https://python.langchain.com/v0.2/docs/introduction/): Overview of the framework and the structure of the docs.
- [Tutorials](https://python.langchain.com/docs/use_cases/): If you're looking to build something specific or are more of a hands-on learner, check out our tutorials. This is the best place to get started.
- [How-to guides](https://python.langchain.com/v0.2/docs/how_to/): Answers to “How do I….?” type questions. These guides are goal-oriented and concrete; they're meant to help you complete a specific task.
- [Conceptual guide](https://python.langchain.com/v0.2/docs/concepts/): Conceptual explanations of the key parts of the framework.
- [API Reference](https://api.python.langchain.com): Thorough documentation of every class and method.

## 🌐 Ecosystem

- [🦜🛠️ LangSmith](https://docs.smith.langchain.com/): Trace and evaluate your language model applications and intelligent agents to help you move from prototype to production.
- [🦜🕸️ LangGraph](https://langchain-ai.github.io/langgraph/): Create stateful, multi-actor applications with LLMs. Integrates smoothly with LangChain, but can be used without it.
- [🦜🏓 LangServe](https://python.langchain.com/docs/langserve): Deploy LangChain runnables and chains as REST APIs.


## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](https://python.langchain.com/v0.2/docs/contributing/).

## 🌟 Contributors

[![langchain contributors](https://contrib.rocks/image?repo=langchain-ai/langchain&max=2000)](https://github.com/langchain-ai/langchain/graphs/contributors)



문서 카데고리 설명


1. General (일반):
   - 혈압에 관한 일반적인 정보나 다른 카테고리에 명확히 속하지 않는 내용을 포함합니다.

2. Measurement (측정):
   - 혈압 측정 방법, 기기, 기술 등에 관한 정보를 다룹니다.

3. Diagnosis (진단):
   - 혈압 수치의 해석, 고혈압 진단 기준, 분류 등에 관한 내용입니다.

4. Treatment (치료):
   - 고혈압 치료의 전반적인 방법과 접근법에 대한 정보를 포함합니다.

5. Prevention (예방):
   - 고혈압 예방을 위한 방법과 전략에 관한 내용입니다.

6. Risk Factors (위험 요인):
   - 고혈압 발생에 영향을 미치는 다양한 위험 요인들에 대한 정보를 다룹니다.

7. Complications (합병증):
   - 고혈압으로 인해 발생할 수 있는 다양한 건강 문제와 질병에 대한 내용입니다.

8. Lifestyle (생활 습관):
   - 혈압에 영향을 미치는 일상적인 생활 습관에 관한 정보를 포함합니다.

9. Diet (식이):
   - 혈압 관리에 도움이 되는 식단과 영양에 관한 구체적인 정보를 다룹니다.

10. Exercise (운동):
    - 혈압 관리에 도움이 되는 다양한 운동 방법과 지침에 관한 내용입니다.

11. Stress Management (스트레스 관리):
    - 스트레스가 혈압에 미치는 영향과 이를 관리하는 방법에 대한 정보를 포함합니다.

12. Medications (약물):
    - 고혈압 치료에 사용되는 다양한 약물에 대한 상세한 정보를 다룹니다.

13. Emergency (응급 상황):
    - 고혈압으로 인한 응급 상황과 그 대처 방법에 관한 내용입니다.

14. Monitoring (모니터링):
    - 혈압을 지속적으로 관찰하고 기록하는 방법과 도구에 대한 정보를 포함합니다.

15. Special Populations (특수 인구집단):
    - 임산부, 어린이, 노인 등 특별한 관리가 필요한 집단의 고혈압에 관한 정보를 다룹니다.

