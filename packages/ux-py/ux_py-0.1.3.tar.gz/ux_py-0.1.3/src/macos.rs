//! macOS .app bundle creation

use anyhow::{Context, Result, anyhow};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use crate::config::MacOSConfig;

/// Icon sizes required for macOS .icns files
const ICON_SIZES: &[(u32, &str)] = &[
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
];

/// Generate Info.plist content
pub fn generate_info_plist(
    executable_name: &str,
    project_name: &str,
    macos_config: Option<&MacOSConfig>,
) -> String {
    let bundle_name = macos_config
        .and_then(|c| c.bundle_name.as_ref())
        .map(|s| s.as_str())
        .unwrap_or(project_name);

    let default_identifier = format!("com.ux.{}", project_name);
    let bundle_identifier = macos_config
        .and_then(|c| c.bundle_identifier.as_ref())
        .map(|s| s.as_str())
        .unwrap_or(&default_identifier);

    let version = macos_config
        .and_then(|c| c.version.as_ref())
        .map(|s| s.as_str())
        .unwrap_or("1.0.0");

    let icon_entry = macos_config
        .and_then(|c| c.icon.as_ref())
        .map(|_| "    <key>CFBundleIconFile</key>\n    <string>AppIcon</string>\n")
        .unwrap_or("");

    format!(
        r#"<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{executable_name}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_identifier}</string>
    <key>CFBundleName</key>
    <string>{bundle_name}</string>
    <key>CFBundleVersion</key>
    <string>{version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
{icon_entry}</dict>
</plist>
"#
    )
}

/// Create .app bundle directory structure
/// Returns (executable_path, info_plist_path, resources_dir)
pub fn create_app_structure(
    app_path: &Path,
    executable_name: &str,
) -> Result<(PathBuf, PathBuf, PathBuf)> {
    // Create directory structure
    let contents_dir = app_path.join("Contents");
    let macos_dir = contents_dir.join("MacOS");
    let resources_dir = contents_dir.join("Resources");

    fs::create_dir_all(&macos_dir)?;
    fs::create_dir_all(&resources_dir)?;

    let executable_path = macos_dir.join(executable_name);
    let info_plist_path = contents_dir.join("Info.plist");

    Ok((executable_path, info_plist_path, resources_dir))
}

/// Copy or convert icon file to Resources directory
/// Supports both .icns and .png files (PNG will be converted to ICNS)
pub fn copy_icon(project_dir: &Path, icon_path: &str, resources_dir: &Path) -> Result<()> {
    let source = project_dir.join(icon_path);
    if !source.exists() {
        return Err(anyhow!("Icon file not found: {}", source.display()));
    }

    let dest = resources_dir.join("AppIcon.icns");

    if icon_path.ends_with(".icns") {
        // Direct copy for .icns files
        fs::copy(&source, &dest)?;
    } else if icon_path.ends_with(".png") {
        // Convert PNG to ICNS
        println!("Converting PNG to ICNS...");
        convert_png_to_icns(&source, &dest)?;
    } else {
        return Err(anyhow!(
            "Icon must be .icns or .png format. Got: {}",
            icon_path
        ));
    }

    Ok(())
}

/// Convert PNG to ICNS using macOS iconutil
pub fn convert_png_to_icns(png_path: &Path, output_path: &Path) -> Result<()> {
    // Create temporary iconset directory
    let iconset_dir = png_path.with_extension("iconset");
    fs::create_dir_all(&iconset_dir).with_context(|| {
        format!(
            "Failed to create iconset directory: {}",
            iconset_dir.display()
        )
    })?;

    // Generate all required icon sizes using sips
    for (size, filename) in ICON_SIZES {
        let output_file = iconset_dir.join(filename);
        let status = Command::new("sips")
            .args([
                "-z",
                &size.to_string(),
                &size.to_string(),
                png_path.to_str().unwrap(),
                "--out",
                output_file.to_str().unwrap(),
            ])
            .output()
            .with_context(|| "Failed to run sips command")?;

        if !status.status.success() {
            let stderr = String::from_utf8_lossy(&status.stderr);
            return Err(anyhow!("sips failed for size {}: {}", size, stderr));
        }
    }

    // Convert iconset to icns using iconutil
    let status = Command::new("iconutil")
        .args([
            "-c",
            "icns",
            iconset_dir.to_str().unwrap(),
            "-o",
            output_path.to_str().unwrap(),
        ])
        .output()
        .with_context(|| "Failed to run iconutil command")?;

    if !status.status.success() {
        let stderr = String::from_utf8_lossy(&status.stderr);
        return Err(anyhow!("iconutil failed: {}", stderr));
    }

    // Clean up temporary iconset directory
    fs::remove_dir_all(&iconset_dir).ok();

    Ok(())
}
