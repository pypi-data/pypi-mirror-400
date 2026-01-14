from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GitDetails(BaseModel):
    repo: str
    ref: str
    sha: str
    head_ref: str
    subdirectory: str


class Dependency(BaseModel):
    name: str
    version: str | None = None
    features: list[str] | None = None
    platform: str | None = None


class Feature(BaseModel):
    name: str
    description: str
    dependencies: list[Dependency] = Field(default_factory=list)


class PortalModule(BaseModel):
    name: str
    short_name: str = ""
    version: str = ""
    description: str = ""
    options: list[str] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)


class GitStatus(BaseModel):
    repo: str | None = None
    branch: str | None = None
    commit: str | None = None
    sha: str | None = None


class LocalStatus(BaseModel):
    framework: GitStatus = Field(default_factory=GitStatus)
    registry: GitStatus = Field(default_factory=GitStatus)


class Configuration(BaseSettings):
    repo: str = "JonatanNevo/portal-framework"
    repo_branch: str = "main"
    vcpkg_registry_repo: str = "JonatanNevo/portal-vcpkg-registry"
    registry_url_template: str = "github.com:{repo}"
