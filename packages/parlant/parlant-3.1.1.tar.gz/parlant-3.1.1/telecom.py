# Copyright 2025 Emcie Co Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import AsyncExitStack
from lagom import Container
from typing import Annotated

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
    ToolContext,
    ToolParameterOptions,
    ToolResult,
    tool,
)


EXIT_STACK = AsyncExitStack()


async def verify_zip_code(customer, code) -> bool:
    return True


@tool
async def verify_account(
    context: ToolContext,
    zip_code: Annotated[
        int,
        ToolParameterOptions(
            description="The customer's zip code, for account verification",
            source="customer",
        ),
    ],
) -> ToolResult:
    if zip_code != 12345:
        return ToolResult({"verification_status": "denied - incorrect zip code"})

    return ToolResult({"verification_status": "success - correct zip code"})


@tool
async def load_last_bill(context: ToolContext) -> ToolResult:
    bill = {
        "bill_number": 2395872,
        "bill_date_yyyy_mm_dd": "2025-05-08",
        "bill_total": "$120",
        "breakdown_of_charges": {
            "mobile": "$80",
            "internet": "$40",
        },
        "change": {
            "end_of_discount": {
                "amount": "$25",
                "month": "April",
            }
        },
        "notes": "promotional discount has just ended (in April), which until now saved $25/month",
    }

    return ToolResult(data=bill, utterance_fields={"bill": bill})


@tool
async def get_available_offers(context: ToolContext) -> ToolResult:
    return ToolResult(
        data={"loyalty_offer": "saves 15 USD/month, applies for 12 months"},
        utterance_fields={
            "offer": {
                "discount": {
                    "amount": "$15",
                    "number_of_months": 12,
                }
            }
        },
    )


@tool
async def apply_offer(context: ToolContext) -> ToolResult:
    return ToolResult({"result": "offer applied successfully"})


PORT = 8199
TOOLS = [verify_account, load_last_bill, get_available_offers, apply_offer]


async def initialize_module(container: Container) -> None:
    host = "127.0.0.1"

    server = PluginServer(
        tools=TOOLS,
        port=PORT,
        host=host,
        hosted=True,
    )

    await container[ServiceRegistry].update_tool_service(
        name="telecom",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()
