import asyncio
from textwrap import dedent
import os
from typing import Optional, cast
import openai
import parlant.sdk as p


client = openai.AsyncClient(api_key=os.environ["OPENAI_API_KEY"])


async def configure_hooks(hooks: p.EngineHooks) -> p.EngineHooks:
    async def on_generating_messages(
        context: p.EngineContext,
        exception: Optional[Exception] = None,
    ) -> p.EngineHookResult:
        return p.EngineHookResult.CALL_NEXT

    hooks.on_generating_messages.append(on_generating_messages)

    return hooks


CARDS = {
    1: "VISA",
    2: "Mastercard",
}


@p.tool
async def list_cards(context: p.ToolContext) -> p.ToolResult:
    """
    This tool lists the user's cards.
    """
    cards = list(CARDS.values())
    return p.ToolResult(cards, canned_response_fields={"cards": cards})


@p.tool
async def lock_card(context: p.ToolContext, card_id: int) -> p.ToolResult:
    """
    This tool locks a user's card.
    """
    if card_id not in CARDS:
        return p.ToolResult(
            data="A valid card ID is required to lock the card.",
            canned_response_fields={"error": "A valid card ID is required."},
        )

    # Simulate successful lock operation
    return p.ToolResult(
        f"Card {CARDS[card_id]} has been locked successfully.",
        canned_response_fields={"message": f"Card {CARDS[card_id]} has been locked."},
    )


@p.tool
async def dispute_transaction(
    context: p.ToolContext,
    transaction_date: str,
    transaction_amount: float,
    merchant_name: str,
    reason: str,
) -> p.ToolResult:
    """
    This tool disputes a transaction.
    """
    # Imagine here you have a bunch of validation logic for the arguments.
    # For example, ensure you can find the transaction and confirm the details.
    dispute_id = "12345"

    return p.ToolResult(
        f"A dispute for the transaction on {transaction_date} of amount ${transaction_amount} at {merchant_name} has been filed successfully. Dispute ID is {dispute_id}.",
        canned_response_fields={
            "dispute_id": dispute_id,
            "transaction_date": transaction_date,
            "transaction_amount": transaction_amount,
            "merchant_name": merchant_name,
            "reason": reason,
        },
    )


async def create_card_lock_journey(agent: p.Agent) -> p.Journey:
    card_lock_journey = await agent.create_journey(
        title="Lock a Card",
        description=dedent("""\
            Help the user lock their card.
            """),
        conditions=[
            "The customer asked to lock their card",
            "The customer suspects their card is lost or stolen",
        ],
    )

    step_1 = await card_lock_journey.initial_state.transition_to(
        tool_instruction="Present the user with their list of cards and ask which one they want to lock",
        tool_state=list_cards,
    )

    step_2 = await step_1.target.transition_to(
        chat_state="Ask for the reason for locking the card (e.g., lost, stolen, temporary lock, etc.)",
    )

    step_3 = await step_2.target.transition_to(
        condition="The card is lost or stolen",
        chat_state="Ask them to call customer support at 123456789 to report the lost or stolen card",
    )

    step_4 = await step_2.target.transition_to(
        condition="Otherwise",
        tool_state=lock_card,
    )

    step_5 = await step_4.target.transition_to(
        chat_state="Inform them regarding the success or failure of locking their card"
    )

    _ = step_3, step_5

    for template in [
        ["Here are your cards: {{cards}}. Which one would you like to lock?"],
        [
            "Could you please provide the reason for locking the card?",
            "And why do you want to lock your card?",
            "Can you tell me the reason why you want to lock your card?",
        ],
        ["Your card has been locked successfully."],
        ["Please call customer support at 123456789 to report the lost or stolen card."],
    ]:
        content, *signals = template
        await card_lock_journey.create_canned_response(content, signals=signals)

    return card_lock_journey


async def create_dispute_transaction_journey(agent: p.Agent) -> p.Journey:
    dispute_transaction_journey = await agent.create_journey(
        title="Dispute a Transaction",
        description=dedent("""\
            Help the user dispute a transaction.
            """),
        conditions=[
            "The customer asked to dispute a transaction",
            "The customer suspects a transaction",
        ],
    )

    step_1 = await dispute_transaction_journey.initial_state.transition_to(
        chat_state="Determine the date of the transaction they want to dispute",
    )

    step_2 = await step_1.target.transition_to(
        chat_state="Determine the amount and merchant name of the transaction",
    )

    step_3 = await step_2.target.transition_to(
        chat_state="Determine the reason for the dispute (e.g., unauthorized charge, incorrect amount, fraud, etc.)",
    )

    step_4 = await step_3.target.transition_to(
        chat_state="Ask the customer to confirm if you can proceed with filing the dispute on their behalf",
    )

    step_5 = await step_4.target.transition_to(
        condition="The customer confirms",
        tool_instruction="File the dispute",
        tool_state=dispute_transaction,
    )

    _ = await step_5.target.transition_to(
        condition="The customer confirms",
        chat_state="Provide the dispute ID and assure them that the dispute will be investigated and resolved as soon as possible. Let them know they can check the status of their dispute in the app or by contacting customer support.",
    )

    _ = await step_4.target.transition_to(
        condition="The customer does not confirm",
        chat_state="Ask them if they could explain why they do not want to proceed with the dispute",
    )

    await dispute_transaction_journey.create_guideline(
        condition="the customer does not remember a detail that you requested",
        action="ask them to contact the customer support line at 123456789",
    )

    for template in [
        "Could you please provide the amount and merchant name of that transaction?",
        "Since you have already provided the amount, please provide the merchant name of that transaction.",
        "And what is the reason for the dispute, please?",
        "Can I have your confirmation to proceed with filing the dispute on your behalf.",
        "Your dispute has been filed successfully. Your dispute ID is 12345. The date is {{generative.date}}, amount is {{generative.amount}}, merchant name is {{generative.merchant_name}}. We will investigate and resolve it as soon as possible. You can check the status of your dispute in the app or by contacting customer support.",
        "Let me know when you have the details of the transaction you want to dispute.",
    ]:
        await dispute_transaction_journey.create_canned_response(template)

    return dispute_transaction_journey


@p.tool
async def report_customer_unable_to_make_phone_call(context: p.ToolContext) -> p.ToolResult:
    server = p.ToolContextAccessor(context).server

    if customer := await server.find_customer(id=context.customer_id):
        if agent := await server.find_agent(id=context.agent_id):
            if variable := await agent.find_variable(name="customer_observations"):
                current_observations = set(
                    cast(list[str] | None, await variable.get_value_for_customer(customer)) or []
                )

                current_observations.add("The customer is unable to make a phone call.")

                await variable.set_value_for_customer(customer, list(current_observations))

                return p.ToolResult(
                    "Reported that the customer is unable to make a phone call.",
                    control={"lifespan": "response"},
                )

    return p.ToolResult("Error", control={"lifespan": "response"})


async def main() -> None:
    async with p.Server(
        configure_hooks=configure_hooks,
        nlp_service=p.NLPServices.openai,
    ) as server:
        agent = await server.create_agent(
            name="Bank Digital Assistant",
            description=dedent("""\
                You're a customer service agent for the bank.

                You work directly on the mobile app and help customers with their needs with respect to the bank's offerings, such as credit cards, loans, and other banking services.

                When talking about and representing the bank, use "we" and "us" to signify that you're speaking on behalf of the company.

                IMPORTANT: Always reply in markdown format with proper paragraph separation.
                """),
            composition_mode=p.CompositionMode.STRICT,
        )

        dispute_transaction_journey = await create_dispute_transaction_journey(agent)
        card_lock_journey = await create_card_lock_journey(agent)

        disambiguator = await agent.create_observation(
            "The user suspects fraud but it's not clear whether they want to dispute a transaction or lock a card."
        )

        await disambiguator.disambiguate(
            dispute_transaction_journey.conditions + card_lock_journey.conditions
        )

        customer_observations = await agent.create_variable(
            name="customer_observations",
            description="A list of observations made about the customer during this conversation and other ones.",
        )

        await customer_observations.set_global_value("None")

        await agent.create_guideline(
            "the customer is unable to make a phone call",
            action="report this observation using the tool, and ask if they want to chat with a human",
            tools=[report_customer_unable_to_make_phone_call],
        )

        for template in [
            "How can I help you today?",
            "Could you please clarify what you mean?",
            "I can help you with {{generative.relevant_capability}}. Please let me know how to proceed.",
        ]:
            await agent.create_canned_response(template)

        for preamble_template in [
            "Hi there, {{std.customer.name}}.",
            "Hello, {{std.customer.name}}.",
            "Noted.",
            "I see.",
            "I understand.",
            "Understood.",
            "Got it.",
            "Just a moment, please.",
            "Let me look into that for you.",
            "Thank you for your patience.",
            "I understand your concern.",
        ]:
            await agent.create_canned_response(preamble_template, tags=[p.Tag.preamble()])

        await agent.experimental_features.create_capability(
            title="Dispute a transaction",
            description="Customer does not recognize a transaction and wants to dispute it. Also includes cases where the customer is suspicious of fraud transactions to have taken place from their card",
            signals=[
                "Dispute transaction",
                "I don't recognize the 400$ charge",
                "I dont remember making this payment",
            ],
        )

        await agent.experimental_features.create_capability(
            title="Lock a card",
            description="Customer wants to lock their card for security reasons, such as lost or stolen card. Also includes cases where the customer is suspicious of fraud transactions to have taken place from their card",
            signals=["Lock card", "I want to lock my card for security reasons"],
        )


asyncio.run(main())
