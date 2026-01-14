from typing import Any, Optional
import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json
import os 
import sys
import subprocess

# Initialize FastMCP server
mcp = FastMCP("automata-playwright-mcp")

async def get_actionable_elements_for_llm(page: Page) -> str:
    """
    Extracts structured, token-efficient JSON data for actionable elements 
    using a single page.evaluate() call, minimizing network latency.
    
    Returns:
        str: A JSON string containing the list of elements for the LLM agent.
    """
    
    # 1. Broad, robust selector targeting common actionable roles/tags, 
    # and includes the :visible pseudo-class for efficiency.
    # Note: :visible is a Playwright extension and must be used with page.locator() 
    # in Python, but we can filter for visibility within JS for page.evaluate().
    ACTIONABLE_SELECTOR = 'a, button, input:not([type="hidden"]), textarea, select, [role="button"], [role="link"], [tabindex]'

    # 2. Execute a single JavaScript function in the browser context
    elements_data = await page.evaluate(f"""
        (selector) => {{
            const elements = document.querySelectorAll(selector);
            const data = [];

            elements.forEach((el, index) => {{
                // Check if the element is visually rendered (offsetWidth > 0) to avoid hidden elements
                if (el.offsetWidth > 0 && el.offsetHeight > 0) {{
                    
                    // Generate a Playwright-preferred locator string using accessibility attributes
                    let locator_strategy = '';
                    if (el.id) {{
                        locator_strategy = `#${{el.id}}`;
                    }} else if (el.placeholder) {{
                        locator_strategy = `[placeholder="${{el.placeholder.substring(0, 50)}}"]`;
                    }} else if (el.hasAttribute('aria-label')) {{
                        locator_strategy = `[aria-label="${{el.getAttribute('aria-label').substring(0, 50)}}"]`;
                    }} else if (el.getAttribute('data-testid')) {{
                        locator_strategy = `[data-testid="${{el.getAttribute('data-testid')}}"]`;
                    }} else {{
                        // Fallback to text content and tag name (LESS RELIABLE)
                        const textContent = el.textContent ? el.textContent.trim().substring(0, 50) : '';
                        if (textContent) {{
                            locator_strategy = `text="${{textContent}}"`;
                        }} else {{
                            locator_strategy = el.tagName.toLowerCase();
                        }}
                    }}

                    // Create the clean, structured data object
                    data.push({{
                        "index": index,
                        "tag": el.tagName.toLowerCase(),
                        "role": el.getAttribute('role') || el.tagName.toLowerCase(),
                        "locator_id": locator_strategy, 
                        "text": el.textContent.trim().substring(0, 50),
                        "placeholder": el.placeholder || '',
                        "name": el.name || '',
                        "type": el.type || el.getAttribute('type') || '',
                    }});
                }}
            }});
            return data;
        }}
    """, ACTIONABLE_SELECTOR)

    # Return the structured data as a token-efficient JSON string
    return json.dumps(elements_data, indent=2)


# Global state to track browser instances
class BrowserState:
    playwright = None
    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

state = BrowserState()

@mcp.tool()
async def open_browser(url: str) -> dict:
    """
    Opens a browser and navigates to a URL.
    If a browser is already open, it reuses it but navigates to the new URL.
    """
    try:
        # Initialize Playwright if not already started
        if not state.playwright:
            state.playwright = await async_playwright().start()

        # Launch browser if not already running
        if not state.browser:
            state.browser = await state.playwright.chromium.launch(headless=False)
            state.context = await state.browser.new_context()
            state.page = await state.context.new_page()

        # Navigate to URL
        response = await state.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        if not response:
            return {
                "ok": False,
                "action": "open_browser",
                "target": url,
                "data": None,
                "page": None,
                "error": {
                    "type": "NoResponse",
                    "message": "No response received from server",
                    "retryable": True
                }
            }

        return {
            "ok": True,
            "action": "open_browser",
            "target": url,
            "data": {
                "status": response.status
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "open_browser",
            "target": url,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": False
            }
        }

    
@mcp.tool()
async def navigate_to(url: str) -> dict:
    """
    Navigates the currently open browser to a new URL.
    Use this when the browser is already open and you want to change the address.
    """

    if not state.page:
        return {
            "ok": False,
            "action": "navigate_to",
            "target": url,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session found. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        response = await state.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        if not response:
            return {
                "ok": False,
                "action": "navigate_to",
                "target": url,
                "data": None,
                "page": {
                    "url": state.page.url,
                    "title": await state.page.title()
                },
                "error": {
                    "type": "NoResponse",
                    "message": "Navigation failed: no response from server",
                    "retryable": True
                }
            }

        return {
            "ok": True,
            "action": "navigate_to",
            "target": url,
            "data": {
                "status": response.status
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "navigate_to",
            "target": url,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def finish() -> dict:
    """
    Safely closes the active browser and cleans up resources.
    """
    try:
        browser_was_open = state.browser is not None
        playwright_was_running = state.playwright is not None

        if state.browser:
            await state.browser.close()
            state.browser = None
            state.context = None
            state.page = None

        if state.playwright:
            await state.playwright.stop()
            state.playwright = None

        return {
            "ok": True,
            "action": "finish",
            "target": None,
            "data": {
                "browser_closed": browser_was_open,
                "playwright_stopped": playwright_was_running
            },
            "page": None,
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "finish",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": False
            }
        }

    
@mcp.tool()
async def get_actionable_elements() -> dict:
    """Returns a structured list of actionable elements for the LLM."""
    
    if not state.page:
        return {
            "ok": False,
            "action": "get_actionable_elements",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        # Get raw JSON string from your existing logic
        elements_json = await get_actionable_elements_for_llm(state.page)

        # Parse once on the server side (important)
        elements = json.loads(elements_json)

        return {
            "ok": True,
            "action": "get_actionable_elements",
            "target": None,
            "data": {
                "count": len(elements),
                "elements": elements
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "get_actionable_elements",
            "target": None,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def click_element(locator_id: str) -> dict:
    """
    Clicks an element on the current page.
    Pass the 'locator_id' obtained from the get_actionable_elements tool.
    """

    if not state.page:
        return {
            "ok": False,
            "action": "click_element",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        # Capture pre-click state (important for navigation detection)
        previous_url = state.page.url
        previous_title = await state.page.title()

        await state.page.click(locator_id, timeout=10000)

        # Capture post-click state
        current_url = state.page.url
        current_title = await state.page.title()

        navigated = (
            previous_url != current_url or
            previous_title != current_title
        )

        return {
            "ok": True,
            "action": "click_element",
            "target": locator_id,
            "data": {
                "navigated": navigated
            },
            "page": {
                "url": current_url,
                "title": current_title
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "click_element",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def type_text(locator_id: str, text: str) -> dict:
    """
    Types text into an input field or textarea.
    Pass the 'locator_id' from get_actionable_elements and the text to type.
    """

    if not state.page:
        return {
            "ok": False,
            "action": "type_text",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        # Clear existing value first
        await state.page.fill(locator_id, "")
        await state.page.type(locator_id, text)

        # Optional verification (very useful for LLM confidence)
        entered_value = await state.page.locator(locator_id).input_value()

        return {
            "ok": True,
            "action": "type_text",
            "target": locator_id,
            "data": {
                "text_length": len(text),
                "verified": entered_value == text
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "type_text",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def extract_text_from_page() -> dict:
    """
    Extracts all visible text from the page.
    Use this to find prices, product names, or verify order totals.
    """

    if not state.page:
        return {
            "ok": False,
            "action": "extract_text_from_page",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        text = await state.page.evaluate(
            """() => {
                const scripts = document.querySelectorAll('script, style, nav, footer');
                scripts.forEach(s => s.remove());
                return document.body.innerText.replace(/\\n\\s*\\n/g, '\\n');
            }"""
        )

        MAX_CHARS = 15000
        truncated = len(text) > MAX_CHARS

        return {
            "ok": True,
            "action": "extract_text_from_page",
            "target": None,
            "data": {
                "text": text[:MAX_CHARS],
                "truncated": truncated,
                "char_count": min(len(text), MAX_CHARS)
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "extract_text_from_page",
            "target": None,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
@mcp.tool()
async def get_element_text(locator_id: str) -> dict:
    """
    Extracts text from a specific element.
    Use this to accurately get a product's price or name once you have its locator.
    """

    if not state.page:
        return {
            "ok": False,
            "action": "get_element_text",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        element = state.page.locator(locator_id)

        text = await element.inner_text(timeout=5000)
        text = text.strip()

        return {
            "ok": True,
            "action": "get_element_text",
            "target": locator_id,
            "data": {
                "text": text,
                "char_count": len(text)
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "get_element_text",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def get_element_attribute(locator_id: str, attribute: str) -> dict:
    """Gets a specific attribute value from an element."""

    if not state.page:
        return {
            "ok": False,
            "action": "get_element_attribute",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        value = await state.page.locator(locator_id).get_attribute(attribute)

        return {
            "ok": True,
            "action": "get_element_attribute",
            "target": locator_id,
            "data": {
                "attribute": attribute,
                "value": value,
                "is_present": value is not None
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "get_element_attribute",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
@mcp.tool()
async def select_option(locator_id: str, option_value: str) -> dict:
    """Selects an option from a dropdown."""

    if not state.page:
        return {
            "ok": False,
            "action": "select_option",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session. Call 'open_browser' first.",
                "retryable": False
            }
        }

    try:
        await state.page.locator(locator_id).select_option(option_value)

        return {
            "ok": True,
            "action": "select_option",
            "target": locator_id,
            "data": {
                "selected_value": option_value
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "select_option",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url if state.page else None,
                "title": await state.page.title() if state.page else None
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
@mcp.tool()
async def get_page_url() -> dict:
    """Returns the current page URL."""

    if not state.page:
        return {
            "ok": False,
            "action": "get_page_url",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    return {
        "ok": True,
        "action": "get_page_url",
        "target": None,
        "data": {
            "url": state.page.url
        },
        "page": {
            "url": state.page.url,
            "title": await state.page.title()
        },
        "error": None
    }


@mcp.tool()
async def go_back() -> dict:
    """Goes back to the previous page."""

    if not state.page:
        return {
            "ok": False,
            "action": "go_back",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        response = await state.page.go_back(timeout=10000)

        return {
            "ok": True,
            "action": "go_back",
            "target": None,
            "data": {
                "navigated": response is not None
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "go_back",
            "target": None,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def go_forward() -> dict:
    """Goes forward to the next page."""

    if not state.page:
        return {
            "ok": False,
            "action": "go_forward",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        response = await state.page.go_forward(timeout=10000)

        return {
            "ok": True,
            "action": "go_forward",
            "target": None,
            "data": {
                "navigated": response is not None
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "go_forward",
            "target": None,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def refresh_page() -> dict:
    """Refreshes the current page."""

    if not state.page:
        return {
            "ok": False,
            "action": "refresh_page",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        await state.page.reload(wait_until="domcontentloaded")

        return {
            "ok": True,
            "action": "refresh_page",
            "target": None,
            "data": {
                "reloaded": True
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "refresh_page",
            "target": None,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
@mcp.tool()
async def hover_element(locator_id: str) -> dict:
    """Hovers over an element to trigger hover states."""

    if not state.page:
        return {
            "ok": False,
            "action": "hover_element",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        await state.page.locator(locator_id).hover()

        return {
            "ok": True,
            "action": "hover_element",
            "target": locator_id,
            "data": {
                "hovered": True
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "hover_element",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    

@mcp.tool()
async def scroll_page(direction: str, pixels: int = 500) -> dict:
    """Scrolls the page in a direction (up/down/left/right)."""

    if not state.page:
        return {
            "ok": False,
            "action": "scroll_page",
            "target": direction,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        direction = direction.lower()

        if direction == "down":
            await state.page.evaluate(f"window.scrollBy(0, {pixels})")
        elif direction == "up":
            await state.page.evaluate(f"window.scrollBy(0, {-pixels})")
        elif direction == "right":
            await state.page.evaluate(f"window.scrollBy({pixels}, 0)")
        elif direction == "left":
            await state.page.evaluate(f"window.scrollBy({-pixels}, 0)")
        else:
            return {
                "ok": False,
                "action": "scroll_page",
                "target": direction,
                "data": None,
                "page": {
                    "url": state.page.url,
                    "title": await state.page.title()
                },
                "error": {
                    "type": "InvalidInput",
                    "message": "Direction must be up, down, left, or right.",
                    "retryable": False
                }
            }

        return {
            "ok": True,
            "action": "scroll_page",
            "target": direction,
            "data": {
                "pixels": pixels
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "scroll_page",
            "target": direction,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def double_click_element(locator_id: str) -> dict:
    """Double-clicks an element."""

    if not state.page:
        return {
            "ok": False,
            "action": "double_click_element",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        await state.page.locator(locator_id).dblclick()

        return {
            "ok": True,
            "action": "double_click_element",
            "target": locator_id,
            "data": {
                "double_clicked": True
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "double_click_element",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }


@mcp.tool()
async def right_click_element(locator_id: str) -> dict:
    """Right-clicks an element."""

    if not state.page:
        return {
            "ok": False,
            "action": "right_click_element",
            "target": locator_id,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        await state.page.locator(locator_id).click(button="right")

        return {
            "ok": True,
            "action": "right_click_element",
            "target": locator_id,
            "data": {
                "right_clicked": True
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "right_click_element",
            "target": locator_id,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
@mcp.tool()
async def get_page_title() -> dict:
    """Returns the current page title."""

    if not state.page:
        return {
            "ok": False,
            "action": "get_page_title",
            "target": None,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    title = await state.page.title()

    return {
        "ok": True,
        "action": "get_page_title",
        "target": None,
        "data": {
            "title": title
        },
        "page": {
            "url": state.page.url,
            "title": title
        },
        "error": None
    }


@mcp.tool()
async def check_page_contains_text(text: str) -> dict:
    """Checks if visible page text contains a specific string."""

    if not state.page:
        return {
            "ok": False,
            "action": "check_page_contains_text",
            "target": text,
            "data": None,
            "page": None,
            "error": {
                "type": "NoSession",
                "message": "No active browser session.",
                "retryable": False
            }
        }

    try:
        visible_text = await state.page.evaluate(
            "() => document.body.innerText"
        )

        found = text in visible_text

        return {
            "ok": True,
            "action": "check_page_contains_text",
            "target": text,
            "data": {
                "found": found
            },
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "action": "check_page_contains_text",
            "target": text,
            "data": None,
            "page": {
                "url": state.page.url,
                "title": await state.page.title()
            },
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": True
            }
        }

    
def install_playwright():
    """Install Playwright browsers on first run"""
    try:
        # Check if browsers are already installed
        result = subprocess.run(
            ["playwright", "install", "--help"],
            capture_output=True,
            text=True
        )
        
        # Install chromium
        print("Installing Playwright Chromium browser...")
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True
        )
        print("✓ Playwright Chromium installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install Playwright browsers: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: playwright command not found", file=sys.stderr)
        return False

def main():
    """Main entry point for the MCP server"""
    # Check if this is the first run
    first_run_file = os.path.expanduser("~/.automata_playwright_mcp_installed")
    
    if not os.path.exists(first_run_file):
        print("First run detected. Installing Playwright browsers...")
        if install_playwright():
            # Mark as installed
            os.makedirs(os.path.dirname(first_run_file), exist_ok=True)
            with open(first_run_file, "w") as f:
                f.write("installed")
    
    # Run the MCP server
    mcp.run()

# Add this at the bottom of your existing server.py
if __name__ == "__main__":
    main()