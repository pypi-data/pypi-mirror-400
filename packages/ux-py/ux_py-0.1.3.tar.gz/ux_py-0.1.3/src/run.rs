use anyhow::{Context, Result};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use crate::config::Config;
use crate::download::{download_uv, get_uv_cache_dir, uv_exists};
use crate::embed::{extract_embedded_archive, has_embedded_archive, read_metadata};
use crate::platform::Platform;

/// Find uv binary in the following order:
/// 1. Same directory as ux binary (bundled mode)
/// 2. Cache directory (downloaded mode)
pub fn find_uv(platform: &Platform) -> Option<PathBuf> {
    let binary_name = platform.uv_binary_name();

    // 1. Check same directory as ux binary
    if let Ok(exe_path) = std::env::current_exe()
        && let Some(exe_dir) = exe_path.parent()
    {
        let bundled_uv = exe_dir.join(binary_name);
        if uv_exists(&bundled_uv) {
            return Some(bundled_uv);
        }
    }

    // 2. Check cache directory
    if let Ok(cache_dir) = get_uv_cache_dir() {
        let cached_uv = cache_dir.join(binary_name);
        if uv_exists(&cached_uv) {
            return Some(cached_uv);
        }
    }

    None
}

/// Ensure uv is available, downloading if necessary
pub async fn ensure_uv(platform: &Platform, version: &str) -> Result<PathBuf> {
    // First, try to find existing uv
    if let Some(uv_path) = find_uv(platform) {
        return Ok(uv_path);
    }

    // Download uv to cache directory
    let cache_dir = get_uv_cache_dir()?;
    download_uv(platform, version, &cache_dir).await
}

/// Run application from embedded archive (bundled binary mode)
pub fn run_embedded(args: &[String]) -> Result<i32> {
    // Extract embedded archive
    let extracted_dir = extract_embedded_archive()?;

    // Read metadata
    let metadata = read_metadata(&extracted_dir)?;

    // Find uv in extracted directory
    let uv_path = extracted_dir.join("uv");
    if !uv_path.exists() {
        return Err(anyhow::anyhow!("uv binary not found in bundle"));
    }

    println!("Running {} ...", metadata.entry_point);

    // Build command: uv run --project <dir> <entry_point> [args...]
    let mut cmd = Command::new(&uv_path);
    cmd.arg("run")
        .arg("--project")
        .arg(&extracted_dir)
        .arg(&metadata.entry_point);

    // Add user arguments
    for arg in args {
        cmd.arg(arg);
    }

    // Inherit stdio
    cmd.stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit());

    // Run the command
    let status = cmd
        .status()
        .with_context(|| format!("Failed to execute: {}", uv_path.display()))?;

    Ok(status.code().unwrap_or(1))
}

/// Run the application using uv (development mode)
pub async fn run_app(project_dir: &Path, args: &[String]) -> Result<i32> {
    let platform = Platform::current()?;
    let config = Config::load(project_dir)?;

    println!("Running {} ...", config.entry_point);

    // Ensure uv is available
    let uv_path = ensure_uv(&platform, &config.uv_version).await?;

    // Build command: uv run --project <dir> <entry_point> [args...]
    let mut cmd = Command::new(&uv_path);
    cmd.arg("run")
        .arg("--project")
        .arg(project_dir)
        .arg(&config.entry_point);

    // Add user arguments
    for arg in args {
        cmd.arg(arg);
    }

    // Inherit stdio
    cmd.stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit());

    // Run the command
    let status = cmd
        .status()
        .with_context(|| format!("Failed to execute: {}", uv_path.display()))?;

    Ok(status.code().unwrap_or(1))
}

/// Check if running as a bundled binary
pub fn is_bundled() -> bool {
    has_embedded_archive().unwrap_or(false)
}
