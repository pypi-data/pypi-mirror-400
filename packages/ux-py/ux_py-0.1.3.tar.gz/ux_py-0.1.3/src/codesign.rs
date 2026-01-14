//! Code signing for macOS applications

use anyhow::{Context, Result, anyhow};
use std::path::Path;
use std::process::Command;

/// Sign an app bundle with codesign
pub fn sign_app_bundle(app_path: &Path, identity: &str) -> Result<()> {
    println!("Signing app bundle with identity: {}", identity);

    let status = Command::new("codesign")
        .args([
            "--deep",
            "--force",
            "--verify",
            "--verbose",
            "--sign",
            identity,
            "--options",
            "runtime",
            app_path.to_str().unwrap(),
        ])
        .output()
        .with_context(|| "Failed to run codesign command")?;

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        return Err(anyhow!("Code signing failed: {}", stderr));
    }

    println!("Code signing successful");
    Ok(())
}

/// Verify code signature of an app bundle
#[allow(dead_code)]
pub fn verify_signature(app_path: &Path) -> Result<bool> {
    let status = Command::new("codesign")
        .args([
            "--verify",
            "--deep",
            "--strict",
            "--verbose=2",
            app_path.to_str().unwrap(),
        ])
        .output()
        .with_context(|| "Failed to run codesign verify command")?;

    Ok(status.status.success())
}

/// List available signing identities
pub fn list_signing_identities() -> Result<Vec<String>> {
    let output = Command::new("security")
        .args(["find-identity", "-v", "-p", "codesigning"])
        .output()
        .with_context(|| "Failed to run security find-identity command")?;

    if !output.status.success() {
        return Err(anyhow!("Failed to list signing identities"));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let identities: Vec<String> = stdout
        .lines()
        .filter(|line| line.contains("Developer ID Application"))
        .filter_map(|line| {
            // Extract identity string between quotes
            let start = line.find('"')?;
            let end = line.rfind('"')?;
            if start < end {
                Some(line[start + 1..end].to_string())
            } else {
                None
            }
        })
        .collect();

    Ok(identities)
}

/// Find default signing identity or return error with available options
pub fn get_default_identity() -> Result<String> {
    let identities = list_signing_identities()?;

    if identities.is_empty() {
        return Err(anyhow!(
            "No code signing identities found.\n\
            Please install a Developer ID Application certificate from Apple Developer."
        ));
    }

    if identities.len() == 1 {
        return Ok(identities.into_iter().next().unwrap());
    }

    // Multiple identities found, show them
    let mut msg = String::from("Multiple signing identities found. Please specify one:\n");
    for identity in &identities {
        msg.push_str(&format!("  - {}\n", identity));
    }
    msg.push_str("\nSet codesign_identity in [tool.ux.macos] section of pyproject.toml");

    Err(anyhow!(msg))
}
