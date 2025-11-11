"""Comprehensive Pydantic models for Xcode MCP tool inputs and outputs."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


# ============================================================================
# Project Management Schemas
# ============================================================================

class CreateProjectRequest(BaseModel):
    """Request to create a new Xcode project or Swift package."""
    name: str = Field(..., description="Name of the project (e.g., 'MyApp', 'MyLibrary')")
    directory: str = Field(..., description="Directory path where the project will be created (absolute or relative)")


class OpenProjectRequest(BaseModel):
    """Request to open a project or workspace in Xcode."""
    project_path: str = Field(..., description="Path to .xcodeproj or .xcworkspace file (absolute path recommended)")


class SwitchSchemeRequest(BaseModel):
    """Request to switch the active build scheme."""
    scheme: str = Field(..., description="Name of the build scheme to activate (e.g., 'MyApp', 'MyAppTests')")


class SetBuildConfigurationRequest(BaseModel):
    """Request to switch build configuration."""
    configuration: Literal["Debug", "Release"] = Field(..., description="Build configuration: 'Debug' or 'Release'")


# ============================================================================
# Build & Archive Schemas
# ============================================================================

class BuildProjectRequest(BaseModel):
    """Request to build a project using xcodebuild."""
    project_path: str = Field(..., description="Path to .xcodeproj file")
    scheme: str = Field(..., description="Build scheme name to use")


class BuildWorkspaceRequest(BaseModel):
    """Request to build a workspace."""
    workspace_path: str = Field(..., description="Path to .xcworkspace file")
    scheme: str = Field(..., description="Build scheme name to use")


class ArchiveProjectRequest(BaseModel):
    """Request to create an .xcarchive."""
    scheme: str = Field(..., description="Build scheme to archive")
    archive_path: str = Field(..., description="Output path for the .xcarchive file")


class ExportIPARequest(BaseModel):
    """Request to export .ipa from archive."""
    archive_path: str = Field(..., description="Path to the .xcarchive file")
    export_plist: str = Field(..., description="Path to export options plist file")
    export_path: str = Field(..., description="Directory where the .ipa will be exported")


# ============================================================================
# Testing Schemas
# ============================================================================

class RunTestsRequest(BaseModel):
    """Request to run tests for a project/scheme."""
    project_or_workspace: str = Field(..., description="Path to .xcodeproj or .xcworkspace")
    scheme: str = Field(..., description="Test scheme name")
    destination: Optional[str] = Field(None, description="Destination specifier (e.g., 'platform=iOS Simulator,name=iPhone 15')")


class RunUITestsRequest(BaseModel):
    """Request to run UI tests on simulator."""
    scheme: str = Field(..., description="UI test scheme name")
    destination: Optional[str] = Field(None, description="Simulator destination (e.g., 'platform=iOS Simulator,name=iPhone 15')")


class RunSpecificTestRequest(BaseModel):
    """Request to run a specific test case."""
    test_identifier: str = Field(..., description="Test identifier in format 'TestClass/testMethod' or full XCTest identifier")


class GenerateTestReportRequest(BaseModel):
    """Request to generate test report."""
    output_path: str = Field(..., description="Path where the test report will be saved (JSON or JUnit XML)")


# ============================================================================
# Simulator Schemas
# ============================================================================

class CreateSimulatorRequest(BaseModel):
    """Request to create a new simulator."""
    device_name: str = Field(..., description="Name for the simulator (e.g., 'iPhone 15 Pro', 'iPad Pro')")
    runtime: str = Field(..., description="iOS runtime version (e.g., 'iOS-17-0', 'com.apple.CoreSimulator.SimRuntime.iOS-17-0')")


class DeleteSimulatorRequest(BaseModel):
    """Request to delete a simulator."""
    udid: str = Field(..., description="Unique Device Identifier (UDID) of the simulator to delete")


class BootSimulatorRequest(BaseModel):
    """Request to boot a simulator."""
    device_name: str = Field(..., description="Name or UDID of the simulator to boot")


class SimulatorAppRequest(BaseModel):
    """Base request for simulator app operations."""
    bundle_id: str = Field(..., description="Bundle identifier of the app (e.g., 'com.example.MyApp')")


class InstallAppRequest(BaseModel):
    """Request to install app on simulator."""
    app_path: str = Field(..., description="Path to .app bundle or .ipa file")


class OpenURLRequest(BaseModel):
    """Request to open URL in simulator Safari."""
    url: str = Field(..., description="URL to open (e.g., 'https://example.com')")


class RecordVideoRequest(BaseModel):
    """Request to record simulator screen."""
    output_path: str = Field(..., description="Output path for the .mov video file")


class ScreenshotRequest(BaseModel):
    """Request to capture simulator screenshot."""
    output_path: str = Field(..., description="Output path for the screenshot image (PNG)")


# ============================================================================
# Device & Provisioning Schemas
# ============================================================================

class InstallOnDeviceRequest(BaseModel):
    """Request to install app to physical device."""
    device_id: str = Field(..., description="UDID of the physical device")
    app_path: str = Field(..., description="Path to .app bundle or .ipa file")


class UninstallFromDeviceRequest(BaseModel):
    """Request to uninstall app from device."""
    device_id: str = Field(..., description="UDID of the physical device")
    bundle_id: str = Field(..., description="Bundle identifier of the app to uninstall")


class PairDeviceRequest(BaseModel):
    """Request to pair physical device."""
    device_id: str = Field(..., description="UDID of the physical device to pair")


class ResignAppRequest(BaseModel):
    """Request to re-sign an app."""
    app_path: str = Field(..., description="Path to .app bundle or .ipa file")
    certificate: str = Field(..., description="Name or identity of the signing certificate")


# ============================================================================
# Swift & CLI Schemas
# ============================================================================

class RunSwiftScriptRequest(BaseModel):
    """Request to execute a Swift script."""
    file_path: str = Field(..., description="Path to .swift script file")


class CompileSwiftFileRequest(BaseModel):
    """Request to compile a standalone Swift file."""
    file_path: str = Field(..., description="Path to .swift source file")


class ExportLogRequest(BaseModel):
    """Request to export build log."""
    output_path: str = Field(..., description="Path where the log will be exported")


# ============================================================================
# Git & CI/CD Schemas
# ============================================================================

class GitCommitRequest(BaseModel):
    """Request to commit changes."""
    message: str = Field(..., description="Commit message")


# ============================================================================
# LLM Configuration Schemas
# ============================================================================

class SetLLMProviderRequest(BaseModel):
    """Request to switch LLM provider."""
    provider: Literal["ollama", "deepseek", "openai"] = Field(..., description="LLM provider name")
    model: Optional[str] = Field(None, description="Model name (optional, uses provider default if not specified)")


class ListLLMModelsRequest(BaseModel):
    """Request to list available models for a provider."""
    provider: Literal["ollama", "deepseek", "openai"] = Field(..., description="LLM provider name")


# ============================================================================
# Agentic AI Schemas
# ============================================================================

class SuggestTestsRequest(BaseModel):
    """Request to suggest tests for code."""
    code: str = Field(..., description="Source code to generate tests for")
    language: str = Field(default="swift", description="Programming language (default: 'swift')")


class AnalyzePerformanceProfileRequest(BaseModel):
    """Request to analyze Instruments performance profile."""
    profile_path: str = Field(..., description="Path to Instruments .trace file or performance profile")


class ExplainBuildFailureRequest(BaseModel):
    """Request to explain build failure."""
    build_log: str = Field(..., description="Build log output or error messages")


class RecommendNextActionRequest(BaseModel):
    """Request to recommend next action."""
    context: str = Field(..., description="Current context or situation description")


# ============================================================================
# Response Schemas
# ============================================================================

class ToolResult(BaseModel):
    """Standard tool execution result."""
    success: bool = Field(..., description="Whether the tool execution was successful")
    result: Dict[str, Any] = Field(default_factory=dict, description="Tool execution result data")
    error: Optional[str] = Field(None, description="Error message if execution failed")


class ProjectInfo(BaseModel):
    """Information about an Xcode project."""
    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Full path to project file")
    type: Literal["project", "workspace"] = Field(..., description="Project type")


class SchemeInfo(BaseModel):
    """Information about a build scheme."""
    name: str = Field(..., description="Scheme name")
    project: str = Field(..., description="Associated project name")


class DeviceInfo(BaseModel):
    """Information about a simulator or device."""
    name: str = Field(..., description="Device name")
    udid: str = Field(..., description="Unique Device Identifier")
    state: str = Field(..., description="Device state (e.g., 'Booted', 'Shutdown')")
    runtime: Optional[str] = Field(None, description="iOS runtime version")


class BuildInfo(BaseModel):
    """Information about a build."""
    success: bool = Field(..., description="Whether the build succeeded")
    duration: Optional[float] = Field(None, description="Build duration in seconds")
    warnings: int = Field(default=0, description="Number of warnings")
    errors: int = Field(default=0, description="Number of errors")


class TestResult(BaseModel):
    """Information about test execution."""
    passed: int = Field(..., description="Number of passed tests")
    failed: int = Field(..., description="Number of failed tests")
    total: int = Field(..., description="Total number of tests")
    duration: Optional[float] = Field(None, description="Test execution duration in seconds")


class LLMStatus(BaseModel):
    """Current LLM service status."""
    provider: str = Field(..., description="Current LLM provider")
    model: str = Field(..., description="Current model name")
    available: bool = Field(..., description="Whether the LLM service is available")
    configured: bool = Field(..., description="Whether the provider is properly configured")

