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
from enum import Enum
from lagom import Container
from typing import Annotated, TypedDict

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
    ToolContext,
    ToolParameterOptions,
    ToolResult,
    tool,
)


EXIT_STACK = AsyncExitStack()


class OrderItem(TypedDict):
    item_name: str


class Order(TypedDict):
    order_number: int
    items: list[OrderItem]


class RefundType(Enum):
    CASH = "cash"
    STORE_CREDIT = "store_credit"


@tool
async def load_last_order(context: ToolContext) -> ToolResult:
    order: Order = {
        "order_number": 611887,
        "items": [
            {"item_name": "Bose Headphones"},
            {"item_name": "Razer Mousepad"},
        ],
    }

    return ToolResult(
        data=order,
        utterance_fields={"order": order},
    )


@tool
async def load_specific_order(
    context: ToolContext,
    order_number: Annotated[int, ToolParameterOptions(source="customer")],
) -> ToolResult:
    order: Order = {
        "order_number": 123598,
        "items": [
            {"item_name": "Takeya Stainless Steel Water Bottle"},
        ],
    }

    return ToolResult(
        data=order,
    )


@tool
async def return_item(
    context: ToolContext,
    order_number: Annotated[str, ToolParameterOptions(source="customer", precedence=1)],
    item_name: Annotated[str, ToolParameterOptions(source="customer", precedence=2)],
    refund_type: Annotated[RefundType, ToolParameterOptions(source="customer", precedence=3)],
) -> ToolResult:
    return ToolResult(
        data=f"Successfully returned {item_name} and refunded with {refund_type.value}",
    )


PORT = 8199
TOOLS = [load_last_order, load_specific_order, return_item]


async def initialize_module(container: Container) -> None:
    host = "127.0.0.1"

    server = PluginServer(
        tools=TOOLS,
        port=PORT,
        host=host,
        hosted=True,
    )

    await container[ServiceRegistry].update_tool_service(
        name="retail",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()
