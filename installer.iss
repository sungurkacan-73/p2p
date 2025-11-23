[Setup]
AppName=P2P Paylaş
AppVersion=1.0
DefaultDirName={pf}\P2P Paylaş
DefaultGroupName=P2P Paylaş
OutputBaseFilename=p2p_installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
WizardStyle=modern

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Files]
; Main executable produced by PyInstaller (expected in dist\)
Source: "{#Src}\dist\p2p_gui.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include README and license if present
Source: "{#Src}\README.md"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: FileExistsExpand('{#Src}\README.md')

[Icons]
Name: "{group}\P2P Paylaş"; Filename: "{app}\p2p_gui.exe"
Name: "{group}\Uninstall P2P Paylaş"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\p2p_gui.exe"; Description: "P2P Paylaş'ı başlat"; Flags: nowait postinstall skipifsilent

[Code]
function FileExistsExpand(path: string): boolean;
begin
  Result := ExpandConstant(path) <> '';
end;
