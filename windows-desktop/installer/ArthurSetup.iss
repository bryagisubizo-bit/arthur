#define MyAppName "Arthur"
#ifndef MyAppVersion
#define MyAppVersion "0.1.0"
#endif
#define MyAppPublisher "Arthur Developer"
#define MyAppExeName "Arthur.exe"

#ifexist "..\dist\Arthur\Arthur.exe"
#else
  #error "Arthur.exe is missing. From the Arthur project folder, run build_windows.bat first. Then compile this installer again."
#endif

[Setup]
AppId={{B6A5C17A-5A0C-44A0-8BA1-000000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Arthur
DefaultGroupName=Arthur
OutputDir=output
OutputBaseFilename=ArthurSetup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\Arthur.exe
SetupIconFile=..\assets\arthur_hawk.ico
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startup"; Description: "Start Arthur with Windows"; GroupDescription: "Background behavior:"; Flags: unchecked

[Files]
Source: "..\dist\Arthur\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Arthur"; Filename: "{app}\Arthur.exe"
Name: "{autodesktop}\Arthur"; Filename: "{app}\Arthur.exe"; Tasks: desktopicon
Name: "{userstartup}\Arthur"; Filename: "{app}\Arthur.exe"; Tasks: startup

[Run]
Filename: "{app}\Arthur.exe"; Description: "Launch Arthur"; Flags: nowait postinstall skipifsilent

[Code]
var
  CapabilityPage: TInputOptionWizardPage;
  SpatialProtectionPage: TInputOptionWizardPage;

function ChoiceValue(Index: Integer): String;
begin
  if CapabilityPage.Values[Index] then
    Result := 'true'
  else
    Result := 'false';
end;

function SpatialProtectionValue: String;
begin
  if SpatialProtectionPage.Values[0] then
    Result := 'password'
  else if SpatialProtectionPage.Values[1] then
    Result := 'windows_hello'
  else if SpatialProtectionPage.Values[2] then
    Result := 'local_camera_face'
  else
    Result := '';
end;

procedure InitializeWizard;
begin
  CapabilityPage := CreateInputOptionPage(
    wpSelectTasks,
    'Arthur permissions review',
    'Choose optional capabilities for first run',
    'Arthur does not need administrator access. These choices are initial local preferences only. Windows will ask separately for microphone or camera access, and you can change every option later in Arthur.',
    False,
    False
  );
  CapabilityPage.Add('Allow Arthur to offer microphone and wake-word setup');
  CapabilityPage.Add('Allow Arthur to offer local camera setup for face access or air gestures');
  CapabilityPage.Add('Allow Arthur to remain ready after its window closes (does not start listening)');
  CapabilityPage.Add('Allow API Vault and smart-home provider setup screens (does not contact any service)');
  CapabilityPage.Add('Allow reviewed PC-action setup (each action still needs in-app approval)');

  SpatialProtectionPage := CreateInputOptionPage(
    CapabilityPage.ID,
    'Spatial Room protection',
    'Select one protection method',
    'One method is required to unlock Arthur''s Spatial Room after first-run setup. This selection does not create a password, grant Windows Hello, open a camera, or retain biometric data. Arthur will guide you through the selected method on first entry.',
    True,
    False
  );
  SpatialProtectionPage.Add('Local password — create a password during first-run Spatial Room setup');
  SpatialProtectionPage.Add('Windows Hello — verify through Windows during first-run Spatial Room setup');
  SpatialProtectionPage.Add('Local camera face access — optional camera enrolment during first-run Spatial Room setup');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = SpatialProtectionPage.ID) and (SpatialProtectionValue = '') then
  begin
    MsgBox('Choose one Spatial Room protection method before continuing. You can change it later in Arthur after verifying your existing method.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConsentDirectory, ConsentFile, Content: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConsentDirectory := ExpandConstant('{userappdata}\Arthur');
    ConsentFile := ConsentDirectory + '\installer_permissions.json';
    ForceDirectories(ConsentDirectory);
    Content := '{' + #13#10 +
      '  "schema": 1,' + #13#10 +
      '  "microphone_wake_word": ' + ChoiceValue(0) + ',' + #13#10 +
      '  "camera_features": ' + ChoiceValue(1) + ',' + #13#10 +
      '  "background_ready": ' + ChoiceValue(2) + ',' + #13#10 +
      '  "network_provider_setup": ' + ChoiceValue(3) + ',' + #13#10 +
      '  "reviewed_pc_actions": ' + ChoiceValue(4) + ',' + #13#10 +
      '  "spatial_room_protection": "' + SpatialProtectionValue + '"' + #13#10 +
      '}';
    SaveStringToFile(ConsentFile, Content, False);
  end;
end;
