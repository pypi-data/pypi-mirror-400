# Patent Application

## Method and System for Controlled Content Generation Using Parameterized Fragments with Contextual Filtering

**Filing Type:** Continuation-in-Part (CIP)
**Priority:** Claims priority from provisional application "Method for Controlled Content Generation Using Dynamic Fragment Constraints"
**Inventors:** Yam Marcovitz, Dor Zohar, Bar Karov
**Field of Invention:** Generative AI

---

## Abstract

A method and system for controlled text and voice-audio content generation using generative artificial intelligence. The invention applies to AI-powered conversational systems that generate text responses for display or voice-audio responses for speech synthesis. A predictive model iteratively selects from a curated set of pre-approved text fragments, directed by contextual information, continuing until a termination condition is met (such as selecting a STOP fragment or reaching a maximum fragment limit). The selected fragments are then assembled into a cohesive response. Fragments may contain parameterized variable placeholders that are resolved at generation time from contextual data sources, enabling dynamic personalization while maintaining compliance with pre-approved response structures. Fragments are stored with associations to contextual cues—such as behavioral guidelines, topics, user journeys, and external data integrations—enabling the system to dynamically filter which fragments are available to the predictive model based on active contextual cues. This approach ensures compliant, personalized, context-appropriate responses across text-based chatbots, voice assistants, and other AI-driven communication channels.

---

## Background of the Invention

### Field of the Invention

The present invention relates to methods and systems for generating controlled text and voice-audio content using generative artificial intelligence, and more particularly to systems that constrain AI outputs to pre-approved text fragments while enabling dynamic personalization and context-aware filtering. The invention is applicable to any AI system that generates natural language output, whether rendered as text for visual display (in chatbots, messaging applications, email, or web interfaces) or converted to voice-audio through text-to-speech synthesis (in voice assistants, interactive voice response systems, or audio-enabled applications).

### Description of Related Art

Generative AI technologies, particularly Large Language Models (LLMs), are increasingly being deployed for customer interactions through multiple modalities including text-based chatbots, voice assistants, interactive voice response (IVR) systems, and other digital channels. These systems generate natural language text that may be displayed directly to users or synthesized into voice-audio for spoken delivery. However, organizations in regulated industries face significant challenges in ensuring these AI systems consistently produce compliant outputs regardless of the output modality.

The fundamental challenge stems from how LLMs generate responses. These models process language by breaking it into "tokens" (word fragments) and generate responses based on patterns learned from diverse and often inconsistent training data. Because tokens are small units and extremely diverse, and the models are statistical in nature, the generative outputs of these models frequently contain what the industry terms "hallucinations": incorrect, unverifiable, or incoherent content. This problem affects both text and voice-audio outputs, as voice systems typically rely on text generation followed by speech synthesis. For organizations operating under strict regulatory requirements, these unpredictable outputs present an unacceptable risk whether delivered as text or spoken audio.

A prior approach described in the provisional application addresses this challenge through a fragment-based generation system that:

- Employs a predictive model that processes contextual information together with a curated set of predefined text fragments
- Constrains the fragment predictor to select outputs exclusively from the predefined set
- Allows fragments ranging from individual words to complete paragraphs
- Selects multiple fragments in sequence until a STOP fragment or maximum limit is reached
- Assembles fragments into a cohesive response via a CompletionGenerator
- Provides a controllable axis between context-adaptability (through smaller fragments) and output determinism (through larger fragments)

While effective at preventing hallucinations, this approach has practical limitations that the present invention addresses.

---

## Summary of the Invention

The present invention extends the fragment-based generation system with two enhancements:

1. **Parameterized Fragments**: Fragments can contain variable placeholders that are filled at generation time, eliminating the need for separate fragments for each data variation.

2. **Fragment Store with Contextual Cue Associations**: Fragments are stored with associations to contextual cues (such as behavioral guidelines, topics, user journeys, and external data integrations), enabling context-aware filtering of which fragments are available to the predictive model.

---

## Detailed Description of the Invention

### Core Mechanism: Sequential Fragment Generation

The foundation of the invention is a fragment-based generation system where a predictive model (which may be an LLM or any NLP classification model) iteratively selects text fragments from a dynamic, curated, and pre-approved set. The generation process operates as follows:

1. **Initialization**: The system receives contextual information (user input, conversation history, response hints, etc.) and accesses the available fragment pool.

2. **Iterative Selection**: The predictive model selects one fragment from the available pool based on the context. This fragment is added to the response sequence.

3. **Termination Check**: After each selection, the system checks for termination conditions:

   - If a **STOP fragment** is selected, generation terminates
   - If the **maximum fragment limit** is reached, generation terminates
   - Otherwise, the context is updated with the newly selected fragment, and selection continues

4. **Assembly**: Once terminated, the selected fragments are assembled into a cohesive response by a CompletionGenerator component.

This iterative approach provides a controllable axis between context-adaptability and output determinism:

- **Smaller fragments** (words, short phrases) allow more adaptive, varied responses but require more selection steps
- **Larger fragments** (sentences, paragraphs) provide more deterministic outputs with fewer selection steps

The system may also include **system fragments** such as STOP, NEW_LINE, or punctuation markers that control response structure without adding semantic content.

### Extension 1: Parameterized Fragments

In the prior fragment-based approach, each unique response requires a separate pre-approved fragment. For example, to communicate account balances to customers, an operator would need to create and approve fragments such as:

- "Your account balance is $100"
- "Your account balance is $200"
- "Your account balance is $1,234.56"

This approach becomes impractical when dealing with dynamic data that can take many values.

The present invention introduces **parameterized fragments**: fragments containing variable placeholders denoted by a syntax such as `{{variable_name}}`. For example:

- "Your account balance is {{balance}}"

At generation time, before the fragment is output, placeholders are resolved from contextual data sources including conversation variables, user profile data, session state, or system-provided values.

#### Placeholder Resolution Process

1. Parse the fragment text to identify all variable placeholders
2. For each placeholder, look up the corresponding value in the context data
3. Substitute each placeholder with its resolved value
4. If any placeholder cannot be resolved, the fragment may be excluded from selection

Clause 4 is particularly important in preventing the system from generating false claims. For example, when the system, working within a banking context, must assist the user in disputing a transaction on their credit card, the fragment selection process runs the risk of saying, "The dispute has been filed successfully," even when it wasn't. However, by placing a placeholder, "The dispute (id={{dispute_id}}) has been filed successfully", this exclusion process ensures that the fragment can never be selected and displayed to the user unless a data source has reliably introduced this variable into the context.

### Extension 2: Fragment Store with Contextual Cue Associations

The present invention introduces the concept of **contextual cues**: metadata associations that determine when a fragment is appropriate for use. Contextual cues include:

| Contextual Cue Type        | Description                           | Examples                                                       |
| -------------------------- | ------------------------------------- | -------------------------------------------------------------- |
| Behavioral guidelines      | Rules governing agent behavior        | "HIPAA compliance", "banking disclosure", "no-refund policy"   |
| Topics                     | Subject matter categories             | "billing", "technical support", "product inquiry"              |
| User journeys              | Stages in a customer interaction flow | "onboarding", "renewal", "cancellation"                        |
| External data integrations | Connections to external systems       | "Salesforce CRM", "order management system", "payment gateway" |

Fragments are stored in a repository with zero or more contextual cue associations. Before fragment selection, the system:

1. Determines active contextual cues for the current context (based on conversation state, user attributes, connected integrations, regulatory requirements, etc.)
2. Filters the fragment pool to include only fragments associated with at least one active contextual cue, plus any global (untagged) fragments
3. Provides the filtered pool to the fragment predictor

This ensures the predictive model only sees contextually-appropriate fragments, improving both relevance and compliance.

### Combined System Flow

```
Context (user message, conversation history, active contextual cues)
    |
    v
Fragment Store --> [Contextual Cue Filter] --> Filtered Fragment Pool
    |
    v
┌─────────────────────────────────────────────────────────────┐
│              ITERATIVE FRAGMENT SELECTION                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Fragment Predictor selects next fragment from pool    │ │
│  │                         |                              │ │
│  │                         v                              │ │
│  │  Is fragment STOP or max limit reached?                │ │
│  │         |                    |                         │ │
│  │        NO                   YES                        │ │
│  │         |                    |                         │ │
│  │         v                    v                         │ │
│  │  Add to sequence,      Exit loop                       │ │
│  │  update context,       ─────────────────────────>      │ │
│  │  loop back                                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
    |
    v
Selected fragment sequence: ["Hello, ", "your balance is {{balance}}", STOP]
    |
    v
Placeholder Resolution from context data
    |
    v
Resolved fragments: ["Hello, ", "your balance is $1,234.56"]
    |
    v
CompletionGenerator assembles final response
    |
    v
Final output: "Hello, your balance is $1,234.56"
```

---

## Claims

### Independent Method Claim 1 (Parameterized Fragments)

A computer-implemented method for generating controlled text or voice-audio content, comprising:

1. Storing a plurality of pre-approved text fragments, wherein fragments may contain one or more variable placeholders;
2. Receiving contextual information including user input and context data;
3. Iteratively selecting fragments from the stored fragments using a predictive model, wherein the predictive model selects each fragment based on the contextual information and previously selected fragments, continuing until a termination condition is met;
4. For each selected fragment containing variable placeholders, resolving said placeholders using values from the context data; and
5. Assembling the selected fragments into a cohesive response and outputting the response.

### Claim 2

The method of claim 1, wherein the variable placeholders are denoted by a predefined syntax pattern within the fragment text.

### Claim 3

The method of claim 1, wherein the context data includes one or more of: conversation variables, user profile data, session state, or system-provided values.

### Claim 4

The method of claim 1, wherein a fragment containing an unresolvable placeholder is excluded from selection by the predictive model.

### Claim 5

The method of claim 1, wherein the termination condition comprises one or more of: selection of a designated STOP fragment, reaching a maximum fragment count limit, or selection of a fragment marked as terminal.

### Independent Method Claim 6 (Contextual Cue Filtering)

A computer-implemented method for generating controlled text or voice-audio content, comprising:

1. Storing a plurality of pre-approved text fragments, each fragment associated with zero or more contextual cues;
2. Receiving contextual information including user input and a set of active contextual cues for the current context;
3. Filtering the stored fragments to produce a filtered fragment pool containing only fragments associated with active contextual cue or fragments with no contextual cue associations;
4. Iteratively selecting fragments from the filtered fragment pool using a predictive model, wherein the predictive model selects each fragment based on the contextual information and previously selected fragments, continuing until a termination condition is met; and
5. Assembling the selected fragments into a cohesive response and outputting the response.

### Claim 7

The method of claim 6, wherein the contextual cues comprise one or more of: behavioral guidelines, topics, user journeys, or external data integrations.

### Claim 8

The method of claim 6, wherein the active contextual cues are determined based on conversation state, user attributes, connected external systems, or regulatory requirements.

### Claim 9

The method of claim 6, wherein each fragment is further associated with semantic signals, and the filtering additionally comprises matching fragments based on semantic similarity to the user input.

### Independent System Claim 10

A system for generating controlled text or voice-audio content, comprising:

- A fragment store containing pre-approved text fragments, wherein fragments may contain variable placeholders and may be associated with contextual cues;
- A contextual cue filter configured to filter fragments based on active contextual cues;
- A fragment predictor configured to iteratively select fragments from the filtered pool based on contextual information and previously selected fragments, continuing until a termination condition is met;
- A placeholder resolver configured to substitute variable placeholders with values from context data; and
- A response assembler configured to assemble the selected fragments into a cohesive response.

### Claim 11

The system of claim 10, wherein the termination condition comprises one or more of: selection of a designated STOP fragment, reaching a maximum fragment count limit, or selection of a fragment marked as terminal.

### Claim 12

The system of claim 10, wherein the contextual cues comprise one or more of: behavioral guidelines, topics, user journeys, or external data integrations.

### Claim 13

The system of claim 10, wherein fragments are further associated with semantic signals enabling relevance-based filtering.

### Claim 14

The system of claim 10, wherein the placeholder resolver excludes fragments with unresolvable placeholders from selection.

### Claim 15

The system of claim 10, wherein the fragment store further contains system fragments including at least one of: STOP fragments for terminating generation, NEW_LINE fragments for controlling response structure, or punctuation fragments.

---

## Drawings

### Figure 1: System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CONTEXT                                  │
│  (user message, conversation history, active contextual cues)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                      FRAGMENT STORE                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Fragment: "Hello, "                                     │    │
│  │   Contextual Cues: []  (always available)               │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Fragment: "your balance is {{balance}}"                 │    │
│  │   Contextual Cues: [banking_disclosure, account_inquiry]│    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Fragment: " as of {{date}}."                            │    │
│  │   Contextual Cues: [banking_disclosure]                 │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Fragment: STOP                                          │    │
│  │   (system fragment - terminates generation)             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                   CONTEXTUAL CUE FILTER                          │
│  Active cues: [banking_disclosure, account_inquiry]              │
│  Result: All matching fragments pass filter                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│              ITERATIVE FRAGMENT PREDICTOR                        │
│                                                                  │
│  Iteration 1: Selects "Hello, "                                 │
│  Iteration 2: Selects "your balance is {{balance}}"             │
│  Iteration 3: Selects " as of {{date}}."                        │
│  Iteration 4: Selects STOP  -->  [TERMINATE]                    │
│                                                                  │
│  Selected sequence: ["Hello, ", "your balance is {{balance}}",  │
│                      " as of {{date}}.", STOP]                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                   PLACEHOLDER RESOLVER                           │
│  Context: {balance: "$1,234.56", date: "January 15, 2025"}      │
│  Resolves placeholders in each fragment                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE ASSEMBLER                            │
│  Assembles: "Hello, " + "your balance is $1,234.56" +           │
│             " as of January 15, 2025."                          │
│                                                                  │
│  Final output: "Hello, your balance is $1,234.56 as of          │
│                 January 15, 2025."                              │
└─────────────────────────────────────────────────────────────────┘
```

### Figure 2: Contextual Cue Filtering Flowchart

```
                    ┌─────────────────┐
                    │  START: Get all │
                    │    fragments    │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │ Get active      │
                    │ contextual cues │
                    └────────┬────────┘
                             │
                             v
              ┌──────────────────────────────┐
              │  For each fragment:          │
              │  Does fragment have          │
              │  contextual cue associations?│
              └──────────────┬───────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              v                             v
        ┌───────────┐                ┌───────────────┐
        │    NO     │                │      YES      │
        │ (untagged)│                │               │
        └─────┬─────┘                └───────┬───────┘
              │                              │
              v                              v
        ┌───────────┐          ┌─────────────────────────┐
        │  INCLUDE  │          │ Do any fragment cues    │
        │ in pool   │          │ match active cues?      │
        └───────────┘          └────────────┬────────────┘
                                            │
                               ┌────────────┴────────────┐
                               │                         │
                               v                         v
                         ┌───────────┐             ┌───────────┐
                         │    YES    │             │    NO     │
                         └─────┬─────┘             └─────┬─────┘
                               │                         │
                               v                         v
                         ┌───────────┐             ┌───────────┐
                         │  INCLUDE  │             │  EXCLUDE  │
                         │  in pool  │             │ from pool │
                         └───────────┘             └───────────┘
```

### Figure 3: Iterative Fragment Selection Loop

```
                    ┌─────────────────────┐
                    │  START: Initialize  │
                    │  empty sequence     │
                    │  fragment_count = 0 │
                    └──────────┬──────────┘
                               │
                               v
              ┌────────────────────────────────┐
              │  Predictive model selects      │
              │  next fragment from filtered   │
              │  pool based on:                │
              │  - User input                  │
              │  - Conversation history        │
              │  - Previously selected frags   │
              └───────────────┬────────────────┘
                              │
                              v
              ┌────────────────────────────────┐
              │  Is selected fragment = STOP?  │
              └───────────────┬────────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
              YES                            NO
               │                             │
               v                             v
        ┌─────────────┐         ┌────────────────────────┐
        │  TERMINATE  │         │  Add fragment to       │
        │  (go to     │         │  sequence              │
        │  assembly)  │         │  fragment_count++      │
        └─────────────┘         └───────────┬────────────┘
                                            │
                                            v
                           ┌────────────────────────────────┐
                           │  Is fragment_count >= MAX_LIMIT?│
                           └───────────────┬────────────────┘
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                             YES                        NO
                              │                         │
                              v                         │
                       ┌─────────────┐                  │
                       │  TERMINATE  │                  │
                       │  (go to     │                  │
                       │  assembly)  │                  │
                       └─────────────┘                  │
                                                       │
                              ┌─────────────────────────┘
                              │
                              v
                    ┌─────────────────────┐
                    │  Update context     │
                    │  with new fragment  │
                    │  (loop back)        │
                    └──────────┬──────────┘
                               │
                               └──────────> (back to selection)
```

### Figure 4: Placeholder Resolution Flow

```
┌─────────────────────────────────────────┐
│  Input: Fragment with placeholders      │
│  "Your order {{order_id}} shipped on    │
│   {{ship_date}} via {{carrier}}"        │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  Parse placeholders:                    │
│  ["order_id", "ship_date", "carrier"]   │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  Context data available:                │
│  {                                      │
│    order_id: "ORD-12345",               │
│    ship_date: "January 15, 2025",       │
│    carrier: "FedEx"                     │
│  }                                      │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  For each placeholder:                  │
│  - Look up value in context             │
│  - Substitute in fragment text          │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  Output: Resolved fragment              │
│  "Your order ORD-12345 shipped on       │
│   January 15, 2025 via FedEx"           │
└─────────────────────────────────────────┘
```

---

## Examples of Use

### Example 1: Financial Services

**Fragment stored:**

```
"Your balance is {{balance}} as of {{date}}. This may not reflect pending transactions."
```

**Contextual cue associations:**

- guideline: "banking_disclosure"
- topic: "account_inquiry"

**Context data:**

```
{
  balance: "$5,432.10",
  date: "January 15, 2025"
}
```

**Active contextual cues:** ["banking_disclosure", "account_inquiry"]

**Generated response:**

```
"Your balance is $5,432.10 as of January 15, 2025. This may not reflect pending transactions."
```

**Compliance benefit:** The disclaimer text ("This may not reflect pending transactions") is guaranteed to appear because it is part of the pre-approved fragment.

### Example 2: Healthcare

**Fragment stored:**

```
"Your appointment with {{provider}} is scheduled for {{date}} at {{time}}. Please bring your insurance card and a valid ID."
```

**Contextual cue associations:**

- guideline: "hipaa_compliant"
- journey: "appointment_scheduling"

**Context data:**

```
{
  provider: "Dr. Smith",
  date: "January 20, 2025",
  time: "2:30 PM"
}
```

**Active contextual cues:** ["hipaa_compliant", "appointment_scheduling"]

**Generated response:**

```
"Your appointment with Dr. Smith is scheduled for January 20, 2025 at 2:30 PM. Please bring your insurance card and a valid ID."
```

**Compliance benefit:** This fragment is only available when healthcare-related contextual cues are active, ensuring HIPAA-appropriate language is used.

### Example 3: E-commerce with External Integration

**Fragment stored:**

```
"Your order {{order_id}} shipped on {{ship_date}} via {{carrier}}. Track your package at {{tracking_url}}."
```

**Contextual cue associations:**

- integration: "order_management_system"
- topic: "order_status"

**Context data (from integration):**

```
{
  order_id: "ORD-98765",
  ship_date: "January 18, 2025",
  carrier: "UPS",
  tracking_url: "https://ups.com/track/1Z999..."
}
```

**Active contextual cues:** ["order_management_system", "order_status"]

**Generated response:**

```
"Your order ORD-98765 shipped on January 18, 2025 via UPS. Track your package at https://ups.com/track/1Z999..."
```

**Integration benefit:** This fragment is only available when the order management integration is connected, ensuring order-related responses are only generated when accurate data is available.

---

## Advantages of the Invention

1. **Controllable Response Generation**: The iterative fragment selection process, with configurable termination conditions (STOP fragments, maximum limits), provides precise control over response length and structure while maintaining natural language flow.

2. **Adaptability-Determinism Tradeoff**: By adjusting fragment granularity (from individual words to complete paragraphs), operators can tune the system along a spectrum from highly adaptive responses (smaller fragments, more selection steps) to highly deterministic responses (larger fragments, fewer steps).

3. **Reduced Fragment Count**: Parameterized fragments eliminate the need to create separate fragments for each data variation, significantly reducing the number of fragments that must be curated and approved.

4. **Improved Personalization**: Dynamic placeholder resolution enables personalized responses while maintaining compliance guarantees.

5. **Context-Appropriate Responses**: Contextual cue filtering ensures fragments are only available when appropriate, improving both relevance and compliance.

6. **Integration Awareness**: External data integration cues enable the system to use integration-specific fragments only when those integrations are connected and data is available.

7. **Regulatory Compliance**: By combining pre-approved fragments with contextual filtering, organizations can ensure responses meet regulatory requirements for specific contexts (e.g., HIPAA for healthcare, banking disclosures for financial services).

8. **Operational Efficiency**: Topics and user journey cues enable more targeted fragment selection, reducing the cognitive load on the fragment predictor and improving response quality.

9. **Hallucination Prevention**: Since all output derives exclusively from pre-approved fragments, the system eliminates the risk of AI-generated hallucinations, making it suitable for regulated industries.
