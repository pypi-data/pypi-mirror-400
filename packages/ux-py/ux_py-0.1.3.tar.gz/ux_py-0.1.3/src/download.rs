use anyhow::{Context, Result, anyhow};
use flate2::read::GzDecoder;
use futures_util::StreamExt;
use indicatif::{ProgressBar, ProgressStyle};
use std::fs::{self, File};
use std::io::{self, Cursor};
use std::path::{Path, PathBuf};
use tar::Archive;

use crate::platform::Platform;

/// Download and extract uv binary to the specified directory
pub async fn download_uv(platform: &Platform, version: &str, dest_dir: &Path) -> Result<PathBuf> {
    let url = platform.uv_download_url(version);
    let binary_name = platform.uv_binary_name();
    let dest_path = dest_dir.join(binary_name);

    // Create destination directory if it doesn't exist
    fs::create_dir_all(dest_dir)
        .with_context(|| format!("Failed to create directory: {}", dest_dir.display()))?;

    println!("Downloading uv from {}...", url);

    // Download with progress
    let bytes = download_with_progress(&url).await?;

    // Extract based on file extension
    if url.ends_with(".tar.gz") {
        extract_tar_gz(&bytes, dest_dir, binary_name)?;
    } else if url.ends_with(".zip") {
        extract_zip(&bytes, dest_dir, binary_name)?;
    } else {
        return Err(anyhow!("Unsupported archive format"));
    }

    // Make binary executable on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&dest_path)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&dest_path, perms)?;
    }

    Ok(dest_path)
}

/// Download a file with progress bar
async fn download_with_progress(url: &str) -> Result<Vec<u8>> {
    let client = reqwest::Client::new();

    let response = client
        .get(url)
        .send()
        .await
        .with_context(|| format!("Failed to download from {}", url))?;

    if !response.status().is_success() {
        return Err(anyhow!(
            "Download failed with status: {}",
            response.status()
        ));
    }

    let total_size = response.content_length().unwrap_or(0);

    let pb = if total_size > 0 {
        let pb = ProgressBar::new(total_size);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {bytes}/{total_bytes} ({eta})")
                .unwrap()
                .progress_chars("#>-"),
        );
        Some(pb)
    } else {
        let pb = ProgressBar::new_spinner();
        pb.set_style(
            ProgressStyle::default_spinner()
                .template("{spinner:.green} [{elapsed_precise}] {bytes}")
                .unwrap(),
        );
        Some(pb)
    };

    let mut stream = response.bytes_stream();
    let mut bytes = Vec::new();

    while let Some(chunk) = stream.next().await {
        let chunk = chunk.with_context(|| "Error while downloading")?;
        bytes.extend_from_slice(&chunk);
        if let Some(ref pb) = pb {
            pb.set_position(bytes.len() as u64);
        }
    }

    if let Some(pb) = pb {
        pb.finish_with_message("Download complete");
    }

    Ok(bytes)
}

/// Extract tar.gz archive
fn extract_tar_gz(data: &[u8], dest_dir: &Path, binary_name: &str) -> Result<()> {
    let decoder = GzDecoder::new(Cursor::new(data));
    let mut archive = Archive::new(decoder);

    for entry in archive.entries()? {
        let mut entry = entry?;
        let path = entry.path()?;

        // Look for the uv binary
        if let Some(file_name) = path.file_name()
            && file_name == binary_name
        {
            let dest_path = dest_dir.join(binary_name);
            let mut file = File::create(&dest_path)?;
            io::copy(&mut entry, &mut file)?;
            return Ok(());
        }
    }

    Err(anyhow!("Binary '{}' not found in archive", binary_name))
}

/// Extract zip archive
fn extract_zip(data: &[u8], dest_dir: &Path, binary_name: &str) -> Result<()> {
    let cursor = Cursor::new(data);
    let mut archive = zip::ZipArchive::new(cursor)?;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let name = file.name().to_string();

        // Look for the uv binary
        if name.ends_with(binary_name) || name == binary_name {
            let dest_path = dest_dir.join(binary_name);
            let mut dest_file = File::create(&dest_path)?;
            io::copy(&mut file, &mut dest_file)?;
            return Ok(());
        }
    }

    Err(anyhow!("Binary '{}' not found in archive", binary_name))
}

/// Check if uv binary exists at the given path
pub fn uv_exists(path: &Path) -> bool {
    path.exists() && path.is_file()
}

/// Get the default uv cache directory
pub fn get_uv_cache_dir() -> Result<PathBuf> {
    let cache_dir = dirs::cache_dir()
        .ok_or_else(|| anyhow!("Could not determine cache directory"))?
        .join("ux")
        .join("uv");

    Ok(cache_dir)
}

/// Get the cache directory for ux stub binaries
pub fn get_stub_cache_dir() -> Result<PathBuf> {
    let cache_dir = dirs::cache_dir()
        .ok_or_else(|| anyhow!("Could not determine cache directory"))?
        .join("ux")
        .join("stubs");

    Ok(cache_dir)
}

/// Download and extract ux stub binary for the target platform
pub async fn download_ux_stub(platform: &Platform, dest_dir: &Path) -> Result<PathBuf> {
    let url = platform.ux_download_url();
    let binary_name = platform.ux_binary_name();
    let cache_key = platform.ux_cache_key();
    let dest_path = dest_dir.join(&cache_key).join(binary_name);

    // Check if already cached
    if dest_path.exists() {
        println!("Using cached ux stub: {}", dest_path.display());
        return Ok(dest_path);
    }

    // Create destination directory if it doesn't exist
    let dest_subdir = dest_dir.join(&cache_key);
    fs::create_dir_all(&dest_subdir)
        .with_context(|| format!("Failed to create directory: {}", dest_subdir.display()))?;

    println!("Downloading ux stub from {}...", url);

    // Download with progress
    let bytes = download_with_progress(&url).await?;

    // Extract based on file extension
    if url.ends_with(".tar.gz") {
        extract_tar_gz(&bytes, &dest_subdir, binary_name)?;
    } else if url.ends_with(".zip") {
        extract_zip(&bytes, &dest_subdir, binary_name)?;
    } else {
        return Err(anyhow!("Unsupported archive format"));
    }

    // Make binary executable on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&dest_path)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&dest_path, perms)?;
    }

    Ok(dest_path)
}
