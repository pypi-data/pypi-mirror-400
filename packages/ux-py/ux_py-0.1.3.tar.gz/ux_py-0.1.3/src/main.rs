mod bundle;
mod cli;
#[cfg(target_os = "macos")]
mod codesign;
mod config;
#[cfg(target_os = "macos")]
mod dmg;
mod download;
mod embed;
#[cfg(target_os = "macos")]
mod macos;
#[cfg(target_os = "macos")]
mod notarize;
mod platform;
mod run;

use anyhow::Result;
use clap::Parser;
use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

use cli::{Cli, Commands};

#[tokio::main]
async fn main() -> ExitCode {
    // Check if this is a bundled binary
    if run::is_bundled() {
        // Running as bundled binary - run embedded application
        let args: Vec<String> = env::args().skip(1).collect();
        match run::run_embedded(&args) {
            Ok(code) => return ExitCode::from(code as u8),
            Err(e) => {
                eprintln!("Error: {:#}", e);
                return ExitCode::FAILURE;
            }
        }
    }

    // Normal CLI mode
    match run_cli().await {
        Ok(code) => ExitCode::from(code as u8),
        Err(e) => {
            eprintln!("Error: {:#}", e);
            ExitCode::FAILURE
        }
    }
}

async fn run_cli() -> Result<i32> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Run { project, args } => {
            let project_dir = resolve_project_dir(project)?;
            run::run_app(&project_dir, &args).await
        }

        Commands::Bundle {
            output,
            project,
            target,
            format,
            codesign,
            notarize,
            dmg,
        } => {
            let project_dir = resolve_project_dir(project)?;
            let target_platform = match target {
                Some(t) => Some(platform::Platform::from_target(&t)?),
                None => None,
            };

            bundle::create_bundled_binary(
                &project_dir,
                &output,
                target_platform.as_ref(),
                &format,
                codesign,
                notarize,
                dmg,
            )
            .await?;
            Ok(0)
        }

        Commands::Init { project } => {
            let project_dir = resolve_project_dir(project)?;
            bundle::init_config(&project_dir)?;
            Ok(0)
        }
    }
}

/// Resolve project directory from argument or current directory
fn resolve_project_dir(project: Option<PathBuf>) -> Result<PathBuf> {
    match project {
        Some(p) => Ok(p),
        None => env::current_dir()
            .map_err(|e| anyhow::anyhow!("Failed to get current directory: {}", e)),
    }
}
