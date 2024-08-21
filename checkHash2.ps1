<#
.SYNOPSIS
    Retrieves the Git hash for all files and directories in a specified directory within a repository recursively.

.DESCRIPTION
    This script finds the hash for all files and directories in the HEAD commit of a specified directory in a given repository. It outputs the hash and path for each file and directory.

.PARAMETER repo
    The path to the local copy of the repository.

.PARAMETER dir
    The relative path to the directory from the repository root.

.EXAMPLE
    .\checkHash2.ps1 -repo C:\Path\To\Repo -dir Subfolder
    Retrieves the hash for all files and directories in 'Subfolder' in the repository located at 'C:\Path\To\Repo'.

.NOTES
    Requires Git to be installed and accessible from the command line.

#>

param (
    [string]$repo, # Path to the local copy of the repository
    [string]$dir # Relative path to the directory from the repository root
)

# Save the current directory to return later
$originalPath = Get-Location

try {
    # Ensure the path to the repository is absolute
    $repo = Resolve-Path -Path $repo

    # Navigate to the repository's root directory
    Set-Location -Path $repo

    # Use git ls-tree to list all files recursively in the specified directory
    $files = git ls-tree -r HEAD -- $dir

    # Use git ls-tree to list all directories recursively in the specified directory
    $dirs = git ls-tree -d HEAD -- $dir

    # Combine files and directories
    $items = $files + "`n" + $dirs

    # Extract and output the hash and path for each file and directory
    $items -split "`n" | ForEach-Object {
        $parts = $_ -split "\s+"
        if ($parts.Length -ge 4) {
            $hash = $parts[2]
            $path = $parts[3]
            Write-Output "$path ::: $hash"
        }
    }
}
finally {
    # Return to the original directory
    Set-Location -Path $originalPath
}