import asyncio
import json
import traceback

from browser_use.dom.serializer.serializer import DOMTreeSerializer

from optexity.inference.core.interaction.handle_select import select_option_index
from optexity.inference.core.interaction.handle_select_utils import (
    SelectOptionValue,
    smart_select,
)
from optexity.inference.infra.browser import Browser
from optexity.schema.actions.interaction_action import SelectOptionAction
from optexity.schema.memory import BrowserState, Memory


async def main():
    memory = Memory()
    browser = Browser(
        memory=memory,
        headless=False,
        channel="chromium",
        debug_port=9222,
        use_proxy=False,
    )
    try:
        await browser.start()
        await browser.go_to_url("https://practice.expandtesting.com/dropdown")

        # await asyncio.to_thread(input, "Press Enter to continue...")

        browser_state_summary = await browser.get_browser_state_summary()
        browser_state = BrowserState(
            url=browser_state_summary.url,
            screenshot=browser_state_summary.screenshot,
            title=browser_state_summary.title,
            axtree=browser_state_summary.dom_state.llm_representation(),
        )

        with open("/tmp/axtree.txt", "w") as f:
            f.write(browser_state.axtree)

        index = await asyncio.to_thread(input, "Enter index: ")
        print(f"Index: {index}")
        node = await browser.backend_agent.browser_session.get_element_by_index(
            int(index)
        )
        if node is None:
            print("Node not found")
            return

        select_option_values = DOMTreeSerializer(node)._extract_select_options(node)
        print("Select option values:")
        print(json.dumps(select_option_values["all_options"], indent=4))

        all_options = [
            SelectOptionValue(value=o["value"], label=o["text"])
            for o in select_option_values["all_options"]
        ]

        while True:
            patterns = await asyncio.to_thread(input, "Enter patterns (exit to exit): ")

            if patterns.startswith("exit"):
                return

            patterns = patterns.split(",")

            matched_values = await smart_select(all_options, patterns, memory)

            print(f"Matched values: {matched_values}")

            select_option_action = SelectOptionAction(
                select_values=patterns,
                prompt_instructions=f"Select the option that matches the patterns: {patterns}",
            )

            await select_option_index(select_option_action, browser, memory, None)

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
