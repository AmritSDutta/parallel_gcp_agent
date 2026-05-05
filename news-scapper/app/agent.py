# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import LongRunningFunctionTool
from google.genai import types
from pydantic import Field, BaseModel

from .logging_config import setup_logging
import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
setup_logging()


class News(BaseModel):
    headline: str = Field(description="headline of the news.")
    summary: str = Field(description="gist of the news.")
    references: list[str] = Field(description="references of the news.")


class DailyNews(BaseModel):
    all_news: list[News] = Field(description="all news items.")


def get_news(place: str) -> str:
    """
    Retrieves the latest news for a specified location using the Exa search API.

    This function performs a targeted search for news articles published within the
    last 7 days for the given geographic location. It utilizes the ExaSearchResults
    tool to fetch content, including text snippets and highlights.

    Args:
        place (str): The name of the city, region, or location to search for news.

    Returns:
        str: A string representation of the search results, including article
             content and highlights, or an error message if the search fails.
    """
    from langchain_exa import ExaSearchResults

    # Initialize the ExaSearchResults tool
    search_tool = ExaSearchResults(exa_api_key=os.environ["EXA_API_KEY"])

    # Perform a search query using the provided place
    search_results = search_tool._run(
        query=f"latest news and updates about {place}",
        num_results=9,
        text_contents_options=True,
        highlights=True,
        start_published_date=get_publish_start_time(),
    )

    return str(search_results)


def get_publish_start_time() -> str:
    """Calculates the start time (24 hours ago) for publishing news."""
    tz = ZoneInfo('Asia/Kolkata')
    # Use explicit tz argument for awareness
    now = datetime.datetime.now(tz=tz)

    # Calculate 24 hours ago
    start_time = now - datetime.timedelta(days=1)

    # Log in a readable format
    logging.info(f"Calculated start time: {start_time.isoformat()}")

    # Return as an ISO 8601 formatted string
    return start_time.isoformat()


ai_reporter = Agent(
    name="AI_Reporter",
    model=Gemini(
        model="gemini-flash-lite-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json",
    ),
    output_schema=DailyNews,
    description="An agent that can provide news for specific town, state, country in last 24 hors.",
    instruction="""
    You are a helpful AI news generator, use get_news tool to get news of last 24 hour for the place: {}, 
    If it is not related to user's relevant place,  discard it.
    please synthesize the tool calling result with appropriate references, links.
    provide at the most 5 relevant results amongst them. 
    format should be like schema provided.
    
    """,
    tools=[
        get_news,
    ],
)

app = App(
    root_agent=ai_reporter,
    name="app",
)
