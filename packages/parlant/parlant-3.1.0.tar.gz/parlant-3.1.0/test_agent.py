import parlant.sdk as p
import asyncio


async def main() -> None:
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Demo Agent",
            description="An agent demonstrating custom retrievers",
        )

        async def custom_retriever(ctx: p.RetrieverContext) -> p.RetrieverResult:
            return p.RetrieverResult(data="Choogoo is a type of golden eggplant")

        await agent.create_guideline(
            condition="the customer asks about a convenience store other than Target",
            action="aggressively and rudely tell them to forget about that one and go to Target instead",
        )

        await agent.attach_retriever(custom_retriever)


asyncio.run(main())
