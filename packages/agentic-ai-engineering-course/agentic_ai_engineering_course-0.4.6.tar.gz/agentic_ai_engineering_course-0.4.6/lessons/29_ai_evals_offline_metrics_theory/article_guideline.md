## What We Are Planning to Share

This is a theoretical lesson where we want to teach people the fundamentals of designing business metrics for evaluating their AI applications. 
First, we have to understand how to properly integrate AI evals into your software development cycles such as using them to guide your optimization processes or catch regressions when pushing new features.
Next, we plan to go over the core metric types for unstructured data, especially text, such as:
    - Bleu, rogue
    - BertScore (based on embeddings similarity)
    - LLM judges + Why we chose LLM judges
Next, we will go deveper into how to choose your measuring strategy touching:
    - Custom business metrics vs. benchmarks: Explain why we used custom business metrics rather than open benchmarks such as AgentBench, WebArena, and GAIA
    - Custom business metrics vs. generic business metrics: Explain why generic metrics are useless and stay more in your way than being helpful.
        - That’s why tools such as RAGAS or pre-built metrics in Opik are pretty useless and misleading
    - Explain why you should choose binary metrics over anything else.
        - Easier to understand what is good and bad
        - Easier to label
        - Translates to more stable LLM judges

## Why We Think It's Valuable

Knowing how to define good business metrics that actually provide signal over noise it's the most important part of building AI evals pipelines. And the most underrrated one. Most people use out of the box metrics that are only noise. Build business metrics that are not working properly, thus people are not using them because they don't trust them. Or use generic benchmarks to take business decisions. 

Knowing how to define clear business metrics that people can trust and use them as guidance is hard and underrated. Thus, in this lesson we want to lay down the foundations on how to do that, while in the next lesson we will implement a series of LLM Judges to evaluate your Brown writing workflow on a series of tasks that we actually care about.

Also, we have to understand how to properly integrate AI evals into your software development cycles such as using them to guide your optimization processes or catch regressions when pushing new features.

## Who Is the Intended Audience

Aspiring AI engineers who are learning for the first time about AI agents and workflows. People who transition from other fields, such as data engineering, data science or software engineering and want to learn more about building AI agents and workflows.

⚠️ *EVERYTHING WILL BE WRITTEN RELATIVE TO THE LEVEL AND PERSPECTIVE OF THIS INTENDED AUDIENCE.*

## Theory / Practice Ratio

**100% theory – 0% practice**

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
- 🚨 *<<< **L29 - Offline Evaluation - Evaluating the Writing Agent Theory**: Understanding metric types (BLEU, ROUGE, BERTScore, LLM judges) and choosing custom binary business metrics over generic benchmarks >>> CURRENT LESSON - REFERENCE PREVIOUS AND FUTURE LESSONS RELATIVE TO THIS ONE*
- **L30 - Offline Evaluation - Evaluating the Writing Agent Practice**: Implementing LLM judge-based evaluation pipelines with train-val-test splits, metric definitions, and alignment scoring for reliable assessments
- **L31 - Continuous Integration (CI) for AI Engineering**: Setting up pre-commit hooks, linting, formatting, and unit tests with mocked LLM calls, automated via GitHub Actions
- **L32 - Preparing for the Cloud: Docker, State, and Infrastructure**: Containerizing agents with Docker, replacing local file paths with UI-based uploads, integrating Cloud SQL for state management, and deploying to GCP Cloud Run
- **L33 - Securing the Agent: Authentication with Descope**: Implementing authentication layers for MCP servers, securing API endpoints, and managing user identities for safe public or internal deployment
- **L34 - Continuous Deployment (CD) with GitHub Actions**: Automating deployment pipelines that build Docker containers, authenticate with GCP, and deploy new versions to Cloud Run on code pushes

**Part 4:**

- In this final part of the course, you will build and submit your own advanced LLM agent, applying what you've learned throughout the previous sections. We provide a complete project template repository, enabling you to either extend our agent pipeline or build your own novel solution. Your project will be reviewed to ensure functionality, relevance, and adherence to course guidelines for the awarding of your course certification.

### CURRENT LESSON:

Now we are writing lesson 29 on understanding metric types (BLEU, ROUGE, BERTScore, LLM judges) and choosing custom binary business metrics over generic benchmarks

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

---

## Lesson Outline

1. Introduction
2. Using Evals Through the Optimization Flywheel
3. Exploring Possible Metric Types
4. Why Business Metrics Over Benchmarks
5. Why Custom Business Metrics Over Generic Metrics
6. Choosing Binary Metrics Over Anything Else
7. Conclusion

## Section  1 - Introduction

- **Quick reference to what we've learned in previous lessons:**  One sentence on what we’ve learnt in previous lessons, with a focus on lessons 27 and 28 as they are part of teaching observability and AI evals.

- **Transition to what we'll learn in this lesson:** After presenting what we learned in the past, make a transition to what we will learn in this lesson. Take the core ideas of the lesson from the `What We Are Planning to Share` section and highlight the importance and existence of the lesson based on the `Why We Think It's Valuable` section.

- Evaluation driven development is one of the most underrated ways of developing AI products. In reality, in the data science and ML research world, it's the only way to train new models, but as in the AI Engineering world, we combined AI with software engineering and the models are already trained for you, many people don't know about this practice, think they don't have time for it or just don't prioritize it enough. The reality is that you need to put some effort at first to implement your AI evals layer, which doesn't translate directly to features, but in the long run it will speed up your development 10 folds.

- **Transition:** Enumerate what we are going to learn in this lesson with bullet points. Focus on outcomes of this lesson:
    - The optimization flywheel
    - metric types
    - business over generic metrics

- **Section length:** 250 words

## Section 2 - Using Evals Through the Optimization Flywheel

- **Transition:** Let's kick off this article by highlighting how we can actually use and integrate AI Evals into our AI app.

- Explain how we can use AI Evals to optimize our system. 
- There are three core scenarios where AI Evals are useful:
    1. To quantify the quality of your system on a set of given metrics (the obvious one).
    2. To use the metrics as guidance when optimazing your system. For example, whenever you do a change to your AI app, instead of vibe checking you run your AI evals and check if the metrics are better, worse or the same as the baseline (this is known as an experiment).
    3. To use the metrics as regression tests. This is similar to `point 2`, but instead of using the AI evals as a north star for optimizing your system, you use them as `tests` to insure you don't break old features when pushing new ones.
- How does this look in a real-world scenario? Let's look at a step-by-step plan of attack
    1. The first phase is to gather your dataset (what we explain in the previous step).
    2. Next you build your metrics (what we will explain in this and next lessons).
    3. You run the AI evals on your sytem. This is known as the baseline. At this point, your system will be far from perfect. Thus, your goal is to further optimize it. Now that you have a clear way to quantify the "quality" of your system you have a clear direction, a north start, on how "better" looks like.
    4. Next, you start the optimization process. To do that, you do one change to your system that you think it will improve the performance.
    5. You compare the new score with the baseline. 
    6. If the score is better, you accept the change. If the score is the same you consider if it's worth it or not. If the score is worse, you know that's not a path worth exploring. The key is to fix everything, except one change. Like this, if it doesn't work, you know exactly where the issue comes from. If you do multiple changes at once, you won't know what affected the change in metrics. Also, often, you want the score, not to just be better in a vacuum, but to be statistical significant better. From our experience, the word `statistical significat` depends a lot on your use case. To keep it simple we like to keep it anchored in business impact. For example, if your score is within the `[0, 1]` interval and your improvement is only of `0.0001` you might think that's insignificat, right? Well, not always. In some cases it might be, but in some cases it might translate to a cost reduction of 10 million dollars. More on this later, for now we just want to emphasize that "better" is always relative to your business use case.
    7. You repeat steps 4-6 until the metric score is good enough for your use case. The score will rarely be perfect, that's why I emphasize on "good enough" for your use case.
- Mermaid diagram with steps 1 to 7 as the optimization flyswheel
In the data world this is known as an "experiment", where you do one change to your system, measure it, and compare it side-by-side to the baseline. 
- You can also leverage a similar strategy as regression tests. Let's image that instead of trying to directly optimize a particular part of your AI app you push new features that affect multiple parts of your code, such as system prompts, tool descriptions and orchestrations layers. Your new feature works perfect. But as you touched parts of the code that affect other features, the change that you modified a prompt that broke other functionality is quite big. That's why running the AI evals as regression tests it's an extremely powerful technique to ensure your new features don't break old features. You can modify the strategy from above as follows:
    1. You implement a new feature.
    2. You run the AI evals.
    3. If the scores are similar to the baseline your feature is OK as it didn't affect any old feature. So you can merge the feature into your production codebase.
    4. If the score is worst, you should fix your code. Then repeat steps 2 and 3.
💡 Note: You usually run these AI evals within your CI pipeline before merging and deploying your code.
- Mermaid diagram with steps 1 to 4 as a way to catch regressions within your CI pipelines
Basically, AI evals can be used in a similar strategy to classic unit or  integration tests, but instead of expecting them to "succeed" or "fail", as AI apps are never perfect we check if the score relative to the baseline. We will understand this better as we progress into the AI evals metrics sections.

- **Transition:** Now that we understand how AI Evals can practically be used to optimize and keep your AI app in check, let's start digging into how to properly define your own metrics.

- **Section length:** 1000 words (without counting the mermaid diagram code and captions)

## Section 3 - Exploring Possible Metric Types

- We will start by exploring what are possible metric types. As we work only with unstructured data such as text and images, we will look only for metrics compatible with these data types, which are often unique to classical machine learning metrics that leverage structured data.

- There are 3 popular family of metrics:
    1. BLEU, ROUGE:
        - General description of the family of metrics (don't need any formal definiton, just focus on the idea of classic metrics):
        - PROs:
        - CONs:
    2. BertScore (based on embeddings similarity)
        - Definition: Present what is BertScore and in general the family of scores based on embedding similarity
        - PROs:
        - CONs:
    3. LLM judges
        - Definition:
        - PROs:
        - CONs:
    
- In our projects we chose to go with LLM judges because they offer a lot of flexibility and control in computing concrete business metrics on dimensions and criteria that we actually care about. Also, as we care more than just seeing similarity between the generated output and a ground truth, the BertScore family of models didn't offer enough customization for our needs such as checking if the generated output follows the article guideline, adheres to the research and the expected structure. We will dig deeper into this in the next lesson where will implement a series of LLM Judges from scratch.

**Transition:** Now, you kept hearing from us: "business metrics here, business metrics there". Thus, let's understand why defining your own business metrics it's such an important, and underrrated step in building your AI evals strategy.

- **Section length:** 500 words

## Section 4 -  Why Business Metrics Over Benchmarks

- Benchmarks are the most deceiving type of metrics out there. We all look at popular leaderboards such as the [LMArena Leaderboard](https://lmarena.ai/leaderboard) to look for the "best LLM", which is often the wrong strategy.

- Why? There are two core reasons:
    1. First, these benchmarks are often just marketing. Thus, all these companies directly or indirectly overfit these benchmarks just to see their models at the top. The most extremele example was when Meta fine-tuned their open-source model, llama, on the test set, just to see their model at the top. Even if companies don't directly train on the test split, they indirectly overfit it, as they try to highly optimize their models just for this use cases. There is a saying: "If the test set is public, is no longer a test set." Which is often true.
    2. Which brings us to the second reason. You might think, but what's wrong if these models are highly optimized to work great on these benchamrks? Isn't that what we want? Well, most of the time no. These benchamrks don't reflect your custom business use. Thus, they can be the best at solving math problems, but if you need your LLM for creative writing, that won't help you much, right?

- Benchmarks are ok to keep the LLM field competivie and have a standardized way to push research forward. But you will most probably build AI applications that solve a particular business problem making these benchamrks irrelevant for you. We don't want to demonize benchmarks, they are amazing to quickly look up for a list of capable models, but we want to highlight that they are NOT enough.

- **Transition:** To conclude, benchmarks are fine to quickly filter and find a list of capable models, but in reality you need a list of custom metrics that reflect your business problem.

- **Section length:** 300 words

## Section 5 - Why Custom Business Metrics Over Generic Metrics

- Under the same idea of why benchmarks are not useful, we want to highlight why generic business metrics such as "toxicity", "helpfulness" or "hallucination" are also irrelevant. Even metrics like ROUGE or BertScore fall under this umbrella. These generic metrics add more noise than signal, only wasting your time and adding congitive load into your decision process.

- As Hamel Husain says in prolific work on AI Evals, they are just a "mirage". Relying on these prefab evals is one of the fastest ways to build false confidence and waste time optimizing for things that don’t matter to your users.

- We need **application-centric evals**, as the focus of our work is to answer concrete questions. A model can score brillaintly on "helpfulness", but what does that even mean? Even worst it can fail catastrophically on use cases relevant to our real-world product because our product has specific constrains, a unique domain and user expectations that no generic metric can capture.

- Image from the research on how your LLM Eval Dashboard shouldn't look like

- For example, let's assume that we want to check if the article written by Brown contains any hallucinations or not. Thus, we use a `hallucination` score. In case the score is positive, how do we know what was hallucinated? It added additional information relative to the `research` or relative to the `article_guideline`? How do we actually define "hallucination" for our technical writing use case? In what section of the article is the hallucination located?

- For example, it might flag as `hallucination` a personal story that is not present within the research, but at the same time it's relevant and correct as it doesn't contain any technical concepts that we actually want to check against hallunications. Thus, it will lead us to false directions. 

- The idea is that these generic metrics, in the best case they waste our time, and in the worst case they create an illusion of confidence that is unjustified.

- Again, we don't want to demonize generic metrics, but the idea is to know when to use them. For example, you could use:
 1. Verbosity to reveal that your most verbose answers are rambling and unhelpful
 2. Similarity score to evalute your RAG retriever to see if it pulled relevant documents
 3. BertScore to check the quality of your golden references. For example, if you find a cluster with low scores you might realize the LLM found more creative ways to solve a given problem.
Thus, generic metrics are usually more useful in the exploraty phase, where you want to filter and sort your data to find all kind of insights to understand and curate your data.

- To conclude, even if generic metrics have their porpouse, to grade the quality and outcome of your AI app you need custom business metrics deeply anchored into your domain and problem you want to solve.

- **Section length:** 500 words (without counting the image URL and captions)

## Section 6 - Choosing Binary Metrics Over Anything Else

- The seductive trap of subjective scales:
    1. it leads to inconsistent labeling
    2. it masks real issues with statistical noise
    3. Likert scales encourage lazy decision-making
- The power of forced decisions: Why binary evals work
    1. It Forces Clearer Thinking
    2. It's Faster and More Consistent
    3. It's More Actionable
- 💡 Note: When buildining LLM Judges, building metrics where scoring is not interpretable is a key design choice to control and mitigate the randomness that comes with LLMs. It is a common trend for LLM Judges to give different results between multiple runs for the same input and configuration. Thus, building a set of metrics where the decision is a no-brainer can drastically increase the stability of your LLM Judges between multiple runs.
- "But I'm Losing Nuance!": How to Track Gradual Improvement:
    - The right way to capture nuance is not by making your scale fuzzier, but by making your criteria more granular.
    - Instead of a single, subjective rating for a complex quality like "factual accuracy," you should break it down into multiple, specific, binary checks.
    - For example, instead of rating the quality of the article on a 1-5 scale for "Accuracy", we will create multiple binary evaluartions on different dimensions, such as:
        1. Content adherence: Does the generated article contain the same content as the expected article?
        2. Flow of ideas adherence: Does the generated article contain the ideas in the same order as the expected article?
        3. Article guideline adherence: Does the generated article follow the flow of ideas from the article guideline input?
        4. Research anchoring: Does the generated article contain ideas only from the research to avoid hallucinations?

- **Transition:** To conclude, even if there might be other methods to frame your metrics than binary, using this strategy is simple, intuitive, scalable, robust and proven in production systems.

- **Section length:** 500 words

## Section 7 - Conclusion
(Connect our solution to the bigger field of AI Engineering. Add course next steps.)

- One paragraph conclusion: Leverage insights from the `Why We Think It's Valuable` section.

- **Transition to future lessons:** Still, in this lesson we looked only over the theory behind building business AI evals metrics. The next lesson is fully hands-on, where we will implement from scratch everything we discussed.

- **Section length:** 100 words

## Golden Sources

1. [The Mirage of Generic AI Metrics](https://www.decodingai.com/p/the-mirage-of-generic-ai-metrics)
2. [The 5-Star Lie: You Are Doing AI Evals Wrong](https://www.decodingai.com/p/the-5-star-lie-you-are-doing-ai-evals)
3. [Escaping POC Purgatory: Evaluation-Driven Development for AI Systems](https://www.decodingai.com/p/escaping-poc-purgatory-evaluation)
4. [Stop Launching AI Apps Without This Framework](https://www.decodingai.com/p/stop-launching-ai-apps-without-this)
5. [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/)
6. [Evaluating the Effectiveness of LLM-Evaluators (aka LLM-as-Judge)](https://eugeneyan.com/writing/llm-evaluators/)
