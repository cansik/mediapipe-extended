param(
    [string]$PackageName = "mediapipe-extended",
    [string]$PackageVersion = "0.9.1",
    [string]$BuildPath = "./build",
    [string]$DistPath = "./dist",
    [switch]$IsLocal = $False,
    [string]$MediaPipeRepository = "https://github.com/cansik/mediapipe.git",
    [string]$MediaPipeBranch = "face-geometry-python"
)

function Replace-In-File([string]$InputFile, [System.Collections.Specialized.OrderedDictionary]$Tokens) {
    $content = Get-Content -Path $InputFile -Raw

    foreach ($key in $Tokens.Keys) {
        $content = $content.Replace($key, $Tokens[$key])
    }

    Set-Content -Path C:\ReplaceDemo.txt -Value $content
}

function Try-Resolve-Path([string]$Path) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

# resolve paths
$BuildPath = Try-Resolve-Path $BuildPath
$DistPath = Try-Resolve-Path $DistPath

Write-Host -ForegroundColor Blue "Mediapipe Build Script"
Write-Host -ForegroundColor Blue "building $PackageName in $BuildPath..."

# install os specific pre-requisites and set path
$env:GLOG_logtostderr = 1

if ($IsMacOS)
{
    brew install git wget cmake protobuf bazelisk opencv@3
    brew uninstall --ignore-dependencies glog

    pip install delocate

    if ($IsLocal)
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
if (Test-Path $BuildPath)
{
    Remove-Item -Recurse -Force $BuildPath
}

# clone repository to build
git clone --recurse-submodules --shallow-submodules --depth 1 --branch $MediaPipeBranch $MediaPipeRepository $BuildPath

Push-Location $BuildPath

# rename project and setup workspace
Replace-In-File -InputFile "setup.py" -Tokens @{ "name='mediapipe'" = "name='$PackageName'" }

# build
python setup.py gen_protos
python setup.py bdist_wheel
# --plat-name macosx-12.0-arm64

Push-Location "dist"

# find wheel file
$wheels = Get-ChildItem "*.whl"
if ($wheels.Length -eq 0)
{
    Write-Host -ForegroundColor Red "Could not find wheel in dist folder. Please, check if build did not work!"
    Exit-PSSession 1
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
$OutputPath = Join-Path $DistPath $WheelFile.Name
Copy-Item -Force $WheelFile -Destination $OutputPath

Pop-Location
Pop-Location

Write-Host -ForegroundColor Blue "Done!"