from optexity.inference.infra.browser import Browser
from optexity.schema.actions.interaction_action import KeyPressAction, KeyPressType
from optexity.schema.memory import Memory


async def handle_key_press(
    keypress_action: KeyPressAction,
    memory: Memory,
    browser: Browser,
):
    page = await browser.get_current_page()
    if page is None:
        return

    if keypress_action.type == KeyPressType.ENTER:
        await page.keyboard.press("Enter")
