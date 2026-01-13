# src/weather_agent/agent.py
"""Weather Ensemble Agent - main agent loop.

This module implements an AI agent that uses Claude with tool calling (function calling)
to help users analyze weather forecasts. The agent follows an agentic loop pattern:
1. Receive user input
2. Send to Claude with available tools
3. Execute any tools Claude requests
4. Return results to Claude
5. Repeat until Claude provides a final answer

This pattern allows the AI to autonomously decide when and how to use tools to
accomplish the user's request.
"""

import json
from datetime import datetime

from anthropic import Anthropic

from weather_agent.config import get_api_key_or_raise
from weather_agent.tools.geocoding import geocode_location
from weather_agent.tools.statistics import (
    calculate_daily_temperature_range_statistics,
    calculate_ensemble_statistics,
    calculate_model_agreement,
    summarize_forecast_uncertainty,
)
from weather_agent.tools.weather_api import (
    fetch_daily_weather_forecast,
    fetch_weather_forecast,
    get_available_models,
)
from weather_agent.visualization.plotter import create_ensemble_uncertainty_plot


class WeatherEnsembleAgent:
    """An AI agent for weather analysis using Claude and tool calling.

    This agent demonstrates the agentic loop pattern where an AI model can:
    - Reason about which tools to use
    - Call tools autonomously
    - Process tool results
    - Provide helpful responses based on tool outputs

    Attributes:
        client: Anthropic API client for making requests to Claude
        conversation_history: List of messages (currently unused, for future expansion)
        tools: List of tool definitions that Claude can call
    """

    def __init__(self):
        """Initialize the Weather Ensemble Agent.

        Sets up the Anthropic client with the API key from configuration,
        initializes conversation history tracking, and defines available tools.

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not configured
        """
        # Get API key from config (environment, config file, or raise error)
        api_key = get_api_key_or_raise()

        # Initialize the Anthropic client
        self.client = Anthropic(api_key=api_key)

        # Track conversation history (for future use in multi-turn conversations)
        self.conversation_history = []

        # Define the tools available to the agent
        self.tools = self._define_tools()

    def _define_tools(self):
        """Define the tools available to the agent.

        Tools are defined using Anthropic's tool calling format, which follows
        JSON Schema for parameter validation. Each tool needs:
        - name: The function name that will be called
        - description: Instructions to Claude about when and how to use the tool
        - input_schema: JSON Schema defining the expected parameters

        The agent uses these definitions to:
        1. Tell Claude what tools are available
        2. Validate Claude's tool call requests
        3. Map tool names to actual Python functions

        Returns:
            list: List of tool definition dictionaries compatible with Anthropic's API
        """
        return [
            {
                "name": "geocode_location",
                "description": (
                    "Convert a location name or address to latitude/longitude "
                    "coordinates. Use this when you need coordinates for a location."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location string like 'Denver, CO' or 'New York City'",
                        }
                    },
                    "required": ["location"],
                },
            },
            {
                "name": "fetch_weather_forecast",
                "description": (
                    "Fetch weather forecast data from numerical weather models. "
                    "Returns hourly temperature (F), precipitation (inches), and "
                    "wind speed (mph) for the specified number of days. "
                    "All timestamps are in the location's local timezone."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude coordinate",
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude coordinate",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-16)",
                            "default": 7,
                        },
                        "models": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of weather models to query. "
                                "Options: 'gfs', 'ecmwf', 'gem', 'icon'. "
                                "If not specified, defaults to ['gfs']"
                            ),
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
            {
                "name": "get_available_models",
                "description": "Get list of available weather models that can be queried.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "calculate_ensemble_statistics",
                "description": (
                    "Calculate ensemble statistics (mean, median, std dev, percentiles, "
                    "spread) for a weather variable across multiple models. "
                    "Use this to quantify forecast uncertainty."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "forecast_data": {
                            "type": "object",
                            "description": (
                                "The forecast data dictionary returned by fetch_weather_forecast"
                            ),
                        },
                        "variable": {
                            "type": "string",
                            "enum": ["temperature", "precipitation", "wind_speed"],
                            "description": "Which variable to analyze",
                            "default": "temperature",
                        },
                    },
                    "required": ["forecast_data"],
                },
            },
            {
                "name": "calculate_model_agreement",
                "description": (
                    "Calculate how much different models agree with each other for a "
                    "given variable. Returns agreement scores and identifies periods of "
                    "high/low agreement."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "forecast_data": {
                            "type": "object",
                            "description": (
                                "The forecast data dictionary returned by fetch_weather_forecast"
                            ),
                        },
                        "variable": {
                            "type": "string",
                            "enum": ["temperature", "precipitation", "wind_speed"],
                            "description": "Which variable to analyze",
                            "default": "temperature",
                        },
                        "threshold": {
                            "type": "number",
                            "description": (
                                "Agreement threshold - models agree if within this value "
                                "(default: 5.0 for temp, auto-adjusted for other variables)"
                            ),
                            "default": 5.0,
                        },
                    },
                    "required": ["forecast_data"],
                },
            },
            {
                "name": "summarize_forecast_uncertainty",
                "description": (
                    "Provide a high-level summary of forecast uncertainty across all variables "
                    "(temperature, precipitation, wind). Good for getting an overall sense of "
                    "forecast confidence."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "forecast_data": {
                            "type": "object",
                            "description": (
                                "The forecast data dictionary returned by fetch_weather_forecast"
                            ),
                        }
                    },
                    "required": ["forecast_data"],
                },
            },
            {
                "name": "fetch_daily_weather_forecast",
                "description": (
                    "Fetch DAILY weather forecast summaries (daily min/max/mean) instead of "
                    "hourly data. Use this for multi-day forecasts when hourly detail isn't "
                    "needed. Much more efficient than hourly data."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude coordinate"},
                        "longitude": {"type": "number", "description": "Longitude coordinate"},
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-16)",
                            "default": 7,
                        },
                        "models": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of weather models to query. "
                                "Options: 'gfs', 'ecmwf', 'gem', 'icon'"
                            ),
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
            {
                "name": "calculate_daily_temperature_range_statistics",
                "description": (
                    "For daily forecasts, calculate ensemble statistics for BOTH "
                    "temperature_max and temperature_min. This gives complete temperature "
                    "uncertainty analysis including daily highs and lows."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "forecast_data": {
                            "type": "object",
                            "description": (
                                "The forecast data dictionary returned by "
                                "fetch_daily_weather_forecast"
                            ),
                        }
                    },
                    "required": ["forecast_data"],
                },
            },
            {
                "name": "create_ensemble_uncertainty_plot",
                "description": (
                    "Create a visualization showing ensemble forecast uncertainty. "
                    "Generates a multi-panel plot with temperature, precipitation, and wind "
                    "speed, showing individual model traces and uncertainty envelopes. "
                    "Returns the path to the saved image."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "forecast_data": {
                            "type": "object",
                            "description": (
                                "The forecast data dictionary returned by "
                                "fetch_weather_forecast or fetch_daily_weather_forecast"
                            ),
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Where to save the plot (e.g., 'outputs/denver_forecast.png')"
                            ),
                            "default": "forecast_uncertainty.png",
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the plot",
                            "default": "Weather Forecast Ensemble Analysis",
                        },
                    },
                    "required": ["forecast_data"],
                },
            },
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict):
        """Execute a tool by name with the provided inputs.

        This method acts as a dispatcher, routing tool calls from Claude to the
        actual Python functions that implement the tools. It uses the tool name
        to determine which function to call and unpacks the input dictionary
        as keyword arguments.

        Args:
            tool_name: The name of the tool to execute (e.g., "geocode_location")
            tool_input: Dictionary of parameters to pass to the tool function
                       Keys must match the function's parameter names

        Returns:
            dict: The result from the tool execution (structure varies by tool)

        Raises:
            ValueError: If the tool_name doesn't match any known tools

        Example:
            >>> agent._execute_tool("geocode_location", {"location": "Denver, CO"})
            {'latitude': 39.7392, 'longitude': -104.9903, 'display_name': '...'}
        """
        if tool_name == "geocode_location":
            # Unpack the input dict as keyword arguments using **
            return geocode_location(**tool_input)
        elif tool_name == "fetch_weather_forecast":
            return fetch_weather_forecast(**tool_input)
        elif tool_name == "get_available_models":
            return get_available_models()
        elif tool_name == "calculate_ensemble_statistics":
            return calculate_ensemble_statistics(**tool_input)
        elif tool_name == "calculate_model_agreement":
            return calculate_model_agreement(**tool_input)
        elif tool_name == "summarize_forecast_uncertainty":
            return summarize_forecast_uncertainty(**tool_input)
        elif tool_name == "fetch_daily_weather_forecast":
            return fetch_daily_weather_forecast(**tool_input)
        elif tool_name == "calculate_daily_temperature_range_statistics":
            return calculate_daily_temperature_range_statistics(**tool_input)
        elif tool_name == "create_ensemble_uncertainty_plot":
            return create_ensemble_uncertainty_plot(**tool_input)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def run(self, user_message: str, max_iterations: int = 10):
        """Run the agentic loop to process a user message.

        This is the main execution method that implements the agentic loop:
        1. Send user message + tools to Claude
        2. Claude responds with either:
           a) A final text answer (stop_reason="end_turn")
           b) Tool calls to execute (stop_reason="tool_use")
        3. If tool calls: execute them and send results back to Claude
        4. Repeat until Claude provides a final answer or max iterations reached

        The loop allows Claude to:
        - Chain multiple tool calls together
        - Make decisions based on tool results
        - Gather all needed information before responding

        Args:
            user_message: The user's request or question
            max_iterations: Maximum number of loops to prevent infinite execution.
                          Each iteration is one request to Claude. Default is 10.

        Returns:
            str: The final response from Claude, or "Max iterations reached" if
                 the loop doesn't complete within max_iterations

        Example:
            >>> agent = WeatherEnsembleAgent()
            >>> response = agent.run("What are the coordinates for Denver?")
            >>> print(response)
            The coordinates for Denver, Colorado are approximately 39.74°N, 104.99°W.
        """
        # Print a visual separator and the user's message
        print(f"\n{'=' * 60}")
        print(f"USER: {user_message}")
        print(f"{'=' * 60}\n")

        # System prompt defines the agent's role and behavior
        # This guides Claude on how to use tools and format responses
        current_date = datetime.now().strftime("%A, %B %d, %Y")

        system_prompt = f"""You are a weather analysis agent. Your goal is to help users
understand weather forecasts by analyzing data from multiple weather models.

IMPORTANT: Today's date is {current_date}. When you receive forecast data with
timestamps like "2026-01-05T00:00", convert those dates to the correct day.

You have access to:
1. Geocoding - convert location names to coordinates
2. Weather forecast data:
   - fetch_daily_weather_forecast: Use for 7-day outlooks (daily summaries)
   - fetch_weather_forecast: Use only when hourly detail is specifically needed
3. Statistical analysis tools to calculate ensemble statistics, model agreement,
   and uncertainty
4. Information about available models

CRITICAL: For multi-day forecasts, use fetch_daily_weather_forecast to avoid
overwhelming data. After fetching forecast data, ALWAYS use the statistical
analysis tools rather than manually analyzing arrays of numbers.

When a user asks about weather forecast or uncertainty:
1. Geocode the location
2. Fetch DAILY forecasts from multiple models (unless hourly detail requested)
3. Use statistical tools to analyze the data
4. Provide insights about forecast confidence

Be concise and helpful."""

        # Initialize the conversation with the user's message
        # Messages alternate between "user" and "assistant" roles
        messages = [{"role": "user", "content": user_message}]

        # Agentic loop: continue until we get a final answer or hit max iterations
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"--- Iteration {iteration} ---")

            # Send request to Claude with:
            # - model: Which Claude model to use
            # - max_tokens: Maximum length of response
            # - system: Instructions for Claude's behavior
            # - messages: Conversation history (user messages + assistant responses + tool results)
            # - tools: Available tools Claude can choose to call
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                messages=messages,
                tools=self.tools,
            )

            # stop_reason tells us why Claude stopped generating:
            # - "end_turn": Claude finished and provided a final answer
            # - "tool_use": Claude wants to call one or more tools
            # - "max_tokens": Response was cut off (rare with good max_tokens setting)
            print(f"Stop reason: {response.stop_reason}")

            # Case 1: Claude provided a final answer (no more tool calls needed)
            if response.stop_reason == "end_turn":
                # Response content is a list of blocks (text, tool_use, etc.)
                # When stop_reason is end_turn, we expect text blocks
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAGENT: {block.text}")
                        return block.text

            # Case 2: Claude wants to use tools
            elif response.stop_reason == "tool_use":
                # Add Claude's response to the conversation history
                # This preserves what Claude said and which tools it wants to call
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool call and collect results
                tool_results = []
                for block in response.content:
                    # response.content can have multiple blocks:
                    # - text blocks (if Claude explains what it's doing)
                    # - tool_use blocks (the actual tool calls)
                    if block.type == "tool_use":
                        # Log the tool call for debugging
                        print(f"\nTool call: {block.name}")
                        print(f"Input keys: {list(block.input.keys())}")

                        try:
                            # Execute the tool function
                            result = self._execute_tool(block.name, block.input)

                            # Truncate large results for display
                            result_str = json.dumps(result, indent=2)
                            if len(result_str) > 1000:
                                print(f"Result: [Large dataset - {len(result_str)} chars]")
                            else:
                                print(f"Result: {result_str}")

                            # Format result as a tool_result message to send back to Claude
                            # tool_use_id links this result to Claude's original request
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": json.dumps(result),
                                }
                            )
                        except Exception as e:
                            # If tool execution fails, send error back to Claude
                            # Claude can often handle errors gracefully and explain them to the user
                            print(f"Tool error: {str(e)}")
                            import traceback

                            traceback.print_exc()
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": json.dumps({"error": str(e)}),
                                    "is_error": True,
                                }
                            )

                # Send tool results back to Claude as a "user" message
                # This allows Claude to see the results and continue reasoning
                # The loop will then make another request with the updated messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Handle unexpected stop reasons (shouldn't normally happen)
                print(f"Unexpected stop reason: {response.stop_reason}")
                break

        return "Max iterations reached"


def main():
    """Main entry point for running the agent.

    Creates a WeatherEnsembleAgent instance and runs a sample query
    to demonstrate the agent's capabilities. This is useful for:
    - Testing the agent during development
    - Demonstrating how to use the agent
    - Quick experimentation with different queries

    To run:
        python -m weather_agent.agent
    """
    # Create an agent instance
    agent = WeatherEnsembleAgent()

    # Test with visualization
    agent.run(
        "Create a 7-day weather forecast visualization for Denver, Colorado. "
        "Include multiple models and show the uncertainty. Save it as outputs/denver_forecast.png"
    )


if __name__ == "__main__":
    main()
