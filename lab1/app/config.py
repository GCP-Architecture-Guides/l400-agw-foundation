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

"""TrialShield POC Agent Centralized Configuration Module."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AegisSettings(BaseSettings):
    """Centralized configuration for TrialShield POC Agent."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_id: str = Field(
        default="prod-proj-ge",
        validation_alias="GOOGLE_CLOUD_PROJECT",
        description="GCP Project ID hosting TrialShield POC Agent",
    )
    location: str = Field(
        default="us-central1",
        validation_alias="GOOGLE_CLOUD_LOCATION",
        description="GCP regional deployment location",
    )
    model_name: str = Field(
        default="gemini-3.7-flash",
        validation_alias="AEGIS_MODEL_NAME",
        description="Active Gemini model engine",
    )
    legacy_service_account: str = Field(
        default="sa-legacy-god-mode@prod-proj-ge.iam.gserviceaccount.com",
        validation_alias="LEGACY_SA",
        description="Over-permissioned legacy service account identity (CISO Audit Finding #6)",
    )
    app_id: str = Field(
        default="gemini-enterprise-demo_1789999455608",
        validation_alias="GEMINI_ENTERPRISE_APP_ID",
        description="Gemini Enterprise Application Hub ID",
    )


@lru_cache(maxsize=1)
def get_settings() -> AegisSettings:
    """Returns the cached singleton application settings instance."""
    return AegisSettings()


settings = get_settings()
