<#
.SYNOPSIS
    Retrieves the Git tree hash for a specified directory within a repository.

.DESCRIPTION
    This script finds the tree hash for the HEAD commit of a specified directory in a given repository. It outputs the tree hash and optionally lists the contents of the directory as represented by the tree hash.

.PARAMETER repo
    The path to the local copy of the repository.

.PARAMETER dir
    The relative path to the directory from the repository root.

.EXAMPLE
    .\checkHash.ps1 -repo C:\Path\To\Repo -dir Subfolder
    Retrieves the tree hash for 'Subfolder' in the repository located at 'C:\Path\To\Repo'.

.NOTES
    Requires Git to be installed and accessible from the command line.

#>

param (
    [string]$repo, # Path to the local copy of the repository
    [string]$dir # Relative path to the directory from the repository root
)


# Save the current directory to return later
$originalPath = Get-Location

# Ensure the path to the repository is absolute
$repo = Resolve-Path -Path $repo

# Navigate to the repository's root directory
Set-Location -Path $repo

# Find the tree hash for the HEAD commit of the specified directory
$treeHash = git ls-tree HEAD -- $dir | ForEach-Object { ($_ -split "\s+")[2] }

# Output the tree hash
Write-Output "Tree hash for '$dir': $treeHash"

# Optionally, list contents of the directory by its tree hash
if ($treeHash) {
    $contents = git cat-file -p $treeHash
    Write-Output "Contents of '$dir':"
    Write-Output $contents
} else {
    Write-Output "Directory '$dir' not found in the current HEAD."
}

# Return to the original directory
Set-Location -Path $originalPath