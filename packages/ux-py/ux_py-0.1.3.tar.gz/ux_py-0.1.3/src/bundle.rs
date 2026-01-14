use anyhow::{Context, Result, anyhow};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

use crate::cli::BundleFormat;
use crate::config::Config;
use crate::download::{download_uv, download_ux_stub, get_stub_cache_dir, get_uv_cache_dir};
use crate::embed::{BundleMetadata, create_archive, create_bundle};
use crate::platform::Platform;

#[cfg(target_os = "macos")]
use crate::codesign;
#[cfg(target_os = "macos")]
use crate::dmg;
#[cfg(target_os = "macos")]
use crate::macos;
#[cfg(target_os = "macos")]
use crate::notarize;

/// Create a single-file bundled executable
pub async fn create_bundled_binary(
    project_dir: &Path,
    output_path: &Path,
    target_platform: Option<&Platform>,
    format: &BundleFormat,
    do_codesign: bool,
    do_notarize: bool,
    do_dmg: bool,
) -> Result<PathBuf> {
    let config = Config::load(project_dir)?;

    // Use target platform or current platform
    let platform = match target_platform {
        Some(p) => p.clone(),
        None => Platform::current()?,
    };

    // Check format compatibility and handle .app bundle
    if matches!(format, BundleFormat::App) {
        #[cfg(target_os = "macos")]
        {
            if platform.os != crate::platform::Os::Darwin {
                return Err(anyhow!("--format app is only supported on macOS (Darwin)"));
            }
            return create_app_bundle(
                project_dir,
                output_path,
                &config,
                do_codesign,
                do_notarize,
                do_dmg,
            )
            .await;
        }
        #[cfg(not(target_os = "macos"))]
        {
            return Err(anyhow!(
                "--format app is only supported when running on macOS"
            ));
        }
    }

    // Validate macOS-only options
    if do_codesign || do_notarize || do_dmg {
        return Err(anyhow!(
            "--codesign, --notarize, and --dmg options require --format app"
        ));
    }

    // Determine output file path
    let output_file = if output_path.is_dir() {
        let binary_name = if platform.os == crate::platform::Os::Windows {
            format!("{}.exe", config.project_name)
        } else {
            config.project_name.clone()
        };
        output_path.join(binary_name)
    } else {
        output_path.to_path_buf()
    };

    // Create output directory if needed
    if let Some(parent) = output_file.parent() {
        fs::create_dir_all(parent)?;
    }

    println!("Creating bundled binary: {}", output_file.display());

    // 1. Download uv binary for target platform
    println!("Downloading uv for {} ...", platform.to_target_string());
    let uv_cache_dir = get_uv_cache_dir()?;
    let uv_path = download_uv(&platform, &config.uv_version, &uv_cache_dir).await?;

    // 2. Get stub binary (ux itself or downloaded for cross-compilation)
    let stub_binary = get_stub_binary(&platform).await?;

    // 3. Create metadata
    let metadata = BundleMetadata {
        project_name: config.project_name.clone(),
        entry_point: config.entry_point.clone(),
        uv_version: config.uv_version.clone(),
    };

    // 4. Create archive with project files
    println!("Creating archive...");
    let archive_data = create_archive(project_dir, &uv_path, &metadata, &config.include)?;

    println!("Archive size: {} bytes", archive_data.len());

    // 5. Create bundled binary
    println!("Creating bundled binary...");
    create_bundle(&stub_binary, &archive_data, &output_file)?;

    let final_size = fs::metadata(&output_file)?.len();
    println!(
        "\nBundle created successfully: {} ({:.2} MB)",
        output_file.display(),
        final_size as f64 / 1024.0 / 1024.0
    );
    println!("\nTo run:");
    println!("  ./{}", output_file.file_name().unwrap().to_string_lossy());

    Ok(output_file)
}

/// Get the stub binary for the target platform
async fn get_stub_binary(platform: &Platform) -> Result<PathBuf> {
    let current_platform = Platform::current()?;

    // Optimization: use current exe if platforms match
    if current_platform.to_target_string() == platform.to_target_string() {
        return std::env::current_exe().with_context(|| "Failed to get current executable path");
    }

    // Cross-compilation: download stub for target platform
    println!(
        "Cross-compiling for {} (current: {})",
        platform.to_target_string(),
        current_platform.to_target_string()
    );
    let stub_cache_dir = get_stub_cache_dir()?;
    download_ux_stub(platform, &stub_cache_dir).await
}

/// Initialize ux configuration in pyproject.toml
pub fn init_config(project_dir: &Path) -> Result<()> {
    let pyproject_path = project_dir.join("pyproject.toml");

    if !pyproject_path.exists() {
        return Err(anyhow!(
            "pyproject.toml not found in {}. Create one first with 'uv init'",
            project_dir.display()
        ));
    }

    // Read existing content
    let content = fs::read_to_string(&pyproject_path)?;

    // Check if [tool.ux] already exists
    if content.contains("[tool.ux]") {
        println!("[tool.ux] section already exists in pyproject.toml");
        return Ok(());
    }

    // Append [tool.ux] section
    let mut file = fs::OpenOptions::new().append(true).open(&pyproject_path)?;

    writeln!(file)?;
    writeln!(file, "[tool.ux]")?;
    writeln!(
        file,
        "# entry = \"myapp\"  # Entry point command (auto-detected from [project.scripts])"
    )?;
    writeln!(file, "# uv_version = \"latest\"  # uv version to bundle")?;
    writeln!(file)?;

    println!("Added [tool.ux] section to pyproject.toml");
    println!("Edit the configuration as needed.");

    Ok(())
}

/// Create macOS .app bundle
#[cfg(target_os = "macos")]
async fn create_app_bundle(
    project_dir: &Path,
    output_path: &Path,
    config: &Config,
    do_codesign: bool,
    do_notarize: bool,
    do_dmg: bool,
) -> Result<PathBuf> {
    let platform = Platform::current()?;

    // Determine .app path
    let app_name = format!("{}.app", config.project_name);
    let app_path = if output_path.is_dir() {
        output_path.join(&app_name)
    } else if output_path.extension().map(|e| e == "app").unwrap_or(false) {
        output_path.to_path_buf()
    } else {
        output_path.join(&app_name)
    };

    // Create output directory if needed
    if let Some(parent) = app_path.parent() {
        fs::create_dir_all(parent)?;
    }

    println!("Creating macOS app bundle: {}", app_path.display());

    // Create .app structure
    let (executable_path, info_plist_path, resources_dir) =
        macos::create_app_structure(&app_path, &config.project_name)?;

    // Download uv binary
    println!("Downloading uv for {} ...", platform.to_target_string());
    let uv_cache_dir = get_uv_cache_dir()?;
    let uv_path = download_uv(&platform, &config.uv_version, &uv_cache_dir).await?;

    // Get stub binary
    let stub_binary = get_stub_binary(&platform).await?;

    // Create metadata
    let metadata = BundleMetadata {
        project_name: config.project_name.clone(),
        entry_point: config.entry_point.clone(),
        uv_version: config.uv_version.clone(),
    };

    // Create archive
    println!("Creating archive...");
    let archive_data = create_archive(project_dir, &uv_path, &metadata, &config.include)?;

    println!("Archive size: {} bytes", archive_data.len());

    // Create bundled executable in MacOS directory
    println!("Creating bundled executable...");
    create_bundle(&stub_binary, &archive_data, &executable_path)?;

    // Generate and write Info.plist
    let info_plist = macos::generate_info_plist(
        &config.project_name,
        &config.project_name,
        config.macos.as_ref(),
    );
    fs::write(&info_plist_path, info_plist)?;

    // Copy icon if specified
    if let Some(ref macos_config) = config.macos
        && let Some(ref icon_path) = macos_config.icon
    {
        println!("Processing icon...");
        macos::copy_icon(project_dir, icon_path, &resources_dir)?;
    }

    println!("\nApp bundle created successfully: {}", app_path.display());

    // Code signing (required for notarization)
    if do_codesign || do_notarize {
        let identity = get_codesign_identity(config)?;
        codesign::sign_app_bundle(&app_path, &identity)?;
    }

    // Notarization
    if do_notarize {
        let macos_config = config.macos.as_ref();
        let (apple_id, team_id, password) = notarize::get_credentials(
            macos_config.and_then(|c| c.apple_id.as_deref()),
            macos_config.and_then(|c| c.team_id.as_deref()),
        )?;
        notarize::notarize_app(&app_path, &apple_id, &team_id, &password)?;
    }

    // DMG creation
    let final_path = if do_dmg {
        let output_dir = app_path.parent().unwrap_or(output_path);
        dmg::create_dmg(&app_path, output_dir, &config.project_name)?
    } else {
        app_path.clone()
    };

    println!("\nTo run:");
    if do_dmg {
        println!("  Mount the DMG and drag the app to Applications");
    } else {
        println!("  open {}", app_path.display());
    }

    Ok(final_path)
}

/// Get code signing identity from config or auto-detect
#[cfg(target_os = "macos")]
fn get_codesign_identity(config: &Config) -> Result<String> {
    // Check config first
    if let Some(ref macos_config) = config.macos
        && let Some(ref identity) = macos_config.codesign_identity
    {
        return Ok(identity.clone());
    }

    // Try to auto-detect
    codesign::get_default_identity()
}
