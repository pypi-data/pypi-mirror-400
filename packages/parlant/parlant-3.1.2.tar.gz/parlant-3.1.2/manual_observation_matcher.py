import asyncio
from datetime import datetime, timezone
from itertools import count
from typing import Iterator, cast

from parlant.adapters.nlp.openai_service import OpenAIService
from parlant.core.agents import Agent, AgentId
from parlant.core.common import JSONSerializable, generate_id
from parlant.core.contextual_correlator import ContextualCorrelator
from parlant.core.customers import Customer, CustomerId
from parlant.core.engines.alpha.guideline_matching.generic.observational_batch import (
    GenericObservationalGuidelineMatchSchema,
    GenericObservationalGuidelineMatchesSchema,
    GenericObservationalGuidelineMatchingBatch,
)
from parlant.core.engines.alpha.guideline_matching.guideline_matcher import GuidelineMatchingContext
from parlant.core.engines.alpha.optimization_policy import BasicOptimizationPolicy
from parlant.core.guidelines import Guideline, GuidelineContent, GuidelineId
from parlant.core.loggers import LogLevel, StdoutLogger
from parlant.core.sessions import (
    Event,
    EventId,
    EventKind,
    EventSource,
    MessageEventData,
    Participant,
    Session,
    SessionId,
)


def make_message_event(
    offset_generator: Iterator[int],
    source: EventSource,
    message: str,
) -> Event:
    return Event(
        id=EventId(generate_id()),
        source=source,
        kind=EventKind.MESSAGE,
        creation_utc=datetime.now(timezone.utc),
        offset=next(offset_generator),
        correlation_id="<unused>",
        data=cast(
            JSONSerializable,
            MessageEventData(
                message=message,
                participant=Participant(
                    display_name=source.value,
                ),
            ),
        ),
        deleted=False,
    )


def make_observation(condition: str) -> Guideline:
    return Guideline(
        id=GuidelineId(generate_id()),
        creation_utc=datetime.now(timezone.utc),
        enabled=True,
        tags=[],
        metadata={},
        content=GuidelineContent(condition=condition, action=None),
    )


class CustomObservationalMatcher(GenericObservationalGuidelineMatchingBatch):
    def _match_applies(self, match: GenericObservationalGuidelineMatchSchema) -> bool:
        return True


async def main() -> None:
    correlator = ContextualCorrelator()
    logger = StdoutLogger(correlator=correlator, log_level=LogLevel.TRACE)
    op_policy = BasicOptimizationPolicy()

    generator = await OpenAIService(logger).get_schematic_generator(
        GenericObservationalGuidelineMatchesSchema
    )

    agent = Agent(
        id=AgentId("dummy-agent"),
        name="Dummy Agent",
        description=None,
        creation_utc=datetime.now(timezone.utc),
        max_engine_iterations=1,
        tags=[],
    )

    customer = Customer(
        id=CustomerId("dummy-customer"),
        creation_utc=datetime.now(timezone.utc),
        name="Dummy Customer",
        extra={},
        tags=[],
    )

    session = Session(
        id=SessionId("dummy-session"),
        creation_utc=datetime.now(timezone.utc),
        customer_id=CustomerId("dummy-customer"),
        agent_id=AgentId("dummy-agent"),
        title=None,
        consumption_offsets={},
        agent_states=[],
        mode="auto",
    )

    # Initialize event counter
    C = iter(count())

    interaction_history: list[Event] = [
        make_message_event(C, EventSource.CUSTOMER, "Hello, I want to buy a car."),
        make_message_event(C, EventSource.AI_AGENT, "Sure! What kind of car are you looking for?"),
        make_message_event(C, EventSource.CUSTOMER, "I don't know yet, maybe something on sale?"),
        make_message_event(C, EventSource.AI_AGENT, "Let me check the current offers."),
        make_message_event(C, EventSource.AI_AGENT, "The Hyundai i20 is on sale right now."),
        make_message_event(C, EventSource.CUSTOMER, "That sounds good! I want to buy it."),
    ]

    observational_guidelines: list[Guideline] = [
        make_observation("The customer wants to buy a Ford Focus"),
        make_observation("The customer wants to buy a Hyundai i20"),
    ]

    matcher = CustomObservationalMatcher(
        logger=logger,
        optimization_policy=op_policy,
        schematic_generator=generator,
        guidelines=observational_guidelines,
        journeys=[],
        context=GuidelineMatchingContext(
            agent=agent,
            session=session,
            customer=customer,
            context_variables=[],
            interaction_history=interaction_history,
            terms=[],
            capabilities=[],
            staged_events=[],
        ),
    )

    result = await matcher.process()

    for m in result.matches:
        print(f"Observation: {m.guideline.content.condition}")
        print(f"    Matched: {'Yes' if m.score > 5 else 'No'}")
        print(f"    Rationale: {m.rationale}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
