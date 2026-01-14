//! DMG creation for macOS application distribution

use anyhow::{Context, Result, anyhow};
use std::fs;
use std::os::unix::fs::symlink;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Create a DMG from an app bundle
pub fn create_dmg(app_path: &Path, output_dir: &Path, volume_name: &str) -> Result<PathBuf> {
    println!("Creating DMG...");

    // Create temporary directory for DMG contents
    let temp_dir = output_dir.join(".dmg_temp");
    if temp_dir.exists() {
        fs::remove_dir_all(&temp_dir)?;
    }
    fs::create_dir_all(&temp_dir)?;

    // Copy .app to temp directory
    let app_name = app_path.file_name().unwrap();
    let dest_app = temp_dir.join(app_name);
    copy_dir_recursive(app_path, &dest_app)?;

    // Create symlink to /Applications
    let applications_link = temp_dir.join("Applications");
    symlink("/Applications", &applications_link)
        .with_context(|| "Failed to create Applications symlink")?;

    // Determine output DMG path
    let dmg_name = format!("{}.dmg", volume_name);
    let dmg_path = output_dir.join(&dmg_name);

    // Remove existing DMG if present
    if dmg_path.exists() {
        fs::remove_file(&dmg_path)?;
    }

    // Create DMG using hdiutil
    let status = Command::new("hdiutil")
        .args([
            "create",
            "-volname",
            volume_name,
            "-srcfolder",
            temp_dir.to_str().unwrap(),
            "-ov",
            "-format",
            "UDZO",
            dmg_path.to_str().unwrap(),
        ])
        .output()
        .with_context(|| "Failed to run hdiutil create")?;

    // Clean up temp directory
    fs::remove_dir_all(&temp_dir).ok();

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        return Err(anyhow!("Failed to create DMG: {}", stderr));
    }

    let dmg_size = fs::metadata(&dmg_path)?.len();
    println!(
        "DMG created: {} ({:.2} MB)",
        dmg_path.display(),
        dmg_size as f64 / 1024.0 / 1024.0
    );

    Ok(dmg_path)
}

/// Recursively copy a directory
fn copy_dir_recursive(src: &Path, dst: &Path) -> Result<()> {
    fs::create_dir_all(dst)?;

    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let src_path = entry.path();
        let dst_path = dst.join(entry.file_name());

        if src_path.is_dir() {
            copy_dir_recursive(&src_path, &dst_path)?;
        } else {
            fs::copy(&src_path, &dst_path)?;
        }
    }

    Ok(())
}
