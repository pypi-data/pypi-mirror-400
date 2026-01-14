import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page

    from ...types import ActionResult

from ...telemetry import get_tracer
from ...types import Action

logger = logging.getLogger(__name__)
tracer = get_tracer()


async def execute_actions(page: "Page", actions: list[Action]) -> list["ActionResult"]:
    """
    Execute a list of actions on a Playwright page.

    Args:
        page: Playwright page instance
        actions: List of Action objects

    Returns:
        List of ActionResult objects
    """
    import time

    from opentelemetry import trace

    from ...types import ActionResult

    results = []

    for action in actions:
        with tracer.start_as_current_span(
            f"phantomfetch.action.{action.action}"
        ) as span:
            span.set_attribute("phantomfetch.action.type", action.action)
            if action.selector:
                span.set_attribute("phantomfetch.action.selector", action.selector)

            logger.debug(
                f"[browser] Executing: {action.action} {action.selector or ''}"
            )

            # Handle conditional action logic
            if action.if_selector:
                condition_met = False

                # If timeout is specified, wait for selector
                if action.if_selector_timeout > 0:
                    try:
                        logger.debug(
                            f"[browser] Waiting up to {action.if_selector_timeout}ms for condition: {action.if_selector}"
                        )
                        # wait_for_selector waits for state='visible' by default which is usually what we want
                        # for a "label appearing".
                        await page.wait_for_selector(
                            action.if_selector,
                            timeout=action.if_selector_timeout,
                            state="attached",  # Just existence in DOM as per original logic, checks existence
                        )
                        condition_met = True
                    except (
                        Exception
                    ):  # TimeoutError primarily, but playwright errors can be diverse
                        condition_met = False
                else:
                    # Immediate check
                    condition_count = await page.locator(action.if_selector).count()
                    condition_met = condition_count > 0

                if not condition_met:
                    logger.debug(
                        f"[browser] Skipping action {action.action} because if_selector '{action.if_selector}' not found (timeout={action.if_selector_timeout})"
                    )
                    # Create a skipped result
                    result = ActionResult(
                        action=action,
                        success=True,
                        data="Skipped (condition not met)",
                    )
                    span.set_attribute("phantomfetch.action.skipped", True)
                    span.set_attribute(
                        "phantomfetch.action.skipped_reason", "condition_not_met"
                    )
                    results.append(result)
                    continue

                logger.debug(
                    f"[browser] Condition met for {action.action}: '{action.if_selector}' found"
                )
                span.set_attribute("phantomfetch.action.condition_met", True)

            start_time = time.perf_counter()
            result = ActionResult(action=action, success=True)

            try:
                match action.action:
                    case "wait":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )

                        if action.selector:
                            # Use state if provided, default to visible or attached based on context?
                            # Playwright wait_for_selector defaults to 'visible'.
                            # If user provided state (visible, detached, hidden, attached), use it.
                            state = action.state or "visible"
                            await page.wait_for_selector(
                                action.selector,
                                timeout=action.timeout,
                                state=state,
                            )
                        elif action.timeout:
                            await page.wait_for_timeout(action.timeout)

                    case "click":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )
                        if action.selector:
                            await page.click(
                                action.selector,
                                timeout=action.timeout,
                            )

                    case "input":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )
                        if action.selector and action.value is not None:
                            val_str = str(action.value)
                            span.set_attribute(
                                "phantomfetch.action.input.length", len(val_str)
                            )
                            await page.fill(
                                action.selector,
                                val_str,
                                timeout=action.timeout,
                            )

                    case "scroll":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )

                        if action.selector == "top":
                            await page.evaluate("window.scrollTo(0, 0)")
                        elif action.x is not None or action.y is not None:
                            x = action.x or 0
                            y = action.y or 0
                            await page.evaluate(f"window.scrollTo({x}, {y})")
                        elif action.selector:
                            await page.locator(
                                action.selector
                            ).scroll_into_view_if_needed(timeout=action.timeout)
                        else:
                            # Scroll to bottom if no selector and no coordinates
                            await page.evaluate(
                                "window.scrollTo(0, document.body.scrollHeight)"
                            )
                    
                    case "extract":
                        # Validate schema
                        if not action.schema:
                            result.error = "Extraction requires a schema"
                            result.success = False
                        else:
                            # We use a JS evaluation to extract data efficiently
                            # We define a mini-engine in JS
                            js_extract = """
                            (args) => {
                                const { rootSelector, schema } = args;
                                
                                const getEl = (ctx, sel) => sel ? ctx.querySelector(sel) : ctx;
                                const getEls = (ctx, sel) => ctx.querySelectorAll(sel);
                                
                                const extractSingle = (ctx, spec) => {
                                    // Syntax: "selector :: attr(foo)" or "selector :: text"
                                    // If simple string "selector", default to text? or require syntax?
                                    // User prompt implied: "h2.title", "a :: attr(href)"
                                    
                                    let selector = spec;
                                    let op = "text";
                                    let param = null;
                                    
                                    if (spec.includes(" :: ")) {
                                        const parts = spec.split(" :: ");
                                        selector = parts[0];
                                        const opPart = parts[1];
                                        if (opPart.startsWith("attr(")) {
                                            op = "attr";
                                            param = opPart.slice(5, -1);
                                        } else if (opPart === "text") {
                                            op = "text";
                                        } else if (opPart === "html") {
                                            op = "html";
                                        }
                                    }
                                    
                                    const el = selector ? ctx.querySelector(selector) : ctx;
                                    if (!el) return null;
                                    
                                    if (op === "text") return el.innerText.trim();
                                    if (op === "html") return el.outerHTML;
                                    if (op === "attr" && param) return el.getAttribute(param);
                                    return null;
                                };
                                
                                const processSchema = (ctx, s) => {
                                    const out = {};
                                    for (const [key, val] of Object.entries(s)) {
                                        if (typeof val === "string") {
                                            out[key] = extractSingle(ctx, val);
                                        } else if (typeof val === "object" && val !== null) {
                                            // Nested object or list?
                                            // Complex nested schema logic could be indefinite.
                                            // Let's keep it simple: string checks
                                            // If dict, recursion on same context?
                                            // What if list? Allow list definition?
                                            // User requested Structured Extract.
                                            // Let's support recursive dicts on SAME context for now.
                                            out[key] = processSchema(ctx, val);
                                        }
                                    }
                                    return out;
                                };

                                const root = rootSelector ? document.querySelector(rootSelector) : document;
                                if (!root) return null;
                                
                                return processSchema(root, schema);
                            }
                            """
                            extracted_data = await page.evaluate(
                                js_extract, 
                                {"rootSelector": action.selector, "schema": action.schema}
                            )
                            result.data = extracted_data
                            # Also attach to last ActionResult? 
                            # ActionResult has 'data' field. Perfect.

                    case "select":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )
                        if action.selector and action.value is not None:
                            await page.select_option(
                                action.selector,
                                str(action.value),
                                timeout=action.timeout,
                            )

                    case "hover":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )
                        if action.selector:
                            await page.hover(
                                action.selector,
                                timeout=action.timeout,
                            )

                    case "screenshot":
                        # action.value = file path
                        path = str(action.value) if action.value else None
                        if path:
                            span.set_attribute(
                                "phantomfetch.action.screenshot.path", path
                            )

                        img_bytes = await page.screenshot(path=path)
                        if img_bytes:
                            span.set_attribute(
                                "phantomfetch.action.screenshot.size_bytes",
                                len(img_bytes),
                            )

                        if not path:
                            result.data = img_bytes

                    case "wait_for_load":
                        if action.timeout:
                            span.set_attribute(
                                "phantomfetch.action.timeout", action.timeout
                            )
                        await page.wait_for_load_state(
                            "networkidle", timeout=action.timeout
                        )

                    case "evaluate":
                        # action.value = JS code
                        if action.value:
                            eval_result = await page.evaluate(str(action.value))
                            result.data = eval_result

                    case "solve_captcha":
                        from ...captcha import TwoCaptchaSolver

                        solver = TwoCaptchaSolver()
                        token = await solver.solve(page, action)
                        if token:
                            result.data = token
                        else:
                            result.success = False
                            result.error = "Failed to solve CAPTCHA"

                    case _:
                        logger.warning(f"[browser] Unknown action: {action.action}")
                        result.success = False
                        result.error = f"Unknown action: {action.action}"
                        span.set_attribute("error", True)
                        span.set_attribute("phantomfetch.action.error", result.error)

            except Exception as e:
                result.success = False
                result.error = str(e)
                logger.error(f"[browser] Action failed: {action.action} - {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            finally:
                result.duration = time.perf_counter() - start_time
                span.set_attribute("phantomfetch.action.success", result.success)
                span.set_attribute(
                    "phantomfetch.action.duration_ms", result.duration * 1000
                )
                results.append(result)

    return results


def actions_to_payload(actions: list[Action]) -> list[dict]:
    """
    Convert Action objects to JSON-serializable dicts for BaaS API.

    Args:
        actions: List of Action objects

    Returns:
        List of action dicts
    """
    import msgspec

    return [msgspec.to_builtins(a) for a in actions]
