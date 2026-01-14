//! Apple notarization for macOS applications

use anyhow::{Context, Result, anyhow};
use std::fs;
use std::path::Path;
use std::process::Command;

/// Submit app for notarization and wait for result
pub fn notarize_app(app_path: &Path, apple_id: &str, team_id: &str, password: &str) -> Result<()> {
    println!("Submitting app for notarization...");

    // Create zip for submission
    let zip_path = app_path.with_extension("zip");
    create_zip(app_path, &zip_path)?;

    // Submit to notarization service with --wait
    let status = Command::new("xcrun")
        .args([
            "notarytool",
            "submit",
            zip_path.to_str().unwrap(),
            "--apple-id",
            apple_id,
            "--team-id",
            team_id,
            "--password",
            password,
            "--wait",
        ])
        .output()
        .with_context(|| "Failed to run xcrun notarytool submit")?;

    // Clean up zip file
    fs::remove_file(&zip_path).ok();

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        let stdout = String::from_utf8_lossy(&status.stdout);
        return Err(anyhow!(
            "Notarization failed:\nstdout: {}\nstderr: {}",
            stdout,
            stderr
        ));
    }

    let stdout = String::from_utf8_lossy(&status.stdout);
    println!("{}", stdout);

    // Check if notarization was successful
    if !stdout.contains("status: Accepted") {
        return Err(anyhow!(
            "Notarization was not accepted. Check Apple's notarization log for details."
        ));
    }

    println!("Notarization successful!");

    // Staple the notarization ticket
    staple_app(app_path)?;

    Ok(())
}

/// Create a zip file from an app bundle using ditto
fn create_zip(app_path: &Path, zip_path: &Path) -> Result<()> {
    println!("Creating zip for notarization...");

    let status = Command::new("ditto")
        .args([
            "-c",
            "-k",
            "--keepParent",
            app_path.to_str().unwrap(),
            zip_path.to_str().unwrap(),
        ])
        .output()
        .with_context(|| "Failed to run ditto command")?;

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        return Err(anyhow!("Failed to create zip: {}", stderr));
    }

    Ok(())
}

/// Staple the notarization ticket to the app
fn staple_app(app_path: &Path) -> Result<()> {
    println!("Stapling notarization ticket...");

    let status = Command::new("xcrun")
        .args(["stapler", "staple", app_path.to_str().unwrap()])
        .output()
        .with_context(|| "Failed to run xcrun stapler")?;

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        return Err(anyhow!("Failed to staple notarization: {}", stderr));
    }

    println!("Stapling successful!");
    Ok(())
}

/// Get notarization credentials from config or environment variables
pub fn get_credentials(
    config_apple_id: Option<&str>,
    config_team_id: Option<&str>,
) -> Result<(String, String, String)> {
    let apple_id = config_apple_id
        .map(|s| s.to_string())
        .or_else(|| std::env::var("APPLE_ID").ok())
        .ok_or_else(|| {
            anyhow!(
                "Apple ID not found. Set apple_id in [tool.ux.macos] or APPLE_ID environment variable"
            )
        })?;

    let team_id = config_team_id
        .map(|s| s.to_string())
        .or_else(|| std::env::var("APPLE_TEAM_ID").ok())
        .ok_or_else(|| {
            anyhow!(
                "Team ID not found. Set team_id in [tool.ux.macos] or APPLE_TEAM_ID environment variable"
            )
        })?;

    let password = std::env::var("NOTARIZE_PASSWORD").map_err(|_| {
        anyhow!(
            "Notarization password not found. Set NOTARIZE_PASSWORD environment variable.\n\
            This should be an app-specific password from appleid.apple.com"
        )
    })?;

    Ok((apple_id, team_id, password))
}
