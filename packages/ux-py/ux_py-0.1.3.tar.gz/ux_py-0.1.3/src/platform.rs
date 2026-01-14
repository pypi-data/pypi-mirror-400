use anyhow::{Result, anyhow};

#[derive(Debug, Clone, PartialEq)]
pub enum Os {
    Darwin,
    Linux,
    Windows,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Arch {
    X86_64,
    Aarch64,
}

#[derive(Debug, Clone)]
pub struct Platform {
    pub os: Os,
    pub arch: Arch,
}

impl Platform {
    /// Detect current platform
    pub fn current() -> Result<Self> {
        let os = if cfg!(target_os = "macos") {
            Os::Darwin
        } else if cfg!(target_os = "linux") {
            Os::Linux
        } else if cfg!(target_os = "windows") {
            Os::Windows
        } else {
            return Err(anyhow!("Unsupported operating system"));
        };

        let arch = if cfg!(target_arch = "x86_64") {
            Arch::X86_64
        } else if cfg!(target_arch = "aarch64") {
            Arch::Aarch64
        } else {
            return Err(anyhow!("Unsupported architecture"));
        };

        Ok(Self { os, arch })
    }

    /// Parse platform from string (e.g., "darwin-aarch64")
    pub fn from_target(target: &str) -> Result<Self> {
        let parts: Vec<&str> = target.split('-').collect();
        if parts.len() != 2 {
            return Err(anyhow!(
                "Invalid target format. Expected: os-arch (e.g., darwin-aarch64)"
            ));
        }

        let os = match parts[0].to_lowercase().as_str() {
            "darwin" | "macos" => Os::Darwin,
            "linux" => Os::Linux,
            "windows" | "win" => Os::Windows,
            _ => return Err(anyhow!("Unsupported OS: {}", parts[0])),
        };

        let arch = match parts[1].to_lowercase().as_str() {
            "x86_64" | "amd64" | "x64" => Arch::X86_64,
            "aarch64" | "arm64" => Arch::Aarch64,
            _ => return Err(anyhow!("Unsupported architecture: {}", parts[1])),
        };

        Ok(Self { os, arch })
    }

    /// Get uv download URL for this platform
    pub fn uv_download_url(&self, version: &str) -> String {
        let os_str = match self.os {
            Os::Darwin => "apple-darwin",
            Os::Linux => "unknown-linux-gnu",
            Os::Windows => "pc-windows-msvc",
        };

        let arch_str = match self.arch {
            Arch::X86_64 => "x86_64",
            Arch::Aarch64 => "aarch64",
        };

        let ext = match self.os {
            Os::Windows => "zip",
            _ => "tar.gz",
        };

        if version == "latest" {
            format!(
                "https://github.com/astral-sh/uv/releases/latest/download/uv-{}-{}.{}",
                arch_str, os_str, ext
            )
        } else {
            format!(
                "https://github.com/astral-sh/uv/releases/download/{}/uv-{}-{}.{}",
                version, arch_str, os_str, ext
            )
        }
    }

    /// Get the uv binary name for this platform
    pub fn uv_binary_name(&self) -> &'static str {
        match self.os {
            Os::Windows => "uv.exe",
            _ => "uv",
        }
    }

    /// Get the ux binary name for this platform
    pub fn ux_binary_name(&self) -> &'static str {
        match self.os {
            Os::Windows => "ux.exe",
            _ => "ux",
        }
    }

    /// Get ux stub download URL for this platform
    pub fn ux_download_url(&self) -> String {
        let os_str = match self.os {
            Os::Darwin => "apple-darwin",
            Os::Linux => "unknown-linux-gnu",
            Os::Windows => "pc-windows-msvc",
        };

        let arch_str = match self.arch {
            Arch::X86_64 => "x86_64",
            Arch::Aarch64 => "aarch64",
        };

        let ext = match self.os {
            Os::Windows => "zip",
            _ => "tar.gz",
        };

        format!(
            "https://github.com/i2y/ux/releases/latest/download/ux-{}-{}.{}",
            arch_str, os_str, ext
        )
    }

    /// Get the ux stub cache key (used for cache directory naming)
    pub fn ux_cache_key(&self) -> String {
        format!("{}-{}", self.to_target_string(), self.ux_binary_name())
    }

    /// Convert to target string
    pub fn to_target_string(&self) -> String {
        let os = match self.os {
            Os::Darwin => "darwin",
            Os::Linux => "linux",
            Os::Windows => "windows",
        };
        let arch = match self.arch {
            Arch::X86_64 => "x86_64",
            Arch::Aarch64 => "aarch64",
        };
        format!("{}-{}", os, arch)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_target() {
        let p = Platform::from_target("darwin-aarch64").unwrap();
        assert_eq!(p.os, Os::Darwin);
        assert_eq!(p.arch, Arch::Aarch64);

        let p = Platform::from_target("linux-x86_64").unwrap();
        assert_eq!(p.os, Os::Linux);
        assert_eq!(p.arch, Arch::X86_64);
    }

    #[test]
    fn test_uv_download_url() {
        let p = Platform {
            os: Os::Darwin,
            arch: Arch::Aarch64,
        };
        let url = p.uv_download_url("latest");
        assert!(url.contains("aarch64-apple-darwin"));
        assert!(url.ends_with(".tar.gz"));

        let p = Platform {
            os: Os::Windows,
            arch: Arch::X86_64,
        };
        let url = p.uv_download_url("0.5.0");
        assert!(url.contains("x86_64-pc-windows-msvc"));
        assert!(url.ends_with(".zip"));
    }

    #[test]
    fn test_ux_download_url() {
        let p = Platform {
            os: Os::Darwin,
            arch: Arch::Aarch64,
        };
        let url = p.ux_download_url();
        assert!(url.contains("aarch64-apple-darwin"));
        assert!(url.contains("i2y/ux/releases"));
        assert!(url.ends_with(".tar.gz"));

        let p = Platform {
            os: Os::Linux,
            arch: Arch::X86_64,
        };
        let url = p.ux_download_url();
        assert!(url.contains("x86_64-unknown-linux-gnu"));
        assert!(url.ends_with(".tar.gz"));

        let p = Platform {
            os: Os::Windows,
            arch: Arch::X86_64,
        };
        let url = p.ux_download_url();
        assert!(url.contains("x86_64-pc-windows-msvc"));
        assert!(url.ends_with(".zip"));
    }
}
