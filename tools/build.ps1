param(
    [string]$PackageName = "mediapipe-extended",
    [string]$PackageVersion = "0.9.1",
    [string]$BuildPath = "./build",
    [string]$DistPath = "./dist",
    [string]$MediaPipeRepository = "https://github.com/cansik/mediapipe.git",
    [string]$MediaPipeBranch = "face-geometry-python",
    [switch]$IsAppleSilicon = $False,
    [switch]$SkipRepositorySetup = $False
)

function Replace-In-File([string]$InputFile, $Tokens)
{
    $content = Get-Content -Path $InputFile -Raw

    foreach ($key in $Tokens.Keys)
    {
        $content = $content.Replace($key, $Tokens[$key])
    }

    Set-Content -Path $InputFile -Value $content
}

function Try-Resolve-Path([string]$Path)
{
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

# resolve paths
$BuildPath = Try-Resolve-Path $BuildPath
$DistPath = Try-Resolve-Path $DistPath

# Global variables
$BDistPlatformName = ""

Write-Host -ForegroundColor Blue "Mediapipe Build Script"
Write-Host -ForegroundColor Blue "building $PackageName in $BuildPath..."

# install os specific pre-requisites and set path
$env:GLOG_logtostderr = 1

if ($IsMacOS)
{
    brew install git wget cmake protobuf bazelisk opencv@3
    brew uninstall --ignore-dependencies glog

    pip install delocate

    $BDistPlatformName = "macosx-12.0-arm64"

    if ($IsAppleSilicon)
    {
        # setting local opencv variables
        $env:PATH = "/opt/homebrew/opt/opencv@3/bin:$( $env:PATH )"
        $env:LDFLAGS = "-L/opt/homebrew/opt/opencv@3/lib"
        $env:CPPFLAGS = "-I/opt/homebrew/opt/opencv@3/include"
        $env:PKG_CONFIG_PATH = "/opt/homebrew/opt/opencv@3/lib/pkgconfig"
    }
}
elseif ($IsWindows)
{

}
elseif ($IsLinux)
{

}

# install pre-requisites
pip install wheel
pip install six

# clean build path if necessary
if (-Not$SkipRepositorySetup)
{
    if (Test-Path $BuildPath)
    {
        Remove-Item -Recurse -Force $BuildPath
    }

    # clone repository to build
    git clone --recurse-submodules --shallow-submodules --depth 1 --branch $MediaPipeBranch $MediaPipeRepository $BuildPath
}

Push-Location $BuildPath

if (-Not$SkipRepositorySetup)
{
    # rename project and setup workspace
    Replace-In-File -InputFile "setup.py" -Tokens @{
        "name='mediapipe'" = "name='$PackageName'";
        "__version__ = 'dev'" = "__version__ = '$PackageVersion'"
    }

    if ($IsMacOS)
    {
        Replace-In-File -InputFile "setup.py" -Tokens @{
            "self.link_opencv = False" = "self.link_opencv = True";
        }

        if ($IsAppleSilicon)
        {
            Replace-In-File -InputFile "WORKSPACE" -Tokens @{
                "/usr/local" = "/opt/homebrew/";
            }
        }
    }
}

# clear dist
Remove-Item -Path "dist/*.whl" -Force

# build
python setup.py gen_protos
if ($BDistPlatformName -eq "")
{
    python setup.py bdist_wheel
}
else
{
    python setup.py bdist_wheel --plat-name $BDistPlatformName
}

Push-Location "dist"

# find wheel file
[array]$wheels = Get-ChildItem "*.whl"
if ($wheels.Length -eq 0)
{
    Write-Host -ForegroundColor Red "Could not find wheel in dist folder. Please, check if build did not work!"
    exit 1
}
$WheelFile = $wheels[0]

# post-process wheel
if ($IsMacOS)
{
    delocate-wheel -v $WheelFile
}
elseif ($IsWindows)
{

}
elseif ($IsLinux)
{

}

# copy file to dist
if (!(Test-Path $DistPath))
{
    New-Item -Path $DistPath -ItemType Directory
}

$OutputPath = Join-Path $DistPath $WheelFile.Name
Copy-Item -Force $WheelFile -Destination $OutputPath

Pop-Location
Pop-Location

Write-Host -ForegroundColor Blue "Done!"