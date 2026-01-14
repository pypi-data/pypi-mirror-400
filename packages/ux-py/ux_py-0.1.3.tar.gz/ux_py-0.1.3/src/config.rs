use anyhow::{Context, Result, anyhow};
use serde::Deserialize;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize, Default)]
pub struct PyProject {
    pub project: Option<ProjectSection>,
    pub tool: Option<ToolSection>,
}

#[derive(Debug, Deserialize, Default)]
pub struct ProjectSection {
    pub name: Option<String>,
    pub scripts: Option<HashMap<String, String>>,
}

#[derive(Debug, Deserialize, Default)]
pub struct ToolSection {
    pub ux: Option<UxConfig>,
}

#[derive(Debug, Deserialize, Default, Clone)]
#[allow(dead_code)] // Used only on macOS
pub struct MacOSConfig {
    /// Path to .icns or .png icon file (PNG will be converted to ICNS)
    pub icon: Option<String>,
    /// Bundle identifier (e.g., com.example.myapp)
    pub bundle_identifier: Option<String>,
    /// Display name in Finder
    pub bundle_name: Option<String>,
    /// App version string
    pub version: Option<String>,
    /// Code signing identity (e.g., "Developer ID Application: Name (XXXXXXXXXX)")
    pub codesign_identity: Option<String>,
    /// Apple ID for notarization
    pub apple_id: Option<String>,
    /// Team ID for notarization
    pub team_id: Option<String>,
}

#[derive(Debug, Deserialize, Default, Clone)]
pub struct UxConfig {
    /// Entry point command name (from [project.scripts])
    pub entry: Option<String>,
    /// uv version to use (default: "latest")
    pub uv_version: Option<String>,
    /// Files/directories to include in bundle
    /// Default: ["*.py", "pyproject.toml", "uv.lock"]
    /// Use "dir/" suffix to include entire directory (e.g., "assets/")
    pub include: Option<Vec<String>>,
    /// macOS-specific configuration
    pub macos: Option<MacOSConfig>,
}

#[derive(Debug)]
pub struct Config {
    #[allow(dead_code)]
    pub project_dir: PathBuf,
    pub project_name: String,
    pub entry_point: String,
    pub uv_version: String,
    pub include: Vec<String>,
    #[allow(dead_code)] // Used only on macOS
    pub macos: Option<MacOSConfig>,
}

impl Config {
    /// Load configuration from project directory
    pub fn load(project_dir: &Path) -> Result<Self> {
        let pyproject_path = project_dir.join("pyproject.toml");

        if !pyproject_path.exists() {
            return Err(anyhow!(
                "pyproject.toml not found in {}",
                project_dir.display()
            ));
        }

        let content = fs::read_to_string(&pyproject_path)
            .with_context(|| format!("Failed to read {}", pyproject_path.display()))?;

        let pyproject: PyProject = toml::from_str(&content)
            .with_context(|| format!("Failed to parse {}", pyproject_path.display()))?;

        // Get project name
        let project_name = pyproject
            .project
            .as_ref()
            .and_then(|p| p.name.clone())
            .ok_or_else(|| anyhow!("[project].name is required in pyproject.toml"))?;

        // Get ux config (optional)
        let ux_config = pyproject
            .tool
            .as_ref()
            .and_then(|t| t.ux.clone())
            .unwrap_or_default();

        // Determine entry point
        let entry_point = Self::resolve_entry_point(&pyproject, &ux_config)?;

        // Get uv version
        let uv_version = ux_config.uv_version.unwrap_or_else(|| "latest".to_string());

        // Get include patterns for extra files/directories
        let include = ux_config.include.unwrap_or_default();

        // Get macOS config
        let macos = ux_config.macos.clone();

        Ok(Self {
            project_dir: project_dir.to_path_buf(),
            project_name,
            entry_point,
            uv_version,
            include,
            macos,
        })
    }

    /// Resolve entry point from config or pyproject.toml scripts
    fn resolve_entry_point(pyproject: &PyProject, ux_config: &UxConfig) -> Result<String> {
        // 1. Check [tool.ux].entry
        if let Some(entry) = &ux_config.entry {
            return Ok(entry.clone());
        }

        // 2. Check [project.scripts] - use first entry
        if let Some(scripts) = pyproject.project.as_ref().and_then(|p| p.scripts.as_ref())
            && let Some(first_script) = scripts.keys().next()
        {
            return Ok(first_script.clone());
        }

        Err(anyhow!(
            "No entry point found. Set [tool.ux].entry or define [project.scripts] in pyproject.toml"
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_load_config() {
        let dir = tempdir().unwrap();
        let pyproject_path = dir.path().join("pyproject.toml");

        let mut file = fs::File::create(&pyproject_path).unwrap();
        write!(
            file,
            r#"
[project]
name = "myapp"

[project.scripts]
myapp = "myapp.main:main"

[tool.ux]
uv_version = "0.5.0"
"#
        )
        .unwrap();

        let config = Config::load(dir.path()).unwrap();
        assert_eq!(config.project_name, "myapp");
        assert_eq!(config.entry_point, "myapp");
        assert_eq!(config.uv_version, "0.5.0");
    }

    #[test]
    fn test_explicit_entry() {
        let dir = tempdir().unwrap();
        let pyproject_path = dir.path().join("pyproject.toml");

        let mut file = fs::File::create(&pyproject_path).unwrap();
        write!(
            file,
            r#"
[project]
name = "myapp"

[project.scripts]
myapp = "myapp.main:main"
other = "myapp.other:run"

[tool.ux]
entry = "other"
"#
        )
        .unwrap();

        let config = Config::load(dir.path()).unwrap();
        assert_eq!(config.entry_point, "other");
    }
}
