[Setup]
AppName=Makhai Rep Grind Tracker
AppVersion=0.90
DefaultDirName=C:\MRGT
DefaultGroupName=MRGT
OutputBaseFilename=MRGT_Installer
SetupIconFile=mrgt_icon.ico
LicenseFile=LICENSE.txt
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\\MRGT.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\MRGT"; Filename: "{app}\\MRGT.exe"
Name: "{commondesktop}\\MRGT"; Filename: "{app}\\MRGT.exe"; Tasks: desktopicon
