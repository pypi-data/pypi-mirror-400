use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Debug, Clone, ValueEnum)]
pub enum BundleFormat {
    /// Standard executable binary
    Binary,
    /// macOS .app bundle
    App,
}

#[derive(Parser)]
#[command(name = "ux")]
#[command(author, version, about = "uv-based Python App Launcher")]
#[command(
    long_about = "Distribute Python apps with embedded uv binary.\n\nux allows you to bundle your Python application with uv,\nso end users can run it without installing Python or uv."
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Run the Python application using embedded/downloaded uv
    Run {
        /// Working directory (default: current directory)
        #[arg(short, long)]
        project: Option<PathBuf>,

        /// Additional arguments to pass to the application
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Bundle the application with uv for distribution
    Bundle {
        /// Output directory for the bundle
        #[arg(short, long, default_value = "dist")]
        output: PathBuf,

        /// Project directory to bundle (default: current directory)
        #[arg(short, long)]
        project: Option<PathBuf>,

        /// Target platform (default: current platform)
        /// Format: os-arch (e.g., darwin-aarch64, linux-x86_64, windows-x86_64)
        #[arg(short, long)]
        target: Option<String>,

        /// Output format: binary (default) or app (macOS .app bundle)
        #[arg(long, default_value = "binary")]
        format: BundleFormat,

        /// Sign the app bundle with codesign (macOS only)
        #[arg(long)]
        codesign: bool,

        /// Notarize the app with Apple (macOS only, implies --codesign)
        #[arg(long)]
        notarize: bool,

        /// Create DMG for distribution (macOS only)
        #[arg(long)]
        dmg: bool,
    },

    /// Initialize ux configuration in pyproject.toml
    Init {
        /// Project directory (default: current directory)
        #[arg(short, long)]
        project: Option<PathBuf>,
    },
}
