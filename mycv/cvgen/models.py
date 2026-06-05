from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Data models now live in the professional_data package
from professional_data.schema import (  # pyright: ignore[reportMissingTypeStubs]
    Affiliation,
    Education,
    Experience,
    Grant,
    Honor,
    PersonalInfo,
    PresentationRef,
    ProfessionalData,
    Project,
    PublicationRef,
    Service,
    Skill,
    Summary,
)

__all__ = [
    "ProfessionalData",
    "PersonalInfo",
    "Education",
    "Experience",
    "Project",
    "Honor",
    "Service",
    "Skill",
    "Grant",
    "Affiliation",
    "Summary",
    "PublicationRef",
    "PresentationRef",
    "CVConfigBase",
    "EntryConfig",
    "SectionConfig",
    "SectionsConfig",
    "CitationsConfig",
    "CVConfigRoot",
]


class CVConfigBase(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")


class EntryConfig(CVConfigBase):
    id: str
    display: list[Literal["compact", "extended"]] = Field(
        default_factory=lambda: ["compact", "extended"]
    )


class SectionConfig(CVConfigBase):
    entries: list[EntryConfig] = Field(default_factory=list)


class SectionsConfig(CVConfigBase):
    education: SectionConfig | None = None
    research_experience: SectionConfig | None = None
    work_experience: SectionConfig | None = None
    skills: SectionConfig | None = None
    projects: SectionConfig | None = None
    honors: SectionConfig | None = None
    service_leadership: SectionConfig | None = None
    teaching_experience: SectionConfig | None = None
    grants: SectionConfig | None = None
    extracurricular: SectionConfig | None = None
    affiliations: SectionConfig | None = None
    wetlab_skills: SectionConfig | None = None


class CitationsConfig(CVConfigBase):
    mode: Literal["selectedpubs", "all", "none", "combinepubs"]
    selected: list[str] = Field(default_factory=list)


class CVConfigRoot(CVConfigBase):
    schema_version: str
    citations: CitationsConfig
    sections: SectionsConfig

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != "1.0":
            raise ValueError("schema_version must be '1.0'")
        return value
