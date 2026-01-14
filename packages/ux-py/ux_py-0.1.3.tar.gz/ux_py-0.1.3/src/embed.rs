use anyhow::{Context, Result, anyhow};
use flate2::Compression;
use flate2::read::GzDecoder;
use flate2::write::GzEncoder;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs::{self, File};
use std::io::{BufReader, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use tar::{Archive, Builder};

/// Magic marker at the end of bundled binary
const MAGIC_MARKER: &[u8; 8] = b"UXARCHIV";

/// Metadata stored in the archive
#[derive(Debug, Serialize, Deserialize)]
pub struct BundleMetadata {
    pub project_name: String,
    pub entry_point: String,
    pub uv_version: String,
}

/// Check if the current binary has an embedded archive
pub fn has_embedded_archive() -> Result<bool> {
    let exe_path = std::env::current_exe()?;
    let mut file = File::open(&exe_path)?;

    // Seek to end - 8 bytes (magic marker)
    file.seek(SeekFrom::End(-8))?;

    let mut marker = [0u8; 8];
    file.read_exact(&mut marker)?;

    Ok(&marker == MAGIC_MARKER)
}

/// Extract embedded archive to cache directory
/// Returns the path to the extracted directory
pub fn extract_embedded_archive() -> Result<PathBuf> {
    let exe_path = std::env::current_exe()?;
    let mut file = BufReader::new(File::open(&exe_path)?);

    // Read magic marker
    file.seek(SeekFrom::End(-8))?;
    let mut marker = [0u8; 8];
    file.read_exact(&mut marker)?;

    if &marker != MAGIC_MARKER {
        return Err(anyhow!("No embedded archive found"));
    }

    // Read archive size (8 bytes before magic marker)
    file.seek(SeekFrom::End(-16))?;
    let mut size_bytes = [0u8; 8];
    file.read_exact(&mut size_bytes)?;
    let archive_size = u64::from_be_bytes(size_bytes);

    // Calculate archive start position
    let archive_start = file.seek(SeekFrom::End(0))? - 16 - archive_size;

    // Calculate hash for cache directory
    let cache_hash = calculate_archive_hash(&exe_path, archive_start, archive_size)?;
    let cache_dir = get_cache_dir()?.join(&cache_hash);

    // Check if already extracted
    let metadata_path = cache_dir.join(".ux_metadata.json");
    if metadata_path.exists() {
        return Ok(cache_dir);
    }

    // Extract archive
    println!("Extracting application...");

    // Read archive data
    file.seek(SeekFrom::Start(archive_start))?;
    let mut archive_data = vec![0u8; archive_size as usize];
    file.read_exact(&mut archive_data)?;

    // Decompress and extract
    let decoder = GzDecoder::new(&archive_data[..]);
    let mut archive = Archive::new(decoder);

    fs::create_dir_all(&cache_dir)?;
    archive.unpack(&cache_dir)?;

    // Make binaries executable on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let uv_path = cache_dir.join("uv");
        if uv_path.exists() {
            let mut perms = fs::metadata(&uv_path)?.permissions();
            perms.set_mode(0o755);
            fs::set_permissions(&uv_path, perms)?;
        }
    }

    Ok(cache_dir)
}

/// Read bundle metadata from extracted directory
pub fn read_metadata(extracted_dir: &Path) -> Result<BundleMetadata> {
    let metadata_path = extracted_dir.join(".ux_metadata.json");
    let content =
        fs::read_to_string(&metadata_path).with_context(|| "Failed to read bundle metadata")?;
    let metadata: BundleMetadata = serde_json::from_str(&content)?;
    Ok(metadata)
}

/// Create a bundled binary
pub fn create_bundle(stub_binary: &Path, archive_data: &[u8], output_path: &Path) -> Result<()> {
    // Copy stub binary
    fs::copy(stub_binary, output_path)?;

    // Append archive
    let mut file = fs::OpenOptions::new().append(true).open(output_path)?;

    // Write archive data
    file.write_all(archive_data)?;

    // Write archive size (8 bytes, big endian)
    let size_bytes = (archive_data.len() as u64).to_be_bytes();
    file.write_all(&size_bytes)?;

    // Write magic marker
    file.write_all(MAGIC_MARKER)?;

    // Make executable on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(output_path)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(output_path, perms)?;
    }

    Ok(())
}

/// Create tar.gz archive from project files
pub fn create_archive(
    project_dir: &Path,
    uv_binary: &Path,
    metadata: &BundleMetadata,
    include_patterns: &[String],
) -> Result<Vec<u8>> {
    let mut archive_data = Vec::new();

    {
        let encoder = GzEncoder::new(&mut archive_data, Compression::default());
        let mut builder = Builder::new(encoder);

        // Add uv binary
        builder.append_path_with_name(uv_binary, "uv")?;

        // Add metadata
        let metadata_json = serde_json::to_string_pretty(metadata)?;
        let metadata_bytes = metadata_json.as_bytes();
        let mut header = tar::Header::new_gnu();
        header.set_path(".ux_metadata.json")?;
        header.set_size(metadata_bytes.len() as u64);
        header.set_mode(0o644);
        header.set_cksum();
        builder.append(&header, metadata_bytes)?;

        // Add required project files
        for file in &["pyproject.toml", "uv.lock", "README.md", "LICENSE"] {
            let file_path = project_dir.join(file);
            if file_path.exists() {
                builder.append_path_with_name(&file_path, file)?;
            }
        }

        // Find and add package directory
        let package_name = &metadata.project_name;
        let package_dir = find_package_dir(project_dir, package_name)?;
        add_package_directory(&mut builder, project_dir, &package_dir)?;

        // Add extra files/directories from include patterns
        add_extra_includes(&mut builder, project_dir, include_patterns)?;

        builder.finish()?;
    }

    Ok(archive_data)
}

/// Find the package directory (flat layout or src layout)
fn find_package_dir(project_dir: &Path, package_name: &str) -> Result<PathBuf> {
    // Try flat layout: ./package_name/
    let flat_path = project_dir.join(package_name);
    if flat_path.is_dir() {
        return Ok(PathBuf::from(package_name));
    }

    // Try src layout: ./src/package_name/
    let src_path = project_dir.join("src").join(package_name);
    if src_path.is_dir() {
        return Ok(PathBuf::from("src").join(package_name));
    }

    // Try with underscores instead of hyphens
    let package_name_underscore = package_name.replace('-', "_");
    let flat_path_underscore = project_dir.join(&package_name_underscore);
    if flat_path_underscore.is_dir() {
        return Ok(PathBuf::from(&package_name_underscore));
    }

    let src_path_underscore = project_dir.join("src").join(&package_name_underscore);
    if src_path_underscore.is_dir() {
        return Ok(PathBuf::from("src").join(&package_name_underscore));
    }

    Err(anyhow!(
        "Package directory not found. Tried: {}, src/{}, {}, src/{}",
        package_name,
        package_name,
        package_name_underscore,
        package_name_underscore
    ))
}

/// Add package directory contents to archive
fn add_package_directory<W: Write>(
    builder: &mut Builder<W>,
    base_dir: &Path,
    package_relative_path: &Path,
) -> Result<()> {
    let full_path = base_dir.join(package_relative_path);

    for entry in fs::read_dir(&full_path)? {
        let entry = entry?;
        let file_name = entry.file_name();
        let file_name_str = file_name.to_string_lossy();

        // Skip __pycache__ directories
        if file_name_str == "__pycache__" {
            continue;
        }

        let entry_relative = package_relative_path.join(&file_name);
        let entry_path = entry.path();

        if entry_path.is_dir() {
            add_package_directory(builder, base_dir, &entry_relative)?;
        } else {
            builder.append_path_with_name(&entry_path, &entry_relative)?;
        }
    }

    Ok(())
}

/// Add extra files/directories specified in include patterns
fn add_extra_includes<W: Write>(
    builder: &mut Builder<W>,
    base_dir: &Path,
    include_patterns: &[String],
) -> Result<()> {
    for pattern in include_patterns {
        if pattern.ends_with('/') {
            // Directory pattern (e.g., "assets/")
            let dir_name = &pattern[..pattern.len() - 1];
            let dir_path = base_dir.join(dir_name);
            if dir_path.is_dir() {
                add_directory_recursive(builder, base_dir, Path::new(dir_name))?;
            }
        } else if !pattern.contains('*') {
            // Specific file (e.g., "config.yaml")
            let file_path = base_dir.join(pattern);
            if file_path.is_file() {
                builder.append_path_with_name(&file_path, pattern)?;
            }
        }
        // Skip glob patterns like "*.py" - package directory handles those
    }
    Ok(())
}

/// Add directory contents recursively (skip __pycache__)
fn add_directory_recursive<W: Write>(
    builder: &mut Builder<W>,
    base_dir: &Path,
    relative_path: &Path,
) -> Result<()> {
    let full_path = base_dir.join(relative_path);

    for entry in fs::read_dir(&full_path)? {
        let entry = entry?;
        let file_name = entry.file_name();
        let file_name_str = file_name.to_string_lossy();

        // Skip __pycache__
        if file_name_str == "__pycache__" {
            continue;
        }

        let entry_relative = relative_path.join(&file_name);
        let entry_path = entry.path();

        if entry_path.is_dir() {
            add_directory_recursive(builder, base_dir, &entry_relative)?;
        } else {
            builder.append_path_with_name(&entry_path, &entry_relative)?;
        }
    }

    Ok(())
}

/// Calculate hash of archive for cache directory name
fn calculate_archive_hash(exe_path: &Path, start: u64, size: u64) -> Result<String> {
    let mut file = File::open(exe_path)?;
    file.seek(SeekFrom::Start(start))?;

    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 8192];
    let mut remaining = size;

    while remaining > 0 {
        let to_read = std::cmp::min(remaining as usize, buffer.len());
        let read = file.read(&mut buffer[..to_read])?;
        if read == 0 {
            break;
        }
        hasher.update(&buffer[..read]);
        remaining -= read as u64;
    }

    let hash = hasher.finalize();
    Ok(format!("{:x}", hash)[..16].to_string())
}

/// Get cache directory for extracted bundles
pub fn get_cache_dir() -> Result<PathBuf> {
    let cache_dir = dirs::cache_dir()
        .ok_or_else(|| anyhow!("Could not determine cache directory"))?
        .join("ux")
        .join("bundles");

    fs::create_dir_all(&cache_dir)?;
    Ok(cache_dir)
}
