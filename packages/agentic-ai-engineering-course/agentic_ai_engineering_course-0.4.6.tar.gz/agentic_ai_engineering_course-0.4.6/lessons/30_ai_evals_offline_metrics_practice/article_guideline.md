## What We Are Planning to Share

This is a pure hands-on lesson containing an associated Notebook, where we will show the following implementation on our concrete Brown the writing workflow use case:

- How to split your dataset between train-val-test splits. Here the train split is used as few shot examples for the LLM judge, val split to align the LLM judge and the test split to actually compute the metrics
- Define the metrics we want to track (FollowsGT, UserIntent)
- Implement the LLM Judges
    - The base classes
    - The metric classes
    - The prompts
    - The few shot examples
    - Explain how we split our initial dataset in:
        - train split for few shot examples (2 articles) —> needs labels & to cache the output
        - validation split to check the correctness of the LLM judge (1 article) —> needs labels & to cache the output
        - inference split which we will actually compute the score on
- The Opik layer, that runs brown on the dataset and computes the metrics:
    - wrap brown as a task
    - Opik code
    - script that calls everything
- Run the LLM Judges on the dataset
- Show to check the reliability of the LLM judges:
    - Caching the article (to lock them), we will run the LLM judges multiple times to compute the variant and see if the judges are stable
    - Compute an “alignment score” between the outputs of the LLM judge and an article labeled by a human. Cache another article, where we manually compute the labels for this (similar to few-shot-examples)
    - Explain how we can further improve the LLM judges by continue improving the prompts and few shot examples until this “alignment score” is good enough.

We will also have a quick video where we will present:
- We walk people through the experiments dashboards
- Compare two experiments with different configs, showing the diff in hyperparameters and scores

## Why We Think It's Valuable

Knowing the theory behind building LLM Judges is one thing, but actually implementing them is another thing. Building custom LLM judges specialized on your business use case requires a lot of context engineering and domain knowledge. Also, understanding how to improve your LLM judge and aligned them with human judgement is extremely valuable and important. And ultimately, understanding how to stabilize them or compute a statistical significance score that signals "better" makes LLM judges actually useful. 

Ultimaltely, building LLM Judges is an AI application in itself, with it's own uniques edge cases and insights.

## Who Is the Intended Audience

Aspiring AI engineers who are learning for the first time about AI agents and workflows. People who transition from other fields, such as data engineering, data science or software engineering and want to learn more about building AI agents and workflows.

⚠️ *EVERYTHING WILL BE WRITTEN RELATIVE TO THE LEVEL AND PERSPECTIVE OF THIS INTENDED AUDIENCE.*

## Theory / Practice Ratio

**5% theory – 95% practice**

## Point of View

The course is created by a team writing for a single reader, also known as the student. Thus, for voice consistency across the course, we will always use 'we,' 'our,' and 'us' to refer to the team that creates the course, and 'you' or 'your' to address the reader. Avoid using the singular 'I’ and don't use 'we' to refer to the student.

## Anchoring the Lesson in the Course

### Details About the Course

This piece is part of a broader course on AI agents and LLM workflows. The course consists of 4 parts, each with multiple lessons. 

Thus, it's essential to always anchor this piece in the broader course, understanding where the reader is in their journey. You will be careful to consider the following:

- To not reintroduce concepts already taught in the previous lesson.
- To be careful when talking about concepts introduced only in future lessons
- To always reference previous and future lessons when discussing topics outside the piece's scope.

### Course Syllabus

In previous lessons of the course, we introduced the following concepts:

**Part 1:**

- **L01 - AI Engineering & Agent Landscape**: Understanding the role, the stack, and why agents matter now
- **L02 - Workflows vs. Agents**: Grasping the crucial difference between predefined logic and LLM-driven autonomy
- **L03 - Context Engineering**: The art of managing information flow to LLMs
- **L04 - Structured Outputs**: Ensuring reliable data extraction from LLM responses
- **L05 - Basic Workflow Ingredients**: Implementing chaining, routing, parallel and the orchestrator-worker patterns
- **L06 - Agent Tools & Function Calling**: Giving your LLM the ability to take action
- **L07 - Planning & Reasoning**: Understanding patterns like ReAct (Reason + Act)
- **L08 - Implementing ReAct**: Building a reasoning agent from scratch
- **L09 - Agent Memory & Knowledge**: Short-term vs. long-term memory (procedural, episodic, semantic)
- **L10 - RAG Deep Dive**: Advanced retrieval techniques for knowledge-augmented agents
- **L11 - Multimodal Processing**: Working with documents, images, and complex data

**Part 2A - Overall Capstone projects Presentation:**

- **L12** — Presenting the capstone projects at a high level
- **L13** — AI framework trade‑offs
- **L14** — Capstone projects system design & cost levers.

**Part 2B - Nova Deep Research Agent:**

- **L15** — Presenting the project structure and design of the Nova deep research agent
- **L16** — MCP foundations (server/client; **tools/resources/prompts**; server‑hosted prompt).
- **L17** — Ingestion layer (guideline URL extraction; local/GitHub/YouTube ingest; Firecrawl scraping; file‑first design).
- **L18** — Research loop (generate queries → **Perplexity** with **structured outputs** → optional HITL between steps).
- **L19** — Testing out the Nova deep research agent

**Part 2C - Brown the Writing Workflow:**

- **L20** — Presenting the project structure and design of the Brown writing workflow
- **L21** — Presenting the system design and architecture of Brown the writing workflow
- **L22** — Implementing the foundations of Brown the writing workflow (such as applying the orchestrator-worker pattern to generate media items + context engineering to write high-quality articles that follow a specific pattern)
- **L23** — Applying the evaluator-optimizer pattern to the Brown writing agent to automatically review and edit the article to automatically force adherence to expected requirements
- **L24** - Expanding Brown the writing agent with multiple editing workflow that let's you edit the whole article or just a piece of selected text. Everything is exposed as tools through MCP servers to facilitate human in the loop cycles

**Part 2D:**

- **Lesson 25:** Orchestrating both MCP Servers (Nova + Brown) within a single MCP client, automating the whole logic as a unified workflow
- **Lesson 26:** End-to-End Demo: Generating a Course Lesson - Demo showing how we used Nova + Brown to research and write professional articles or lessons.

**Part 3:**

With both the capstone projects built, this section focuses on the engineering practices required for production:

- **L27 - Agent Observability with Opik**: Integrating Opik to log inputs, outputs, tool calls, and reasoning steps for diagnosing issues and monitoring costs and latency
- **L28 - Offline Evaluation - Building the Evaluation Dataset**: Creating evaluation datasets with inputs, ground truth outputs, and generated outputs, and uploading them to Opik for versioning and tracking
- **L29 - Offline Evaluation - Evaluating the Writing Agent Theory**: Understanding metric types (BLEU, ROUGE, BERTScore, LLM judges) and choosing custom binary business metrics over generic benchmarks
- 🚨 *<<< **L30 - Offline Evaluation - Evaluating the Writing Agent Practice**: Implementing LLM judge-based evaluation pipelines with train-val-test splits, metric definitions, and alignment scoring for reliable assessments >>> CURRENT LESSON - REFERENCE PREVIOUS AND FUTURE LESSONS RELATIVE TO THIS ONE*
- **L31 - Continuous Integration (CI) for AI Engineering**: Setting up pre-commit hooks, linting, formatting, and unit tests with mocked LLM calls, automated via GitHub Actions
- **L32 - Preparing for the Cloud: Docker, State, and Infrastructure**: Containerizing agents with Docker, replacing local file paths with UI-based uploads, integrating Cloud SQL for state management, and deploying to GCP Cloud Run
- **L33 - Securing the Agent: Authentication with Descope**: Implementing authentication layers for MCP servers, securing API endpoints, and managing user identities for safe public or internal deployment
- **L34 - Continuous Deployment (CD) with GitHub Actions**: Automating deployment pipelines that build Docker containers, authenticate with GCP, and deploy new versions to Cloud Run on code pushes

**Part 4:**

- In this final part of the course, you will build and submit your own advanced LLM agent, applying what you've learned throughout the previous sections. We provide a complete project template repository, enabling you to either extend our agent pipeline or build your own novel solution. Your project will be reviewed to ensure functionality, relevance, and adherence to course guidelines for the awarding of your course certification.

### CURRENT LESSON:

Now we are writing lesson 30 on implementing LLM judge-based evaluation pipelines with train-val-test splits, metric definitions, and alignment scoring for reliable assessments for Brown the writing workflow

## Anchoring the Reader in the Educational Journey

Within the course, we are teaching the reader multiple topics and concepts. Thus, understanding where the reader is in their educational journey is critical for this lesson. You have to use only previously introduced concepts, while being reluctant about using concepts that haven't been introduced yet.

When discussing concepts introduced in previous lessons, avoid reintroducing them to the reader. Especially don't reintroduce the acronyms. Use them as if the reader already knows what they are. 

Avoid using the concepts that will only be introduced in future lessons. Whenever a concept from the current lesson requires references to concepts from future lessons, instead of directly using them, use intuitive analogies or explanations that are more general and easier to understand, as you would explain them to a 7-year-old. For example:

- If the "tools" concept wasn't introduced yet, and you have to talk about tool calling agents, refer to them as "actions".
- If the "routing" concept wasn't introduced yet and you have to talk about it, refer to it as "guiding the workflow between multiple decisions".

The idea is that if you have to use a concept that hasn’t been introduced yet, use real-world analogies that anyone can understand instead of specialized terminology. 

You can use the concepts that haven't been introduced yet only if we explicitly specify them in this guideline. Still, even in that case, as the reader doesn't know how that concept works, you are only allowed to use the term, while keeping the explanation extremely high-level and intuitive, as if you were explaining it to a 7-year-old.

Whenever you use a concept from future lessons, explicitly specify in what lesson it will be explained in more detail. If the lesson number is unclear, specify the part, such as part 3 or 4.

In all use cases, avoid using acronyms that aren't explicitly stated in the guidelines. Rather, use other, more accessible synonyms or descriptions that are easier to understand by non-experts.

## Narrative Flow of the Lesson

- Follow the next narrative flow when writing the end‑to‑end lesson:
- What problem are we learning to solve? Why is it essential to solve it?
- Why other solutions are not working and what's wrong with them.
- At a theoretical level, explain our solution or transformation. Highlight:
    - The theoretical foundations.
    - Why is it better than other solutions?
    - What methods or algorithms can we use?
- Provide simple examples or diagrams where useful.
- Go deeper into the advanced theory.
- Provide a more complex example supporting the advanced theory.
- Connect our solution to the bigger field of AI Engineering. Add course next steps.

## IMPORTANT INSTRUCTIONS

Follow the narrative and code snippets one-on-one as presented in the provided Notebook within the <research>. This lesson is a by-product of that Notebook. Thus, we want to include everything within the notebook as stated within the `Lesson Outline`, but with more in-depth explanations.

The only exceptions we don't need from the Notebook are the first setup sections. Otherwise, we want to include all the explanations and code snippets as provided in the Notebook within the same order, containing both Markdown cell, code cells and output cells. 

---

## Lesson Outline

1. Introduction
2. Understanding the LLM Judges We Will Build
3. Splitting the Evals Dataset
4. Implementing the Follows Ground Truth LLM Judge
5. Implementing the User Intent LLM Judge
6. Accessing LLM Judges Through Our Factory Function
7. Building the AI Evals Pipeline
8. Computing the Alignment Score on the Validation Split
9. Computing the Baseline Score on the Test Split
10. Checking the Stability of the LLM Judge 
11. Conclusion

## Section  1 - Introduction

- **Quick reference to what we've learned in previous lessons:**  One sentence on what we’ve learnt in previous lessons, with a focus on lessons 28 and 29 as they are part of understanding and implementing Brown's AI evals layer.

- **Transition to what we'll learn in this lesson:** After presenting what we learned in the past, make a transition to what we will learn in this lesson. Take the core ideas of the lesson from the `What We Are Planning to Share` section and highlight the importance and existence of the lesson based on the `Why We Think It's Valuable` section.

- Highlight how building the whole AI Evals layer was to some extend harder or as hard as building Brown itself. Most AI tems subestimate the effort it requires to build high-quality AI evals. But they also subestimate their impact and how useful it can be!

- **Transition:** Enumerate what we are going to learn in this lesson with bullet points. Focus on outcomes of this lesson:
    - What LLM Judges we are going to build
    - How we are going to use the evals dataset
    - Implementing multiple LLM Judges to check the performance of Brown the writing workflow
    - Implementing the AI Evals pipeline
    - Techniques for checking the quality of the LLM Judges

- **Section length:** 300 words

## Section 2 - Understanding the LLM Judges We Will Build

- **Transition:** First, let understand what LLM judges we want and need to build.

- Within a subsection, we will quickly remind people that for each evaluation dataset sample, we need the article guideline, research, and expected article
- Remember that the dataset created by us in Lesson 28 contains per each dataset sample: the article guideline, research and expected article, while we have to generate on the fly the generated article. The idea is that everytime we make a change to our AI App (Brown) you have to regenerate the articles and recompute the metrics. That's why everything else is static, while feedling only with the generated outputs and a few of the system parameters during the optimization process of the AI app.
- Mermaid Diagram showing the moving blocks of a dataset sample.
- Then we will building the following LLM judge metrics:
    1. One that compares the expected article with the generated article on dimensions such as content, flow of ideas and structure adherence
    2. One that compares the generated article with the input article guideline and research checking if the input adheres to the article guideline (aka stays on track with human input) and it's written solely based on the research (aka checks hallucination)

- Then we will have another subsection explaining that our LLM judges will use only binary metrics scoped at the section level, instead of the whole article level. Thus, for each article, we will have multiple metrics, computed for each section individually. Like this, we can leverage the beauty of binary metrics, while still having granularity. Also, as from most point of views such as adherence to guideline, research or ground truth a section is independent from one another. Thus, this decision gives us more signal and precision in understanding what our application did wrong or in fixing and calibrating our LLM judge
- A mermaid diagram showing an article with multiple section, where we compute multiple metrics per section

- **Section length:** 400 (without counting the Mermaid diagrams code and image captions)

## Section 3 - Splitting the Evals Dataset

- **Transition:** The last step before digging into the implementation is to understand how we will split the AI evals dataset to properly build the LLM Judges without any data leakage.

- We will split the dataset into training, validation, testing
    - The training split will be used as few shot examples to "train" the LLM judges 
    - The validation split will be used to align the LLM judges with human expectections. In other words used to evaluate the LLM judges themselves.
    - The testing split will be used to compute the metrics on
- Mermaid diagram showing this split.

- **Section length:** 200

## Section 4 - Implementing the Follows Ground Truth LLM Judge

- **Transition:** Now, finally we can start the implementation. We will start by implementing the LLM judges starting with the one that compares the expected and genetered articles on multiple dimensions. Hence, we labeled it `FollowsGTMetricLLMJudge`.

- This subsection starts to dig into the follows ground truth metric code, the first LLM judge metric. As we have some base abstractions leveraged in multiple LLM judge metrics in `brown.evals.metrics.base` and because this is the first metric that uses them, we will bounce between the abstractions and actual implementations, first showing the abstraction and then the implementation. 
- In this section we want to show all the code from the Notebook from the `4. The FollowsGT Metric: Comparing Against Ground Truth` and `5. Running the FollowsGT Metric` sections. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow. 
- Walk over the `4. The FollowsGT Metric: Comparing Against Ground Truth` section from the Notebook as follows:
    1. The `BrownBaseMetric` abstraction from `brown.evals.metrics.base` (ignore the FewShotExamplesT for now)
    2. The `FollowsGTMetricLLMJudge` implementation from `brown.evals.metrics.follows_gt.metric`
    3. The `FollowsGTArticleScores` implementation from `brown.evals.metrics.follows_gt.types` and other subclasses such as `FollowsGTSectionScores` and `FollowsGTCriterionScores`
    4. The `CriteriaScores` and `CriterionScore` classes from `brown.evals.metrics.base`
    5. The `aggregate_section_scores_to_results` function from `brown.evals.metrics.base` that is used within the `FollowsGTArticleScores.to_score_sult` method to aggregate a list of scores to a single score. Explain here in more detail what the function does.
    6. The `CriterionAggregatedScore` that represents an aggregate score
    7. Now we mvoe to the few shot examples classes starting with `FollowsGTMetricFewShotExamples` and `FollowsGTMetricFewShotExample` from `brown.evals.metrics.follows_gt.types`
    8. Then we explain the base entities `BaseFewShotExamples` and `BaseExample` from `brown.evals.metrics.base`
    9. Lastly, we explain the LLM Judge system prompt `SYSTEM_PROMPT` from `brown.evals.metrics.follows_gt.prompts` diving it into the following groups:
        1. Introduction
        2. Instructions: Explain in more depth how we instructed the LLM Judge to compute the scores based on article sections instead of the whole article. Also, explain how we encoded the `content`, `flow` and `structure` binary metrics
        3. Chain of Thought
        4. What to Avoid
        5. Few-shot examples and input
        6. Conclusion
    10. Next, we explain the `DEFAULT_FEW_SHOT_EXAMPLES`. Show the core initialization logic of the data structure, while within the `scores` list, which is the longest highlight only the following:
        1. Start with an explanation on how we labeled the few shot examples and actually prepared them, as preparing the few shot examples is actually the hardest part. Don't invent this part, use the notes from the <note_on_our_process_of_labeling_the_few_shot_examples_for_the_llm_judges> section for this.
        1. `04_structured_outputs`: "Introduction", "Why Structured Outputs Are Critical", ..., "Structured Outputs Are Everywhere", "References"
        2. `07_reasoning_planning`: "Introduction", ..., "Teaching Models to "Think": Chain-of-Thought and Its Limits", "Separating Planning from Answering: Foundations of ReAct and Plan-and-Execute", ..., "Plan-and-Execute in Depth: Structure and Predictability", ....
        3. Explain that to create these few shot examples, we manually generated the articles based on these inputs, added noise to it to create as much variation as possible and manually labeled each section along these dimensions
        4. (CODE SECTION) Call the few shot examples as context for people to see how it looks
    11. The last piece of the puzzle is the `get_eval_prompt` function that aggregates the `get_eval_prompt` into the final prompt.

- Code subsection in which we will run the `FollowsGTMetricLLMJudge` metric on a simple example for people to actually understand how it works using the code from the `5. Running the FollowsGT Metric` section of the Notebook. We will mock a simple isolated example based on the article example from `inputs.tests.01_sample_small`. Use that sample as `expected_output` and add variatns for the `output` to see the LLM judge in action. make these two as constants so we can use them later on as well. Print the outputs.

- **Section length:** 900 (without counting the code snippets or prompts)

## Section 5 - Implementing the User Intent LLM Judge

- **Transition:** Now, let's go through the implemention of the user intent LLM Judge, which compares the generated article against the article guideline and research. It doesn't require ground truth! 

- Subsection where we will go over the User Intent metric from `brown.evals.metrics.user_intent`. As we already explained the base classes and functions from `brown.evals.metrics.base` in the previous section, this time we will focus solely on the particularities of the `UserIntentMetricLLMJudge` metric.
- In this section we want to show all the code from the Notebook from the `6. The UserIntent Metric: Checking Guideline Adherence and Research Anchoring` and `7. Running the UserIntent Metric` sections. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow. 
- Walk over the `6. The UserIntent Metric: Checking Guideline Adherence and Research Anchoring` from the Notebook as follows:
    1. The `UserIntentMetricLLMJudge` implementation from `brown.evals.metrics.user_intent.metric`
    2. The `UserIntentArticleScores` implementation from `brown.evals.metrics.user_intent.types` and other subclasses such as `UserIntentSectionScores` and `UserIntentCriteriaScores`
    3. Now we move to the few shot examples classes starting with `UserIntentMetricFewShotExamples` and `UserIntentMetricFewShotExample` from `brown.evals.metrics.user_intent.types`
    4. Lastly, we explain the LLM Judge system prompt `SYSTEM_PROMPT` from `brown.evals.metrics.user_intent.prompts` diving it into the following groups:
        1. Introduction
        2. Instructions: Explain in more depth how we instructed the LLM Judge to compute the scores based on article sections instead of the whole article. Also, explain how we encoded the `Guideline Adherence`, and `Research Anchoring` binary metrics
        3. Chain of Thought
        4. What to Avoid
        5. Few-shot examples and input
        6. Conclusion
    5. Next, we explain the `DEFAULT_FEW_SHOT_EXAMPLES`. Show the core initialization logic of the data structure, while within the `scores` list, which is the longest highlight only the following:
        1. `04_structured_outputs`: "Introduction", "Understanding why structured outputs are critical", ..., "Conclusion: Structured Outputs Are Everywhere"
        2. `07_reasoning_planning`: "Introduction", ..., "Teaching Models to "Think": Chain-of-Thought and Its Limits", "Separating Planning from Answering: Foundations of ReAct and Plan-and-Execute", ..., "Plan-and-Execute in Depth: Structure and Predictability", ....
        3. Explain that to create these few shot examples, we manually generated the articles based on these inputs, added noise to it to create as much variation as possible and manually labeled each section along these dimensions
        4. (CODE SECTION) Call the few shot examples as context for people to see how it looks
    6. The last piece of the puzzle is the `get_eval_prompt` function that aggregates the `get_eval_prompt` into the final prompt. 

- Code subsection in which we will run the `UserIntentMetricLLMJudge` metric on a simple example for people to actually understand how it works using the code from the `7. Running the UserIntent Metric` section of the Notebook. We will show a similar scenario as in section 4 of the lesson, where we will use as seed the example from `inputs.tests.01_sample_small`. Use the input and context as is, while injecting noise into the article as `output` to put the LLM judge in action. Print the outputs.

- **Section length:** 600 (without counting the code snippets or prompts)

## Section 6 - Accessing LLM Judges Through Our Factory Function

- **Transition:** Before building the AI evals pipeline, let's build a factory method that quickly allows us to dynamically instantiate and configure the LLM judges implemented above.

- Small section showing the factory method from `brown.evals.metrics.__init__.py` used to build the required metrics using the code from the `8. The Metrics Factory Function` section of the Notebook:
    - (markdown) show the function
    - (code) call the function with the `user_intent` and `follows_gt` inputs and gemini 2.5 flash model
    - show the output

- **Section length:** 150 (without counting the code snippets)

## Section 7 - Building the AI Evals Pipeline

- **Transition:** Now that we have our LLM judges in place, the final step is to implement the AI evals pipeline that runs the LLM Judges on the AI evals dataset and reports all the results to an experimentation dashboard in Opik.

- In this section we want to show all the code from the Notebook from the `9. Running Evaluations on the Dataset`, `10. Hooking to Opik for Full Evaluation` and `11. Running the End-to-End Evaluation` sections. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow. 

- From the `9. Running Evaluations on the Dataset` section of the Notebook, we will start by explaining the functions from `brown.evals.metrics.tasks.py` which are used to run the generate article workflow of Brown on a dataset sample:
    1. (Markdown) `evaluation_task`
    2. (Markdown) `__run`

- Now, from the `10. Hooking to Opik for Full Evaluation` section of the Notebook, hook our `evaluation` task to the dataset stored in Opik and run the LLM judges defined above on each dataset sample, we have to run a bit more glue code:
    1. (Markdown) `evaluate` from `brown.observability.evaluation`
    2. (Markdown) `get_dataset` from `brown.observability.opik_utils`
    3. (Markdown) `create_evaluation_task` from `brown.evals.metrics.tasks.py` (we need it because the `evaluate` function from Opik doesn't allow us to pass any other parameters to the `task` function used to generate the output on each dataset sample. Thus we use it to pin other attributes of the function leveraging the `partial` function from Python)

- Now, a subsection based on the `11. Running the End-to-End Evaluation` section of the Notebook, show how we glue all the code into the final AI evals pipeline, by walking over:
    - the constants
    - instantiating the `evaluation_task`, `model`, `model_config` and `evaluation_metrics`
    - printing the eval pipeline config
    - defining the split
(DO NOT RUN THE PIPELINE AT THIS STAGE. RUN IT ONLY THE NEXT SECTION)

- **Section length:** 500 (without counting the code snippets)

## Section 8 - Computing the Alignment Score on the Validation Split

- **Transition:** Now that we have all pieces in place, let's run the AI evals pipeline on the validation split to compute the alignment score

- In this section we want to show all the code from the Notebook from the `12. Computing the Alignment Score on the Validation Split` section. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow.

- A paragraph defining what's the alignment score and why it's critical for aligning the LLM judges with human judgment. At this point keep it generic as we will show a concrete example soon.

- Run the AI evals pipeline on the validation split
    - show code
    - show output
- Screenshot placeholder showing how the experiment looks in Opik

- Explain how we will compute the alignment score on our concrete example for Brown the writing workflow. 
    - Walk people through the general idea
    - Then walk people step by step throug the process
- Show the:
    - Content Metric Alignment table and alignment score result
    - Flow Metric Alignment table and alignment score result
    - Structure Metric Alignment table and alignment score result
- Next steps: Explain how we can leverage these alignment scores to further improve our LLM judges to be able to fully trust them as our north star as explained in the  `12. Computing the Alignment Score on the Validation Split` section of the Notebook

- **Section length:** 400 (without counting the code snippets, tables or image captions)

## Section 9 - Computing the Baseline Score on the Test Split

- **Transition:** Usually, you would want to improve the LLM Judges and recompute the alignment score until it reaches a score close to 100%, but for the sake of this example let's assume we are OK with the current implementation. Thus, let's run the AI pipeline on the test split to comptue the baseline score.

- In this section we want to show all the code from the Notebook from the `13. Computing the Baseline Score on the Test Split` section. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow.

- Run the AI evals pipeline on the test split
    - show code
    - show output
- Screenshot placeholder showing how the experiment looks in Opik

- **Section length:** 200 (without counting the code snippets, tables or image captions)

## Section 10 - Checking the Stability of the LLM Judge

- **Transition:** The last step to be able to fully trust your LLM Judges is to check their stability across multiple runs. Why? Because we use LLMs to compute the metrics, we might get different scores after each run. Even if we did our best to stabilize these scores, for example, by using binary scores to make it easier for the LLM to choose one option, the LLM judge can still be unstable.

- In this section we want to show all the code from the Notebook from the `14. Checking the Stability of the LLM Judge` section. We want a one-one replica with the notebook, where we go over all the code snippets, descriptions, outputs and examples. The only difference between this lesson and the notebook will be that we will expand on the description of the code snippets and further split it into logical groups that is easier to follow.

- Explain how we computed the stability score and show the results.
- Screenshot from the Notebook with the results
- Show the results from the table
- Explain what's next and how they can leverage these results:
    1. standard deviation scenario
    2. stabilize the LLM judge scenario

- **Section length:** 200 (without counting the code snippets, tables or image captions)

## Section 11 - Conclusion
(Connect our solution to the bigger field of AI Engineering. Add course next steps.)

- One paragraph conclusion: Leverage insights from the `Why We Think It's Valuable` section.

- Highlight how building the whole AI Evals layer was to some extend harder or as hard as building Brown itself. Most AI tems subestimate the effort it requires to build high-quality AI evals. But they also subestimate their impact and how useful it can be!

- **Transition to future lessons:** We wrapped up the AI evals lessons, in the next lessons we will focus on building the CI/CD pipelines and deploying Nova to Google Cloud.

- subsection on practicing ideas:
    1. **Test LLM Judge Stability**: We showed the LLM Judge stability on the article generated with `gemini-pro`. Use the cached articles from the `outputs/evals-flash` directory to run the LLM judges 5 times with all inputs fixed. Measure the stability of the scores across runs.

    2. **Compute the Alignment Score on the User Intent Metrics**: Use the Memory lesson from the validation split and manually score each section on the user intent metrics, such as article guideline adherence and research anchoring. Compare your scores with the LLM judge scores to see how aligned they are.

    3. **Iterate on Brown**: Make changes to the Brown AI app (prompts, model, temperature) and rerun the AI evals. See if your change improves or degrades the metrics?

- **Section length:** 300 words

## Lesson Code

Links to code that will be used to support the lesson. Always prioritize this code over every other piece of code found in the sources:

1. [Notebook](https://github.com/towardsai/agentic-ai-engineering-course/blob/dev/lessons/30_ai_evals_offline_metrics_practice/notebook.ipynb)
